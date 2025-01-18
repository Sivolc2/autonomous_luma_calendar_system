import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    API_KEY: str = os.getenv("LUMA_API_KEY")
    if not API_KEY:
        raise ValueError("LUMA_API_KEY environment variable is not set")
    BASE_URL: str = "https://api.lu.ma/public/v1"
    DEFAULT_BUFFER_MINUTES: int = 15 