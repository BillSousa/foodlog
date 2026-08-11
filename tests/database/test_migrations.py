import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from foodlog.database.connection import get_connection
from foodlog.database.migrations import migrate_schema
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data


def test_migrate_schema_adds_missing_columns() -> None:
    """Test migrate_schema adds the 3 new unit columns to old schema."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()

            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE ref_daily_values (
                    nutrient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nutrient_name TEXT NOT NULL,
                    dv_amount REAL NOT NULL,
                    is_tracked INTEGER NOT NULL DEFAULT 0
                )
            ''')
            cursor.execute(
                "INSERT INTO ref_daily_values "
                "(nutrient_name, dv_amount, is_tracked) "
                "VALUES (?, ?, ?)",
                ("Sodium", 2300000, 0)
            )
            conn.commit()

            migrate_schema(conn)

            cursor.execute("PRAGMA table_info(ref_daily_values)")
            columns = {row[1] for row in cursor.fetchall()}

            expected = {
                'nutrient_id',
                'nutrient_name',
                'nutrient_fda_label_unit',
                'nutrient_entry_unit',
                'nutrient_dim_items_unit',
                'dv_amount',
                'is_tracked',
            }

            assert columns == expected
            conn.close()


def test_migrate_schema_populates_columns_correctly() -> None:
    """Test migrate_schema populates unit columns with correct values."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()

            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE ref_daily_values (
                    nutrient_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nutrient_name TEXT NOT NULL,
                    dv_amount REAL NOT NULL,
                    is_tracked INTEGER NOT NULL DEFAULT 0
                )
            ''')
            cursor.execute(
                "INSERT INTO ref_daily_values "
                "(nutrient_name, dv_amount, is_tracked) "
                "VALUES (?, ?, ?)",
                ("Sodium", 2300000, 0)
            )
            cursor.execute(
                "INSERT INTO ref_daily_values "
                "(nutrient_name, dv_amount, is_tracked) "
                "VALUES (?, ?, ?)",
                ("Vitamin D", 20, 0)
            )
            conn.commit()

            migrate_schema(conn)

            cursor.execute(
                "SELECT nutrient_fda_label_unit, nutrient_entry_unit, "
                "nutrient_dim_items_unit FROM ref_daily_values "
                "WHERE nutrient_name = ?",
                ("Sodium",)
            )
            sodium_row = cursor.fetchone()
            assert tuple(sodium_row) == ("mg", "mg", "mcg")

            cursor.execute(
                "SELECT nutrient_fda_label_unit, nutrient_entry_unit, "
                "nutrient_dim_items_unit FROM ref_daily_values "
                "WHERE nutrient_name = ?",
                ("Vitamin D",)
            )
            vitamin_d_row = cursor.fetchone()
            assert tuple(vitamin_d_row) == ("mcg", "%", "mcg")

            conn.close()


def test_migrate_schema_is_idempotent() -> None:
    """Test migrate_schema can be called multiple times safely."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)

            migrate_schema(conn)
            migrate_schema(conn)

            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(ref_daily_values)")
            columns = {row[1] for row in cursor.fetchall()}

            expected = {
                'nutrient_id',
                'nutrient_name',
                'nutrient_fda_label_unit',
                'nutrient_entry_unit',
                'nutrient_dim_items_unit',
                'dv_amount',
                'is_tracked',
            }

            assert columns == expected
            conn.close()
