from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class OUModule(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    module_code: str
    module_title: str
    url: str
    credits: int
    ou_study_level: str
    next_start: datetime | None = None
    last_updated: datetime | None = Field(default=None, alias="last_updated_utc")
