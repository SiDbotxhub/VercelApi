import os
from datetime import timedelta
from typing import List

class Config:
    # Main API configuration
    API_KEYS = os.getenv("API_KEYS", "By6ixoZY0LqSr1bfUqZOl8Cn,AXETa3XBAanMBHwWslJRUmB9").split(",")
    CACHE_DURATION = timedelta(minutes=30)
    
    # List of backend APIs to try (in order)
    BACKEND_APIS: List[str] = [
        "https://deadlinetech.site/song/{video_id}?key={api_key}",
        # Add more fallback APIs here if needed
        "http://64.227.79.220:8080/song/{video_id}?key={api_key}",
    ]
    
    # Retry configuration
    MAX_RETRIES = 5
    RETRY_DELAY = 4  # seconds
    TIMEOUT = 4  # seconds per request
    MAX_CONCURRENT_REQUESTS = 100  # Limit concurrent requests
