import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.models.dim_items import Item
from foodlog.models.fact_order_lines import OrderLine
from foodlog.models.fact_orders import Order
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.order_lines_repository import OrderLinesRepository
from foodlog.repository.orders_repository import OrdersRepository
from foodlog.repository.product_names_repository import ProductNamesRepository
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
def sample_order_line(test_db: Path) -> tuple[int, int]:
    """Create a sample order and line, return (order_id, line_id)."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        # Create product name
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")

        # Create item
        items_repo = ItemsRepository()
        item = Item(
            name_id=name_id,
            price=5.00,
            servings_per_block=4.0,
            units='oz',
            container_size=16,
            serving_size=4,
            calories=200.0,
            protein_g=10.0,
            choline_mcg=0,
        )
        item_id = items_repo.create_item(item)

        # Create order
        orders_repo = OrdersRepository()
        order = Order(order_date="2026-08-15", is_delivery=False)
        order_id = orders_repo.create_order(order)

        # Create order line
        lines_repo = OrderLinesRepository()
        line = OrderLine(
            order_id=order_id,
            item_id=item_id,
            servings_ordered=8.0,
            actual_servings=8.0,
            stated_price=5.00,
            sale=0.0,
            discount=0.0,
            coupon=0.0,
            net_price=40.00,
        )
        line_id = lines_repo.create_order_line(line)

        return order_id, line_id


class TestUpdateOrderLine:
    """Test update_order_line() method."""

    def test_update_actual_servings(self, test_db: Path, sample_order_line: tuple[int, int]) -> None:
        """Test updating actual_servings only."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            repo.update_order_line(line_id, actual_servings=6.0)

            lines = repo.get_order_lines(order_id)
            assert len(lines) == 1
            assert lines[0].actual_servings == 6.0
            assert lines[0].servings_ordered == 8.0
            assert lines[0].stated_price == 5.00
            assert lines[0].sale == 0.0

    def test_update_sale(self, test_db: Path, sample_order_line: tuple[int, int]) -> None:
        """Test updating sale only."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            repo.update_order_line(line_id, sale=-1.00)

            lines = repo.get_order_lines(order_id)
            assert lines[0].sale == -1.00
            assert lines[0].actual_servings == 8.0
            assert lines[0].discount == 0.0

    def test_update_discount(self, test_db: Path, sample_order_line: tuple[int, int]) -> None:
        """Test updating discount only."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            repo.update_order_line(line_id, discount=-2.50)

            lines = repo.get_order_lines(order_id)
            assert lines[0].discount == -2.50
            assert lines[0].sale == 0.0
            assert lines[0].coupon == 0.0

    def test_update_coupon(self, test_db: Path, sample_order_line: tuple[int, int]) -> None:
        """Test updating coupon only."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            repo.update_order_line(line_id, coupon=-0.50)

            lines = repo.get_order_lines(order_id)
            assert lines[0].coupon == -0.50
            assert lines[0].sale == 0.0
            assert lines[0].discount == 0.0

    def test_update_stated_price(self, test_db: Path, sample_order_line: tuple[int, int]) -> None:
        """Test updating stated_price only."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            repo.update_order_line(line_id, stated_price=6.00)

            lines = repo.get_order_lines(order_id)
            assert lines[0].stated_price == 6.00
            assert lines[0].actual_servings == 8.0
            assert lines[0].sale == 0.0

    def test_update_net_price(self, test_db: Path, sample_order_line: tuple[int, int]) -> None:
        """Test updating net_price only."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            repo.update_order_line(line_id, net_price=38.50)

            lines = repo.get_order_lines(order_id)
            assert lines[0].net_price == 38.50
            assert lines[0].actual_servings == 8.0
            assert lines[0].stated_price == 5.00

    def test_update_multiple_fields(self, test_db: Path, sample_order_line: tuple[int, int]) -> None:
        """Test updating multiple fields simultaneously."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            repo.update_order_line(
                line_id,
                actual_servings=7.0,
                sale=-1.50,
                discount=-1.00,
                stated_price=5.50,
                net_price=35.00
            )

            lines = repo.get_order_lines(order_id)
            assert lines[0].actual_servings == 7.0
            assert lines[0].sale == -1.50
            assert lines[0].discount == -1.00
            assert lines[0].stated_price == 5.50
            assert lines[0].net_price == 35.00
            assert lines[0].coupon == 0.0
            assert lines[0].servings_ordered == 8.0

    def test_update_with_no_fields_is_noop(
        self, test_db: Path, sample_order_line: tuple[int, int]
    ) -> None:
        """Test calling update with no fields to update is a no-op."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            # Call with no fields to update
            repo.update_order_line(line_id)

            lines = repo.get_order_lines(order_id)
            assert lines[0].actual_servings == 8.0
            assert lines[0].stated_price == 5.00
            assert lines[0].net_price == 40.00

    def test_servings_ordered_never_updated(
        self, test_db: Path, sample_order_line: tuple[int, int]
    ) -> None:
        """Test that servings_ordered is frozen and never updated."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            # Try to update multiple fields, but servings_ordered should
            # remain unchanged
            repo.update_order_line(
                line_id,
                actual_servings=2.0,
                sale=-5.00
            )

            lines = repo.get_order_lines(order_id)
            assert lines[0].servings_ordered == 8.0

    def test_update_with_zero_values(self, test_db: Path, sample_order_line: tuple[int, int]) -> None:
        """Test that zero values are allowed and not treated as None."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            repo = OrderLinesRepository()
            repo.update_order_line(
                line_id,
                actual_servings=0.0,
                sale=0.0,
                discount=0.0,
                coupon=0.0
            )

            lines = repo.get_order_lines(order_id)
            assert lines[0].actual_servings == 0.0
            assert lines[0].sale == 0.0
            assert lines[0].discount == 0.0
            assert lines[0].coupon == 0.0

    def test_update_reconciled_order_raises_error(
        self, test_db: Path, sample_order_line: tuple[int, int]
    ) -> None:
        """Test that updating a line in a reconciled order raises ValidationError."""
        order_id, line_id = sample_order_line
        with patch(
            'foodlog.database.connection.get_database_path',
            return_value=test_db
        ):
            orders_repo = OrdersRepository()
            orders_repo.update_order_status(order_id, 'reconciled')

            repo = OrderLinesRepository()
            with pytest.raises(ValidationError):
                repo.update_order_line(line_id, actual_servings=6.0)
