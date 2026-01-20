from sqlalchemy.orm import Session
from app.models.models import Subscription
from datetime import datetime
from typing import List, Optional


class SubscriptionService:
    """Manages user subscriptions"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def subscribe(self, phone_number: str) -> Subscription:
        """
        Subscribe a phone number to notifications
        
        Args:
            phone_number: Phone number in format like "+12345678900"
            
        Returns:
            Subscription object
        """
        # Check if already subscribed
        existing = self.db.query(Subscription).filter(
            Subscription.phone_number == phone_number
        ).first()
        
        if existing:
            if not existing.is_active:
                # Reactivate if they were unsubscribed
                existing.is_active = True
                existing.subscribed_at = datetime.now()
                self.db.commit()
                print(f"♻️ Reactivated subscription for {phone_number}")
            else:
                print(f"ℹ️ {phone_number} already subscribed")
            return existing
        
        # Create new subscription
        subscription = Subscription(
            phone_number=phone_number,
            subscribed_at=datetime.now(),
            is_active=True
        )
        
        self.db.add(subscription)
        self.db.commit()
        self.db.refresh(subscription)
        
        print(f"✅ New subscription: {phone_number}")
        return subscription
    
    def unsubscribe(self, phone_number: str) -> bool:
        """
        Unsubscribe a phone number from notifications
        
        Args:
            phone_number: Phone number to unsubscribe
            
        Returns:
            True if unsubscribed, False if not found
        """
        subscription = self.db.query(Subscription).filter(
            Subscription.phone_number == phone_number
        ).first()
        
        if not subscription:
            print(f"⚠️ {phone_number} not found")
            return False
        
        subscription.is_active = False
        self.db.commit()
        
        print(f"🛑 Unsubscribed: {phone_number}")
        return True
    
    def get_all_active_subscribers(self) -> List[Subscription]:
        """
        Get all active subscribers
        
        Returns:
            List of active Subscription objects
        """
        return self.db.query(Subscription).filter(
            Subscription.is_active == True
        ).all()
    
    def get_subscriber(self, phone_number: str) -> Optional[Subscription]:
        """Get subscription by phone number"""
        return self.db.query(Subscription).filter(
            Subscription.phone_number == phone_number
        ).first()
    
    def get_subscriber_count(self) -> int:
        """Get count of active subscribers"""
        return self.db.query(Subscription).filter(
            Subscription.is_active == True
        ).count()