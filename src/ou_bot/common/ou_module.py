from datetime import datetime
from sqlite3 import Cursor
from pydantic import BaseModel


class OUModule(BaseModel):
    last_updated: datetime | None = None
    module_code: str
    module_title: str
    url: str
    credits: int
    ou_study_level: str
    next_start: datetime | None


def ou_module_factory(cursor: Cursor, row) -> OUModule:
    fields = [column[0] for column in cursor.description]
    data = dict(zip(fields, row))

    # Map 'last_updated_utc' to 'last_updated'
    if "last_updated_utc" in data:
        data["last_updated"] = data.pop("last_updated_utc")

    return OUModule(**data)
