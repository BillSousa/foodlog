import tempfile
import tkinter as tk
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from foodlog.gui.windows.order_summary_window import OrderSummaryWindow
from foodlog.models.dim_categories import Category
from foodlog.models.dim_items import Item
from foodlog.models.fact_order_lines import OrderLine
from foodlog.models.fact_orders import Order


@pytest.fixture
def mock_orders_repo() -> MagicMock:
    """Create a mock OrdersRepository with default Order."""
    mock = MagicMock()
    default_order = Order(
        order_id=123,
        delivery_charge=0.0,
        tip=0.0,
        tax=0.0,
        order_level_coupon=0.0,
    )
    mock.return_value.get_order.return_value = default_order
    return mock


def test_order_summary_window_init() -> None:
    """Window initializes with correct title."""
    root = tk.Tk()
    try:
        with patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrdersRepository"
        ) as MockOrdersRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo:

            order = Order(
                order_id=123,
                delivery_charge=0.0,
                tip=0.0,
                tax=0.0,
                order_level_coupon=0.0,
            )

            MockLinesRepo.return_value.get_order_lines.return_value = []
            MockOrdersRepo.return_value.get_order.return_value = order
            MockItemsRepo.return_value.get_item.return_value = None
            MockCatRepo.return_value.get_category.return_value = None
            MockNamesRepo.return_value.get_product_name.return_value = None

            window = OrderSummaryWindow(root, order_id=123)
            assert window.title() == "Order #123 — Money Summary"
            window.destroy()
    finally:
        root.destroy()


def test_order_summary_window_single_category() -> None:
    """Display items grouped in a single category."""
    root = tk.Tk()
    try:
        with patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrdersRepository"
        ) as MockOrdersRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo:

            line1 = OrderLine(
                line_id=1,
                order_id=123,
                item_id=10,
                actual_servings=1.0,
                stated_price=5.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=5.00,
            )
            line2 = OrderLine(
                line_id=2,
                order_id=123,
                item_id=20,
                actual_servings=2.0,
                stated_price=6.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=6.00,
            )

            item1 = Item(item_id=10, category_id=5, name_id=100)
            item2 = Item(item_id=20, category_id=5, name_id=101)

            category = Category(category_id=5, category_name="Produce")

            order = Order(
                order_id=123,
                delivery_charge=2.00,
                tip=1.50,
                tax=0.80,
                order_level_coupon=0.0,
            )

            MockLinesRepo.return_value.get_order_lines.return_value = [
                line1,
                line2,
            ]
            MockItemsRepo.return_value.get_item.side_effect = lambda id: (
                item1 if id == 10 else item2 if id == 20 else None
            )
            MockCatRepo.return_value.get_category.return_value = category
            MockOrdersRepo.return_value.get_order.return_value = order

            product_name1 = MagicMock(name_text="Apples")
            product_name2 = MagicMock(name_text="Carrots")
            MockNamesRepo.return_value.get_product_name.side_effect = (
                lambda id: (
                    product_name1 if id == 100 else product_name2
                    if id == 101 else None
                )
            )

            window = OrderSummaryWindow(root, order_id=123)
            assert window.winfo_exists()
            window.destroy()
    finally:
        root.destroy()


