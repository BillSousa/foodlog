import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
import tkinter as tk

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.migrations import migrate_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.models.dim_items import Item
from foodlog.models.fact_order_lines import OrderLine
from foodlog.repository.product_names_repository import ProductNamesRepository
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
        product_names_repo = ProductNamesRepository()
        name_id = product_names_repo.create_product_name("Test Product")
        return Item(
            item_id=1,
            name_id=name_id,
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
            choline_mcg=0.0,
        )


@pytest.fixture
def sample_order_line() -> OrderLine:
    """Create a sample order line for testing."""
    return OrderLine(
        line_id=42,
        order_id=1,
        item_id=1,
        servings_ordered=25.0,
        actual_servings=25.0,
        stated_price=6.50,
        sale=-1.00,
        discount=-0.50,
        coupon=-0.25,
        net_price=156.25,
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

        # Net should be: (5.00 / 10.0) * 10 + 0 + (-2.00) + 0 = 3.00
        net_text = row.net_label.cget("text")
        assert net_text == "$3.00"


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

        # Net should be: (5.00 / 10.0) * 10 + 0 + 0 + (-3.00) = 2.00
        net_text = row.net_label.cget("text")
        assert net_text == "$2.00"


def test_order_item_row_displays_product_name_not_units(
    test_db: Path,
) -> None:
    """Test that OrderItemRow displays resolved product name, not item.units."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        product_names_repo = ProductNamesRepository()
        name_id = product_names_repo.create_product_name("Red Delicious Apple")
        item = Item(
            item_id=1,
            name_id=name_id,
            category_id=None,
            price=2.50,
            servings_per_block=5.0,
            units="oz",
            container_size=100,
            serving_size=10,
            blocks_must_be_integer=False,
            active=True,
            glycemic_index=None,
            calories=50.0,
            total_fat_g=0.3,
            sodium_mcg=100000.0,
            choline_mcg=0.0,
        )

        root = tk.Tk()
        row = OrderItemRow(root, item)

        # The first label in the row should display the product name,
        # not the units
        labels = [
            child for child in row.frame.winfo_children()
            if isinstance(child, tk.Label)
        ]
        assert len(labels) > 0
        assert labels[0].cget("text") == "Red Delicious Apple"
        # Verify it's not showing the units
        assert labels[0].cget("text") != "oz"


def test_update_price_btn_exists(
    test_db: Path, test_item: Item
) -> None:
    """Test that update price button exists."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        assert row.update_price_btn is not None


@patch('foodlog.gui.components.order_item_row.PriceUpdatePopup')
def test_update_price_click_opens_popup(
    mock_popup_class, test_db: Path, test_item: Item
) -> None:
    """Test that clicking update price button opens popup with correct params."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row._on_update_price_click()

        mock_popup_class.assert_called_once()
        call_args = mock_popup_class.call_args
        assert call_args[0][1] == test_item.item_id
        assert call_args[0][2] == test_item.price


def test_update_price_callback_updates_display(
    test_db: Path, test_item: Item
) -> None:
    """Test that price callback updates item and display."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        original_price = float(row.price_var.get())

        # Simulate callback
        def on_price_saved(new_price):
            row.item.price = new_price
            row.price_var.set(str(new_price))
            row.last_valid_price = str(new_price)
            row._update_display()

        on_price_saved(10.50)

        assert row.item.price == 10.50
        assert float(row.price_var.get()) == 10.50
        assert row.last_valid_price == "10.5"


def test_update_price_btn_disabled_when_locked(
    test_db: Path, test_item: Item
) -> None:
    """Test that update price button is disabled when row is locked."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row.set_locked(True)

        assert row.update_price_btn.cget("state") == tk.DISABLED

        row.set_locked(False)
        assert row.update_price_btn.cget("state") == tk.NORMAL


@patch('foodlog.gui.components.order_item_row.PriceUpdatePopup')
def test_update_price_click_callback_is_callable(
    mock_popup_class, test_db: Path, test_item: Item
) -> None:
    """Test that callback passed to popup is callable."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row._on_update_price_click()

        call_args = mock_popup_class.call_args
        callback = call_args[0][3]
        assert callable(callback)


def test_update_price_callback_calls_on_change_callback(
    test_db: Path, test_item: Item
) -> None:
    """Test that price callback invokes on_change_callback if set."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row.on_change_callback = Mock()

        # Simulate the callback from _on_update_price_click
        def on_price_saved(new_price):
            row.item.price = new_price
            row.price_var.set(str(new_price))
            row.last_valid_price = str(new_price)
            row._update_display()
            if row.on_change_callback:
                row.on_change_callback()

        on_price_saved(10.50)
        row.on_change_callback.assert_called_once()


def test_set_locked_disables_all_widgets(
    test_db: Path, test_item: Item
) -> None:
    """Test that set_locked(True) disables all editable widgets."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item)
        row.set_locked(True)

        # Verify all entry/button widgets are disabled
        assert row.blocks_entry.cget("state") == tk.DISABLED
        assert row.servings_entry.cget("state") == tk.DISABLED
        assert row.price_entry.cget("state") == tk.DISABLED
        assert row.update_price_btn.cget("state") == tk.DISABLED
        assert row.sale_entry.cget("state") == tk.DISABLED
        assert row.discount_entry.cget("state") == tk.DISABLED
        assert row.coupon_entry.cget("state") == tk.DISABLED
        assert row.delete_btn.cget("state") == tk.DISABLED

        # Verify all re-enabled when unlocked
        row.set_locked(False)
        assert row.blocks_entry.cget("state") == tk.NORMAL
        assert row.servings_entry.cget("state") == tk.NORMAL
        assert row.price_entry.cget("state") == tk.NORMAL
        assert row.update_price_btn.cget("state") == tk.NORMAL
        assert row.sale_entry.cget("state") == tk.NORMAL
        assert row.discount_entry.cget("state") == tk.NORMAL
        assert row.coupon_entry.cget("state") == tk.NORMAL
        assert row.delete_btn.cget("state") == tk.NORMAL


def test_existing_line_none_uses_item_defaults(
    test_db: Path, test_item: Item
) -> None:
    """Test that existing_line=None uses item defaults."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(root, test_item, existing_line=None)

        assert row.line_id is None
        assert float(row.price_var.get()) == 5.00
        assert float(row.blocks_var.get()) == 1.0
        assert float(row.servings_var.get()) == 10.0
        assert float(row.sale_var.get()) == 0.0
        assert float(row.discount_var.get()) == 0.0
        assert float(row.coupon_var.get()) == 0.0


def test_existing_line_populates_all_fields(
    test_db: Path, test_item: Item, sample_order_line: OrderLine
) -> None:
    """Test that existing_line populates all fields correctly."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(
            root, test_item, existing_line=sample_order_line
        )

        assert row.line_id == 42
        assert float(row.price_var.get()) == 6.50
        assert float(row.servings_var.get()) == 25.0
        assert float(row.sale_var.get()) == -1.00
        assert float(row.discount_var.get()) == -0.50
        assert float(row.coupon_var.get()) == -0.25


def test_existing_line_calculates_blocks_from_servings(
    test_db: Path, test_item: Item, sample_order_line: OrderLine
) -> None:
    """Test that blocks are calculated from actual_servings."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(
            root, test_item, existing_line=sample_order_line
        )

        # sample_order_line has actual_servings=25.0
        # test_item has servings_per_block=10.0
        # so blocks should be 25.0 / 10.0 = 2.5
        assert float(row.blocks_var.get()) == 2.5


def test_existing_line_sets_last_valid_values(
    test_db: Path, test_item: Item, sample_order_line: OrderLine
) -> None:
    """Test that last_valid_price and last_valid_blocks are initialized."""
    with patch(
        "foodlog.database.connection.get_database_path", return_value=test_db
    ):
        root = tk.Tk()
        row = OrderItemRow(
            root, test_item, existing_line=sample_order_line
        )

        assert row.last_valid_price == "6.5"
        assert float(row.last_valid_blocks) == 2.5
