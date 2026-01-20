from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List

from app.models.database import get_db
from app.services.subscription_service import SubscriptionService


router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


class SubscribeRequest(BaseModel):
    phone_number: str = Field(
        ..., 
        description="Phone number in format +1234567890",
        example="+12345678900"
    )


class SubscriptionResponse(BaseModel):
    phone_number: str
    is_active: bool
    subscribed_at: str
    
    class Config:
        from_attributes = True


@router.post("/subscribe", response_model=SubscriptionResponse)
async def subscribe(
    request: SubscribeRequest,
    db: Session = Depends(get_db)
):
    """
    Subscribe a phone number to appointment notifications
    
    - **phone_number**: Phone number in E.164 format (e.g., +12345678900)
    """
    service = SubscriptionService(db)
    subscription = service.subscribe(request.phone_number)
    
    return SubscriptionResponse(
        phone_number=subscription.phone_number,
        is_active=subscription.is_active,
        subscribed_at=subscription.subscribed_at.isoformat()
    )


@router.post("/unsubscribe")
async def unsubscribe(
    request: SubscribeRequest,
    db: Session = Depends(get_db)
):
    """
    Unsubscribe a phone number from notifications
    
    - **phone_number**: Phone number to unsubscribe
    """
    service = SubscriptionService(db)
    success = service.unsubscribe(request.phone_number)
    
    if not success:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return {
        "message": "Successfully unsubscribed",
        "phone_number": request.phone_number
    }


@router.get("/status/{phone_number}")
async def get_status(
    phone_number: str,
    db: Session = Depends(get_db)
):
    """
    Check subscription status for a phone number
    
    - **phone_number**: Phone number to check
    """
    service = SubscriptionService(db)
    subscription = service.get_subscriber(phone_number)
    
    if not subscription:
        return {
            "phone_number": phone_number,
            "subscribed": False
        }
    
    return {
        "phone_number": subscription.phone_number,
        "subscribed": subscription.is_active,
        "subscribed_at": subscription.subscribed_at.isoformat() if subscription.is_active else None
    }


@router.get("/list", response_model=List[SubscriptionResponse])
async def list_subscribers(db: Session = Depends(get_db)):
    """
    Get list of all active subscribers (admin endpoint)
    """
    service = SubscriptionService(db)
    subscribers = service.get_all_active_subscribers()
    
    return [
        SubscriptionResponse(
            phone_number=sub.phone_number,
            is_active=sub.is_active,
            subscribed_at=sub.subscribed_at.isoformat()
        )
        for sub in subscribers
    ]


@router.get("/count")
async def subscriber_count(db: Session = Depends(get_db)):
    """Get total count of active subscribers"""
    service = SubscriptionService(db)
    count = service.get_subscriber_count()
    
    return {
        "active_subscribers": count
    }