def test_order_summary_window_multiple_categories() -> None:
    """Display items grouped across multiple categories."""
    root = tk.Tk()
    try:
        with patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrdersRepository"
        ) as MockOrdersRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo:

            line1 = OrderLine(
                line_id=1,
                order_id=123,
                item_id=10,
                actual_servings=1.0,
                stated_price=5.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=5.00,
            )
            line2 = OrderLine(
                line_id=2,
                order_id=123,
                item_id=20,
                actual_servings=1.0,
                stated_price=8.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=8.00,
            )

            item1 = Item(item_id=10, category_id=5, name_id=100)
            item2 = Item(item_id=20, category_id=6, name_id=101)

            cat1 = Category(category_id=5, category_name="Produce")
            cat2 = Category(category_id=6, category_name="Meat")

            order = Order(
                order_id=123,
                delivery_charge=2.00,
                tip=1.00,
                tax=1.00,
                order_level_coupon=0.0,
            )

            MockLinesRepo.return_value.get_order_lines.return_value = [
                line1,
                line2,
            ]
            MockItemsRepo.return_value.get_item.side_effect = lambda id: (
                item1 if id == 10 else item2 if id == 20 else None
            )
            MockCatRepo.return_value.get_category.side_effect = lambda id: (
                cat1 if id == 5 else cat2 if id == 6 else None
            )
            MockOrdersRepo.return_value.get_order.return_value = order

            product_name1 = MagicMock(name_text="Apples")
            product_name2 = MagicMock(name_text="Chicken")
            MockNamesRepo.return_value.get_product_name.side_effect = (
                lambda id: (
                    product_name1 if id == 100 else product_name2
                    if id == 101 else None
                )
            )

            window = OrderSummaryWindow(root, order_id=123)
            assert window.winfo_exists()
            window.destroy()
    finally:
        root.destroy()


def test_order_summary_window_uncategorized_items() -> None:
    """Display items with no category."""
    root = tk.Tk()
    try:
        with patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrdersRepository"
        ) as MockOrdersRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo:

            line1 = OrderLine(
                line_id=1,
                order_id=123,
                item_id=10,
                actual_servings=1.0,
                stated_price=3.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=3.00,
            )

            item1 = Item(item_id=10, category_id=None, name_id=100)

            order = Order(
                order_id=123,
                delivery_charge=0.0,
                tip=0.0,
                tax=0.0,
                order_level_coupon=0.0,
            )

            MockLinesRepo.return_value.get_order_lines.return_value = [
                line1
            ]
            MockItemsRepo.return_value.get_item.return_value = item1
            MockCatRepo.return_value.get_category.return_value = None
            MockOrdersRepo.return_value.get_order.return_value = order

            product_name1 = MagicMock(name_text="Mystery Item")
            MockNamesRepo.return_value.get_product_name.return_value = (
                product_name1
            )

            window = OrderSummaryWindow(root, order_id=123)
            assert window.winfo_exists()
            window.destroy()
    finally:
        root.destroy()


def test_order_summary_window_csv_export_single_category(
    mock_orders_repo: MagicMock,
) -> None:
    """Export order summary to CSV with single category."""
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "test.csv"

        with patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrdersRepository",
            mock_orders_repo,
        ), patch(
            "foodlog.gui.windows.order_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".export_rows_to_csv"
        ) as MockExport, patch(
            "foodlog.gui.windows.order_summary_window.messagebox"
        ), patch(
            "foodlog.gui.windows.order_summary_window.get_database_path"
        ) as MockDbPath:

            line1 = OrderLine(
                line_id=1,
                order_id=123,
                item_id=10,
                actual_servings=1.5,
                stated_price=10.00,
                sale=-1.00,
                discount=0.0,
                coupon=0.0,
                net_price=9.00,
            )

            item1 = Item(item_id=10, category_id=5, name_id=100)
            category = Category(category_id=5, category_name="Produce")
            product_name1 = MagicMock(name_text="Apples")

            MockLinesRepo.return_value.get_order_lines.return_value = [
                line1
            ]
            MockItemsRepo.return_value.get_item.return_value = item1
            MockCatRepo.return_value.get_category.return_value = category
            MockNamesRepo.return_value.get_product_name.return_value = (
                product_name1
            )
            MockDbPath.return_value = Path(tmpdir) / "foodlog.db"

            root = tk.Tk()
            try:
                window = OrderSummaryWindow(root, order_id=123)
                window._export_csv()

                # Verify export_rows_to_csv was called
                MockExport.assert_called_once()
                call_args = MockExport.call_args
                path_arg = call_args[0][0]
                header_arg = call_args[0][1]
                rows_arg = call_args[0][2]

                assert "order_123_money_summary" in str(path_arg)
                assert header_arg == [
                    "Item",
                    "Blocks",
                    "Servings",
                    "Stated Price",
                    "Sale",
                    "Discount",
                    "Coupon",
                    "Net Price",
                ]
                # Expected structure:
                # Row 0: ["Produce", "", "", "", "", "", "", ""]
                # Row 1: ["Apples", "0.00", "1.5", "$10.00", "$-1.00", "$0.00", "$0.00", "$9.00"]
                # Row 2: ["Subtotal", "", "", "", "", "", "", "$9.00"]
                # Row 3: ["Subtotal", "", "", "", "", "", "", "$9.00"]
                # Row 4: ["", "", "", "", "", "", "", ""]
                # Row 5-8: Delivery, Tip, Tax, Coupon
                # Row 9: TOTAL
                assert len(rows_arg) == 10
                assert rows_arg[0] == ["Produce", "", "", "", "", "", "", ""]
                assert rows_arg[1][0] == "Apples"
                assert rows_arg[1][1] == "0.00"
                assert rows_arg[1][2] == "1.5"
                assert rows_arg[1][3] == "$10.00"
                assert rows_arg[1][4] == "$-1.00"
                assert rows_arg[1][5] == "$0.00"
                assert rows_arg[1][6] == "$0.00"
                assert rows_arg[1][7] == "$9.00"
                assert rows_arg[2] == [
                    "Subtotal",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "$9.00",
                ]
                assert rows_arg[3] == [
                    "Subtotal",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "$9.00",
                ]

                window.destroy()
            finally:
                root.destroy()


