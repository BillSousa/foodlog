import tempfile
from pathlib import Path
from unittest.mock import patch

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data, NUTRIENTS


def test_seed_reference_data_inserts_nutrients() -> None:
    """Test seed_reference_data inserts all nutrients."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
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
            'foodlog.database.connection.get_database_path',
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
    """Test NUTRIENTS list has 6 fields for each nutrient."""
    for nutrient in NUTRIENTS:
        assert len(nutrient) == 6
        (
            name, label_unit, entry_unit, dim_items_unit, dv, tracked
        ) = nutrient
        assert isinstance(name, str) and name
        assert isinstance(label_unit, str) and label_unit
        assert isinstance(entry_unit, str) and entry_unit
        assert isinstance(dim_items_unit, str) and dim_items_unit
        assert isinstance(dv, (int, float))
        assert isinstance(tracked, int) and tracked in (0, 1)


def test_seed_reference_data_calories_tracked() -> None:
    """Test Calories nutrient is present."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
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
            'foodlog.database.connection.get_database_path',
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
            'foodlog.database.connection.get_database_path',
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


def test_sodium_has_correct_units() -> None:
    """Test Sodium nutrient has correct unit columns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)

            cursor = conn.cursor()
            cursor.execute(
                'SELECT nutrient_fda_label_unit, nutrient_entry_unit, '
                'nutrient_dim_items_unit FROM ref_daily_values '
                'WHERE nutrient_name = ?',
                ('Sodium',)
            )
            result = cursor.fetchone()

            assert result is not None
            assert tuple(result) == ("mg", "mg", "mcg")
            conn.close()


def test_cholesterol_has_correct_units() -> None:
    """Test Cholesterol nutrient has correct unit columns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)

            cursor = conn.cursor()
            cursor.execute(
                'SELECT nutrient_fda_label_unit, nutrient_entry_unit, '
                'nutrient_dim_items_unit FROM ref_daily_values '
                'WHERE nutrient_name = ?',
                ('Cholesterol',)
            )
            result = cursor.fetchone()

            assert result is not None
            assert tuple(result) == ("mg", "mg", "mcg")
            conn.close()


def test_vitamin_d_has_correct_units() -> None:
    """Test Vitamin D nutrient has correct unit columns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)

            cursor = conn.cursor()
            cursor.execute(
                'SELECT nutrient_fda_label_unit, nutrient_entry_unit, '
                'nutrient_dim_items_unit FROM ref_daily_values '
                'WHERE nutrient_name = ?',
                ('Vitamin D',)
            )
            result = cursor.fetchone()

            assert result is not None
            assert tuple(result) == ("mcg", "%", "mcg")
            conn.close()


def test_choline_has_correct_units() -> None:
    """Test Choline nutrient has correct unit columns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)

            cursor = conn.cursor()
            cursor.execute(
                'SELECT nutrient_fda_label_unit, nutrient_entry_unit, '
                'nutrient_dim_items_unit FROM ref_daily_values '
                'WHERE nutrient_name = ?',
                ('Choline',)
            )
            result = cursor.fetchone()

            assert result is not None
            assert tuple(result) == ("mg", "%", "mcg")
            conn.close()
