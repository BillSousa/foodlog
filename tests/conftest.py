"""Pytest configuration for all tests."""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data


@pytest.fixture(autouse=True)
def test_database():
    """Create and initialize a temporary test database.

    This fixture is automatically used by all tests. It creates a
    temporary database with the full schema and reference data, then
    patches get_database_path to use this temp database for the test.
    After the test, the temporary file is cleaned up.
    """
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "test_foodlog.db"

    patcher = patch(
        "foodlog.database.connection.get_database_path",
        return_value=db_path
    )
    patcher.start()

    conn = get_connection()
    create_schema(conn)
    seed_reference_data(conn)
    conn.close()

    yield

    patcher.stop()
