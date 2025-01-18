from typing import List
from datetime import datetime, timedelta
from models.event import Event
from config import Config

class ConflictChecker:
    def __init__(self, config: Config):
        self.buffer_minutes = config.DEFAULT_BUFFER_MINUTES
    
    def has_conflict(self, new_event: Event, existing_events: List[Event]) -> bool:
        """Check if new event conflicts with any existing events"""
        new_start = new_event.start_time - timedelta(minutes=self.buffer_minutes)
        new_end = new_event.end_time + timedelta(minutes=self.buffer_minutes)
        
        return any(
            self._events_overlap(
                new_start, new_end,
                event.start_time, event.end_time
            )
            for event in existing_events
        )
    
    def _events_overlap(
        self,
        start1: datetime,
        end1: datetime,
        start2: datetime,
        end2: datetime
    ) -> bool:
        return start1 < end2 and start2 < end1 