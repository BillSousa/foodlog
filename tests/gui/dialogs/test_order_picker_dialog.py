import tkinter as tk
from unittest.mock import Mock, patch, call
import pytest

from foodlog.gui.dialogs.order_picker_dialog import OrderPickerDialog
from foodlog.models.fact_orders import Order


@pytest.fixture
def root() -> tk.Tk:
    """Create a test root window."""
    return tk.Tk()


@pytest.fixture
def sample_orders() -> list[Order]:
    """Create sample orders for testing."""
    return [
        Order(
            order_id=1,
            order_date="2026-08-20",
            is_delivery=1,
            status="planning",
            total_net_cost=50.0,
        ),
        Order(
            order_id=2,
            order_date="2026-08-19",
            is_delivery=0,
            status="ordered",
            total_net_cost=35.0,
        ),
        Order(
            order_id=3,
            order_date="2026-08-18",
            is_delivery=1,
            status="delivered",
            total_net_cost=60.0,
        ),
    ]


def test_dialog_initialized_with_correct_title(root: tk.Tk) -> None:
    """Test dialog is initialized with correct title."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = []
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        assert dialog.title() == "Select an Order to Manage"
        dialog.destroy()


def test_dialog_initialized_with_correct_geometry(root: tk.Tk) -> None:
    """Test dialog geometry call is made during initialization."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = []
        mock_repo_class.return_value = mock_repo

        # Mock the geometry call to verify it's called with correct value
        with patch.object(
            tk.Toplevel, "geometry"
        ) as mock_geometry:
            dialog = OrderPickerDialog(root)
            # Verify geometry was called with the correct dimension string
            mock_geometry.assert_called_with("500x400")


def test_selected_order_id_initialized_to_none(root: tk.Tk) -> None:
    """Test selected_order_id is initialized to None."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = []
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        assert dialog.selected_order_id is None
        dialog.destroy()


def test_layout_creates_listbox(root: tk.Tk) -> None:
    """Test layout creates listbox widget."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = []
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        assert hasattr(dialog, "listbox")
        assert isinstance(dialog.listbox, tk.Listbox)
        dialog.destroy()


def test_load_orders_populates_listbox(
    root: tk.Tk, sample_orders: list[Order]
) -> None:
    """Test load_orders populates listbox with order text."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = sample_orders
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        assert dialog.listbox.size() == 3
        dialog.destroy()


def test_load_orders_formats_delivery_correctly(
    root: tk.Tk,
) -> None:
    """Test load_orders formats delivery status correctly."""
    delivery_order = Order(
        order_id=1,
        order_date="2026-08-20",
        is_delivery=1,
        status="planning",
        total_net_cost=50.0,
    )
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = [delivery_order]
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        text = dialog.listbox.get(0)
        assert "Delivery" in text
        assert "Order #1" in text
        assert "2026-08-20" in text
        assert "planning" in text
        dialog.destroy()


def test_load_orders_formats_pickup_correctly(
    root: tk.Tk,
) -> None:
    """Test load_orders formats pickup (not delivery) correctly."""
    pickup_order = Order(
        order_id=2,
        order_date="2026-08-19",
        is_delivery=0,
        status="ordered",
        total_net_cost=35.0,
    )
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = [pickup_order]
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        text = dialog.listbox.get(0)
        assert "Pickup" in text
        assert "Order #2" in text
        assert "2026-08-19" in text
        assert "ordered" in text
        dialog.destroy()


def test_load_orders_stores_order_ids(
    root: tk.Tk, sample_orders: list[Order]
) -> None:
    """Test load_orders stores order_ids for later lookup."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = sample_orders
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        assert dialog.order_ids == [1, 2, 3]
        dialog.destroy()


@patch(
    "foodlog.gui.windows.order_creation_window.OrderCreationWindow"
)
def test_on_create_new_creates_window(
    mock_window_class, root: tk.Tk
) -> None:
    """Test _on_create_new creates OrderCreationWindow."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = []
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        dialog._on_create_new()

        mock_window_class.assert_called_once_with(dialog)


@patch(
    "foodlog.gui.windows.order_creation_window.OrderCreationWindow"
)
def test_on_create_new_window_created_without_order_id(
    mock_window_class, root: tk.Tk
) -> None:
    """Test _on_create_new creates window without order_id parameter."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = []
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        dialog._on_create_new()

        # Verify called with just parent, no order_id
        call_args = mock_window_class.call_args
        assert call_args[0][0] == dialog  # First positional arg is parent
        # order_id not in kwargs
        assert "order_id" not in call_args[1]


