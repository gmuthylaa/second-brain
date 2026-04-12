from functools import lru_cache
from pathlib import Path
from typing import List, Optional

try:
    from pydantic_settings import BaseSettings
except Exception:
    try:
        from pydantic import BaseSettings  
    except Exception as exc:
        raise ImportError(
            "BaseSettings is not available. Install pydantic-settings for pydantic v2: `pip install pydantic-settings`"
        ) from exc

from pydantic import Field, field_validator


class Settings(BaseSettings):
    app_env: str = Field("development", env="APP_ENV")
    debug: bool = Field(False, env="DEBUG")
    cors_origins: Optional[List[str]] = Field(None, env="CORS_ORIGINS")

    @field_validator("cors_origins", mode="before")
    def parse_cors(cls, v):
        if v is None:
            return None
        if isinstance(v, (list, tuple)):
            return list(v)
        if isinstance(v, str):
            # try JSON first
            try:
                import json

                parsed = json.loads(v)
                if isinstance(parsed, list):
                    return parsed
            except Exception:
                pass
            # fall back to comma-separated
            return [s.strip() for s in v.split(",") if s.strip()]
        return v


    class Config:
        # Resolve .env relative to the backend folder where this project stores it
        env_file = str(Path(__file__).resolve().parents[1] / ".env")
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
