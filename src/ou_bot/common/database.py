from datetime import datetime, timezone
import sqlite3
from ou_bot.common.config import DatabaseConfig
from ou_bot.common.ou_module import OUModule, ou_module_factory


class db:
    config: DatabaseConfig

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.conn = sqlite3.connect("data/" + self.config.database_name + ".db")
        self.cursor = self.conn.cursor()

        # Create the OUModule table if it doesn't exist
        self.cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS ou_modules (
                module_code TEXT PRIMARY KEY,
                module_title TEXT,
                url TEXT,
                credits INTEGER,
                ou_study_level INTEGER,
                related_qualifications TEXT,
                course_work_includes TEXT,
                next_start TEXT,
                next_end TEXT,
                last_updated_utc TEXT
            )
        """
        )
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, _exc_type, _exc_value, _traceback):
        if self.conn:
            self.conn.close()

    def close(self):
        if hasattr(self, "conn") and self.conn:
            self.conn.commit()
            self.cursor.close()
            self.conn.close()

    def upsert_ou_module(self, module: OUModule):
        sql = """
            INSERT OR REPLACE INTO ou_modules (
                module_code,
                module_title,
                url,
                credits,
                ou_study_level,
                related_qualifications,
                course_work_includes,
                next_start,
                next_end,
                last_updated_utc
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
            module.module_code,
            module.module_title,
            module.url,
            module.credits,
            module.ou_study_level,
            ", ".join(module.related_qualifications),
            ", ".join(module.course_work_includes),
            next_start,
            next_end,
            datetime.now(tz=timezone.utc),
        )
        self.cursor.execute(sql, values)
        self.conn.commit()

    def query_ou_modules(self, module_codes: list[str]) -> list[OUModule]:
        original_row_factory = self.conn.row_factory
        placeholders = ",".join("?" for _ in module_codes)

        sql = f"""
            SELECT * FROM ou_modules
            WHERE module_code IN ({placeholders})
        """

        self.conn.row_factory = ou_module_factory
        cursor = self.conn.cursor()
        cursor.execute(sql, tuple(module_codes))
        self.conn.row_factory = original_row_factory
        return cursor.fetchall()

    def get_all_module_codes(self) -> list[str]:
        sql = """
            SELECT module_code FROM ou_modules;
        """
        self.cursor.execute(sql)
        results = self.cursor.fetchall()
        return [row[0] for row in results]
