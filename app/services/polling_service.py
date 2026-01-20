import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.setmore_client import SetmoreClient
from app.services.slot_tracker import SlotTracker
from app.models.database import SessionLocal
from app.config import settings


class PollingService:
    """Handles automated polling of Setmore API"""
    
    def __init__(self):
        self.setmore = SetmoreClient()
    
    async def poll_for_new_slots(self):
        """
        Main polling function - checks for new slots across all days
        This runs every hour automatically
        """
        print(f"\n{'='*60}")
        print(f"🔄 Starting poll at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}")
        
        db = SessionLocal()
        try:
            tracker = SlotTracker(db)
            new_slots_found = {}
            
            # Poll for next N days
            for i in range(settings.DAYS_TO_POLL):
                date = datetime.now() + timedelta(days=i)
                date_str = date.strftime("%Y-%m-%d")
                
                try:
                    # Fetch current slots from Setmore
                    current_slots = await self.setmore.get_slots(date)
                    
                    # Find new slots
                    new_slots = tracker.find_new_slots(date_str, current_slots)
                    
                    # Save snapshot
                    tracker.save_snapshot(date_str, current_slots)
                    
                    # Track new slots found
                    if new_slots:
                        new_slots_found[date_str] = new_slots
                    
                except Exception as e:
                    print(f"❌ Error polling {date_str}: {e}")
            
            # Cleanup old snapshots (dates in the past)
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
            tracker.cleanup_old_snapshots(yesterday)
            
            # Summary
            if new_slots_found:
                print(f"\n🎉 FOUND NEW SLOTS:")
                for date, slots in new_slots_found.items():
                    print(f"   {date}: {slots}")
                print(f"\n📱 TODO: Notify {self._get_subscriber_count(db)} subscribers")
            else:
                print(f"\n✅ No new slots detected")
            
            print(f"{'='*60}\n")
            
            return new_slots_found
            
        finally:
            db.close()
    
    def _get_subscriber_count(self, db: Session) -> int:
        """Get count of active subscribers (we'll implement subscriptions later)"""
        from app.models.models import Subscription
        return db.query(Subscription).filter(Subscription.is_active == True).count()


# Global instance
polling_service = PollingService()


def run_poll_sync():
    """
    Synchronous wrapper for the async poll function
    APScheduler needs a sync function, so we use asyncio.run()
    """
    asyncio.run(polling_service.poll_for_new_slots())