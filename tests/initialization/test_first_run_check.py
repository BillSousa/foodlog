import tempfile
from pathlib import Path
from unittest.mock import patch

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.initialization.first_run_check import is_first_run
from foodlog.initialization.initialize_defaults import initialize_defaults


def test_is_first_run_fresh_db() -> None:
    """Test is_first_run returns True for fresh database."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)
            conn.close()

            assert is_first_run() is True


def test_is_first_run_after_init() -> None:
    """Test is_first_run after initialize_defaults."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)
            conn.close()

            initialize_defaults()

            assert is_first_run() is True


def test_is_first_run_after_wizard() -> None:
    """Test is_first_run returns False after wizard completion."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)
            conn.close()

            initialize_defaults()

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE settings SET setting_value = ? '
                'WHERE setting_key = ?',
                ('1', 'wizard_completed')
            )
            conn.commit()
            conn.close()

            assert is_first_run() is False
