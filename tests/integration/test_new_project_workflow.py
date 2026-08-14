"""Integration test: Fresh project setup through first order."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.initialization.initialize_defaults import initialize_defaults
from foodlog.initialization.first_run_check import is_first_run
from foodlog.models.dim_items import Item
from foodlog.models.fact_orders import Order
from foodlog.models.fact_order_lines import OrderLine
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.orders_repository import OrdersRepository
from foodlog.repository.order_lines_repository import OrderLinesRepository
from foodlog.repository.settings_repository import SettingsRepository
from foodlog.repository.tracked_nutrients_repository import (
    TrackedNutrientsRepository,
)


def test_new_project_setup_workflow() -> None:
    """Test complete new project setup workflow."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        with patch(
            "foodlog.database.connection.get_database_path", return_value=db_path
        ):
            # Step 1: Initialize database
            conn = get_connection()
            assert db_path.exists()

            # Step 2: Create schema
            create_schema(conn)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row[0] for row in cursor.fetchall()}
            assert "dim_items" in tables
            assert "fact_orders" in tables

            # Step 3: Seed reference data
            seed_reference_data(conn)
            cursor.execute("SELECT COUNT(*) FROM ref_daily_values")
            nutrient_count = cursor.fetchone()[0]
            assert nutrient_count > 0
            conn.close()

            # Step 4: Initialize defaults
            assert is_first_run()
            initialize_defaults()

            settings_repo = SettingsRepository()
            cal_target = settings_repo.get_setting("cal_per_day_target")
            assert cal_target == "2000"

            # Step 5: Create item
            items_repo = ItemsRepository()
            item = Item(
                name_id=1,
                price=5.99,
                servings_per_block=12.0,
                units="box",
                container_size=360,
                serving_size=30,
                blocks_must_be_integer=False,
                active=True,
                calories=150,
                protein_g=5,
                sodium_mcg=400,
                choline_mcg=0,
            )
            item_id = items_repo.create_item(item)
            assert item_id is not None

            # Step 6: Create order
            orders_repo = OrdersRepository()
            order = Order(
                order_date="2024-01-15",
                is_delivery=False,
                status="planning"
            )
            order_id = orders_repo.create_order(order)
            assert order_id is not None

            # Step 7: Add order line
            lines_repo = OrderLinesRepository()
            line = OrderLine(
                order_id=order_id,
                item_id=item_id,
                servings_ordered=12.0,
                actual_servings=12.0,
                stated_price=5.99,
                sale=0,
                discount=0,
                coupon=0,
                net_price=71.88,
            )
            line_id = lines_repo.create_order_line(line)
            assert line_id is not None

            # Step 8: Verify order data
            lines = lines_repo.get_order_lines(order_id)
            assert len(lines) == 1
            assert lines[0].item_id == item_id
            assert lines[0].actual_servings == 12.0


def test_nutrient_tracking_workflow() -> None:
    """Test enabling/disabling nutrient tracking."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"

        with patch(
            "foodlog.database.connection.get_database_path", return_value=db_path
        ):
            conn = get_connection()
            create_schema(conn)
            seed_reference_data(conn)
            initialize_defaults()
            conn.close()

            # Initially, all nutrients should be untracked
            repo = TrackedNutrientsRepository()
            tracked = repo.get_tracked_nutrients()
            assert len(tracked) == 0

            # Enable tracking for Calories
            repo.set_tracked("Calories", True)
            tracked = repo.get_tracked_nutrients()
            assert "Calories" in tracked

            # Disable tracking
            repo.set_tracked("Calories", False)
            tracked = repo.get_tracked_nutrients()
            assert "Calories" not in tracked
