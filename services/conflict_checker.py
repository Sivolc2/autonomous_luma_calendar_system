from typing import List
from datetime import datetime, timedelta
import os
import json
from models.event import Event
from config import Config

class ConflictChecker:
    def __init__(self, config: Config):
        self.buffer_minutes = config.DEFAULT_BUFFER_MINUTES
        # Load rooms configuration
        rooms_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'rooms.json')
        with open(rooms_path) as f:
            rooms_config = json.load(f)
            
        # Build room conflicts mapping
        self.room_conflicts = {}
        for building in rooms_config["buildings"].values():
            for room in building["rooms"]:
                if "conflicts_with" in room:
                    self.room_conflicts[room["name"]] = room["conflicts_with"]
    
    def has_conflict(self, new_event: Event, existing_events: List[Event]) -> bool:
        """Check if new event conflicts with any existing events"""
        new_start = new_event.start_time - timedelta(minutes=self.buffer_minutes)
        new_end = new_event.end_time + timedelta(minutes=self.buffer_minutes)
        
        for event in existing_events:
            # Check time overlap
            if self._events_overlap(new_start, new_end, event.start_time, event.end_time):
                # Check if same location or conflicting studio spaces
                if self._locations_conflict(new_event.location, event.location):
                    return True
        return False
    
    def _events_overlap(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        """Check if two time periods overlap"""
        return start1 < end2 and start2 < end1
    
    def _locations_conflict(self, location1: str, location2: str) -> bool:
        """Check if two locations conflict based on configuration"""
        # Direct location match
        if location1 == location2:
            return True
            
        # Check configured conflicts
        if location1 in self.room_conflicts and location2 in self.room_conflicts[location1]:
            return True
        if location2 in self.room_conflicts and location1 in self.room_conflicts[location2]:
            return True
            
        return False