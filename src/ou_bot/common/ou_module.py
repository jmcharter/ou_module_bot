from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class OUModule(BaseModel):
    module_code: str
    module_title: str
    url: str
    credits: int
    ou_study_level: int
    related_qualifications: list[str]
    course_work_includes: list[str]
    next_start: datetime
    next_end: Optional[datetime]
