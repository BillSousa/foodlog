import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema


def test_create_schema_creates_all_tables() -> None:
    """Test create_schema creates all 8 tables."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'
        
        try:
            with patch(
                'foodlog.database.connection.get_database_path',
                return_value=db_path
            ):
                conn = get_connection()
                create_schema(conn)
    
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
                )
                tables = {row[0] for row in cursor.fetchall()}
    
                expected = {
                    'dim_product_names',
                    'dim_categories',
                    'ref_daily_values',
                    'dim_items',
                    'fact_orders',
                    'fact_order_lines',
                    'fact_consumption',
                    'settings',
                }
    
                assert tables == expected
        finally:
            conn.close()


def test_ref_daily_values_has_correct_columns() -> None:
    """Test ref_daily_values table has expected columns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)

            cursor = conn.cursor()
            cursor.execute('PRAGMA table_info(ref_daily_values)')
            columns = {row[1] for row in cursor.fetchall()}

            expected = {
                'nutrient_id',
                'nutrient_name',
                'dv_amount',
                'is_tracked',
            }

            assert columns == expected
            conn.close()


def test_dim_items_has_nutrition_columns() -> None:
    """Test dim_items table includes nutrition columns."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)

            cursor = conn.cursor()
            cursor.execute('PRAGMA table_info(dim_items)')
            columns = {row[1] for row in cursor.fetchall()}

            expected_nutrition = {
                'calories',
                'total_fat_g',
                'sodium_mcg',
                'protein_g',
                'vitamin_d_mcg',
                'calcium_mcg',
            }

            assert expected_nutrition.issubset(columns)
            conn.close()


def test_fact_orders_status_constraint() -> None:
    """Test fact_orders status column has CHECK constraint."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        try:
            with patch(
                'foodlog.database.connection.get_database_path',
                return_value=db_path
            ):
                conn = get_connection()
                create_schema(conn)
    
                cursor = conn.cursor()
    
                try:
                    cursor.execute(
                        '''INSERT INTO fact_orders
                        (order_date, is_delivery, status)
                        VALUES ('2026-07-29', 1, 'invalid_status')'''
                    )
                    assert False, "Should have raised constraint error"
                except sqlite3.IntegrityError:
                    pass
        finally:
            conn.close()


def test_create_schema_is_idempotent() -> None:
    """Test create_schema can be called multiple times safely."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / 'test.db'

        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            create_schema(conn)

            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%'"
            )
            count = cursor.fetchone()[0]

            assert count == 8
            conn.close()
