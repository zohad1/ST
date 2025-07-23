
# # app/crud/payment.py
# from sqlalchemy.orm import Session
# from typing import List, Optional, Tuple
# from uuid import UUID

# from app.models.payment import Payment
# from app.models.payment_enums import PaymentStatus
# from app.schemas.payment import PaymentCreate, PaymentUpdate

# def get(db: Session, payment_id: UUID) -> Optional[Payment]:
#     """Get payment by ID"""
#     return db.query(Payment).filter(Payment.id == payment_id).first()

# def get_by_creator_id(
#     db: Session, creator_id: UUID, skip: int = 0, limit: int = 100
# ) -> List[Payment]:
#     """Get all payments for a creator"""
#     return db.query(Payment).filter(
#         Payment.creator_id == creator_id
#     ).offset(skip).limit(limit).all()

# def get_by_campaign_id(db: Session, campaign_id: UUID) -> List[Payment]:
#     """Get all payments for a campaign"""
#     return db.query(Payment).filter(
#         Payment.campaign_id == campaign_id
#     ).all()

# def get_by_external_id(
#     db: Session, external_id: str, provider: str = "stripe"
# ) -> Optional[Payment]:
#     """Get payment by external provider ID"""
#     if provider == "stripe":
#         return db.query(Payment).filter(
#             Payment.stripe_payment_intent_id == external_id
#         ).first()
#     elif provider == "fanbasis":
#         return db.query(Payment).filter(
#             Payment.fanbasis_transaction_id == external_id
#         ).first()
#     return None

# def get_multi_filtered(
#     db: Session,
#     skip: int = 0,
#     limit: int = 100,
#     creator_id: Optional[UUID] = None,
#     campaign_id: Optional[UUID] = None,
#     status: Optional[str] = None
# ) -> Tuple[List[Payment], int]:
#     """Get payments with filtering and total count"""
#     query = db.query(Payment)
    
#     if creator_id:
#         query = query.filter(Payment.creator_id == creator_id)
#     if campaign_id:
#         query = query.filter(Payment.campaign_id == campaign_id)
#     if status:
#         query = query.filter(Payment.status == status)
    
#     total = query.count()
#     payments = query.offset(skip).limit(limit).all()
    
#     return payments, total

# def get_pending_payments(db: Session) -> List[Payment]:
#     """Get all pending payments"""
#     return db.query(Payment).filter(
#         Payment.status == PaymentStatus.pending
#     ).all()

# def get_failed_payments(db: Session) -> List[Payment]:
#     """Get all failed payments"""
#     return db.query(Payment).filter(
#         Payment.status == PaymentStatus.failed
#     ).all()

# def create(db: Session, payment: PaymentCreate) -> Payment:
#     """Create new payment"""
#     db_payment = Payment(**payment.model_dump())
#     db.add(db_payment)
#     db.commit()
#     db.refresh(db_payment)
#     return db_payment

# def update(
#     db: Session, payment_id: UUID, payment_update: PaymentUpdate
# ) -> Optional[Payment]:
#     """Update payment"""
#     db_payment = get(db, payment_id)
#     if not db_payment:
#         return None
    
#     update_data = payment_update.model_dump(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_payment, key, value)
    
#     db.add(db_payment)
#     db.commit()
#     db.refresh(db_payment)
#     return db_payment

# def remove(db: Session, payment_id: UUID) -> bool:
#     """Delete payment"""
#     db_payment = get(db, payment_id)
#     if not db_payment:
#         return False
    
#     db.delete(db_payment)
#     db.commit()
#     return True


# Update app/crud/payment.py to work with string IDs
# app/crud/payment.py
from sqlalchemy.orm import Session
from typing import List, Optional, Tuple
from uuid import UUID

from app.models.standalone_models import Payment
from app.models.payment_enums import PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentUpdate

def get(db: Session, payment_id: UUID) -> Optional[Payment]:
    """Get payment by ID"""
    return db.query(Payment).filter(Payment.id == payment_id).first()

def get_by_creator_id(
    db: Session, creator_id: UUID, skip: int = 0, limit: int = 100
) -> List[Payment]:
    """Get all payments for a creator"""
    return db.query(Payment).filter(
        Payment.creator_id == str(creator_id)
    ).offset(skip).limit(limit).all()

def get_by_campaign_id(db: Session, campaign_id: UUID) -> List[Payment]:
    """Get all payments for a campaign"""
    return db.query(Payment).filter(
        Payment.campaign_id == str(campaign_id)
    ).all()

def get_by_external_id(
    db: Session, external_id: str, provider: str = "stripe"
) -> Optional[Payment]:
    """Get payment by external provider ID"""
    if provider == "stripe":
        return db.query(Payment).filter(
            Payment.stripe_payment_intent_id == external_id
        ).first()
    elif provider == "fanbasis":
        return db.query(Payment).filter(
            Payment.fanbasis_transaction_id == external_id
        ).first()
    return None

def get_multi_filtered(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    creator_id: Optional[UUID] = None,
    campaign_id: Optional[UUID] = None,
    status: Optional[str] = None
) -> Tuple[List[Payment], int]:
    """Get payments with filtering and total count"""
    query = db.query(Payment)
    
    if creator_id:
        query = query.filter(Payment.creator_id == str(creator_id))
    if campaign_id:
        query = query.filter(Payment.campaign_id == str(campaign_id))
    if status:
        query = query.filter(Payment.status == status)
    
    total = query.count()
    payments = query.offset(skip).limit(limit).all()
    
    return payments, total

def create(db: Session, payment: PaymentCreate) -> Payment:
    """Create new payment"""
    payment_dict = payment.model_dump()
    # Convert UUID fields to strings
    payment_dict['creator_id'] = str(payment_dict['creator_id'])
    if payment_dict.get('campaign_id'):
        payment_dict['campaign_id'] = str(payment_dict['campaign_id'])
    
    db_payment = Payment(**payment_dict)
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment

def update(
    db: Session, payment_id: UUID, payment_update: PaymentUpdate
) -> Optional[Payment]:
    """Update payment"""
    db_payment = get(db, payment_id)
    if not db_payment:
        return None
    
    update_data = payment_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_payment, key, value)
    
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment
