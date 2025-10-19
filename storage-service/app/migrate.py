"""Simple SQLite migration runner for storage-service.

This runner applies SQL migration files from the migrations/versions directory
and records applied migrations in a `migrations` table in the SQLite database.

Usage:
    python app/migrate.py

The default DB path is /app/data/database.db. You can override it with DB_PATH env var.
"""

import os
import sqlite3
from pathlib import Path

DB_PATH = os.environ.get("DB_PATH", "/app/data/database.db")
MIGRATIONS_DIR = Path(__file__).resolve().parents[1] / "migrations" / "versions"


def ensure_db_dir(path: str):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)


def get_migration_files():
    files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    return files


def ensure_migrations_table(conn: sqlite3.Connection):
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS migrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL UNIQUE,
            applied_at DATETIME DEFAULT (CURRENT_TIMESTAMP)
        )
        """
    )
    conn.commit()


def already_applied(conn: sqlite3.Connection, filename: str) -> bool:
    cur = conn.execute("SELECT 1 FROM migrations WHERE filename = ?", (filename,))
    return cur.fetchone() is not None


def apply_migration(conn: sqlite3.Connection, path: Path):
    with open(path, "r") as f:
        sql = f.read()
    conn.executescript(sql)
    conn.execute("INSERT INTO migrations (filename) VALUES (?)", (path.name,))
    conn.commit()
    print(f"Applied migration: {path.name}")


def main():
    ensure_db_dir(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    ensure_migrations_table(conn)
    files = get_migration_files()
    for f in files:
        if already_applied(conn, f.name):
            print(f"Skipping already applied migration: {f.name}")
            continue
        apply_migration(conn, f)
    conn.close()
    print("All migrations applied.")


if __name__ == "__main__":
    main()
