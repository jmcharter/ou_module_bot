from datetime import datetime
from sqlite3 import Cursor
from pydantic import BaseModel


class OUModule(BaseModel):
    last_updated: datetime
    module_code: str
    module_title: str
    url: str
    credits: int
    ou_study_level: int
    related_qualifications: list[str]
    course_work_includes: list[str]
    next_start: datetime | None
    next_end: datetime | None


def ou_module_factory(cursor: Cursor, row):
    fields = [column[0] for column in cursor.description]
    data = dict(zip(fields, row))

    # Map 'last_updated_utc' to 'last_updated'
    if "last_updated_utc" in data:
        data["last_updated"] = data.pop("last_updated_utc")

    # Convert comma-separated strings to lists
    if "related_qualifications" in data:
        data["related_qualifications"] = (
            [x.strip() for x in data["related_qualifications"].split(",")] if data["related_qualifications"] else []
        )

    if "course_work_includes" in data:
        data["course_work_includes"] = (
            [x.strip() for x in data["course_work_includes"].split(",")] if data["course_work_includes"] else []
        )

    return OUModule(**data)
