import tkinter as tk

import pytest

from foodlog.gui.components.order_header import OrderHeader


@pytest.fixture
def root() -> tk.Tk:
    """Create a test root window."""
    return tk.Tk()


@pytest.fixture
def order_header(root: tk.Tk) -> OrderHeader:
    """Create an OrderHeader widget."""
    return OrderHeader(root)


def test_get_values_returns_dict(order_header: OrderHeader) -> None:
    """Test get_values returns a dict with expected keys."""
    values = order_header.get_values()
    assert isinstance(values, dict)
    assert "order_date" in values
    assert "is_delivery" in values
    assert "status" in values


def test_get_values_defaults(order_header: OrderHeader) -> None:
    """Test get_values returns default values."""
    values = order_header.get_values()
    assert values["is_delivery"] == 0
    assert values["status"] == "planning"


def test_set_locked_disables_widgets(order_header: OrderHeader) -> None:
    """Test set_locked(True) disables editable widgets."""
    order_header.set_locked(True)
    assert order_header.date_entry.cget("state") == tk.DISABLED
    assert order_header.is_delivery_check.cget("state") == tk.DISABLED


def test_set_locked_enables_widgets(order_header: OrderHeader) -> None:
    """Test set_locked(False) enables editable widgets."""
    order_header.set_locked(True)
    order_header.set_locked(False)
    assert order_header.date_entry.cget("state") == tk.NORMAL
    assert order_header.is_delivery_check.cget("state") == tk.NORMAL


def test_set_locked_status_combo_always_enabled(order_header: OrderHeader) -> None:
    """Test status combobox is NOT disabled when set_locked is called."""
    order_header.set_locked(True)
    # Status combo should remain in its normal state (not DISABLED)
    # In Tkinter, combobox state is not "NORMAL" but defaults to 'readonly'
    # The important thing is we don't explicitly set it to DISABLED
    assert order_header.status_combo.cget("state") != tk.DISABLED
