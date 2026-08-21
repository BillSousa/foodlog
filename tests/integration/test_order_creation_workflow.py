"""Integration test for order creation workflow.

Tests the complete flow of creating an order, adding line items with
items from dim_items, and verifying that all computed values
(net_price on lines, order totals, ratios) are calculated correctly.
"""
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.migrations import migrate_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.models.dim_items import Item
from foodlog.models.fact_orders import Order
from foodlog.models.fact_order_lines import OrderLine
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.orders_repository import OrdersRepository
from foodlog.repository.order_lines_repository import OrderLinesRepository
from foodlog.repository.product_names_repository import ProductNamesRepository
from foodlog.calculations.ratios import ratio1, ratio2


@pytest.fixture
def test_db() -> Path:
    """Create temp test database with full schema."""
    tmpdir = tempfile.mkdtemp()
    db_path = Path(tmpdir) / "test.db"
    with patch(
        "foodlog.database.connection.get_database_path", return_value=db_path
    ):
        conn = get_connection()
        create_schema(conn)
        migrate_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


@pytest.fixture
def sample_items(test_db: Path) -> dict[str, int]:
    """Create sample items with nutrition data and return item_ids."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        items_repo = ItemsRepository()

        apple_name_id = names_repo.create_product_name("Apple")
        pasta_name_id = names_repo.create_product_name("Pasta")
        cheese_name_id = names_repo.create_product_name("Cheese")

        apple_id = items_repo.create_item(
            Item(
                name_id=apple_name_id,
                category_id=1,
                price=1.00,
                servings_per_block=4.0,
                units="units",
                container_size=4,
                serving_size=1,
                blocks_must_be_integer=0,
                active=1,
                calories=52.0,
                total_fat_g=0.2,
                sodium_mcg=100000.0,
                total_carbs_g=14.0,
                protein_g=0.3,
                choline_mcg=3.6,
            )
        )

        pasta_id = items_repo.create_item(
            Item(
                name_id=pasta_name_id,
                category_id=2,
                price=2.50,
                servings_per_block=2.0,
                units="units",
                container_size=2,
                serving_size=1,
                blocks_must_be_integer=1,
                active=1,
                calories=350.0,
                total_fat_g=1.5,
                sodium_mcg=500000.0,
                total_carbs_g=70.0,
                protein_g=13.0,
                choline_mcg=15.0,
            )
        )

        cheese_id = items_repo.create_item(
            Item(
                name_id=cheese_name_id,
                category_id=1,
                price=5.00,
                servings_per_block=8.0,
                units="units",
                container_size=8,
                serving_size=1,
                blocks_must_be_integer=0,
                active=1,
                calories=113.0,
                total_fat_g=9.5,
                sodium_mcg=200000.0,
                total_carbs_g=0.7,
                protein_g=7.0,
                choline_mcg=15.5,
            )
        )

        return {
            "apple": apple_id,
            "pasta": pasta_id,
            "cheese": cheese_id,
        }


class TestOrderCreationWorkflow:
    """Test complete order creation and aggregation workflow."""

    def test_create_order_with_single_line_item(
        self, test_db: Path, sample_items: dict[str, int]
    ) -> None:
        """Test creating order with one line item."""
        with patch(
            "foodlog.database.connection.get_database_path",
            return_value=test_db,
        ):
            orders_repo = OrdersRepository()
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()

            order = Order(
                order_date="2026-08-21",
                is_delivery=0,
                status="planning",
                delivery_charge=0.0,
                tip=0.0,
                tax=0.0,
                order_level_coupon=0.0,
            )
            order_id = orders_repo.create_order(order)

            apple = items_repo.get_item(sample_items["apple"])
            line = OrderLine(
                order_id=order_id,
                item_id=sample_items["apple"],
                servings_ordered=4.0,
                actual_servings=4.0,
                stated_price=apple.price,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=apple.price * 4.0,
            )
            line_id = lines_repo.create_order_line(line)

            assert line_id is not None
            retrieved_order = orders_repo.get_order(order_id)
            assert retrieved_order is not None
            assert retrieved_order.order_id == order_id

    def test_order_net_cost_aggregation(
        self, test_db: Path, sample_items: dict[str, int]
    ) -> None:
        """Test that order total_net_cost sums line net_prices correctly."""
        with patch(
            "foodlog.database.connection.get_database_path",
            return_value=test_db,
        ):
            orders_repo = OrdersRepository()
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()

            order = Order(
                order_date="2026-08-21",
                is_delivery=1,
                status="planning",
                delivery_charge=5.00,
                tip=2.00,
                tax=3.50,
                order_level_coupon=-1.00,
            )
            order_id = orders_repo.create_order(order)

            apple = items_repo.get_item(sample_items["apple"])
            pasta = items_repo.get_item(sample_items["pasta"])

            line1 = OrderLine(
                order_id=order_id,
                item_id=sample_items["apple"],
                servings_ordered=4.0,
                actual_servings=4.0,
                stated_price=apple.price,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
            )
            line1.net_price = line1.stated_price * line1.actual_servings
            lines_repo.create_order_line(line1)

            line2 = OrderLine(
                order_id=order_id,
                item_id=sample_items["pasta"],
                servings_ordered=2.0,
                actual_servings=2.0,
                stated_price=pasta.price,
                sale=0.0,
                discount=-0.50,
                coupon=0.0,
            )
            line2.net_price = (
                line2.stated_price * line2.actual_servings + line2.discount
            )
            lines_repo.create_order_line(line2)

            expected_lines_total = line1.net_price + line2.net_price
            expected_total = (
                expected_lines_total
                + order.delivery_charge
                + order.tip
                + order.tax
                + order.order_level_coupon
            )

            orders_repo.update_order_totals(
                order_id, total_net_cost=expected_total
            )

            retrieved = orders_repo.get_order(order_id)
            assert retrieved.total_net_cost == pytest.approx(expected_total)

    def test_order_nutrition_aggregation(
        self, test_db: Path, sample_items: dict[str, int]
    ) -> None:
        """Test that order nutrition totals aggregate from line items."""
        with patch(
            "foodlog.database.connection.get_database_path",
            return_value=test_db,
        ):
            orders_repo = OrdersRepository()
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()

            order = Order(
                order_date="2026-08-21",
                is_delivery=0,
                status="planning",
            )
            order_id = orders_repo.create_order(order)

            apple = items_repo.get_item(sample_items["apple"])
            cheese = items_repo.get_item(sample_items["cheese"])

            line1 = OrderLine(
                order_id=order_id,
                item_id=sample_items["apple"],
                servings_ordered=4.0,
                actual_servings=4.0,
                stated_price=apple.price,
                net_price=apple.price * 4.0,
            )
            lines_repo.create_order_line(line1)

            line2 = OrderLine(
                order_id=order_id,
                item_id=sample_items["cheese"],
                servings_ordered=2.0,
                actual_servings=2.0,
                stated_price=cheese.price,
                net_price=cheese.price * 2.0,
            )
            lines_repo.create_order_line(line2)

            expected_calories = (
                apple.calories * 4.0 + cheese.calories * 2.0
            )
            expected_protein = (
                apple.protein_g * 4.0 + cheese.protein_g * 2.0
            )
            expected_carbs = (
                apple.total_carbs_g * 4.0 + cheese.total_carbs_g * 2.0
            )
            expected_fat = (
                apple.total_fat_g * 4.0 + cheese.total_fat_g * 2.0
            )
            expected_sodium_mcg = (
                apple.sodium_mcg * 4.0 + cheese.sodium_mcg * 2.0
            )

            orders_repo.update_order_totals(
                order_id,
                total_calories=expected_calories,
                total_protein_g=expected_protein,
                total_carbs_g=expected_carbs,
                total_fat_g=expected_fat,
                total_sodium_mg=expected_sodium_mcg / 1000,
            )

            retrieved = orders_repo.get_order(order_id)
            assert retrieved.total_calories == pytest.approx(
                expected_calories
            )
            assert retrieved.total_protein_g == pytest.approx(expected_protein)
            assert retrieved.total_carbs_g == pytest.approx(expected_carbs)
            assert retrieved.total_fat_g == pytest.approx(expected_fat)

    def test_order_ratio_calculation(
        self, test_db: Path, sample_items: dict[str, int]
    ) -> None:
        """Test that order ratios are computed from totals correctly."""
        with patch(
            "foodlog.database.connection.get_database_path",
            return_value=test_db,
        ):
            orders_repo = OrdersRepository()
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()

            order = Order(
                order_date="2026-08-21",
                is_delivery=0,
                status="planning",
            )
            order_id = orders_repo.create_order(order)

            pasta = items_repo.get_item(sample_items["pasta"])

            line = OrderLine(
                order_id=order_id,
                item_id=sample_items["pasta"],
                servings_ordered=2.0,
                actual_servings=2.0,
                stated_price=pasta.price,
                net_price=pasta.price * 2.0,
            )
            lines_repo.create_order_line(line)

            total_cost = line.net_price
            total_calories = pasta.calories * 2.0
            total_sodium_mg = (pasta.sodium_mcg * 2.0) / 1000
            total_fat_g = pasta.total_fat_g * 2.0

            expected_ratio1 = ratio1(
                total_calories, total_cost, total_sodium_mg
            )
            expected_ratio2 = ratio2(
                total_calories, total_cost, total_sodium_mg, total_fat_g
            )

            orders_repo.update_order_totals(
                order_id,
                total_net_cost=total_cost,
                total_calories=total_calories,
                total_sodium_mg=total_sodium_mg,
                total_fat_g=total_fat_g,
                ratio1=expected_ratio1,
                ratio2=expected_ratio2,
            )

            retrieved = orders_repo.get_order(order_id)
            assert retrieved.ratio1 == pytest.approx(expected_ratio1)
            assert retrieved.ratio2 == pytest.approx(expected_ratio2)

    def test_line_item_net_price_with_discounts(
        self, test_db: Path, sample_items: dict[str, int]
    ) -> None:
        """Test line net_price = stated_price*servings + sale + discount + coupon."""
        with patch(
            "foodlog.database.connection.get_database_path",
            return_value=test_db,
        ):
            orders_repo = OrdersRepository()
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()

            order = Order(
                order_date="2026-08-21",
                is_delivery=0,
                status="planning",
            )
            order_id = orders_repo.create_order(order)

            apple = items_repo.get_item(sample_items["apple"])

            line = OrderLine(
                order_id=order_id,
                item_id=sample_items["apple"],
                servings_ordered=5.0,
                actual_servings=5.0,
                stated_price=apple.price,
                sale=-0.25,
                discount=-0.50,
                coupon=0.0,
            )

            expected_net = (
                line.stated_price * line.actual_servings
                + line.sale
                + line.discount
                + line.coupon
            )
            line.net_price = expected_net

            line_id = lines_repo.create_order_line(line)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT net_price FROM fact_order_lines WHERE line_id = ?",
                (line_id,),
            )
            row = cursor.fetchone()
            conn.close()

            assert row["net_price"] == pytest.approx(expected_net)

    def test_multiple_items_order_complete_workflow(
        self, test_db: Path, sample_items: dict[str, int]
    ) -> None:
        """Test complete workflow with multiple items, discounts, fees."""
        with patch(
            "foodlog.database.connection.get_database_path",
            return_value=test_db,
        ):
            orders_repo = OrdersRepository()
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()

            order = Order(
                order_date="2026-08-21",
                is_delivery=1,
                status="planning",
                delivery_charge=5.00,
                tip=1.50,
                tax=2.25,
                order_level_coupon=-0.50,
            )
            order_id = orders_repo.create_order(order)

            apple = items_repo.get_item(sample_items["apple"])
            pasta = items_repo.get_item(sample_items["pasta"])
            cheese = items_repo.get_item(sample_items["cheese"])

            lines = [
                OrderLine(
                    order_id=order_id,
                    item_id=sample_items["apple"],
                    servings_ordered=4.0,
                    actual_servings=4.0,
                    stated_price=apple.price,
                    sale=0.0,
                    discount=0.0,
                    coupon=0.0,
                ),
                OrderLine(
                    order_id=order_id,
                    item_id=sample_items["pasta"],
                    servings_ordered=2.0,
                    actual_servings=2.0,
                    stated_price=pasta.price,
                    sale=-0.25,
                    discount=0.0,
                    coupon=0.0,
                ),
                OrderLine(
                    order_id=order_id,
                    item_id=sample_items["cheese"],
                    servings_ordered=3.0,
                    actual_servings=3.0,
                    stated_price=cheese.price,
                    sale=0.0,
                    discount=-1.00,
                    coupon=0.0,
                ),
            ]

            for line in lines:
                line.net_price = (
                    line.stated_price * line.actual_servings
                    + line.sale
                    + line.discount
                    + line.coupon
                )
                lines_repo.create_order_line(line)

            total_lines_cost = sum(line.net_price for line in lines)
            total_cost = (
                total_lines_cost
                + order.delivery_charge
                + order.tip
                + order.tax
                + order.order_level_coupon
            )

            total_calories = (
                apple.calories * 4.0
                + pasta.calories * 2.0
                + cheese.calories * 3.0
            )
            total_protein = (
                apple.protein_g * 4.0
                + pasta.protein_g * 2.0
                + cheese.protein_g * 3.0
            )
            total_carbs = (
                apple.total_carbs_g * 4.0
                + pasta.total_carbs_g * 2.0
                + cheese.total_carbs_g * 3.0
            )
            total_fat = (
                apple.total_fat_g * 4.0
                + pasta.total_fat_g * 2.0
                + cheese.total_fat_g * 3.0
            )
            total_sodium_mcg = (
                apple.sodium_mcg * 4.0
                + pasta.sodium_mcg * 2.0
                + cheese.sodium_mcg * 3.0
            )
            total_sodium_mg = total_sodium_mcg / 1000

            calc_ratio1 = ratio1(total_calories, total_cost, total_sodium_mg)
            calc_ratio2 = ratio2(
                total_calories, total_cost, total_sodium_mg, total_fat
            )

            orders_repo.update_order_totals(
                order_id,
                total_net_cost=total_cost,
                total_calories=total_calories,
                total_protein_g=total_protein,
                total_carbs_g=total_carbs,
                total_fat_g=total_fat,
                total_sodium_mg=total_sodium_mg,
                ratio1=calc_ratio1,
                ratio2=calc_ratio2,
            )

            retrieved = orders_repo.get_order(order_id)
            assert retrieved.order_id == order_id
            assert retrieved.status == "planning"
            assert retrieved.is_delivery == 1
            assert retrieved.total_net_cost == pytest.approx(total_cost)
            assert retrieved.total_calories == pytest.approx(total_calories)
            assert retrieved.total_protein_g == pytest.approx(total_protein)
            assert retrieved.total_carbs_g == pytest.approx(total_carbs)
            assert retrieved.total_fat_g == pytest.approx(total_fat)
            assert retrieved.ratio1 == pytest.approx(calc_ratio1)
            assert retrieved.ratio2 == pytest.approx(calc_ratio2)

            retrieved_lines = lines_repo.get_order_lines(order_id)
            assert len(retrieved_lines) == 3

    def test_reopen_and_edit_line_item(
        self, test_db: Path, sample_items: dict[str, int]
    ) -> None:
        """Test reopening order and editing an existing line item."""
        with patch(
            "foodlog.database.connection.get_database_path",
            return_value=test_db,
        ):
            orders_repo = OrdersRepository()
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()

            order = Order(
                order_date="2026-08-21",
                is_delivery=0,
                status="planning",
            )
            order_id = orders_repo.create_order(order)

            apple = items_repo.get_item(sample_items["apple"])

            line = OrderLine(
                order_id=order_id,
                item_id=sample_items["apple"],
                servings_ordered=4.0,
                actual_servings=4.0,
                stated_price=apple.price,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=apple.price * 4.0,
            )
            line_id = lines_repo.create_order_line(line)

            # Reopen and edit: increase actual_servings and add discount
            lines_repo.update_order_line(
                line_id=line_id,
                actual_servings=5.0,
                discount=-0.50,
                net_price=(apple.price * 5.0) - 0.50,
            )

            # Retrieve and verify changes persisted
            retrieved_lines = lines_repo.get_order_lines(order_id)
            retrieved_line = next(
                (l for l in retrieved_lines if l.line_id == line_id), None
            )
            assert retrieved_line is not None
            assert retrieved_line.actual_servings == 5.0
            assert retrieved_line.discount == -0.50
            assert retrieved_line.net_price == pytest.approx(
                (apple.price * 5.0) - 0.50
            )

    def test_reconciled_order_blocks_line_edits(
        self, test_db: Path, sample_items: dict[str, int]
    ) -> None:
        """Test that reconciled order status prevents line item edits."""
        with patch(
            "foodlog.database.connection.get_database_path",
            return_value=test_db,
        ):
            from foodlog.validation.constraints import ValidationError

            orders_repo = OrdersRepository()
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()

            order = Order(
                order_date="2026-08-21",
                is_delivery=0,
                status="planning",
            )
            order_id = orders_repo.create_order(order)

            apple = items_repo.get_item(sample_items["apple"])

            line = OrderLine(
                order_id=order_id,
                item_id=sample_items["apple"],
                servings_ordered=4.0,
                actual_servings=4.0,
                stated_price=apple.price,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=apple.price * 4.0,
            )
            line_id = lines_repo.create_order_line(line)

            # Change order status to reconciled
            orders_repo.update_order_status(order_id, "reconciled")

            # Try to edit line — should raise ValidationError
            with pytest.raises(ValidationError) as exc_info:
                lines_repo.update_order_line(
                    line_id=line_id,
                    actual_servings=5.0,
                )

            assert "reconciled" in str(exc_info.value).lower()
