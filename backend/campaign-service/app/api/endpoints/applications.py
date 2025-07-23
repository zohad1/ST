# app/api/endpoints/applications.py
from fastapi import APIRouter, Depends, status, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
import logging

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.schemas.application import (
    CreatorApplicationCreate, 
    CreatorApplicationResponse, 
    CreatorApplicationUpdate
)
from app.services.application_service import ApplicationService

logger = logging.getLogger(__name__)

# Create router WITHOUT prefix (prefix is added in main.py)
router = APIRouter(
    tags=["applications"]
)

@router.post("/", response_model=CreatorApplicationResponse, status_code=status.HTTP_201_CREATED)
async def apply_to_campaign(
    application: CreatorApplicationCreate,
    current_user: dict = Depends(require_role(["creator"])),
    db: Session = Depends(get_db)
):
    """
    Creator applies to a campaign.
    
    Required role: creator
    """
    logger.info(f"Creator {current_user['id']} applying to campaign {application.campaign_id}")
    
    try:
        service = ApplicationService(db)
        result = service.create_application(application, creator_id=UUID(current_user["id"]))
        logger.info(f"Application created successfully with ID: {result.id}")
        return result
    except Exception as e:
        logger.error(f"Error creating application: {str(e)}")
        if "already applied" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied to this campaign"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create application: {str(e)}"
        )

@router.get("/my-applications", response_model=List[CreatorApplicationResponse])
async def get_my_applications(
    current_user: dict = Depends(require_role(["creator"])),
    db: Session = Depends(get_db)
):
    """
    Get creator's own applications.
    
    Required role: creator
    """
    logger.info(f"Fetching applications for creator {current_user['id']}")
    
    try:
        service = ApplicationService(db)
        applications = service.get_creator_applications(creator_id=UUID(current_user["id"]))
        logger.info(f"Found {len(applications)} applications for creator")
        return applications
    except Exception as e:
        logger.error(f"Error fetching creator applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )

@router.put("/{application_id}/review", response_model=CreatorApplicationResponse)
async def review_application(
    application_id: UUID,
    review_data: CreatorApplicationUpdate,
    current_user: dict = Depends(require_role(["agency", "brand", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Agency/Brand reviews creator application.
    
    Required role: agency, brand, or admin
    """
    logger.info(f"User {current_user['id']} reviewing application {application_id}")
    logger.info(f"Review data: status={review_data.status}, rejection_reason={review_data.rejection_reason}")
    
    try:
        service = ApplicationService(db)
        result = service.review_application(
            application_id, 
            review_data, 
            reviewer_id=UUID(current_user["id"])
        )
        logger.info(f"Application {application_id} reviewed successfully")
        return result
    except Exception as e:
        logger.error(f"Error reviewing application: {str(e)}")
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Application not found"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to review application: {str(e)}"
        )

@router.get("/campaign/{campaign_id}", response_model=List[CreatorApplicationResponse])
async def get_campaign_applications(
    campaign_id: UUID,
    status_filter: Optional[str] = Query(None, description="Filter by status (pending, approved, rejected)"),
    limit: int = Query(100, le=1000, description="Maximum number of applications to return"),
    offset: int = Query(0, ge=0, description="Number of applications to skip"),
    current_user: dict = Depends(require_role(["agency", "brand", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Get all applications for a campaign with full creator details.
    
    This endpoint returns applications with nested creator information including:
    - Basic profile (name, email, phone)
    - Social media handles and follower counts
    - Audience demographics
    - Profile completion status
    
    Required role: agency, brand, or admin
    """
    logger.info(f"Fetching applications for campaign {campaign_id}")
    logger.info(f"Filters: status={status_filter}, limit={limit}, offset={offset}")
    logger.info(f"Requested by user {current_user['id']} with role {current_user['role']}")
    
    try:
        service = ApplicationService(db)
        applications = service.get_campaign_applications(campaign_id, status_filter)
        
        # Apply pagination
        total_count = len(applications)
        paginated_apps = applications[offset:offset + limit]
        
        logger.info(f"Found {total_count} total applications, returning {len(paginated_apps)} after pagination")
        
        # Log sample data for debugging
        if paginated_apps and len(paginated_apps) > 0:
            first_app = paginated_apps[0]
            logger.debug(f"Sample application data - ID: {first_app.id}, Status: {first_app.status}")
            if hasattr(first_app, 'creator') and first_app.creator:
                logger.debug(f"Creator data included: {first_app.creator.username if hasattr(first_app.creator, 'username') else 'No username'}")
            else:
                logger.warning("No creator data included in application response")
        
        return paginated_apps
        
    except Exception as e:
        logger.error(f"Error fetching campaign applications: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )

@router.get("/statistics")
async def get_application_statistics(
    campaign_id: Optional[UUID] = Query(None, description="Filter statistics by campaign"),
    current_user: dict = Depends(require_role(["agency", "brand", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Get application statistics.
    
    Returns statistics including:
    - Total applications
    - Applications by status (pending, approved, rejected)
    - Approval rate
    - Average response time
    
    Required role: agency, brand, or admin
    """
    logger.info(f"Fetching application statistics for user {current_user['id']}")
    if campaign_id:
        logger.info(f"Filtering by campaign: {campaign_id}")
    
    try:
        service = ApplicationService(db)
        stats = service.get_application_statistics(campaign_id)
        logger.info(f"Statistics retrieved: {stats}")
        return stats
    except Exception as e:
        logger.error(f"Error fetching application statistics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch statistics: {str(e)}"
        )

@router.get("/", response_model=List[CreatorApplicationResponse])
async def get_applications_with_filters(
    search: Optional[str] = Query(None, description="Search by creator name, email, or username"),
    status: Optional[str] = Query(None, description="Filter by application status"),
    campaign_name: Optional[str] = Query(None, description="Filter by campaign name"),
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(100, le=1000, description="Maximum number of applications to return"),
    current_user: dict = Depends(require_role(["agency", "brand", "admin"])),
    db: Session = Depends(get_db)
):
    """
    Get applications with advanced filtering.
    
    Supports filtering by:
    - Creator name/email/username (search)
    - Application status
    - Campaign name
    
    Required role: agency, brand, or admin
    """
    logger.info(f"Fetching filtered applications for user {current_user['id']}")
    logger.info(f"Filters: search={search}, status={status}, campaign={campaign_name}")
    
    try:
        service = ApplicationService(db)
        result = service.get_applications_with_filters(
            search=search,
            status=status,
            campaign_name=campaign_name,
            skip=skip,
            limit=limit
        )
        
        # Handle different response formats from service
        if isinstance(result, dict) and 'applications' in result:
            applications = result['applications']
            logger.info(f"Found {result.get('total', len(applications))} total applications")
            return applications
        elif isinstance(result, list):
            logger.info(f"Found {len(result)} applications")
            return result
        else:
            logger.warning(f"Unexpected result format: {type(result)}")
            return []
            
    except Exception as e:
        logger.error(f"Error fetching filtered applications: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch applications: {str(e)}"
        )

# Log router initialization
logger.info(f"Applications router initialized with {len(router.routes)} routes:")
for route in router.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        logger.info(f"  - {route.methods} {route.path}")