@patch(
    "foodlog.gui.windows.order_creation_window.OrderCreationWindow"
)
def test_on_open_shows_warning_when_no_selection(
    mock_window_class, root: tk.Tk
) -> None:
    """Test _on_open shows warning when no order is selected."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = []
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)

        with patch(
            "foodlog.gui.dialogs.order_picker_dialog.messagebox.showwarning"
        ) as mock_warning:
            dialog._on_open()
            mock_warning.assert_called_once_with(
                "Select", "Please select an order"
            )


@patch(
    "foodlog.gui.windows.order_creation_window.OrderCreationWindow"
)
def test_on_open_with_selection_creates_window(
    mock_window_class, root: tk.Tk, sample_orders: list[Order]
) -> None:
    """Test _on_open creates window with selected order_id."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = sample_orders
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        # Select first order
        dialog.listbox.selection_set(0)

        dialog._on_open()

        # Verify OrderCreationWindow called with order_id=1
        mock_window_class.assert_called_once_with(dialog, order_id=1)


@patch(
    "foodlog.gui.windows.order_creation_window.OrderCreationWindow"
)
def test_on_open_uses_correct_order_id_from_selection(
    mock_window_class, root: tk.Tk, sample_orders: list[Order]
) -> None:
    """Test _on_open passes correct order_id from listbox selection."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = sample_orders
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        # Select second order (order_id=2)
        dialog.listbox.selection_set(1)

        dialog._on_open()

        # Verify order_id=2 is passed
        call_args = mock_window_class.call_args
        assert call_args[1]["order_id"] == 2


@patch(
    "foodlog.gui.windows.order_creation_window.OrderCreationWindow"
)
def test_on_open_with_third_order_selection(
    mock_window_class, root: tk.Tk, sample_orders: list[Order]
) -> None:
    """Test _on_open with third order selected."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = sample_orders
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)
        # Select third order (order_id=3)
        dialog.listbox.selection_set(2)

        dialog._on_open()

        # Verify order_id=3 is passed
        call_args = mock_window_class.call_args
        assert call_args[1]["order_id"] == 3


def test_load_orders_calls_repository(root: tk.Tk) -> None:
    """Test _load_orders calls OrdersRepository.list_orders."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = []
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)

        # Verify repository was instantiated
        mock_repo_class.assert_called()
        # Verify list_orders was called
        mock_repo.list_orders.assert_called()
        dialog.destroy()


def test_load_orders_with_empty_list(root: tk.Tk) -> None:
    """Test _load_orders handles empty order list."""
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = []
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)

        assert dialog.listbox.size() == 0
        assert dialog.order_ids == []
        dialog.destroy()


def test_load_orders_all_statuses(root: tk.Tk) -> None:
    """Test _load_orders displays all order statuses correctly."""
    orders = [
        Order(
            order_id=1,
            order_date="2026-08-20",
            is_delivery=1,
            status="planning",
            total_net_cost=50.0,
        ),
        Order(
            order_id=2,
            order_date="2026-08-19",
            is_delivery=0,
            status="ordered",
            total_net_cost=35.0,
        ),
        Order(
            order_id=3,
            order_date="2026-08-18",
            is_delivery=1,
            status="delivered",
            total_net_cost=60.0,
        ),
        Order(
            order_id=4,
            order_date="2026-08-17",
            is_delivery=0,
            status="reconciled",
            total_net_cost=45.0,
        ),
    ]
    with patch(
        "foodlog.gui.dialogs.order_picker_dialog.OrdersRepository"
    ) as mock_repo_class:
        mock_repo = Mock()
        mock_repo.list_orders.return_value = orders
        mock_repo_class.return_value = mock_repo

        dialog = OrderPickerDialog(root)

        # Verify all statuses appear
        text0 = dialog.listbox.get(0)
        text1 = dialog.listbox.get(1)
        text2 = dialog.listbox.get(2)
        text3 = dialog.listbox.get(3)

        assert "planning" in text0
        assert "ordered" in text1
        assert "delivered" in text2
        assert "reconciled" in text3
        dialog.destroy()
