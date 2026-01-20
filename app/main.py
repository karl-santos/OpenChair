from fastapi import FastAPI, Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from contextlib import asynccontextmanager

from app.services.setmore_client import SetmoreClient
from app.services.slot_tracker import SlotTracker
from app.services.scheduler import scheduler
from app.models.database import get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager - runs on startup and shutdown
    """
    # Startup
    print("\n🚀 Starting OpenChair...")
    scheduler.start()
    
    yield
    
    # Shutdown
    print("\n👋 Shutting down OpenChair...")
    scheduler.stop()


app = FastAPI(
    title="OpenChair",
    description="Barbershop appointment notification system",
    version="0.1.0",
    lifespan=lifespan
)

setmore = SetmoreClient()


@app.get("/")
async def root():
    return {
        "message": "OpenChair API",
        "status": "running",
        "scheduler_active": scheduler.is_running
    }


@app.get("/health")
async def health():
    jobs = scheduler.get_jobs()
    return {
        "status": "healthy",
        "scheduler_running": scheduler.is_running,
        "scheduled_jobs": len(jobs),
        "jobs": [{"id": job.id, "name": job.name, "next_run": str(job.next_run_time)} for job in jobs]
    }


@app.post("/admin/poll-now")
async def trigger_poll():
    """
    Admin endpoint - trigger a poll immediately (for testing)
    """
    scheduler.run_now()
    return {
        "message": "Poll triggered",
        "status": "check logs for results"
    }


@app.get("/test/slots")
async def test_slots():
    """Test endpoint - fetch slots for today"""
    try:
        today = datetime.now()
        slots = await setmore.get_slots(today)
        return {
            "date": today.strftime("%Y-%m-%d"),
            "slots": slots,
            "count": len(slots)
        }
    except Exception as e:
        return {
            "error": str(e)
        }


@app.get("/test/slots/week")
async def test_slots_week():
    """Test endpoint - fetch slots for next 7 days"""
    try:
        slots_by_date = await setmore.get_slots_for_date_range(days=7)
        return {
            "slots_by_date": slots_by_date,
            "total_days": len(slots_by_date)
        }
    except Exception as e:
        return {
            "error": str(e)
        }


@app.get("/test/detect-new")
async def test_detect_new(db: Session = Depends(get_db)):
    """
    Test endpoint - fetch slots and detect new ones
    This simulates what the polling job will do
    """
    try:
        tracker = SlotTracker(db)
        today = datetime.now()
        date_str = today.strftime("%Y-%m-%d")
        
        # Fetch current slots from Setmore
        current_slots = await setmore.get_slots(today)
        
        # Find new slots compared to last snapshot
        new_slots = tracker.find_new_slots(date_str, current_slots)
        
        # Save current state
        tracker.save_snapshot(date_str, current_slots)
        
        return {
            "date": date_str,
            "current_slots": current_slots,
            "new_slots": new_slots,
            "message": f"Found {len(new_slots)} new slots!" if new_slots else "No new slots"
        }
    except Exception as e:
        return {
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)