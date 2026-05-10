import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime, timezone

from ou_bot.common.config import DatabaseConfig
from ou_bot.common.ou_module import OUModule


def _ou_module_row_factory(cursor: sqlite3.Cursor, row: tuple) -> OUModule:
    fields = [col[0] for col in cursor.description]
    return OUModule(**dict(zip(fields, row)))


def _ensure_table(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS ou_modules (
            module_code     TEXT PRIMARY KEY,
            module_title    TEXT NOT NULL,
            url             TEXT NOT NULL,
            credits         INTEGER NOT NULL,
            ou_study_level  TEXT NOT NULL,
            next_start      TEXT,
            last_updated_utc TEXT NOT NULL
        )
        """
    )


class ModuleRepository:
    def __init__(self, config: DatabaseConfig | None = None) -> None:
        self._config = config or DatabaseConfig()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        self._config.database_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(
            str(self._config.database_path),
            detect_types=sqlite3.PARSE_DECLTYPES,
        )
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")

        try:
            _ensure_table(conn)
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def upsert(self, module: OUModule) -> None:
        with self._connect() as conn:
            conn.execute(
                """INSERT OR REPLACE INTO ou_modules
                   (module_code, module_title, url, credits,
                    ou_study_level, next_start, last_updated_utc)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    module.module_code,
                    module.module_title,
                    module.url,
                    module.credits,
                    module.ou_study_level,
                    module.next_start.isoformat() if module.next_start else None,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )

    def upsert_many(self, modules: list[OUModule]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            conn.executemany(
                """INSERT OR REPLACE INTO ou_modules
                   (module_code, module_title, url, credits,
                    ou_study_level, next_start, last_updated_utc)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                [
                    (
                        m.module_code,
                        m.module_title,
                        m.url,
                        m.credits,
                        m.ou_study_level,
                        m.next_start.isoformat() if m.next_start else None,
                        now,
                    )
                    for m in modules
                ],
            )

    def find_by_codes(self, module_codes: list[str]) -> list[OUModule]:
        if not module_codes:
            return []
        with self._connect() as conn:
            conn.row_factory = _ou_module_row_factory
            placeholders = ",".join("?" * len(module_codes))
            return conn.execute(
                f"SELECT * FROM ou_modules WHERE module_code IN ({placeholders})",
                tuple(module_codes),
            ).fetchall()

    def get_all_codes(self) -> list[str]:
        with self._connect() as conn:
            return [
                row[0]
                for row in conn.execute(
                    "SELECT module_code FROM ou_modules"
                ).fetchall()
            ]
