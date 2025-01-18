# Autonomous Luma Calendar System

A web application that provides a simple interface for creating events in Luma while automatically checking for conflicts.

## Features

1. **Event Creation**: Simple form interface to create new events
2. **Conflict Detection**: Automatically checks for time/space conflicts
3. **Location Management**: Predefined spaces to choose from
4. **Buffer Time**: Includes buffer time between events (configurable)

## Backend Architecture

### API Endpoints

1. `GET /` - Serves the main application interface
2. `GET /locations` - Returns available spaces/rooms
3. `POST /events/create` - Creates a new event with conflict checking

### Event Creation Flow

1. User submits event details through the form
2. Backend validates the request
3. System checks for conflicts by:
   - Fetching existing events for that day using Luma's `/calendar/list-events` endpoint
   - Comparing time slots including buffer time
   - Checking space availability
4. If no conflicts, creates event using Luma's API
5. Returns success/error response to user

### Configuration

Required environment variables:
```env
LUMA_API_KEY=your_api_key_here # Your Luma Calendar API key
```

```json
{
"name": "Team Meeting",
"start_time": "2024-03-20T14:00:00",
"end_time": "2024-03-20T15:00:00",
"location": "Conference Room A",
"description": "Weekly team sync"
}
```


### Example Response
Success:
```json
{
"event_id": "evt_123abc",
"message": "Event created successfully"
}
```

Error (Conflict):
```json
{
"detail": "Event conflicts with existing events"
}
```

## Known Limitations

1. The Luma API endpoint `/calendar/list-events` only returns events managed by your Calendar, not events that are listed but not managed
2. All times are handled in ISO 8601 format
3. Buffer time is currently fixed at 15 minutes (configurable in config.py)

## Future Improvements

1. Add recurring event support
2. Implement calendar view of existing events
3. Add email notifications for conflicts
4. Support for multiple calendars
5. Custom buffer times per space

## Slack Integration

Users can create events directly from Slack using the `/event` command:

```
/event "Team Meeting" 2024-03-20 14:00 15:00 "Conference Room A" "Weekly team sync"
```

### Slack Configuration

Required environment variables:
```env
SLACK_BOT_TOKEN=xoxb-your-bot-token
SLACK_SIGNING_SECRET=your-signing-secret
```

### Slack Command Format

```
/event "Event Name" YYYY-MM-DD HH:MM HH:MM "Location" "Description"
```

### Slack Responses

Success:
```
✅ Event created successfully!
Team Meeting
📅 March 20, 2024
🕒 14:00 - 15:00
📍 Conference Room A
Event ID: evt_123abc
```

Conflict:
```
⚠️ Cannot create event due to conflicts:
• Daily Standup (13:30 - 14:30)
• Team Lunch (14:00 - 15:00)
```

Error:
```
❌ Error: Invalid format. Please use: /event "Event Name" YYYY-MM-DD HH:MM HH:MM "Location" "Description"
```

