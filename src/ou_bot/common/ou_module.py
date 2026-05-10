from datetime import datetime

from pydantic import BaseModel, Field


class OUModule(BaseModel):
    module_code: str
    module_title: str
    url: str
    credits: int
    ou_study_level: str
    next_start: datetime | None = None
    last_updated: datetime | None = Field(default=None, alias="last_updated_utc")

    class Config:
        allow_population_by_field_name = True
