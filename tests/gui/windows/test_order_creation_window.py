import tkinter as tk
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile

import pytest

from foodlog.database.connection import get_connection
from foodlog.database.schema import create_schema
from foodlog.database.seed_reference_data import seed_reference_data
from foodlog.gui.windows.order_creation_window import OrderCreationWindow
from foodlog.models.dim_items import Item
from foodlog.repository.items_repository import ItemsRepository
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
