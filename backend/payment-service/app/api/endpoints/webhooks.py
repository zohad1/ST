
# app/api/endpoints/webhooks.py
from fastapi import APIRouter, Request, HTTPException, status, Header, Depends
from sqlalchemy.orm import Session
from typing import Optional
import json
import logging

from app.core.database import get_db
from app.services.webhook_service import WebhookProcessingService
from app.external.stripe_client import StripeClient
from app.external.fanbasis_client import FanbasisClient

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/stripe")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="stripe-signature"),
    db: Session = Depends(get_db)
):
    """Handle Stripe webhook events"""
    
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature header"
        )
    
    try:
        # Get raw body
        payload = await request.body()
        
        # Verify webhook signature
        stripe_client = StripeClient()
        if not stripe_client.verify_webhook_signature(payload, stripe_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )
        
        # Parse event
        event = stripe_client.parse_webhook_event(payload, stripe_signature)
        if not event:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook payload"
            )
        
        # Process webhook
        webhook_service = WebhookProcessingService(db)
        result = await webhook_service.process_stripe_webhook(event)
        
        logger.info(f"Processed Stripe webhook: {event['type']}")
        return {"status": "success", "processed": result.success}
        
    except Exception as e:
        logger.error(f"Error processing Stripe webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook processing failed: {str(e)}"
        )

@router.post("/fanbasis")
async def fanbasis_webhook(
    request: Request,
    x_webhook_signature: str = Header(None, alias="x-webhook-signature"),
    db: Session = Depends(get_db)
):
    """Handle Fanbasis webhook events"""
    
    if not x_webhook_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Fanbasis signature header"
        )
    
    try:
        # Get raw body
        payload = await request.body()
        payload_str = payload.decode('utf-8')
        
        # Verify webhook signature
        fanbasis_client = FanbasisClient()
        if not fanbasis_client.verify_webhook_signature(payload_str, x_webhook_signature):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid webhook signature"
            )
        
        # Parse payload
        try:
            webhook_data = json.loads(payload_str)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid JSON payload"
            )
        
        # Process webhook
        webhook_service = WebhookProcessingService(db)
        result = await webhook_service.process_fanbasis_webhook(webhook_data)
        
        logger.info(f"Processed Fanbasis webhook: {webhook_data.get('type', 'unknown')}")
        return {"status": "success", "processed": result.success}
        
    except Exception as e:
        logger.error(f"Error processing Fanbasis webhook: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook processing failed: {str(e)}"
        )

@router.get("/test")
async def test_webhook_endpoint():
    """Test endpoint to verify webhook URL is accessible"""
    return {"message": "Webhook endpoint is accessible", "status": "ok"}