from pydantic import Field
from pydantic_settings import BaseSettings


class CourseListScraperConfig(BaseSettings):
    url: str = Field(..., alias="OU_MODULE_URL", description="URL for OU modules")


class ThreadConfig(BaseSettings):
    max_workers: int = Field(
        5, alias="MAX_CONCURRENT_WORKERS", description="Number of workers to use for scraping pages"
    )
