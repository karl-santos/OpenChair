from sqlalchemy import Column, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.models.database import Base
import json

class SlotSnapshot(Base):
    """Stores the last known state of slots for each date"""
    __tablename__ = "slot_snapshots"
    
    date = Column(String, primary_key=True)  # "2026-01-20"
    slots = Column(Text, nullable=False)  # JSON array: ["1:00 PM", "2:20 PM"]
    last_polled = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def get_slots_list(self):
        """Convert JSON string back to list"""
        return json.loads(self.slots)
    
    def set_slots_list(self, slots_list):
        """Convert list to JSON string"""
        self.slots = json.dumps(slots_list)


class Subscription(Base):
    """Stores user subscriptions (phone numbers)"""
    __tablename__ = "subscriptions"
    
    phone_number = Column(String, primary_key=True)  # "+12345678900"
    subscribed_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
    

class NotificationLog(Base):
    """Log of all notifications sent (for debugging/auditing)"""
    __tablename__ = "notification_logs"
    
    id = Column(String, primary_key=True)  # We'll generate UUID
    phone_number = Column(String, nullable=False)
    date = Column(String, nullable=False)  # "2026-01-20"
    slots = Column(Text, nullable=False)  # JSON array of slots sent
    sent_at = Column(DateTime, default=func.now())
    
    def get_slots_list(self):
        return json.loads(self.slots)
    
    def set_slots_list(self, slots_list):
        self.slots = json.dumps(slots_list)