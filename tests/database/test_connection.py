import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.database.connection import (
    get_database_path,
    get_connection,
)


def test_get_database_path_normal_python() -> None:
    """Test get_database_path for normal Python execution."""
    path = get_database_path()
    assert isinstance(path, Path)
    assert path.name == 'foodlog.db'
    assert path.parent == Path(__file__).parent.parent.parent


def test_get_connection_creates_file() -> None:
    """Test get_connection creates a database file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'src.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            assert db_path.exists()
            conn.close()


def test_get_connection_returns_valid_connection() -> None:
    """Test get_connection returns a valid SQLite connection."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'src.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            assert isinstance(conn, sqlite3.Connection)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            assert result is not None
            conn.close()


def test_get_connection_row_factory() -> None:
    """Test get_connection sets row_factory to sqlite3.Row."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'src.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            assert conn.row_factory == sqlite3.Row
            conn.close()
