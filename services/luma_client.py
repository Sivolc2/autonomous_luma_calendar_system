import requests
from typing import List
from datetime import datetime
from models.event import Event
from config import Config

class LumaClient:
    def __init__(self, config: Config):
        self.config = config
        self.headers = {"x-luma-api-key": config.API_KEY}
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Event]:
        """Fetch events from Luma API within date range"""
        response = requests.get(
            f"{self.config.BASE_URL}/public/v1/calendar/list-events",
            headers=self.headers,
            params={
                "start_time": start_date.isoformat(),
                "end_time": end_date.isoformat()
            }
        )
        response.raise_for_status()
        return [self._parse_event(event) for event in response.json()["events"]]
    
    def create_event(self, event: Event) -> str:
        """Create new event in Luma"""
        response = requests.post(
            f"{self.config.BASE_URL}/event/create",
            headers=self.headers,
            json={
                "name": event.name,
                "start_time": event.start_time.isoformat(),
                "end_time": event.end_time.isoformat(),
                "location": event.location,
                "description": event.description
            }
        )
        response.raise_for_status()
        return response.json()["event_id"]
    
    def _parse_event(self, event_data: dict) -> Event:
        return Event(
            name=event_data["name"],
            start_time=datetime.fromisoformat(event_data["start_time"]),
            end_time=datetime.fromisoformat(event_data["end_time"]),
            location=event_data["location"],
            description=event_data.get("description"),
            event_id=event_data["id"]
        ) 