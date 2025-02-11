import unittest
from datetime import datetime, timedelta
import pytz
import os
import json
from dotenv import load_dotenv
from config import Config
from models.event import Event
from services.luma_client import LumaClient

# Load environment variables
load_dotenv()

class TestLumaCalendar(unittest.TestCase):
    def setUp(self):
        self.config = Config()
        if not self.config.API_KEY:
            self.skipTest("No Luma API key found in environment variables")
        self.luma_client = LumaClient(self.config)
        
        # Load rooms configuration
        rooms_path = os.path.join(os.path.dirname(__file__), 'config', 'rooms.json')
        with open(rooms_path) as f:
            self.rooms_config = json.load(f)
    
    def get_available_rooms(self):
        """Helper method to get all available rooms"""
        rooms = []
        for building in self.rooms_config["buildings"].values():
            rooms.extend(room["name"] for room in building["rooms"])
        return rooms
        
    def test_create_event(self):
        # Create event starting in 1 hour, lasting 1 hour
        pt_timezone = pytz.timezone('America/Los_Angeles')
        now = datetime.now(pt_timezone)
        event_start = now + timedelta(hours=1)  # Start in 1 hour
        event_end = event_start + timedelta(hours=1)  # 1 hour duration
        
        # Get room from configuration
        available_rooms = self.get_available_rooms()
        self.assertIn("Hogwarts Hall", available_rooms, "Hogwarts Hall should be in available rooms")
        
        test_event = Event(
            name="Test Meeting at SF Commons",
            start_time=event_start,
            end_time=event_end,
            location="Hogwarts Hall",
            description="Test event created via Luma API"
        )
        
        try:
            # Create the event
            event_id = self.luma_client.create_event(test_event)
            self.assertIsNotNone(event_id)
            print(f"Successfully created event with ID: {event_id}")
            
        except Exception as e:
            self.fail(f"Failed to create event: {str(e)}")

if __name__ == '__main__':
    unittest.main() 
