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


def test_migrate_schema_adds_both_migrations() -> None:
    """Test single migrate_schema() call adds ref_daily_values units AND choline_mcg."""
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

            cursor.execute('''
                CREATE TABLE dim_items (
                    item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name_id INTEGER NOT NULL,
                    category_id INTEGER,
                    price REAL NOT NULL,
                    servings_per_block REAL NOT NULL,
                    units TEXT NOT NULL,
                    container_size REAL NOT NULL,
                    serving_size REAL NOT NULL,
                    blocks_must_be_integer INTEGER NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1,
                    glycemic_index INTEGER,
                    ratio1 REAL NOT NULL DEFAULT 0,
                    ratio2 REAL NOT NULL DEFAULT 0,
                    calories REAL NOT NULL DEFAULT 0,
                    total_fat_g REAL NOT NULL DEFAULT 0,
                    saturated_fat_g REAL NOT NULL DEFAULT 0,
                    trans_fat_g REAL NOT NULL DEFAULT 0,
                    cholesterol_mcg REAL NOT NULL DEFAULT 0,
                    sodium_mcg REAL NOT NULL DEFAULT 0,
                    total_carbs_g REAL NOT NULL DEFAULT 0,
                    dietary_fiber_g REAL NOT NULL DEFAULT 0,
                    total_sugars_g REAL NOT NULL DEFAULT 0,
                    added_sugars_g REAL NOT NULL DEFAULT 0,
                    protein_g REAL NOT NULL DEFAULT 0,
                    vitamin_d_mcg REAL NOT NULL DEFAULT 0,
                    calcium_mcg REAL NOT NULL DEFAULT 0,
                    iron_mcg REAL NOT NULL DEFAULT 0,
                    potassium_mcg REAL NOT NULL DEFAULT 0,
                    vitamin_a_mcg REAL NOT NULL DEFAULT 0,
                    vitamin_c_mcg REAL NOT NULL DEFAULT 0,
                    vitamin_e_mcg REAL NOT NULL DEFAULT 0,
                    vitamin_k_mcg REAL NOT NULL DEFAULT 0,
                    thiamin_mcg REAL NOT NULL DEFAULT 0,
                    riboflavin_mcg REAL NOT NULL DEFAULT 0,
                    niacin_mcg REAL NOT NULL DEFAULT 0,
                    vitamin_b6_mcg REAL NOT NULL DEFAULT 0,
                    folate_mcg REAL NOT NULL DEFAULT 0,
                    vitamin_b12_mcg REAL NOT NULL DEFAULT 0,
                    biotin_mcg REAL NOT NULL DEFAULT 0,
                    pantothenic_acid_mcg REAL NOT NULL DEFAULT 0,
                    phosphorus_mcg REAL NOT NULL DEFAULT 0,
                    iodine_mcg REAL NOT NULL DEFAULT 0,
                    magnesium_mcg REAL NOT NULL DEFAULT 0,
                    zinc_mcg REAL NOT NULL DEFAULT 0,
                    selenium_mcg REAL NOT NULL DEFAULT 0,
                    copper_mcg REAL NOT NULL DEFAULT 0,
                    manganese_mcg REAL NOT NULL DEFAULT 0,
                    chromium_mcg REAL NOT NULL DEFAULT 0,
                    molybdenum_mcg REAL NOT NULL DEFAULT 0,
                    chloride_mcg REAL NOT NULL DEFAULT 0,
                    ethanol_g REAL NOT NULL DEFAULT 0
                )
            ''')
            conn.commit()

            cursor.execute("PRAGMA table_info(ref_daily_values)")
            ref_cols_before = {row[1] for row in cursor.fetchall()}
            cursor.execute("PRAGMA table_info(dim_items)")
            items_cols_before = {row[1] for row in cursor.fetchall()}

            assert "nutrient_fda_label_unit" not in ref_cols_before
            assert "choline_mcg" not in items_cols_before

            migrate_schema(conn)

            cursor.execute("PRAGMA table_info(ref_daily_values)")
            ref_cols_after = {row[1] for row in cursor.fetchall()}
            cursor.execute("PRAGMA table_info(dim_items)")
            items_cols_after = {row[1] for row in cursor.fetchall()}

            assert "nutrient_fda_label_unit" in ref_cols_after
            assert "nutrient_entry_unit" in ref_cols_after
            assert "nutrient_dim_items_unit" in ref_cols_after
            assert "choline_mcg" in items_cols_after

            conn.close()
