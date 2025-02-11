import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    def __init__(self):
        self.API_KEY = os.getenv('LUMA_API_KEY')
        self.BASE_URL = os.getenv('LUMA_API_BASE_URL', 'https://api.lu.ma/public/v1')
        self.DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
        self.DEFAULT_BUFFER_MINUTES = int(os.getenv('DEFAULT_BUFFER_MINUTES', '0'))
    
    def is_luma_configured(self) -> bool:
        """Check if Luma API is configured"""
        return bool(self.API_KEY) 