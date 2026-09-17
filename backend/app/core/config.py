from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# repo root .env, since one shared file covers both frontend and backend
ROOT_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ROOT_ENV_FILE, extra="ignore")

    database_url: str = ""
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173"]
    )

    # Supabase Auth issues HS256 JWTs signed with this project secret
    supabase_jwt_secret: str = ""
    supabase_jwt_audience: str = "authenticated"

    # Used by AuthService to call the Supabase Auth REST API directly
    supabase_url: str = ""
    supabase_publishable_key: str = ""


settings = Settings()
