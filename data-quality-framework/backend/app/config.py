import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./test.db")
    DEBUG: bool = os.getenv("DEBUG", "False") == "True"
    ENV: str = os.getenv("ENV", "development")

settings = Settings()
