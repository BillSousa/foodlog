import tkinter as tk

import pytest

from foodlog.gui.components.order_header import OrderHeader
from foodlog.models.fact_orders import Order


@pytest.fixture
def root() -> tk.Tk:
    """Create a test root window."""
    window = tk.Tk()
    yield window
    window.destroy()


@pytest.fixture
def order_header(root: tk.Tk) -> OrderHeader:
    """Create an OrderHeader widget."""
    return OrderHeader(root)


@pytest.fixture
def sample_order() -> Order:
    """Create a sample order for testing."""
    return Order(
        order_id=1,
        order_date="2026-08-15",
        is_delivery=1,
        status="ordered",
        delivery_charge=5.50,
        tip=2.00,
        tax=3.25,
        order_level_coupon=-1.50,
        total_net_cost=45.99,
        total_calories=500.0,
        total_protein_g=25.0,
        total_carbs_g=60.0,
        total_fat_g=15.0,
        total_sodium_mg=2300.0,
        ratio1=10.5,
        ratio2=8.3,
    )


def test_get_values_returns_dict(order_header: OrderHeader) -> None:
    """Test get_values returns a dict with expected keys."""
    values = order_header.get_values()
    assert isinstance(values, dict)
    assert "order_date" in values
    assert "is_delivery" in values
    assert "status" in values
    assert "delivery_charge" in values
    assert "tip" in values
    assert "tax" in values
    assert "order_level_coupon" in values


def test_get_values_defaults(order_header: OrderHeader) -> None:
    """Test get_values returns default values."""
    values = order_header.get_values()
    assert values["is_delivery"] == 0
    assert values["status"] == "planning"
    assert values["delivery_charge"] == 0.0
    assert values["tip"] == 0.0
    assert values["tax"] == 0.0
    assert values["order_level_coupon"] == 0.0


def test_set_locked_disables_widgets(order_header: OrderHeader) -> None:
    """Test set_locked(True) disables editable widgets."""
    order_header.set_locked(True)
    assert order_header.date_entry.cget("state") == tk.DISABLED
    assert order_header.is_delivery_check.cget("state") == tk.DISABLED
    assert order_header.delivery_charge_entry.cget("state") == tk.DISABLED
    assert order_header.tip_entry.cget("state") == tk.DISABLED
    assert order_header.tax_entry.cget("state") == tk.DISABLED
    assert order_header.order_level_coupon_entry.cget("state") == tk.DISABLED


def test_set_locked_enables_widgets(order_header: OrderHeader) -> None:
    """Test set_locked(False) enables editable widgets."""
    order_header.set_locked(True)
    order_header.set_locked(False)
    assert order_header.date_entry.cget("state") == tk.NORMAL
    assert order_header.is_delivery_check.cget("state") == tk.NORMAL
    assert order_header.delivery_charge_entry.cget("state") == tk.NORMAL
    assert order_header.tip_entry.cget("state") == tk.NORMAL
    assert order_header.tax_entry.cget("state") == tk.NORMAL
    assert order_header.order_level_coupon_entry.cget("state") == tk.NORMAL


def test_set_locked_status_combo_always_enabled(order_header: OrderHeader) -> None:
    """Test status combobox is NOT disabled when set_locked is called."""
    order_header.set_locked(True)
    # Status combo should remain in its normal state (not DISABLED)
    # In Tkinter, combobox state is not "NORMAL" but defaults to 'readonly'
    # The important thing is we don't explicitly set it to DISABLED
    assert order_header.status_combo.cget("state") != tk.DISABLED


def test_get_values_order_level_coupon_forced_negative(
    order_header: OrderHeader,
) -> None:
    """Test order_level_coupon is forced negative regardless of sign entered."""
    # Test positive value becomes negative
    order_header.order_level_coupon_var.set("5.00")
    values = order_header.get_values()
    assert values["order_level_coupon"] == -5.0

    # Test negative value stays negative
    order_header.order_level_coupon_var.set("-3.50")
    values = order_header.get_values()
    assert values["order_level_coupon"] == -3.5

    # Test zero stays zero
    order_header.order_level_coupon_var.set("0.00")
    values = order_header.get_values()
    assert values["order_level_coupon"] == 0.0


def test_get_values_money_fields_are_floats(
    order_header: OrderHeader,
) -> None:
    """Test money fields are returned as floats."""
    order_header.delivery_charge_var.set("9.99")
    order_header.tip_var.set("5.00")
    order_header.tax_var.set("2.10")
    values = order_header.get_values()
    assert isinstance(values["delivery_charge"], float)
    assert isinstance(values["tip"], float)
    assert isinstance(values["tax"], float)
    assert values["delivery_charge"] == 9.99
    assert values["tip"] == 5.0
    assert values["tax"] == 2.1


def test_set_values_populates_all_fields(
    order_header: OrderHeader, sample_order: Order
) -> None:
    """Test set_values populates all header fields from an order."""
    order_header.set_values(sample_order)
    values = order_header.get_values()
    assert values["order_date"] == "2026-08-15"
    assert values["is_delivery"] == 1
    assert values["status"] == "ordered"
    assert values["delivery_charge"] == 5.50
    assert values["tip"] == 2.00
    assert values["tax"] == 3.25
    assert values["order_level_coupon"] == -1.50


def test_set_values_with_planning_status(
    order_header: OrderHeader,
) -> None:
    """Test set_values with planning status."""
    order = Order(
        order_id=2,
        order_date="2026-08-16",
        is_delivery=0,
        status="planning",
        delivery_charge=0.0,
        tip=0.0,
        tax=0.0,
        order_level_coupon=0.0,
        total_net_cost=20.0,
        total_calories=300.0,
        total_protein_g=10.0,
        total_carbs_g=40.0,
        total_fat_g=8.0,
        total_sodium_mg=1500.0,
        ratio1=5.0,
        ratio2=4.0,
    )
    order_header.set_values(order)
    values = order_header.get_values()
    assert values["status"] == "planning"
    assert values["is_delivery"] == 0


def test_set_values_with_reconciled_status(
    order_header: OrderHeader,
) -> None:
    """Test set_values with reconciled status."""
    order = Order(
        order_id=3,
        order_date="2026-08-10",
        is_delivery=1,
        status="reconciled",
        delivery_charge=7.00,
        tip=3.50,
        tax=4.50,
        order_level_coupon=-2.00,
        total_net_cost=60.0,
        total_calories=600.0,
        total_protein_g=30.0,
        total_carbs_g=70.0,
        total_fat_g=20.0,
        total_sodium_mg=2500.0,
        ratio1=12.0,
        ratio2=9.5,
    )
    order_header.set_values(order)
    assert order_header.status_var.get() == "reconciled"
