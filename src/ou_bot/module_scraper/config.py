from pydantic import BaseSettings, Field


class ScraperConfig(BaseSettings):
    url: str


class CourseListScraperConfig(BaseSettings):
    url: str = Field(..., env="OU_MODULE_URL", description="URL for OU modules")


class ThreadConfig(BaseSettings):
    max_workers: int = Field(5, env="MAX_CONCURRENT_WORKERS", description="Number of workers to use for scraping pages")


class DatabaseConfig(BaseSettings):
    database_name: str = Field(..., env="DATABASE_NAME", description="Name of database")
