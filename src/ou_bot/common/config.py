from pydantic import BaseSettings, Field


class DatabaseConfig(BaseSettings):
    database_name: str = Field(..., env="DATABASE_NAME", description="Name of database")
