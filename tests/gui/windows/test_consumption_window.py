import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from src.database.connection import get_connection
from src.database.schema import create_schema
from src.database.seed_reference_data import seed_reference_data
from src.models.dim_items import Item
from src.models.fact_order_lines import OrderLine
from src.models.fact_orders import Order
from src.repository.items_repository import ItemsRepository
from src.repository.orders_repository import OrdersRepository
from src.repository.order_lines_repository import OrderLinesRepository
from src.calculations.on_hand import calculate_on_hand


@pytest.fixture
def test_db() -> Path:
    """Create temp test database."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "test.db"
    with patch(
        "src.database.connection.get_database_path", return_value=db_path
    ):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


def test_consumption_window_on_hand_calculation(test_db: Path) -> None:
    """Test that on-hand calculates correctly for consumption entry."""
    with patch(
        "src.database.connection.get_database_path", return_value=test_db
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
        "src.database.connection.get_database_path", return_value=test_db
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
