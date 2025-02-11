from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Event:
    name: str
    start_time: datetime
    end_time: datetime
    location: str
    description: Optional[str] = None
    event_id: Optional[str] = None
    url: Optional[str] = None
    host_email: Optional[str] = None 