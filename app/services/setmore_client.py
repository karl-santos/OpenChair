import httpx
from datetime import datetime, timedelta
from typing import List, Optional
from app.config import settings

class SetmoreClient:
    def __init__(self):
        self.base_url = settings.SETMORE_BASE_URL
        self.refresh_token = settings.SETMORE_REFRESH_TOKEN
        self.staff_key = settings.SETMORE_STAFF_KEY
        self.service_key = settings.SETMORE_SERVICE_KEY
        
        # Token management
        self._access_token: Optional[str] = None
        self._token_expiry: Optional[datetime] = None
    
    async def _ensure_valid_token(self):
        """Refresh access token if expired or not set"""
        if self._access_token is None or datetime.now() >= self._token_expiry:
            await self._refresh_access_token()
    
    async def _refresh_access_token(self):
        """Get new access token using refresh token"""
        url = f"{self.base_url}/o/oauth2/token"
        params = {"refreshToken": self.refresh_token}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            token_info = data["data"]["token"]
            
            self._access_token = token_info["access_token"]
            expires_in = token_info["expires_in"]
            
            # Set expiry with 60 second buffer
            self._token_expiry = datetime.now() + timedelta(seconds=expires_in - 60)
            
            print(f"✅ Token refreshed. Expires in {expires_in} seconds")
    
    async def get_slots(self, date: datetime) -> List[str]:
        """
        Fetch available time slots for a specific date
        
        Args:
            date: The date to fetch slots for
            
        Returns:
            List of time slot strings like ["1:00 PM", "2:20 PM"]
        """
        await self._ensure_valid_token()
        
        # Format date as DD/MM/YYYY
        date_str = date.strftime("%d/%m/%Y")
        
        url = f"{self.base_url}/bookingapi/slots"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._access_token}"
        }
        
        payload = {
            "staff_key": self.staff_key,
            "service_key": self.service_key,
            "selected_date": date_str,
            "off_hours": False,
            "double_booking": False,
            "slot_limit": 40
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            slots = data["data"]["slots"]
            
            return slots
    
    async def get_slots_for_date_range(self, days: int = 7) -> dict:
        """
        Fetch slots for the next N days
        
        Args:
            days: Number of days to fetch (default 7)
            
        Returns:
            Dictionary mapping date strings to slot lists
            Example: {"2026-01-20": ["1:00 PM", "2:20 PM"], ...}
        """
        results = {}
        
        for i in range(days):
            date = datetime.now() + timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")  # Store as YYYY-MM-DD
            
            try:
                slots = await self.get_slots(date)
                results[date_key] = slots
                print(f"📅 {date_key}: Found {len(slots)} slots")
            except Exception as e:
                print(f"❌ Error fetching slots for {date_key}: {e}")
                results[date_key] = []
        
        return results