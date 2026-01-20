from sqlalchemy.orm import Session
from app.models.models import SlotSnapshot
from typing import List, Set
from datetime import datetime

class SlotTracker:
    """Manages slot snapshots and detects new slots"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_last_snapshot(self, date: str) -> List[str]:
        """
        Get the last known slots for a date
        
        Args:
            date: Date string like "2026-01-20"
            
        Returns:
            List of slots, or empty list if no snapshot exists
        """
        snapshot = self.db.query(SlotSnapshot).filter(SlotSnapshot.date == date).first()
        if snapshot:
            return snapshot.get_slots_list()
        return []
    
    def save_snapshot(self, date: str, slots: List[str]):
        """
        Save or update slot snapshot for a date
        
        Args:
            date: Date string like "2026-01-20"
            slots: List of slot strings like ["1:00 PM", "2:20 PM"]
        """
        snapshot = self.db.query(SlotSnapshot).filter(SlotSnapshot.date == date).first()
        
        if snapshot:
            # Update existing
            snapshot.set_slots_list(slots)
        else:
            # Create new
            snapshot = SlotSnapshot(date=date)
            snapshot.set_slots_list(slots)
            self.db.add(snapshot)
        
        self.db.commit()
        print(f"💾 Saved snapshot for {date}: {len(slots)} slots")
    
    def find_new_slots(self, date: str, current_slots: List[str]) -> List[str]:
        """
        Compare current slots with last snapshot to find new ones
        
        Args:
            date: Date string
            current_slots: Current slot list from API
            
        Returns:
            List of NEW slots that weren't in the last snapshot
        """
        last_slots = self.get_last_snapshot(date)
        
        # Convert to sets for efficient comparison
        last_set = set(last_slots)
        current_set = set(current_slots)
        
        # Find slots that are in current but NOT in last
        new_slots = list(current_set - last_set)
        
        if new_slots:
            print(f"🆕 Found {len(new_slots)} new slots for {date}: {new_slots}")
        
        return new_slots
    
    def cleanup_old_snapshots(self, cutoff_date: str):
        """
        Delete snapshots older than cutoff date
        
        Args:
            cutoff_date: Date string like "2026-01-20"
        """
        deleted = self.db.query(SlotSnapshot).filter(SlotSnapshot.date < cutoff_date).delete()
        self.db.commit()
        
        if deleted > 0:
            print(f"🧹 Cleaned up {deleted} old snapshots")