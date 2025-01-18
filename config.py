import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class Config:
    DEBUG_MODE: bool = os.getenv("DEBUG_MODE", "false").lower() == "true"
    API_KEY: str = os.getenv("LUMA_API_KEY")
    SLACK_BOT_TOKEN: str = os.getenv("SLACK_BOT_TOKEN")
    SLACK_SIGNING_SECRET: str = os.getenv("SLACK_SIGNING_SECRET")
    BASE_URL: str = "https://api.lu.ma/public/v1"
    DEFAULT_BUFFER_MINUTES: int = 15

    def is_slack_configured(self) -> bool:
        return not self.DEBUG_MODE and self.SLACK_BOT_TOKEN and self.SLACK_SIGNING_SECRET

    def is_luma_configured(self) -> bool:
        return not self.DEBUG_MODE and self.API_KEY 