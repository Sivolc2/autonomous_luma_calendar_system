import os
import json
from datetime import datetime, timedelta, timezone
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from config import Config
from models.event import Event
from services.luma_client import LumaClient
from services.conflict_checker import ConflictChecker
from services.mock_luma_client import MockLumaClient

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
config = Config()

# Load rooms configuration
with open(os.path.join(os.path.dirname(__file__), 'config', 'rooms.json')) as f:
    rooms_config = json.load(f)

# Use mock client in debug mode
if config.DEBUG_MODE:
    luma_client = MockLumaClient()
else:
    luma_client = LumaClient(config)

conflict_checker = ConflictChecker(config)

class EventRequest(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    location: str
    host_email: str
    additional_hosts: Optional[List[str]] = None

@app.post("/events/create")
async def create_event(event_request: EventRequest):
    # Create Event object
    new_event = Event(
        name=event_request.name,
        start_time=event_request.start_time,
        end_time=event_request.end_time,
        location=event_request.location,
        host_email=event_request.host_email,
        additional_hosts=event_request.additional_hosts
    )
    
    # Get existing events for the day
    day_start = new_event.start_time.replace(hour=0, minute=0, second=0)
    day_end = day_start + timedelta(days=1)
    existing_events = luma_client.get_events(day_start, day_end)
    
    # Check for conflicts
    if conflict_checker.has_conflict(new_event, existing_events):
        # Find conflicting events
        conflicting_events = [
            event for event in existing_events 
            if conflict_checker._events_overlap(
                new_event.start_time, new_event.end_time,
                event.start_time, event.end_time
            )
        ]
        
        # Format conflicts for response
        conflicts_data = [{
            "name": event.name,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location
        } for event in conflicting_events]
        
        raise HTTPException(
            status_code=409,
            detail="Event conflicts with existing events",
            headers={
                "X-Error-Type": "conflict",
                "X-Conflicts": json.dumps(conflicts_data)
            },
        ) from None
    
    # Create event if no conflicts
    event_id = luma_client.create_event(new_event)
    return {"event_id": event_id, "message": "Event created successfully"}

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/locations")
async def get_locations() -> List[dict]:
    """Get all rooms from configuration with building info"""
    rooms = []
    for building_id, building in rooms_config["buildings"].items():
        for room in building["rooms"]:
            rooms.append({
                "id": room["id"],
                "name": room["name"],
                "description": room["description"],
                "building": building_id
            })
    return rooms

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "debug_mode": config.DEBUG_MODE,
        "integrations": {
            "luma": config.is_luma_configured()
        }
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    if exc.headers and exc.headers.get("X-Error-Type") == "conflict":
        conflicts = json.loads(exc.headers["X-Conflicts"])
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
                "conflicts": conflicts
            }
        )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )

@app.get("/events/{event_id}")
async def get_event(event_id: str):
    """Get event details including the public URL"""
    try:
        event = luma_client.get_event(event_id)
        return {
            "name": event.name,
            "start_time": event.start_time.isoformat(),
            "end_time": event.end_time.isoformat(),
            "location": event.location,
            "url": event.url
        }
    except Exception as e:
        raise HTTPException(
            status_code=404,
            detail=f"Event not found or error fetching event details: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 