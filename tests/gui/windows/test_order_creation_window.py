import tkinter as tk
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.migrations import migrate_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.gui.windows.order_creation_window import OrderCreationWindow
from foodlog.models.dim_items import Item
from foodlog.models.fact_orders import Order
from foodlog.models.fact_order_lines import OrderLine
from foodlog.repository.categories_repository import CategoriesRepository
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.product_names_repository import ProductNamesRepository
from foodlog.repository.orders_repository import OrdersRepository
from foodlog.repository.order_lines_repository import OrderLinesRepository
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
        migrate_schema(conn)
        seed_reference_data(conn)
        conn.close()
    return db_path


@pytest.fixture
def root() -> tk.Tk:
    """Create a test root window."""
    return tk.Tk()


@pytest.fixture
def order_creation_window(
    root: tk.Tk, test_db: Path
) -> OrderCreationWindow:
    """Create an OrderCreationWindow widget."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        return OrderCreationWindow(root)


def test_set_locked_disables_header(
    order_creation_window: OrderCreationWindow,
) -> None:
    """Test _set_locked(True) disables header widgets."""
    order_creation_window._set_locked(True)
    assert order_creation_window.header.date_entry.cget("state") == tk.DISABLED
    assert (
        order_creation_window.header.is_delivery_check.cget("state")
        == tk.DISABLED
    )


def test_set_locked_enables_header(
    order_creation_window: OrderCreationWindow,
) -> None:
    """Test _set_locked(False) enables header widgets."""
    order_creation_window._set_locked(True)
    order_creation_window._set_locked(False)
    assert order_creation_window.header.date_entry.cget("state") == tk.NORMAL
    assert (
        order_creation_window.header.is_delivery_check.cget("state")
        == tk.NORMAL
    )


def test_set_locked_disables_add_button(
    order_creation_window: OrderCreationWindow,
) -> None:
    """Test _set_locked(True) disables the Add Item button."""
    order_creation_window._set_locked(True)
    assert order_creation_window.add_item_btn.cget("state") == tk.DISABLED


def test_set_locked_enables_add_button(
    order_creation_window: OrderCreationWindow,
) -> None:
    """Test _set_locked(False) enables the Add Item button."""
    order_creation_window._set_locked(True)
    order_creation_window._set_locked(False)
    assert order_creation_window.add_item_btn.cget("state") == tk.NORMAL


def test_set_locked_disables_item_rows(
    order_creation_window: OrderCreationWindow, test_db: Path
) -> None:
    """Test _set_locked(True) disables all item row widgets."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
        item.item_id = item_id

        order_creation_window._add_item_row(item)
        order_creation_window._set_locked(True)

        row = order_creation_window.order_items[0]["row"]
        assert row.blocks_entry.cget("state") == tk.DISABLED
        assert row.servings_entry.cget("state") == tk.DISABLED
        assert row.price_entry.cget("state") == tk.DISABLED
        assert row.sale_entry.cget("state") == tk.DISABLED
        assert row.discount_entry.cget("state") == tk.DISABLED
        assert row.coupon_entry.cget("state") == tk.DISABLED
        assert row.delete_btn.cget("state") == tk.DISABLED


def test_set_locked_enables_item_rows(
    order_creation_window: OrderCreationWindow, test_db: Path
) -> None:
    """Test _set_locked(False) enables all item row widgets."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
        item.item_id = item_id

        order_creation_window._add_item_row(item)
        order_creation_window._set_locked(True)
        order_creation_window._set_locked(False)

        row = order_creation_window.order_items[0]["row"]
        assert row.blocks_entry.cget("state") == tk.NORMAL
        assert row.servings_entry.cget("state") == tk.NORMAL
        assert row.price_entry.cget("state") == tk.NORMAL
        assert row.sale_entry.cget("state") == tk.NORMAL
        assert row.discount_entry.cget("state") == tk.NORMAL
        assert row.coupon_entry.cget("state") == tk.NORMAL
        assert row.delete_btn.cget("state") == tk.NORMAL


def test_save_catches_validation_error(
    order_creation_window: OrderCreationWindow, test_db: Path
) -> None:
    """Test _save() catches ValidationError and shows error dialog."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
        item.item_id = item_id

        order_creation_window._add_item_row(item)

        with patch(
            'foodlog.gui.windows.order_creation_window.OrdersRepository'
        ) as mock_orders_repo_class:
            mock_repo = MagicMock()
            mock_repo.create_order.side_effect = ValidationError(
                "Cannot save: order is locked"
            )
            mock_orders_repo_class.return_value = mock_repo

            with patch(
                'foodlog.gui.windows.order_creation_window.messagebox'
            ) as mock_messagebox:
                order_creation_window._save()

                mock_messagebox.showerror.assert_called_once()
                args = mock_messagebox.showerror.call_args
                assert args[0][0] == "Save failed"
                assert "Cannot save: order is locked" in args[0][1]


