"""SQLite connection factory (doc 04/61): WAL, FK on, backup-first migrations, transactional context."""
from __future__ import annotations

import shutil
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA_VERSION = 1


def connect(db_path: str | Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db(db_path: str | Path) -> sqlite3.Connection:
    conn = connect(db_path)
    schema = (Path(__file__).with_name("schema.sql")).read_text(encoding="utf-8")
    conn.executescript(schema)
    row = conn.execute("SELECT version FROM schema_meta").fetchone()
    if row is None:
        conn.execute("INSERT INTO schema_meta(version) VALUES (?)", (SCHEMA_VERSION,))
    conn.commit()
    return conn


@contextmanager
def transaction(conn: sqlite3.Connection):
    try:
        conn.execute("BEGIN")
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def backup_before_migration(db_path: str | Path, from_version: int) -> Path:
    db_path = Path(db_path)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
    dest = db_path.parent / "backups" / f"pre-migration-{from_version}-{stamp}.db"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(db_path, dest)
    return dest


def verify_integrity(conn: sqlite3.Connection) -> bool:
    return conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
