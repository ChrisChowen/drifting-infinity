from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Drifting Infinity"
    debug: bool = True

    # Database
    database_url: str = f"sqlite+aiosqlite:///{Path(__file__).parent.parent / 'data' / 'drifting_infinity.db'}"

    # Open5e API
    open5e_base_url: str = "https://api.open5e.com/v1"

    # Optional LLM (Phase 4)
    anthropic_api_key: str | None = None
    llm_enabled: bool = False

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
