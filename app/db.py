"""SQLite storage. The database is the last safety net below validation."""

import sqlite3
from pathlib import Path

from app.units import UNITS

SCHEMA = """
CREATE TABLE IF NOT EXISTS units (
    name  TEXT PRIMARY KEY,
    label TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS recipes (
    id                INTEGER PRIMARY KEY,
    name              TEXT NOT NULL,
    prep_time_minutes INTEGER,
    created_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at        TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ingredients (
    id        INTEGER PRIMARY KEY,
    recipe_id INTEGER NOT NULL REFERENCES recipes(id) ON DELETE CASCADE,
    position  INTEGER NOT NULL,
    name      TEXT NOT NULL,
    amount    REAL,
    unit      TEXT NOT NULL REFERENCES units(name)
);
"""


def connect(path: Path | str) -> sqlite3.Connection:
    # One connection per request. FastAPI may open it in one thread and use it in another,
    # but never from two threads at once, so the same-thread check is not needed.
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # SQLite ignores foreign keys unless this is set on every connection.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(SCHEMA)
    conn.executemany("INSERT OR IGNORE INTO units (name, label) VALUES (?, ?)", UNITS)
    conn.commit()
