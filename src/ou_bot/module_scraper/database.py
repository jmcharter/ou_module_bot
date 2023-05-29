import sqlite3
from ou_bot.module_scraper.config import DatabaseConfig
from ou_bot.ou_module import OUModule


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

    def add_ou_module(self, module: OUModule):
        sql = """
            INSERT OR IGNORE INTO ou_modules (
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
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        try:
            next_end = module.next_end.isoformat()
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
            module.next_start.isoformat(),
            next_end,
        )
        self.cursor.execute(sql, values)
        self.conn.commit()
