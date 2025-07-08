from http import HTTPStatus
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import JSONResponse
from lib.fetcher import fetch_download_url
from lib.utils import validate_api_key
import asyncio

app = FastAPI()

# Track ongoing requests to avoid duplicate processing
ongoing_requests = {}

@app.get("/song/{video_id}")
async def get_song_url(
    video_id: str,
    request: Request,
    key: str = Query(..., alias="key")
):
    # Check if this request is already being processed
    if video_id in ongoing_requests:
        # Wait for the existing request to complete
        result = await ongoing_requests[video_id]
        return JSONResponse(content=result)
    
    try:
        # Create a future for this request
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        ongoing_requests[video_id] = future
        
        # Process the request
        result = await fetch_download_url(video_id, key)
        
        # Set the result and clean up
        future.set_result(result)
        return JSONResponse(content=result)
        
    except Exception as e:
        if video_id in ongoing_requests:
            ongoing_requests[video_id].set_exception(e)
            del ongoing_requests[video_id]
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
    finally:
        if video_id in ongoing_requests:
            del ongoing_requests[video_id]

@app.get("/")
async def health_check():
    return {"status": "ok"}