def test_save_doesnt_close_on_validation_error(
    order_creation_window: OrderCreationWindow, test_db: Path
) -> None:
    """Test window stays open when ValidationError occurs."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
        item.item_id = item_id

        order_creation_window._add_item_row(item)

        with patch(
            'foodlog.gui.windows.order_creation_window.OrdersRepository'
        ) as mock_orders_repo_class:
            mock_repo = MagicMock()
            mock_repo.create_order.side_effect = ValidationError(
                "Cannot save"
            )
            mock_orders_repo_class.return_value = mock_repo

            with patch(
                'foodlog.gui.windows.order_creation_window.messagebox'
            ):
                with patch.object(order_creation_window, 'destroy') as mock_destroy:
                    order_creation_window._save()
                    # destroy() should NOT be called on validation error
                    mock_destroy.assert_not_called()


def test_save_calls_update_order_totals(
    order_creation_window: OrderCreationWindow, test_db: Path
) -> None:
    """Test _save() calculates and updates order-level totals."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
            total_carbs_g=5.0,
            total_fat_g=2.0,
            sodium_mcg=500.0,
        )
        item_id = items_repo.create_item(item)
        item.item_id = item_id

        order_creation_window._add_item_row(item)
        order_creation_window.order_items[0]["row"].blocks_var.set("2")

        with patch(
            'foodlog.gui.windows.order_creation_window.messagebox'
        ):
            with patch.object(
                order_creation_window, 'destroy'
            ):
                with patch(
                    'foodlog.gui.windows.order_creation_window.OrdersRepository'
                ) as mock_orders_repo_class:
                    mock_repo = MagicMock()
                    mock_repo.create_order.return_value = 42
                    mock_orders_repo_class.return_value = mock_repo

                    order_creation_window._save()

                    # Verify update_order_totals was called
                    mock_repo.update_order_totals.assert_called_once()
                    call_args = mock_repo.update_order_totals.call_args
                    # order_id is passed as positional arg
                    assert call_args[0][0] == 42
                    call_kwargs = call_args[1]
                    assert call_kwargs["total_calories"] > 0
                    assert call_kwargs["total_protein_g"] > 0
                    assert "ratio1" in call_kwargs
                    assert "ratio2" in call_kwargs


