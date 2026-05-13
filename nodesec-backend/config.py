from pydantic_settings import BaseSettings, SettingsConfigDict


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

    # Pydantic v2 style — replaces deprecated class Config
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()