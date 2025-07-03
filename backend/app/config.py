import os
from typing import List
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    # API Settings
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    api_title: str = "Data Analysis API"
    api_version: str = "1.0.0"
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./data/app.db"
    data_dir: Path = Path("./data")
    

    # OpenAI
    openai_api_key: str
    
    # Security
    secret_key: str = "Josue"
    cors_origins: List[str] = ["http://localhost:8501"]
    
    # File Upload
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = [".csv", ".xlsx"]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "datasets").mkdir(exist_ok=True)
        (self.data_dir / "temp").mkdir(exist_ok=True)

settings = Settings()