def test_order_summary_window_csv_export_multiple_categories(
    mock_orders_repo: MagicMock,
) -> None:
    """Export with multiple categories maintains grouping."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrdersRepository",
            mock_orders_repo,
        ), patch(
            "foodlog.gui.windows.order_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".export_rows_to_csv"
        ) as MockExport, patch(
            "foodlog.gui.windows.order_summary_window.messagebox"
        ), patch(
            "foodlog.gui.windows.order_summary_window.get_database_path"
        ) as MockDbPath:

            line1 = OrderLine(
                line_id=1,
                order_id=123,
                item_id=10,
                actual_servings=1.0,
                stated_price=5.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=5.00,
            )
            line2 = OrderLine(
                line_id=2,
                order_id=123,
                item_id=20,
                actual_servings=1.0,
                stated_price=8.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=8.00,
            )

            item1 = Item(item_id=10, category_id=5, name_id=100)
            item2 = Item(item_id=20, category_id=6, name_id=101)

            cat1 = Category(category_id=5, category_name="Produce")
            cat2 = Category(category_id=6, category_name="Meat")

            product_name1 = MagicMock(name_text="Apples")
            product_name2 = MagicMock(name_text="Chicken")

            MockLinesRepo.return_value.get_order_lines.return_value = [
                line1,
                line2,
            ]
            MockItemsRepo.return_value.get_item.side_effect = lambda id: (
                item1 if id == 10 else item2 if id == 20 else None
            )
            MockCatRepo.return_value.get_category.side_effect = lambda id: (
                cat1 if id == 5 else cat2 if id == 6 else None
            )
            MockNamesRepo.return_value.get_product_name.side_effect = (
                lambda id: (
                    product_name1 if id == 100 else product_name2
                    if id == 101 else None
                )
            )
            MockDbPath.return_value = Path(tmpdir) / "foodlog.db"

            root = tk.Tk()
            try:
                window = OrderSummaryWindow(root, order_id=123)
                window._export_csv()

                MockExport.assert_called_once()
                rows_arg = MockExport.call_args[0][2]

                # Expected structure for 2 items in 2 categories:
                # Row 0: ["Produce", "", "", "", "", "", "", ""]
                # Row 1: ["Apples", "0.00", "1.0", "$5.00", "$0.00", "$0.00", "$0.00", "$5.00"]
                # Row 2: ["Subtotal", "", "", "", "", "", "", "$5.00"]
                # Row 3: ["Meat", "", "", "", "", "", "", ""]
                # Row 4: ["Chicken", "0.00", "1.0", "$8.00", "$0.00", "$0.00", "$0.00", "$8.00"]
                # Row 5: ["Subtotal", "", "", "", "", "", "", "$8.00"]
                # Row 6: ["Subtotal", "", "", "", "", "", "", "$13.00"]
                # Row 7: ["", "", "", "", "", "", "", ""]
                # Row 8-11: Delivery, Tip, Tax, Coupon
                # Row 12: TOTAL
                assert len(rows_arg) == 13
                assert rows_arg[0][0] == "Produce"
                assert rows_arg[1][0] == "Apples"
                assert rows_arg[3][0] == "Meat"
                assert rows_arg[4][0] == "Chicken"

                window.destroy()
            finally:
                root.destroy()


def test_order_summary_window_csv_export_missing_product_name(
    mock_orders_repo: MagicMock,
) -> None:
    """CSV export handles missing product names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".OrdersRepository",
            mock_orders_repo,
        ), patch(
            "foodlog.gui.windows.order_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo, patch(
            "foodlog.gui.windows.order_summary_window"
            ".export_rows_to_csv"
        ) as MockExport, patch(
            "foodlog.gui.windows.order_summary_window.messagebox"
        ), patch(
            "foodlog.gui.windows.order_summary_window.get_database_path"
        ) as MockDbPath:

            line1 = OrderLine(
                line_id=1,
                order_id=123,
                item_id=10,
                actual_servings=1.0,
                stated_price=5.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=5.00,
            )

            item1 = Item(item_id=10, category_id=5, name_id=100)
            category = Category(category_id=5, category_name="Produce")

            MockLinesRepo.return_value.get_order_lines.return_value = [
                line1
            ]
            MockItemsRepo.return_value.get_item.return_value = item1
            MockCatRepo.return_value.get_category.return_value = category
            MockNamesRepo.return_value.get_product_name.return_value = None
            MockDbPath.return_value = Path(tmpdir) / "foodlog.db"

            root = tk.Tk()
            try:
                window = OrderSummaryWindow(root, order_id=123)
                window._export_csv()

                rows_arg = MockExport.call_args[0][2]
                # Row 1 should be the item row with the fallback name
                assert rows_arg[1][0] == "Item #10"

                window.destroy()
            finally:
                root.destroy()


