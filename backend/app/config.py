import os
import json
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
    cors_origins: List[str] = [
        "http://localhost:8501", 
        "http://frontend:8501", 
        "https://testkkok.zapto.org",
        "http://testkkok.zapto.org"
    ]

    # File Upload
    max_upload_size: int = 100 * 1024 * 1024  # 100MB
    allowed_extensions: List[str] = [".csv", ".xlsx"]

    class Config:
        env_file = ".env"
        case_sensitive = False


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # NUEVA LÓGICA: Convierte string del .env a lista
        if isinstance(self.cors_origins, str):
            try:
                self.cors_origins = json.loads(self.cors_origins)
            except json.JSONDecodeError:
                self.cors_origins = [self.cors_origins]

   # Ensure data directory exists
        self.data_dir.mkdir(exist_ok=True)
        (self.data_dir / "datasets").mkdir(exist_ok=True)
        (self.data_dir / "temp").mkdir(exist_ok=True)


settings = Settings()

#sudo nano /etc/nginx/sites-available/itsm
