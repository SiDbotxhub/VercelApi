from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from lib.fetcher import fetch_download_url
from lib.utils import validate_api_key
from lib.config import Config
import asyncio
from contextlib import asynccontextmanager
from typing import Dict, Any
import uuid

# Global state for request deduplication
ongoing_requests: Dict[str, asyncio.Future] = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code
    yield
    # Cleanup code
    ongoing_requests.clear()

app = FastAPI(lifespan=lifespan)

# Add middleware for optimization
app.add_middleware(GZipMiddleware, minimum_size=1000)
# app.add_middleware(HTTPSRedirectMiddleware)  # Uncomment if you want to force HTTPS

@app.get("/song/{video_id}")
async def get_song_url(
    video_id: str,
    request: Request,
    key: str = Query(..., alias="key"),
    request_id: str = Query(default_factory=lambda: str(uuid.uuid4()))
):
    """
    Get download URL for a song with retry logic and caching.
    
    Parameters:
    - video_id: ID of the video to download
    - key: API key for authentication
    - request_id: Unique ID for tracking the request (auto-generated if not provided)
    """
    # Validate API key first (fast fail)
    if not validate_api_key(key):
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    
    # Check cache first (optimization)
    cache_key = f"song_{video_id}"
    cached = app.state.cache.get(cache_key)
    if cached:
        return JSONResponse(content=cached)
    
    # Request deduplication
    if video_id in ongoing_requests:
        try:
            result = await ongoing_requests[video_id]
            return JSONResponse(content=result)
        except Exception as e:
            # If the ongoing request failed, let this one try
            pass
    
    # Create and store a new future for this request
    future = asyncio.get_event_loop().create_future()
    ongoing_requests[video_id] = future
    
    try:
        # Process the request
        result = await fetch_download_url(video_id, key)
        
        # Set the result so other waiting requests get it
        future.set_result(result)
        
        # Clean up
        del ongoing_requests[video_id]
        
        return JSONResponse(content=result)
        
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504,
            detail="Request timed out"
        )
    except Exception as e:
        # Clean up on error
        if video_id in ongoing_requests:
            future.set_exception(e)
            del ongoing_requests[video_id]
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

@app.get("/health")
async def health_check():
    """Endpoint for health checks and load balancing"""
    return {"status": "healthy"}

# Initialize app state
@app.on_event("startup")
async def startup_event():
    app.state.cache = cache
    app.state.ongoing_requests = ongoing_requests