def test_order_summary_window_csv_export_error(
    mock_orders_repo: MagicMock,
) -> None:
    """CSV export error shows error messagebox."""
    with patch(
        "foodlog.gui.windows.order_summary_window"
        ".OrderLinesRepository"
    ) as MockLinesRepo, patch(
        "foodlog.gui.windows.order_summary_window"
        ".ItemsRepository"
    ) as MockItemsRepo, patch(
        "foodlog.gui.windows.order_summary_window"
        ".CategoriesRepository"
    ) as MockCatRepo, patch(
        "foodlog.gui.windows.order_summary_window"
        ".OrdersRepository",
        mock_orders_repo,
    ), patch(
        "foodlog.gui.windows.order_summary_window"
        ".ProductNamesRepository"
    ) as MockNamesRepo, patch(
        "foodlog.gui.windows.order_summary_window.messagebox"
    ) as MockMsgbox:

        line1 = OrderLine(
            line_id=1,
            order_id=123,
            item_id=10,
            actual_servings=1.0,
            stated_price=5.00,
            sale=0.0,
            discount=0.0,
            coupon=0.0,
            net_price=5.00,
        )

        item1 = Item(item_id=10, category_id=5, name_id=100)
        category = Category(category_id=5, category_name="Produce")
        product_name1 = MagicMock(name_text="Apples")

        MockLinesRepo.return_value.get_order_lines.return_value = [line1]
        MockItemsRepo.return_value.get_item.return_value = item1
        MockCatRepo.return_value.get_category.return_value = category
        MockNamesRepo.return_value.get_product_name.return_value = (
            product_name1
        )

        root = tk.Tk()
        try:
            window = OrderSummaryWindow(root, order_id=123)

            # Make export_rows_to_csv raise an error
            with patch(
                "foodlog.gui.windows.order_summary_window"
                ".export_rows_to_csv"
            ) as MockExport:
                MockExport.side_effect = IOError("Write failed")
                window._export_csv()

                MockMsgbox.showerror.assert_called_once()
                call_args = MockMsgbox.showerror.call_args
                assert call_args[0][0] == "Error"
                assert "Export failed" in call_args[0][1]

            window.destroy()
        finally:
            root.destroy()
