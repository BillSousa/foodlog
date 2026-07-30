import tempfile
from pathlib import Path
from unittest.mock import patch

from src.database.connection import get_connection
from src.database.schema import create_schema
from src.database.seed_reference_data import seed_reference_data, NUTRIENTS


def test_seed_reference_data_inserts_nutrients() -> None:
    """Test seed_reference_data inserts all nutrients."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'src.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)

            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM ref_daily_values')
            count = cursor.fetchone()[0]

            assert count == len(NUTRIENTS)
            conn.close()


def test_seed_reference_data_is_idempotent() -> None:
    """Test seed_reference_data only inserts once."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'src.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)
            seed_reference_data(conn)

            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM ref_daily_values')
            count = cursor.fetchone()[0]

            assert count == len(NUTRIENTS)
            conn.close()


def test_nutrients_have_units() -> None:
    """Test NUTRIENTS list has units and %DV flag for each nutrient."""
    for nutrient in NUTRIENTS:
        assert len(nutrient) == 5
        name, unit, dv, tracked, is_dv_percent = nutrient
        assert isinstance(name, str) and name
        assert isinstance(unit, str) and unit
        assert isinstance(dv, (int, float))
        assert isinstance(tracked, int) and tracked in (0, 1)
        assert isinstance(is_dv_percent, bool)


def test_seed_reference_data_calories_tracked() -> None:
    """Test Calories nutrient is present."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'src.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)

            cursor = conn.cursor()
            cursor.execute(
                'SELECT dv_amount FROM ref_daily_values '
                'WHERE nutrient_name = ?',
                ('Calories',)
            )
            result = cursor.fetchone()

            assert result is not None
            assert result[0] == 2000
            conn.close()


def test_seed_reference_data_vitamin_d_tracked() -> None:
    """Test Vitamin D nutrient is present with correct value."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'src.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)

            cursor = conn.cursor()
            cursor.execute(
                'SELECT dv_amount FROM ref_daily_values '
                'WHERE nutrient_name = ?',
                ('Vitamin D',)
            )
            result = cursor.fetchone()

            assert result is not None
            assert result[0] == 20
            conn.close()


def test_all_nutrients_initially_untracked() -> None:
    """Test all nutrients seed with is_tracked = 0."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'src.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)

            cursor = conn.cursor()
            cursor.execute(
                'SELECT COUNT(*) FROM ref_daily_values WHERE is_tracked = 1'
            )
            count = cursor.fetchone()[0]

            assert count == 0
            conn.close()
