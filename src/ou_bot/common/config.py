from pathlib import Path

from pydantic import BaseSettings, Field


class DatabaseConfig(BaseSettings):
    database_path: Path = Field(
        default=Path("data/ou_modules.db"),
        env="DATABASE_PATH",
        description="Full path to the SQLite database file",
    )
