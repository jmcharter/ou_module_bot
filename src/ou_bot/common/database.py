from datetime import datetime, timezone
import sqlite3
from ou_bot.common.config import DatabaseConfig
from ou_bot.common.ou_module import OUModule


class db:
    def __init__(self, config: DatabaseConfig):
        self.conn = None
        self.cursor = None
        self.config = config

    def __enter__(self):
        self.conn = sqlite3.connect(self.config.database_name + ".db")
        self.cursor = self.conn.cursor()

        # Create the OUModule table if it doesn't exist
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ou_modules (
                id INTEGER PRIMARY KEY,
                last_updated_utc TEXT,
                module_code TEXT,
                module_title TEXT,
                url TEXT,
                credits INTEGER,
                ou_study_level INTEGER,
                related_qualifications TEXT,
                course_work_includes TEXT,
                next_start TEXT,
                next_end TEXT
            )
        """
        )
        self.conn.commit()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.conn.close()

    def upsert_ou_module(self, module: OUModule):
        sql = """
            INSERT OR REPLACE INTO ou_modules (
                last_updated_utc,
                module_code,
                module_title,
                url,
                credits,
                ou_study_level,
                related_qualifications,
                course_work_includes,
                next_start,
                next_end
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            next_start = module.next_start.isoformat() if module.next_start else None
        except AttributeError:
            next_start = None

        try:
            next_end = module.next_end.isoformat() if module.next_end else None
        except AttributeError:
            next_end = None

        values = (
            datetime.now(tz=timezone.utc),
            module.module_code,
            module.module_title,
            module.url,
            module.credits,
            module.ou_study_level,
            ", ".join(module.related_qualifications),
            ", ".join(module.course_work_includes),
            next_start,
            next_end,
        )
        self.cursor.execute(sql, values)
        self.conn.commit()

    def query_ou_modules(self, module_codes: list[str]) -> list[tuple]:
        placeholders = ",".join("?" for _ in module_codes)

        sql = f"""
            SELECT * FROM ou_modules
            WHERE module_code IN ({placeholders})
        """
        self.cursor.execute(sql, tuple(module_codes))
        return self.cursor.fetchall()

    def get_all_module_codes(self) -> list[tuple]:
        sql = """
            SELECT module_code FROM ou_modules;
        """
        self.cursor.execute(sql)
        return self.cursor.fetchall()
