import sqlite3
from pathlib import Path
from typing import Generator


def get_database_path() -> Path:
    """
    Locate the foodlog.db file relative to the running executable.

    For normal Python runs, uses the directory containing main.py.
    For PyInstaller bundles, uses the directory containing the executable.
    """
    if getattr(__import__('sys'), 'frozen', False):
        exe_dir = Path(__import__('sys').executable).parent
    else:
        exe_dir = Path(__file__).parent.parent.parent

    return exe_dir / 'foodlog.db'


def get_connection() -> sqlite3.Connection:
    """
    Create and return a SQLite database connection.

    Returns:
        sqlite3.Connection: Connection to foodlog.db
    """
    db_path = get_database_path()
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def get_cursor(conn: sqlite3.Connection) -> Generator:
    """
    Context manager for database cursor.

    Yields:
        sqlite3.Cursor: Database cursor
    """
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
