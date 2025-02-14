import requests
import json
from typing import List
from datetime import datetime, timezone
from models.event import Event
from config import Config
import os

class LumaClient:
    def __init__(self, config: Config):
        self.config = config
        self.headers = {
            "x-luma-api-key": config.API_KEY,
            "accept": "application/json",
            "content-type": "application/json"
        }
        # Load rooms configuration
        rooms_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'rooms.json')
        with open(rooms_path) as f:
            self.rooms_config = json.load(f)
    
    def get_events(self, start_date: datetime, end_date: datetime) -> List[Event]:
        """Fetch events from Luma API within date range"""
        print(f"Fetching events from {start_date} to {end_date}")
        print(f"Headers: {self.headers}")
        
        all_events = []
        next_cursor = None
        
        while True:
            params = {
                "after": start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "before": end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "pagination_limit": 100  # Get maximum events per page
            }
            if next_cursor:
                params["pagination_cursor"] = next_cursor
            
            response = requests.get(
                f"{self.config.BASE_URL}/calendar/list-events",
                headers=self.headers,
                params=params
            )
            print(f"Response status: {response.status_code}")
            print(f"Response text: {response.text}")
            
            response.raise_for_status()
            data = response.json()
            
            # Extract events from the response - they're in the 'entries' array
            if "entries" in data and isinstance(data["entries"], list):
                # Each entry has an 'event' field containing the actual event data
                for entry in data["entries"]:
                    if "event" in entry:
                        all_events.append(entry["event"])
            
            # Check if there are more events to fetch
            if not data.get("has_more"):
                break
            next_cursor = data.get("next_cursor")
            if not next_cursor:
                break
        
        print(f"Found {len(all_events)} events")
        parsed_events = [self._parse_event(event) for event in all_events]
        print(f"Parsed events: {[f'{e.name} at {e.location} ({e.start_time}-{e.end_time})' for e in parsed_events]}")
        return parsed_events
    
    def add_host(self, event_id: str, email: str) -> None:
        """Add a host to an event"""
        print(f"Adding host {email} to event {event_id}")  # Debug print
        
        payload = {
            "event_api_id": event_id,
            "email": email,
            "access_level": "manager",
            "is_visible": True
        }
        
        print(f"Add host payload: {payload}")  # Debug print
        
        response = requests.post(
            f"{self.config.BASE_URL}/event/add-host",
            headers=self.headers,
            json=payload
        )
        
        print(f"Add host response status: {response.status_code}")  # Debug print
        print(f"Add host response text: {response.text}")  # Debug print
        
        if not response.ok:
            error_msg = f"Failed to add host: {response.text}"
            print(error_msg)  # Debug print
            raise Exception(error_msg)
            
        return response.json()

    def create_event(self, event: Event) -> str:
        """Create new event in Luma"""
        # Find the room in our configuration
        room_info = None
        building_info = None
        for building_id, building in self.rooms_config["buildings"].items():
            for room in building["rooms"]:
                if room["name"] == event.location:
                    room_info = room
                    building_info = building
                    break
            if room_info:
                break
        
        if not room_info:
            raise ValueError(f"Room not found: {event.location}")
        
        # Format address with + separator
        base_address = building_info['address'].split(',')[0]  # Get just the street address part
        address = f"{base_address}, San Francisco + {room_info['name']}"
        
        # Convert datetime to UTC
        start_time = event.start_time.astimezone(timezone.utc)
        end_time = event.end_time.astimezone(timezone.utc)
        
        payload = {
            "name": event.name,
            "start_at": start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_at": end_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "timezone": "America/Los_Angeles",
            "require_rsvp_approval": False,
            "geo_address_json": {
                "type": "manual",
                "address": address
            },
            "geo_latitude": self.rooms_config["coordinates"]["latitude"],
            "geo_longitude": self.rooms_config["coordinates"]["longitude"]
        }
        
        print(f"Creating event with payload: {payload}")  # Debug print
        
        response = requests.post(
            f"{self.config.BASE_URL}/event/create",
            headers=self.headers,
            json=payload
        )
        
        if not response.ok:
            print(f"Error response: {response.text}")  # Debug print
            print(f"Status code: {response.status_code}")
            print(f"Headers: {response.headers}")
        
        response.raise_for_status()
        event_id = response.json()["api_id"]

        # If host email is provided, add them as a host
        if event.host_email:
            try:
                print(f"Attempting to add primary host {event.host_email}")  # Debug print
                self.add_host(event_id, event.host_email)
                print("Successfully added primary host")  # Debug print
                
                # Add additional hosts if they exist
                if event.additional_hosts:
                    for additional_host in event.additional_hosts:
                        try:
                            print(f"Attempting to add additional host {additional_host}")  # Debug print
                            self.add_host(event_id, additional_host)
                            print(f"Successfully added additional host {additional_host}")  # Debug print
                        except Exception as e:
                            print(f"Failed to add additional host {additional_host}: {str(e)}")  # Debug print
                            # Continue with other hosts even if one fails
                            continue
                            
            except Exception as e:
                error_msg = f"Failed to add hosts: {str(e)}"
                print(error_msg)  # Debug print
                raise Exception(error_msg)

        return event_id
    
    def get_event(self, event_id: str) -> Event:
        """Fetch a specific event by ID"""
        response = requests.get(
            f"{self.config.BASE_URL}/event/get",
            headers=self.headers,
            params={"api_id": event_id}
        )
        print(f"Get event response: {response.text}")  # Debug log
        response.raise_for_status()
        event_data = response.json()["event"]
        print(f"Event data from API: {event_data}")  # Debug log
        return self._parse_event(event_data)
    
    def _parse_event(self, event_data: dict) -> Event:
        print(f"Raw event data: {event_data}")  # Debug print
        
        # Extract location from geo_address_json
        location = None
        if geo_json := event_data.get("geo_address_json"):
            if address := geo_json.get("address"):
                # Try to extract room name from address (after the '+' if it exists)
                if "+" in address:
                    location = address.split("+")[1].strip()
                else:
                    location = address
            elif full_address := geo_json.get("full_address"):
                location = full_address
        
        # If we still don't have a location, try to extract from the event name
        if not location:
            # Look for room names in the event name
            event_text = event_data.get('name', '')
            for building in self.rooms_config["buildings"].values():
                for room in building["rooms"]:
                    if room["name"] in event_text:
                        location = room["name"]
                        break
                if location:
                    break
        
        # If we still don't have a location, use a default
        if not location:
            location = "Unknown Location"
        
        return Event(
            name=event_data["name"],
            start_time=datetime.fromisoformat(event_data["start_at"].replace('Z', '+00:00')),
            end_time=datetime.fromisoformat(event_data["end_at"].replace('Z', '+00:00')),
            location=location,
            event_id=event_data["api_id"],
            url=event_data.get("url")  # Get the public URL from the API response
        )
    
    