import tempfile
from pathlib import Path
from unittest.mock import patch
import tkinter as tk

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.migrations import migrate_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.models.dim_items import Item
from foodlog.gui.components.order_item_row import OrderItemRow


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
        migrate_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


@pytest.fixture
def test_item(test_db: Path) -> Item:
    """Create a test item."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        return Item(
            item_id=1,
            name_id=1,
            category_id=None,
            price=5.00,
            servings_per_block=10.0,
            units="oz",
            container_size=100,
            serving_size=10,
            blocks_must_be_integer=False,
            active=True,
            glycemic_index=None,
            calories=100.0,
            total_fat_g=5.0,
            sodium_mcg=500000.0,
        )


def test_get_values_positive_sale_forced_negative(
    test_db: Path, test_item: Item
) -> None:
    """Test that positive sale is forced negative in get_values()."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row.sale_var.set("5.00")  # User enters positive

        values = row.get_values()
        assert values["sale"] == -5.00  # Should be negative


def test_get_values_negative_sale_stays_negative(
    test_db: Path, test_item: Item
) -> None:
    """Test that negative sale stays negative in get_values()."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row.sale_var.set("-5.00")

        values = row.get_values()
        assert values["sale"] == -5.00


def test_get_values_zero_sale_stays_zero(
    test_db: Path, test_item: Item
) -> None:
    """Test that zero sale stays zero in get_values()."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row.sale_var.set("0")

        values = row.get_values()
        assert values["sale"] == 0.0


def test_update_display_positive_discount_forced_negative(
    test_db: Path, test_item: Item
) -> None:
    """Test that positive discount is forced negative in _update_display()."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row.servings_var.set("10")
        row.discount_var.set("2.00")  # User enters positive
        row._update_display()

        # Net should be: (5.00 * 10) + 0 + (-2.00) + 0 = 48.00
        net_text = row.net_label.cget("text")
        assert net_text == "$48.00"


def test_update_display_negative_coupon_stays_negative(
    test_db: Path, test_item: Item
) -> None:
    """Test that negative coupon stays negative in _update_display()."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row.servings_var.set("10")
        row.coupon_var.set("-3.00")
        row._update_display()

        # Net should be: (5.00 * 10) + 0 + 0 + (-3.00) = 47.00
        net_text = row.net_label.cget("text")
        assert net_text == "$47.00"
