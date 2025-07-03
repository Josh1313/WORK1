import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Backend API
    BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Streamlit settings
    PAGE_TITLE = "Data Analysis Dashboard"
    PAGE_ICON = "📊"
    
    # File upload limits
    MAX_UPLOAD_SIZE = 100  # MB

config = Config()