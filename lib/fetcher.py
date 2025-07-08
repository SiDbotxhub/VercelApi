import asyncio
import aiohttp
from lib.config import Config
from lib.cache import cache
from lib.utils import validate_api_key
import json
from datetime import datetime
from typing import Dict, Any

async def fetch_download_url(video_id: str, api_key: str) -> Dict[str, Any]:
    # Check cache first (using the new async cache interface)
    cache_key = f"song_{video_id}"
    cached = await cache.get(cache_key)
    if cached:
        return cached
    
    # Validate API key
    if not validate_api_key(api_key):
        return {"error": "Invalid API key", "status": "failed"}
    
    # Try each backend API with retries
    for api_url_template in Config.BACKEND_APIS:
        api_url = api_url_template.format(video_id=video_id, api_key=api_key)
        
        for attempt in range(Config.MAX_RETRIES):
            try:
                async with aiohttp.ClientSession() as session:
                    start_time = datetime.now()
                    
                    async with session.get(
                        api_url, 
                        timeout=Config.TIMEOUT
                    ) as response:
                        data = await response.json()
                        
                        if data.get('status') == 'done' and data.get('download_url'):
                            response_time = (datetime.now() - start_time).total_seconds()
                            result = {
                                **data,
                                "response_time_sec": round(response_time, 3),
                                "source_api": api_url,
                                "attempts": attempt + 1
                            }
                            await cache.set(cache_key, result)
                            return result
                        
                        elif data.get('status') in ['downloading', 'processing']:
                            if attempt < Config.MAX_RETRIES - 1:
                                await asyncio.sleep(Config.RETRY_DELAY)
                                continue
                            
                        # If we get here, the response wasn't successful
                        if attempt == Config.MAX_RETRIES - 1:
                            continue  # Try next API
                            
            except (aiohttp.ClientError, json.JSONDecodeError, asyncio.TimeoutError) as e:
                if attempt == Config.MAX_RETRIES - 1:
                    continue  # Try next API
                await asyncio.sleep(Config.RETRY_DELAY)
    
    return {
        "error": "Failed to get download URL after retries", 
        "status": "failed",
        "attempts": Config.MAX_RETRIES * len(Config.BACKEND_APIS)
    }
