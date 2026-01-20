from twilio.rest import Client
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import uuid

from app.config import settings
from app.models.models import NotificationLog, Subscription


class NotificationService:
    """Handles SMS notifications via Twilio"""
    
    def __init__(self, db: Session):
        self.db = db
        
        # Initialize Twilio client
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_PHONE_NUMBER
        else:
            self.client = None
            print("⚠️ Twilio not configured - notifications disabled")
    
    def send_sms(self, to_number: str, message: str) -> bool:
        """
        Send SMS to a phone number
        
        Args:
            to_number: Recipient phone number
            message: Message text
            
        Returns:
            True if sent successfully, False otherwise
        """
        if not self.client:
            print(f"⚠️ Twilio not configured - would send to {to_number}: {message}")
            return False
        
        try:
            message_obj = self.client.messages.create(
                body=message,
                from_=self.from_number,
                to=to_number
            )
            
            print(f"✅ SMS sent to {to_number} (SID: {message_obj.sid})")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send SMS to {to_number}: {e}")
            return False
    
    def notify_new_slots(self, date: str, new_slots: List[str]) -> int:
        """
        Notify all active subscribers about new slots
        
        Args:
            date: Date string like "2026-01-20"
            new_slots: List of new slot times like ["1:00 PM", "2:20 PM"]
            
        Returns:
            Number of notifications sent
        """
        # Get all active subscribers
        subscribers = self.db.query(Subscription).filter(
            Subscription.is_active == True
        ).all()
        
        if not subscribers:
            print("ℹ️ No active subscribers to notify")
            return 0
        
        # Format the message
        slots_text = ", ".join(new_slots)
        message = self._format_message(date, new_slots)
        
        sent_count = 0
        
        for subscriber in subscribers:
            # Send SMS
            success = self.send_sms(subscriber.phone_number, message)
            
            if success:
                # Log the notification
                self._log_notification(subscriber.phone_number, date, new_slots)
                sent_count += 1
        
        return sent_count
    
    def _format_message(self, date: str, slots: List[str]) -> str:
        """
        Format notification message
        
        Args:
            date: Date string like "2026-01-20"
            slots: List of slots
            
        Returns:
            Formatted SMS message
        """
        # Parse date for better formatting
        date_obj = datetime.strptime(date, "%Y-%m-%d")
        date_formatted = date_obj.strftime("%a, %b %d")  # "Mon, Jan 20"
        
        if len(slots) == 1:
            slots_text = slots[0]
            return f"🪑 OpenChair: New slot available on {date_formatted} at {slots_text}!"
        else:
            slots_text = ", ".join(slots)
            return f"🪑 OpenChair: {len(slots)} new slots on {date_formatted}: {slots_text}"
    
    def _log_notification(self, phone_number: str, date: str, slots: List[str]):
        """Log notification in database"""
        log = NotificationLog(
            id=str(uuid.uuid4()),
            phone_number=phone_number,
            date=date,
            sent_at=datetime.now()
        )
        log.set_slots_list(slots)
        
        self.db.add(log)
        self.db.commit()
    
    def send_test_notification(self, phone_number: str) -> bool:
        """
        Send a test notification
        
        Args:
            phone_number: Phone number to test
            
        Returns:
            True if sent successfully
        """
        message = "🪑 OpenChair: Test notification - you're subscribed! Reply STOP to unsubscribe."
        return self.send_sms(phone_number, message)