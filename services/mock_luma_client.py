from typing import List
from datetime import datetime, timedelta
from models.event import Event

class MockLumaClient:
    def __init__(self):
        self.events = []
        self._add_sample_events()

    def _add_sample_events(self):
        """Add some sample events for testing"""
        now = datetime.now().replace(minute=0, second=0, microsecond=0)
        self.events = [
            Event(
                name="Daily Standup",
                start_time=now.replace(hour=10),
                end_time=now.replace(hour=10, minute=30),
                location="Conference Room A",
                description="Daily team sync",
                event_id="evt_mock_1"
            ),
            Event(
                name="Team Lunch",
                start_time=now.replace(hour=12),
                end_time=now.replace(hour=13),
                location="Collaboration Space",
                description="Team building lunch",
                event_id="evt_mock_2"
            )
        ]

    def get_events(self, start_date: datetime, end_date: datetime) -> List[Event]:
        """Return mock events within date range"""
        return [
            event for event in self.events
            if start_date <= event.start_time <= end_date
        ]

    def create_event(self, event: Event) -> str:
        """Create a mock event"""
        event.event_id = f"evt_mock_{len(self.events) + 1}"
        self.events.append(event)
        return event.event_id 