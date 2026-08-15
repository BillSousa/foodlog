import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.models.fact_orders import Order
from foodlog.repository.orders_repository import OrdersRepository
from foodlog.validation.constraints import ValidationError


@pytest.fixture
def test_db() -> Path:
    """Create temp test database."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / 'test.db'
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=db_path
    ):
        conn = get_connection()
        create_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


@pytest.fixture
def sample_order(test_db: Path) -> int:
    """Create a sample order, return order_id."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        repo = OrdersRepository()
        order = Order(order_date="2026-08-15", is_delivery=False)
        order_id = repo.create_order(order)
        return order_id


class TestUpdateOrderHeader:
    """Test update_order_header() method."""

    def test_update_order_date(self, test_db: Path, sample_order: int) -> None:
        """Test updating order_date only."""
        order_id = sample_order
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrdersRepository()
            repo.update_order_header(order_id, order_date="2026-08-16")

            order = repo.get_order(order_id)
            assert order.order_date == "2026-08-16"
            assert order.is_delivery == 0

    def test_update_is_delivery(self, test_db: Path, sample_order: int) -> None:
        """Test updating is_delivery only."""
        order_id = sample_order
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrdersRepository()
            repo.update_order_header(order_id, is_delivery=True)

            order = repo.get_order(order_id)
            assert order.is_delivery == 1
            assert order.order_date == "2026-08-15"

    def test_update_delivery_charge(self, test_db: Path, sample_order: int) -> None:
        """Test updating delivery_charge only."""
        order_id = sample_order
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrdersRepository()
            repo.update_order_header(order_id, delivery_charge=5.99)

            order = repo.get_order(order_id)
            assert order.delivery_charge == 5.99
            assert order.tip == 0

    def test_update_tip(self, test_db: Path, sample_order: int) -> None:
        """Test updating tip only."""
        order_id = sample_order
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrdersRepository()
            repo.update_order_header(order_id, tip=2.50)

            order = repo.get_order(order_id)
            assert order.tip == 2.50
            assert order.tax == 0

    def test_update_tax(self, test_db: Path, sample_order: int) -> None:
        """Test updating tax only."""
        order_id = sample_order
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrdersRepository()
            repo.update_order_header(order_id, tax=8.75)

            order = repo.get_order(order_id)
            assert order.tax == 8.75
            assert order.tip == 0

    def test_update_order_level_coupon(self, test_db: Path, sample_order: int) -> None:
        """Test updating order_level_coupon only."""
        order_id = sample_order
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrdersRepository()
            repo.update_order_header(order_id, order_level_coupon=-3.50)

            order = repo.get_order(order_id)
            assert order.order_level_coupon == -3.50
            assert order.delivery_charge == 0

    def test_update_multiple_fields(self, test_db: Path, sample_order: int) -> None:
        """Test updating multiple fields simultaneously."""
        order_id = sample_order
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrdersRepository()
            repo.update_order_header(
                order_id,
                order_date="2026-08-16",
                is_delivery=True,
                delivery_charge=5.99,
                tip=2.00,
                tax=10.00,
                order_level_coupon=-5.00
            )

            order = repo.get_order(order_id)
            assert order.order_date == "2026-08-16"
            assert order.is_delivery == 1
            assert order.delivery_charge == 5.99
            assert order.tip == 2.00
            assert order.tax == 10.00
            assert order.order_level_coupon == -5.00

    def test_update_with_no_fields_is_noop(self, test_db: Path, sample_order: int) -> None:
        """Test calling update with no fields to update is a no-op."""
        order_id = sample_order
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrdersRepository()
            repo.update_order_header(order_id)

            order = repo.get_order(order_id)
            assert order.order_date == "2026-08-15"
            assert order.is_delivery == 0
            assert order.delivery_charge == 0

    def test_update_reconciled_order_raises_error(self, test_db: Path, sample_order: int) -> None:
        """Test that updating a reconciled order raises ValidationError."""
        order_id = sample_order
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrdersRepository()
            repo.update_order_status(order_id, 'reconciled')

            with pytest.raises(ValidationError):
                repo.update_order_header(order_id, order_date="2026-08-16")
