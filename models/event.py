from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

@dataclass
class Event:
    name: str
    start_time: datetime
    end_time: datetime
    location: str
    event_id: Optional[str] = None
    url: Optional[str] = None
    host_email: Optional[str] = None
    additional_hosts: Optional[List[str]] = None 