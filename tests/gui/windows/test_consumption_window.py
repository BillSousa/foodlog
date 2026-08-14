import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.models.dim_items import Item
from foodlog.models.fact_consumption import Consumption
from foodlog.models.fact_order_lines import OrderLine
from foodlog.models.fact_orders import Order
from foodlog.repository.consumption_repository import ConsumptionRepository
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.orders_repository import OrdersRepository
from foodlog.repository.order_lines_repository import OrderLinesRepository
from foodlog.calculations.on_hand import calculate_on_hand


@pytest.fixture
def test_db() -> Path:
    """Create temp test database."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "test.db"
    with patch(
        "foodlog.database.connection.get_database_path", return_value=db_path
    ):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


def test_consumption_window_on_hand_calculation(test_db: Path) -> None:
    """Test that on-hand calculates correctly for consumption entry."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)

        items_repo = ItemsRepository()
        orders_repo = OrdersRepository()
        lines_repo = OrderLinesRepository()

        item = Item(
            name_id=1,
            price=5.0,
            servings_per_block=10.0,
            units="units",
            container_size=100,
            serving_size=10,
            blocks_must_be_integer=False,
            active=True,
            calories=100,
            protein_g=5,
            sodium_mcg=200,
            choline_mcg=0,
        )
        item_id = items_repo.create_item(item)

        order = Order(order_date="2024-01-01", is_delivery=False, status="planning")
        order_id = orders_repo.create_order(order)

        line = OrderLine(
            order_id=order_id,
            item_id=item_id,
            servings_ordered=20.0,
            actual_servings=20.0,
            stated_price=5.0,
            sale=0,
            discount=0,
            coupon=0,
            net_price=100.0,
        )
        lines_repo.create_order_line(line)

        on_hand = calculate_on_hand(item_id)
        assert on_hand == 20.0

        conn.close()


def test_consumption_window_on_hand_with_multiple_orders(test_db: Path) -> None:
    """Test on-hand across multiple orders."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)

        items_repo = ItemsRepository()
        orders_repo = OrdersRepository()
        lines_repo = OrderLinesRepository()

        item = Item(
            name_id=1,
            price=5.0,
            servings_per_block=10.0,
            units="units",
            container_size=100,
            serving_size=10,
            blocks_must_be_integer=False,
            active=True,
            calories=100,
            protein_g=5,
            sodium_mcg=200,
            choline_mcg=0,
        )
        item_id = items_repo.create_item(item)

        order1 = Order(order_date="2024-01-01", is_delivery=False, status="planning")
        order_id1 = orders_repo.create_order(order1)

        line1 = OrderLine(
            order_id=order_id1,
            item_id=item_id,
            servings_ordered=10.0,
            actual_servings=10.0,
            stated_price=5.0,
            sale=0,
            discount=0,
            coupon=0,
            net_price=50.0,
        )
        lines_repo.create_order_line(line1)

        order2 = Order(order_date="2024-01-02", is_delivery=False, status="planning")
        order_id2 = orders_repo.create_order(order2)

        line2 = OrderLine(
            order_id=order_id2,
            item_id=item_id,
            servings_ordered=15.0,
            actual_servings=15.0,
            stated_price=5.0,
            sale=0,
            discount=0,
            coupon=0,
            net_price=75.0,
        )
        lines_repo.create_order_line(line2)

        on_hand = calculate_on_hand(item_id)
        assert on_hand == 25.0

        conn.close()


def test_consumption_save_path_end_to_end(test_db: Path) -> None:
    """Test the real consumption save path with Consumption model.

    Exercises the fixed import and method call:
    - Creates a Consumption object (not ConsumptionEntry)
    - Calls log_consumption() (not create_consumption())
    """
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)

        items_repo = ItemsRepository()
        orders_repo = OrdersRepository()
        lines_repo = OrderLinesRepository()
        consumption_repo = ConsumptionRepository()

        # Create an item
        item = Item(
            name_id=1,
            price=5.0,
            servings_per_block=10.0,
            units="units",
            container_size=100,
            serving_size=10,
            blocks_must_be_integer=False,
            active=True,
            calories=100,
            protein_g=5,
            sodium_mcg=200,
            choline_mcg=0,
        )
        item_id = items_repo.create_item(item)

        # Create an order with the item to establish on-hand
        order = Order(order_date="2024-01-01", is_delivery=False, status="planning")
        order_id = orders_repo.create_order(order)

        line = OrderLine(
            order_id=order_id,
            item_id=item_id,
            servings_ordered=20.0,
            actual_servings=20.0,
            stated_price=5.0,
            sale=0,
            discount=0,
            coupon=0,
            net_price=100.0,
        )
        lines_repo.create_order_line(line)

        # Verify on-hand is 20
        assert calculate_on_hand(item_id) == 20.0

        # Log consumption using the fixed Consumption model and log_consumption method
        entry_date = datetime(2024, 1, 2)
        consumption = Consumption(
            item_id=item_id,
            entry_date=entry_date,
            servings_consumed=8.0,
        )
        consumption_repo.log_consumption(consumption)

        # Verify on-hand decreased
        remaining = calculate_on_hand(item_id)
        assert remaining == 12.0

        conn.close()


def test_consumption_multiple_entries(test_db: Path) -> None:
    """Test logging multiple consumption entries for same item."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)

        items_repo = ItemsRepository()
        orders_repo = OrdersRepository()
        lines_repo = OrderLinesRepository()
        consumption_repo = ConsumptionRepository()

        # Create item with 30 servings on-hand
        item = Item(
            name_id=1,
            price=5.0,
            servings_per_block=10.0,
            units="units",
            container_size=100,
            serving_size=10,
            blocks_must_be_integer=False,
            active=True,
            calories=100,
            protein_g=5,
            sodium_mcg=200,
            choline_mcg=0,
        )
        item_id = items_repo.create_item(item)

        order = Order(order_date="2024-01-01", is_delivery=False, status="planning")
        order_id = orders_repo.create_order(order)

        line = OrderLine(
            order_id=order_id,
            item_id=item_id,
            servings_ordered=30.0,
            actual_servings=30.0,
            stated_price=5.0,
            sale=0,
            discount=0,
            coupon=0,
            net_price=150.0,
        )
        lines_repo.create_order_line(line)

        # Log first consumption
        consumption1 = Consumption(
            item_id=item_id,
            entry_date=datetime(2024, 1, 2),
            servings_consumed=10.0,
        )
        consumption_repo.log_consumption(consumption1)
        assert calculate_on_hand(item_id) == 20.0

        # Log second consumption
        consumption2 = Consumption(
            item_id=item_id,
            entry_date=datetime(2024, 1, 3),
            servings_consumed=5.0,
        )
        consumption_repo.log_consumption(consumption2)
        assert calculate_on_hand(item_id) == 15.0

        conn.close()