def test_show_item_picker_filters_by_search_text(
    order_creation_window: OrderCreationWindow, test_db: Path
) -> None:
    """Test _show_item_picker filters items by search text."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        apple_id = names_repo.create_product_name("Apple")
        banana_id = names_repo.create_product_name("Banana")

        items_repo = ItemsRepository()
        apple = Item(
            name_id=apple_id,
            category_id=None,
            price=1.00,
            servings_per_block=1.0,
            units='oz',
            container_size=100,
            serving_size=10,
            calories=52.0,
            protein_g=0.3,
            choline_mcg=0,
        )
        banana = Item(
            name_id=banana_id,
            category_id=None,
            price=0.50,
            servings_per_block=1.0,
            units='oz',
            container_size=100,
            serving_size=10,
            calories=89.0,
            protein_g=1.1,
            choline_mcg=0,
        )
        items_repo.create_item(apple)
        items_repo.create_item(banana)

        order_creation_window.search_filter.search_var.set("apple")

        with patch(
            'foodlog.gui.windows.order_creation_window.tk.Toplevel'
        ) as mock_toplevel:
            mock_dialog = MagicMock()
            mock_toplevel.return_value = mock_dialog
            mock_listbox = MagicMock()
            mock_dialog.winfo_children.return_value = []

            with patch(
                'foodlog.gui.windows.order_creation_window.tk.Listbox'
            ) as mock_listbox_class:
                mock_listbox_class.return_value = mock_listbox

                with patch(
                    'foodlog.gui.windows.order_creation_window.tk.Button'
                ):
                    order_creation_window._show_item_picker()

                    # Verify only apple was inserted into listbox
                    assert mock_listbox.insert.call_count == 1
                    insert_call = mock_listbox.insert.call_args
                    assert "Apple" in insert_call[0][1]


def test_show_item_picker_filters_by_category(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _show_item_picker filters items by selected category."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        cat_repo = CategoriesRepository()
        cat1 = cat_repo.create_category("Fruit")

        names_repo = ProductNamesRepository()
        item1_id = names_repo.create_product_name("Item 1")
        item2_id = names_repo.create_product_name("Item 2")

        items_repo = ItemsRepository()
        item1 = Item(
            name_id=item1_id,
            category_id=cat1.category_id,
            price=1.00,
            servings_per_block=1.0,
            units='oz',
            container_size=100,
            serving_size=10,
            calories=50.0,
            protein_g=1.0,
            choline_mcg=0,
        )
        item2 = Item(
            name_id=item2_id,
            category_id=None,
            price=1.00,
            servings_per_block=1.0,
            units='oz',
            container_size=100,
            serving_size=10,
            calories=50.0,
            protein_g=1.0,
            choline_mcg=0,
        )
        items_repo.create_item(item1)
        items_repo.create_item(item2)

        window = OrderCreationWindow(root)
        window.search_filter.category_vars["Fruit"].set(True)

        with patch(
            'foodlog.gui.windows.order_creation_window.tk.Toplevel'
        ) as mock_toplevel:
            mock_dialog = MagicMock()
            mock_toplevel.return_value = mock_dialog
            mock_listbox = MagicMock()
            mock_dialog.winfo_children.return_value = []

            with patch(
                'foodlog.gui.windows.order_creation_window.tk.Listbox'
            ) as mock_listbox_class:
                mock_listbox_class.return_value = mock_listbox

                with patch(
                    'foodlog.gui.windows.order_creation_window.tk.Button'
                ):
                    window._show_item_picker()

                    # Only item1 should be inserted (it's in the selected cat)
                    assert mock_listbox.insert.call_count == 1
                    insert_call = mock_listbox.insert.call_args
                    assert "Item 1" in insert_call[0][1]


def test_show_item_picker_combines_search_and_category(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _show_item_picker applies both search and category filters."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        cat_repo = CategoriesRepository()
        cat1 = cat_repo.create_category("Fruit")

        names_repo = ProductNamesRepository()
        apple_id = names_repo.create_product_name("Apple")
        apple_pie_id = names_repo.create_product_name("Apple Pie")

        items_repo = ItemsRepository()
        apple = Item(
            name_id=apple_id,
            category_id=cat1.category_id,
            price=1.00,
            servings_per_block=1.0,
            units='oz',
            container_size=100,
            serving_size=10,
            calories=50.0,
            protein_g=1.0,
            choline_mcg=0,
        )
        apple_pie = Item(
            name_id=apple_pie_id,
            category_id=None,
            price=5.00,
            servings_per_block=1.0,
            units='oz',
            container_size=100,
            serving_size=10,
            calories=200.0,
            protein_g=2.0,
            choline_mcg=0,
        )
        items_repo.create_item(apple)
        items_repo.create_item(apple_pie)

        window = OrderCreationWindow(root)
        window.search_filter.search_var.set("apple")
        window.search_filter.category_vars["Fruit"].set(True)

        with patch(
            'foodlog.gui.windows.order_creation_window.tk.Toplevel'
        ) as mock_toplevel:
            mock_dialog = MagicMock()
            mock_toplevel.return_value = mock_dialog
            mock_listbox = MagicMock()
            mock_dialog.winfo_children.return_value = []

            with patch(
                'foodlog.gui.windows.order_creation_window.tk.Listbox'
            ) as mock_listbox_class:
                mock_listbox_class.return_value = mock_listbox

                with patch(
                    'foodlog.gui.windows.order_creation_window.tk.Button'
                ):
                    window._show_item_picker()

                    # Only Apple matches both search AND category
                    assert mock_listbox.insert.call_count == 1
                    insert_call = mock_listbox.insert.call_args
                    assert "Apple" in insert_call[0][1]
                    assert "Apple Pie" not in insert_call[0][1]


def test_window_title_new_order(root: tk.Tk, test_db: Path) -> None:
    """Test window title is 'Create Order' when order_id is None."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        window = OrderCreationWindow(root, order_id=None)
        assert window.title() == "Create Order"


