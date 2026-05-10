from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


class DatabaseConfig(BaseSettings):
    database_path: Path = Field(
        default=Path("data/ou_modules.db"),
        description="Full path to the SQLite database file",
    )
