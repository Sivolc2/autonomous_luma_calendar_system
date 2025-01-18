import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    API_KEY: str = os.getenv("LUMA_API_KEY")
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN")
    SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET")
    BASE_URL: str = "https://api.lu.ma/public/v1"
    DEFAULT_BUFFER_MINUTES: int = 15 