def test_window_title_edit_order(root: tk.Tk, test_db: Path) -> None:
    """Test window title is 'Edit Order #{order_id}' when order_id provided."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        orders_repo = OrdersRepository()
        order = Order(
            order_date="2026-08-20",
            is_delivery=0,
            status="planning"
        )
        order_id = orders_repo.create_order(order)

        window = OrderCreationWindow(root, order_id=order_id)
        assert window.title() == f"Edit Order #{order_id}"


def test_load_existing_order_populates_header(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _load_existing_order populates header fields."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        orders_repo = OrdersRepository()
        order = Order(
            order_date="2026-08-19",
            is_delivery=1,
            status="ordered",
            delivery_charge=5.50,
            tip=2.00,
            tax=3.25,
            order_level_coupon=-1.50
        )
        order_id = orders_repo.create_order(order)

        window = OrderCreationWindow(root, order_id=order_id)

        header_values = window.header.get_values()
        assert header_values["order_date"] == "2026-08-19"
        assert header_values["is_delivery"] == 1
        assert header_values["status"] == "ordered"
        assert header_values["delivery_charge"] == 5.50
        assert header_values["tip"] == 2.00
        assert header_values["tax"] == 3.25
        assert header_values["order_level_coupon"] == -1.50


def test_load_existing_order_loads_order_lines(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _load_existing_order loads all order lines with items."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        # Create item
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
        items_repo = ItemsRepository()
        item = Item(
            name_id=name_id,
            price=5.00,
            servings_per_block=10.0,
            units='oz',
            container_size=100,
            serving_size=10,
            calories=100.0,
            protein_g=5.0,
            choline_mcg=0,
        )
        item_id = items_repo.create_item(item)

        # Create order
        orders_repo = OrdersRepository()
        order = Order(
            order_date="2026-08-18",
            is_delivery=0,
            status="planning"
        )
        order_id = orders_repo.create_order(order)

        # Create order line
        lines_repo = OrderLinesRepository()
        line = OrderLine(
            order_id=order_id,
            item_id=item_id,
            servings_ordered=20.0,
            actual_servings=20.0,
            stated_price=5.00,
            sale=-1.00,
            discount=0.0,
            coupon=0.0,
            net_price=99.00
        )
        lines_repo.create_order_line(line)

        # Load order in window
        window = OrderCreationWindow(root, order_id=order_id)

        # Should have one item row
        assert len(window.order_items) == 1
        row = window.order_items[0]["row"]
        # Check that line_id is set (indicating existing line)
        assert row.line_id is not None


def test_load_existing_order_applies_reconciled_lock(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _load_existing_order applies lock when status is reconciled."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        # Create order with reconciled status
        orders_repo = OrdersRepository()
        order = Order(
            order_date="2026-08-17",
            is_delivery=0,
            status="reconciled"
        )
        order_id = orders_repo.create_order(order)

        window = OrderCreationWindow(root, order_id=order_id)

        # Header widgets should be locked
        assert (
            window.header.date_entry.cget("state") == tk.DISABLED
        )
        assert (
            window.header.is_delivery_check.cget("state") == tk.DISABLED
        )
        # Add button should be locked
        assert window.add_item_btn.cget("state") == tk.DISABLED


def test_load_existing_order_doesnt_lock_for_planning(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _load_existing_order doesn't lock if status is not reconciled."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        orders_repo = OrdersRepository()
        order = Order(
            order_date="2026-08-16",
            is_delivery=0,
            status="planning"
        )
        order_id = orders_repo.create_order(order)

        window = OrderCreationWindow(root, order_id=order_id)

        # Header widgets should be enabled
        assert window.header.date_entry.cget("state") == tk.NORMAL
        assert (
            window.header.is_delivery_check.cget("state") == tk.NORMAL
        )
        # Add button should be enabled
        assert window.add_item_btn.cget("state") == tk.NORMAL


def test_add_item_row_with_existing_line(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _add_item_row with existing_line populates row from line data."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        # Create item
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
        items_repo = ItemsRepository()
        item = Item(
            name_id=name_id,
            price=5.00,
            servings_per_block=10.0,
            units='oz',
            container_size=100,
            serving_size=10,
            calories=100.0,
            protein_g=5.0,
            choline_mcg=0,
        )
        item_id = items_repo.create_item(item)
        item.item_id = item_id

        window = OrderCreationWindow(root)

        # Create order line to pass to _add_item_row
        existing_line = OrderLine(
            line_id=99,
            order_id=1,
            item_id=item_id,
            servings_ordered=25.0,
            actual_servings=25.0,
            stated_price=6.50,
            sale=-1.00,
            discount=-0.50,
            coupon=-0.25,
            net_price=156.25
        )

        window._add_item_row(item, existing_line=existing_line)

        row = window.order_items[0]["row"]
        # Check that line_id is set from existing_line
        assert row.line_id == 99
        # Check that fields are populated from existing_line
        assert float(row.price_var.get()) == 6.50
        assert float(row.servings_var.get()) == 25.0
        assert float(row.sale_var.get()) == -1.00
        assert float(row.discount_var.get()) == -0.50
        assert float(row.coupon_var.get()) == -0.25


def test_save_new_order_calls_create_order(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _save() calls create_order when creating new order."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
            total_carbs_g=20.0,
            total_fat_g=5.0,
            sodium_mcg=500.0,
        )
        item_id = items_repo.create_item(item)
        item.item_id = item_id

        window = OrderCreationWindow(root)
        assert window.order_id is None

        window._add_item_row(item)

        with patch(
            'foodlog.gui.windows.order_creation_window.messagebox'
        ):
            with patch.object(window, 'destroy'):
                with patch(
                    'foodlog.gui.windows.order_creation_window.OrdersRepository'
                ) as mock_orders_repo_class:
                    mock_repo = MagicMock()
                    mock_repo.create_order.return_value = 42
                    mock_orders_repo_class.return_value = mock_repo

                    window._save()

                    # Verify create_order was called (not update_order_header)
                    mock_repo.create_order.assert_called_once()
                    assert window.order_id == 42


def test_save_existing_order_calls_update_header(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _save() calls update_order_header when editing existing order."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
            total_carbs_g=20.0,
            total_fat_g=5.0,
            sodium_mcg=500.0,
        )
        item_id = items_repo.create_item(item)
        item.item_id = item_id

        # Create an order first
        orders_repo = OrdersRepository()
        order = Order(
            order_date="2026-08-15",
            is_delivery=0,
            status="planning"
        )
        order_id = orders_repo.create_order(order)

        # Load it in the window (which sets self.order_id)
        window = OrderCreationWindow(root, order_id=order_id)
        assert window.order_id == order_id

        window._add_item_row(item)

        with patch(
            'foodlog.gui.windows.order_creation_window.messagebox'
        ):
            with patch.object(window, 'destroy'):
                with patch(
                    'foodlog.gui.windows.order_creation_window.OrdersRepository'
                ) as mock_orders_repo_class:
                    mock_repo = MagicMock()
                    mock_orders_repo_class.return_value = mock_repo

                    window._save()

                    # Verify update_order_header was called (not create_order)
                    mock_repo.update_order_header.assert_called_once()
                    mock_repo.create_order.assert_not_called()


def test_save_new_line_calls_create_order_line(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _save() calls create_order_line for rows with no line_id."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
            total_carbs_g=20.0,
            total_fat_g=5.0,
            sodium_mcg=500.0,
        )
        item_id = items_repo.create_item(item)
        item.item_id = item_id

        window = OrderCreationWindow(root)
        window._add_item_row(item)

        # Verify line_id is None
        assert window.order_items[0]["row"].line_id is None

        with patch(
            'foodlog.gui.windows.order_creation_window.messagebox'
        ):
            with patch.object(window, 'destroy'):
                with patch(
                    'foodlog.gui.windows.order_creation_window.OrderLinesRepository'
                ) as mock_lines_repo_class:
                    mock_lines_repo = MagicMock()
                    mock_lines_repo_class.return_value = mock_lines_repo

                    with patch(
                        'foodlog.gui.windows.order_creation_window.OrdersRepository'
                    ) as mock_orders_repo_class:
                        mock_orders_repo = MagicMock()
                        mock_orders_repo.create_order.return_value = 99
                        mock_orders_repo_class.return_value = mock_orders_repo

                        window._save()

                        # Verify create_order_line was called
                        mock_lines_repo.create_order_line.assert_called_once()
                        mock_lines_repo.update_order_line.assert_not_called()


def test_save_existing_line_calls_update_order_line(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _save() calls update_order_line for rows with line_id."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
            total_carbs_g=20.0,
            total_fat_g=5.0,
            sodium_mcg=500.0,
        )
        item_id = items_repo.create_item(item)
        item.item_id = item_id

        # Create an order with a line
        orders_repo = OrdersRepository()
        order = Order(
            order_date="2026-08-14",
            is_delivery=0,
            status="planning"
        )
        order_id = orders_repo.create_order(order)

        lines_repo = OrderLinesRepository()
        line = OrderLine(
            order_id=order_id,
            item_id=item_id,
            servings_ordered=20.0,
            actual_servings=20.0,
            stated_price=5.00,
            sale=0.0,
            discount=0.0,
            coupon=0.0,
            net_price=100.00
        )
        lines_repo.create_order_line(line)

        # Load order in window
        window = OrderCreationWindow(root, order_id=order_id)

        # Verify line_id is set
        assert window.order_items[0]["row"].line_id is not None

        with patch(
            'foodlog.gui.windows.order_creation_window.messagebox'
        ):
            with patch.object(window, 'destroy'):
                with patch(
                    'foodlog.gui.windows.order_creation_window.OrderLinesRepository'
                ) as mock_lines_repo_class:
                    mock_lines_repo = MagicMock()
                    mock_lines_repo_class.return_value = mock_lines_repo

                    with patch(
                        'foodlog.gui.windows.order_creation_window.OrdersRepository'
                    ) as mock_orders_repo_class:
                        mock_orders_repo = MagicMock()
                        mock_orders_repo_class.return_value = mock_orders_repo

                        window._save()

                        # Verify update_order_line was called
                        mock_lines_repo.update_order_line.assert_called_once()
                        mock_lines_repo.create_order_line.assert_not_called()


def test_save_update_order_line_passes_correct_fields(
    root: tk.Tk, test_db: Path
) -> None:
    """Test _save() passes correct fields to update_order_line."""
    with patch(
        'foodlog.database.connection.get_database_path',
        return_value=test_db
    ):
        names_repo = ProductNamesRepository()
        name_id = names_repo.create_product_name("Test Item")
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
            total_carbs_g=20.0,
            total_fat_g=5.0,
            sodium_mcg=500.0,
        )
        item_id = items_repo.create_item(item)
        item.item_id = item_id

        # Create an order with a line
        orders_repo = OrdersRepository()
        order = Order(
            order_date="2026-08-13",
            is_delivery=0,
            status="planning"
        )
        order_id = orders_repo.create_order(order)

        lines_repo = OrderLinesRepository()
        line = OrderLine(
            order_id=order_id,
            item_id=item_id,
            servings_ordered=20.0,
            actual_servings=20.0,
            stated_price=5.00,
            sale=0.0,
            discount=0.0,
            coupon=0.0,
            net_price=100.00
        )
        lines_repo.create_order_line(line)

        # Load order in window
        window = OrderCreationWindow(root, order_id=order_id)
        line_id = window.order_items[0]["row"].line_id

        # Modify the row values
        window.order_items[0]["row"].servings_var.set("25.0")
        window.order_items[0]["row"].price_var.set("6.50")
        window.order_items[0]["row"].sale_var.set("-1.00")
        window.order_items[0]["row"].discount_var.set("-0.50")
        window.order_items[0]["row"].coupon_var.set("-0.25")

        with patch(
            'foodlog.gui.windows.order_creation_window.messagebox'
        ):
            with patch.object(window, 'destroy'):
                with patch(
                    'foodlog.gui.windows.order_creation_window.OrderLinesRepository'
                ) as mock_lines_repo_class:
                    mock_lines_repo = MagicMock()
                    mock_lines_repo_class.return_value = mock_lines_repo

                    with patch(
                        'foodlog.gui.windows.order_creation_window.OrdersRepository'
                    ) as mock_orders_repo_class:
                        mock_orders_repo = MagicMock()
                        mock_orders_repo_class.return_value = mock_orders_repo

                        window._save()

                        # Verify update_order_line was called with correct args
                        mock_lines_repo.update_order_line.assert_called_once()
                        call_args = mock_lines_repo.update_order_line.call_args
                        assert call_args[1]["line_id"] == line_id
                        assert call_args[1]["actual_servings"] == 25.0
                        assert call_args[1]["stated_price"] == 6.50
                        assert call_args[1]["sale"] == -1.00
                        assert call_args[1]["discount"] == -0.50
                        assert call_args[1]["coupon"] == -0.25
