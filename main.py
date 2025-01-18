import os
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from config import Config
from models.event import Event
from services.luma_client import LumaClient
from services.conflict_checker import ConflictChecker

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
config = Config()
luma_client = LumaClient(config)
conflict_checker = ConflictChecker(config)

class EventRequest(BaseModel):
    name: str
    start_time: datetime
    end_time: datetime
    location: str
    description: Optional[str] = None

@app.post("/events/create")
async def create_event(event_request: EventRequest):
    # Create Event object
    new_event = Event(
        name=event_request.name,
        start_time=event_request.start_time,
        end_time=event_request.end_time,
        location=event_request.location,
        description=event_request.description
    )
    
    # Get existing events for the day
    day_start = new_event.start_time.replace(hour=0, minute=0, second=0)
    day_end = day_start + timedelta(days=1)
    existing_events = luma_client.get_events(day_start, day_end)
    
    # Check for conflicts
    if conflict_checker.has_conflict(new_event, existing_events):
        raise HTTPException(
            status_code=409,
            detail="Event conflicts with existing events"
        )
    
    # Create event if no conflicts
    event_id = luma_client.create_event(new_event)
    return {"event_id": event_id, "message": "Event created successfully"}

@app.get("/")
async def read_root():
    return FileResponse("static/index.html")

@app.get("/locations")
async def get_locations() -> List[str]:
    # You can replace this with actual locations from your database/config
    return [
        "Conference Room A",
        "Conference Room B",
        "Meeting Room 1",
        "Meeting Room 2",
        "Auditorium",
        "Collaboration Space",
        "Phone Booth 1",
        "Phone Booth 2"
    ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 