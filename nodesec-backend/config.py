import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://nodesec:password@localhost:5432/nodesec"
    secret_key: str = "change-me-to-a-random-32-char-string"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    allowed_origins: str = "http://localhost:5173"
    sendgrid_api_key: str = ""
    frontend_url: str = "http://localhost:5173"
    hibp_api_key: str = ""
    shodan_api_key: str = ""

    class Config:
        env_file = ".env"


settings = Settings()