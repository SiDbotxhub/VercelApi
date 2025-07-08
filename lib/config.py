import os
from datetime import timedelta

class Config:
    # Main API configuration
    API_KEYS = os.getenv("API_KEYS", "").split(",")
    CACHE_DURATION = timedelta(minutes=30)
    
    # List of backend APIs to try (in order)
    BACKEND_APIS = [
        "https://deadlinetech.site/song/{video_id}?key={api_key}",
        # Add more fallback APIs here if needed
        # "https://alternative-api.com/song/{video_id}?key={api_key}",
    ]
    
    # Retry configuration
    MAX_RETRIES = 3
    RETRY_DELAY = 5  # seconds
    TIMEOUT = 10  # seconds per request
