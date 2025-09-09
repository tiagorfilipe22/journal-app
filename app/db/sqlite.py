import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, date


DB_FILENAME = "journal.db"


def get_db_path() -> str:
    return os.path.join(os.getcwd(), DB_FILENAME)


def initialize_database() -> None:
    db_path = get_db_path()
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL UNIQUE,
                content_md TEXT NOT NULL DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );
            """
        )
        conn.commit()


@contextmanager
def open_db():
    conn = sqlite3.connect(get_db_path())
    try:
        yield conn
    finally:
        conn.close()


def _iso_today() -> str:
    return date.today().isoformat()


def get_entry(entry_date: str | None = None) -> str:
    if entry_date is None:
        entry_date = _iso_today()
    with open_db() as conn:
        cur = conn.execute(
            "SELECT content_md FROM entries WHERE date = ?", (entry_date,)
        )
        row = cur.fetchone()
        return row[0] if row else ""


def upsert_entry(content_md: str, entry_date: str | None = None) -> None:
    if entry_date is None:
        entry_date = _iso_today()
    timestamp = datetime.utcnow().isoformat(timespec="seconds") + "Z"
    with open_db() as conn:
        conn.execute(
            """
            INSERT INTO entries (date, content_md, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(date) DO UPDATE SET
                content_md = excluded.content_md,
                updated_at = excluded.updated_at
            """,
            (entry_date, content_md, timestamp, timestamp),
        )
        conn.commit()


