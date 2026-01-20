from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from app.config import settings
from app.services.polling_service import run_poll_sync
import logging

# Setup logging for APScheduler
logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.INFO)

class Scheduler:
    """Manages background job scheduling"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.is_running = False
    
    def start(self):
        """Start the scheduler"""
        if self.is_running:
            print("⚠️ Scheduler already running")
            return
        
        # Add polling job
        self.scheduler.add_job(
            func=run_poll_sync,
            trigger=IntervalTrigger(minutes=settings.POLL_INTERVAL_MINUTES),
            id='poll_setmore',
            name='Poll Setmore for new slots',
            replace_existing=True
        )
        
        self.scheduler.start()
        self.is_running = True
        
        print(f"✅ Scheduler started - polling every {settings.POLL_INTERVAL_MINUTES} minutes")
        print(f"📅 Monitoring next {settings.DAYS_TO_POLL} days")
    
    def stop(self):
        """Stop the scheduler"""
        if self.is_running:
            self.scheduler.shutdown()
            self.is_running = False
            print("🛑 Scheduler stopped")
    
    def run_now(self):
        """Trigger a poll immediately (for testing)"""
        print("🚀 Triggering manual poll...")
        run_poll_sync()
    
    def get_jobs(self):
        """Get list of scheduled jobs"""
        return self.scheduler.get_jobs()


# Global scheduler instance
scheduler = Scheduler()