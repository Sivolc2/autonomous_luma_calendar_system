from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from datetime import datetime
import re
from typing import Optional, Tuple
from models.event import Event
from services.luma_client import LumaClient
from services.conflict_checker import ConflictChecker
from config import Config

class SlackEventHandler:
    def __init__(self, config: Config, luma_client: LumaClient, conflict_checker: ConflictChecker):
        self.slack_app = App(
            token=config.SLACK_BOT_TOKEN,
            signing_secret=config.SLACK_SIGNING_SECRET
        )
        self.handler = SlackRequestHandler(self.slack_app)
        self.luma_client = luma_client
        self.conflict_checker = conflict_checker
        
        # Register command handler
        self.slack_app.command("/event")(self.handle_event_command)

    def parse_event_command(self, text: str) -> Tuple[Optional[Event], Optional[str]]:
        """Parse event details from Slack command text"""
        # Expected format: "Meeting Name" 2024-03-20 14:00 15:00 "Conference Room A" "Description"
        pattern = r'"([^"]+)"\s+(\d{4}-\d{2}-\d{2})\s+(\d{2}:\d{2})\s+(\d{2}:\d{2})\s+"([^"]+)"\s*(?:"([^"]+)")?\s*$'
        
        match = re.match(pattern, text.strip())
        if not match:
            return None, "Invalid format. Please use: `/event \"Event Name\" YYYY-MM-DD HH:MM HH:MM \"Location\" \"Description\"`"
        
        name, date, start_time, end_time, location, description = match.groups()
        try:
            start_datetime = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
            end_datetime = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
            
            if end_datetime <= start_datetime:
                return None, "End time must be after start time"
                
            return Event(
                name=name,
                start_time=start_datetime,
                end_time=end_datetime,
                location=location,
                description=description or ""
            ), None
        except ValueError as e:
            return None, f"Invalid date/time format: {str(e)}"

    async def handle_event_command(self, ack, respond, command):
        """Handle /event slash command"""
        await ack()
        
        event, error = self.parse_event_command(command['text'])
        if error:
            await respond(f":x: Error: {error}")
            return
            
        try:
            # Check for conflicts
            day_start = event.start_time.replace(hour=0, minute=0, second=0)
            day_end = day_start.replace(hour=23, minute=59, second=59)
            existing_events = self.luma_client.get_events(day_start, day_end)
            
            if self.conflict_checker.has_conflict(event, existing_events):
                conflicting_events = [e for e in existing_events 
                                    if self.conflict_checker._events_overlap(
                                        event.start_time, event.end_time,
                                        e.start_time, e.end_time)]
                
                conflict_details = "\n".join([
                    f"• {e.name} ({e.start_time.strftime('%H:%M')} - {e.end_time.strftime('%H:%M')})"
                    for e in conflicting_events
                ])
                
                await respond(
                    f":warning: Cannot create event due to conflicts:\n{conflict_details}"
                )
                return
            
            # Create event
            event_id = self.luma_client.create_event(event)
            
            # Format success message
            await respond(
                f":white_check_mark: Event created successfully!\n"
                f"*{event.name}*\n"
                f"📅 {event.start_time.strftime('%B %d, %Y')}\n"
                f"🕒 {event.start_time.strftime('%H:%M')} - {event.end_time.strftime('%H:%M')}\n"
                f"📍 {event.location}\n"
                f"Event ID: {event_id}"
            )
            
        except Exception as e:
            await respond(f":x: Error creating event: {str(e)}") 