from fastapi import FastAPI
from datetime import datetime
from app.services.setmore_client import SetmoreClient

app = FastAPI(
    title="OpenChair",
    description="Barbershop appointment notification system",
    version="0.1.0"
)

# Initialize Setmore client
setmore = SetmoreClient()

@app.get("/")
async def root():
    return {
        "message": "OpenChair API",
        "status": "running"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)