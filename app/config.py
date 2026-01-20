import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # Setmore API
    SETMORE_REFRESH_TOKEN = os.getenv("SETMORE_REFRESH_TOKEN")
    SETMORE_STAFF_KEY = os.getenv("SETMORE_STAFF_KEY")
    SETMORE_SERVICE_KEY = os.getenv("SETMORE_SERVICE_KEY")
    SETMORE_BASE_URL = "https://developer.setmore.com/api/v1"
    
    # App config
    POLL_INTERVAL_MINUTES = int(os.getenv("POLL_INTERVAL_MINUTES", 60))
    DAYS_TO_POLL = int(os.getenv("DAYS_TO_POLL", 7))

settings = Settings()