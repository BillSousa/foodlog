import tempfile
import tkinter as tk
from pathlib import Path
from unittest.mock import MagicMock, patch

from foodlog.gui.windows.nutrition_summary_window import NutritionSummaryWindow
from foodlog.models.dim_categories import Category
from foodlog.models.dim_items import Item
from foodlog.models.fact_order_lines import OrderLine


def test_nutrition_summary_window_init() -> None:
    """Window initializes with correct title."""
    root = tk.Tk()
    try:
        with patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".TrackedNutrientsRepository"
        ) as MockTrackedRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo:

            MockLinesRepo.return_value.get_order_lines.return_value = []
            MockTrackedRepo.return_value.get_tracked_nutrients.return_value = [
                "Calories",
                "Protein",
            ]
            MockItemsRepo.return_value.get_item.return_value = None
            MockCatRepo.return_value.get_category.return_value = None
            MockNamesRepo.return_value.get_product_name.return_value = None

            window = NutritionSummaryWindow(root, order_id=456)
            assert window.title() == "Order #456 — Nutrition Summary"
            window.destroy()
    finally:
        root.destroy()


def test_nutrition_summary_window_single_category() -> None:
    """Display nutrients for items in single category."""
    root = tk.Tk()
    try:
        with patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".TrackedNutrientsRepository"
        ) as MockTrackedRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo:

            line1 = OrderLine(
                line_id=1,
                order_id=456,
                item_id=10,
                actual_servings=2.0,
                stated_price=5.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=5.00,
            )

            item1 = Item(
                item_id=10,
                category_id=5,
                name_id=100,
                calories=100.0,
                protein_g=10.0,
                sodium_mcg=200.0,
                total_fat_g=5.0,
            )

            category = Category(category_id=5, category_name="Produce")
            product_name = MagicMock(name_text="Apples")

            MockLinesRepo.return_value.get_order_lines.return_value = [line1]
            MockItemsRepo.return_value.get_item.return_value = item1
            MockCatRepo.return_value.get_category.return_value = category
            MockTrackedRepo.return_value.get_tracked_nutrients.return_value = [
                "Calories",
                "Protein",
                "Sodium",
            ]
            MockNamesRepo.return_value.get_product_name.return_value = (
                product_name
            )

            window = NutritionSummaryWindow(root, order_id=456)
            assert window.winfo_exists()
            window.destroy()
    finally:
        root.destroy()


def test_nutrition_summary_window_multiple_categories() -> None:
    """Display nutrients across multiple categories."""
    root = tk.Tk()
    try:
        with patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".TrackedNutrientsRepository"
        ) as MockTrackedRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo:

            line1 = OrderLine(
                line_id=1,
                order_id=456,
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
                order_id=456,
                item_id=20,
                actual_servings=2.0,
                stated_price=10.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=10.00,
            )

            item1 = Item(
                item_id=10,
                category_id=5,
                name_id=100,
                calories=100.0,
                protein_g=10.0,
                sodium_mcg=200.0,
                total_fat_g=5.0,
            )
            item2 = Item(
                item_id=20,
                category_id=6,
                name_id=101,
                calories=150.0,
                protein_g=15.0,
                sodium_mcg=300.0,
                total_fat_g=8.0,
            )

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
            MockTrackedRepo.return_value.get_tracked_nutrients.return_value = [
                "Calories",
                "Protein",
            ]
            MockNamesRepo.return_value.get_product_name.side_effect = (
                lambda id: (
                    product_name1 if id == 100 else product_name2
                    if id == 101 else None
                )
            )

            window = NutritionSummaryWindow(root, order_id=456)
            assert window.winfo_exists()
            window.destroy()
    finally:
        root.destroy()


def test_nutrition_summary_window_uncategorized_items() -> None:
    """Display uncategorized items."""
    root = tk.Tk()
    try:
        with patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".TrackedNutrientsRepository"
        ) as MockTrackedRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo:

            line1 = OrderLine(
                line_id=1,
                order_id=456,
                item_id=10,
                actual_servings=1.0,
                stated_price=3.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=3.00,
            )

            item1 = Item(
                item_id=10,
                category_id=None,
                name_id=100,
                calories=100.0,
                protein_g=10.0,
            )

            product_name = MagicMock(name_text="Mystery Item")

            MockLinesRepo.return_value.get_order_lines.return_value = [line1]
            MockItemsRepo.return_value.get_item.return_value = item1
            MockCatRepo.return_value.get_category.return_value = None
            MockTrackedRepo.return_value.get_tracked_nutrients.return_value = [
                "Calories",
                "Protein",
            ]
            MockNamesRepo.return_value.get_product_name.return_value = (
                product_name
            )

            window = NutritionSummaryWindow(root, order_id=456)
            assert window.winfo_exists()
            window.destroy()
    finally:
        root.destroy()


def test_nutrition_summary_window_csv_export_single_category() -> None:
    """Export nutrition data to CSV with single category."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".TrackedNutrientsRepository"
        ) as MockTrackedRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".export_rows_to_csv"
        ) as MockExport, patch(
            "foodlog.gui.windows.nutrition_summary_window.messagebox"
        ), patch(
            "foodlog.gui.windows.nutrition_summary_window.get_database_path"
        ) as MockDbPath:

            line1 = OrderLine(
                line_id=1,
                order_id=456,
                item_id=10,
                actual_servings=2.0,
                stated_price=5.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=5.00,
            )

            item1 = Item(
                item_id=10,
                category_id=5,
                name_id=100,
                calories=100.0,
                protein_g=10.0,
                sodium_mcg=200.0,
                total_fat_g=5.0,
            )

            category = Category(category_id=5, category_name="Produce")
            product_name = MagicMock(name_text="Apples")

            MockLinesRepo.return_value.get_order_lines.return_value = [line1]
            MockItemsRepo.return_value.get_item.return_value = item1
            MockCatRepo.return_value.get_category.return_value = category
            MockTrackedRepo.return_value.get_tracked_nutrients.return_value = [
                "Calories",
                "Protein",
            ]
            MockNamesRepo.return_value.get_product_name.return_value = (
                product_name
            )
            MockDbPath.return_value = Path(tmpdir) / "foodlog.db"

            root = tk.Tk()
            try:
                window = NutritionSummaryWindow(root, order_id=456)
                window._export_csv()

                MockExport.assert_called_once()
                call_args = MockExport.call_args
                header_arg = call_args[0][1]
                rows_arg = call_args[0][2]

                assert header_arg == [
                    "Category",
                    "Item",
                    "Blocks",
                    "Servings",
                    "Calories",
                    "Protein",
                    "Ratio1",
                    "Ratio2",
                ]
                assert len(rows_arg) == 3
                assert rows_arg[0][0] == "Produce"
                assert rows_arg[0][1] == "Apples"
                assert rows_arg[0][3] == 2.0
                assert rows_arg[1][0] == "Produce"
                assert rows_arg[1][1] == "Subtotal"
                assert rows_arg[2][0] == ""
                assert rows_arg[2][1] == "GRAND TOTAL"

                window.destroy()
            finally:
                root.destroy()


def test_nutrition_summary_window_csv_export_multiple_nutrients() -> None:
    """CSV export includes all tracked nutrients."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".TrackedNutrientsRepository"
        ) as MockTrackedRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".export_rows_to_csv"
        ) as MockExport, patch(
            "foodlog.gui.windows.nutrition_summary_window.messagebox"
        ), patch(
            "foodlog.gui.windows.nutrition_summary_window.get_database_path"
        ) as MockDbPath:

            line1 = OrderLine(
                line_id=1,
                order_id=456,
                item_id=10,
                actual_servings=1.0,
                stated_price=5.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=5.00,
            )

            item1 = Item(
                item_id=10,
                category_id=5,
                name_id=100,
                calories=100.0,
                protein_g=10.0,
                sodium_mcg=200.0,
                total_fat_g=5.0,
            )

            category = Category(category_id=5, category_name="Produce")
            product_name = MagicMock(name_text="Apples")

            tracked_nutrients = [
                "Calories",
                "Protein",
                "Sodium",
                "Total Fat",
            ]

            MockLinesRepo.return_value.get_order_lines.return_value = [line1]
            MockItemsRepo.return_value.get_item.return_value = item1
            MockCatRepo.return_value.get_category.return_value = category
            MockTrackedRepo.return_value.get_tracked_nutrients.return_value = (
                tracked_nutrients
            )
            MockNamesRepo.return_value.get_product_name.return_value = (
                product_name
            )
            MockDbPath.return_value = Path(tmpdir) / "foodlog.db"

            root = tk.Tk()
            try:
                window = NutritionSummaryWindow(root, order_id=456)
                window._export_csv()

                header_arg = MockExport.call_args[0][1]
                assert header_arg == [
                    "Category",
                    "Item",
                    "Blocks",
                    "Servings",
                    "Calories",
                    "Protein",
                    "Sodium",
                    "Total Fat",
                    "Ratio1",
                    "Ratio2",
                ]

                window.destroy()
            finally:
                root.destroy()


def test_nutrition_summary_window_csv_export_multiple_categories() -> None:
    """CSV export with multiple categories includes category subtotals."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".TrackedNutrientsRepository"
        ) as MockTrackedRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".export_rows_to_csv"
        ) as MockExport, patch(
            "foodlog.gui.windows.nutrition_summary_window.messagebox"
        ), patch(
            "foodlog.gui.windows.nutrition_summary_window.get_database_path"
        ) as MockDbPath:

            line1 = OrderLine(
                line_id=1,
                order_id=456,
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
                order_id=456,
                item_id=20,
                actual_servings=1.0,
                stated_price=10.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=10.00,
            )

            item1 = Item(
                item_id=10,
                category_id=5,
                name_id=100,
                calories=100.0,
                protein_g=10.0,
                sodium_mcg=200.0,
                total_fat_g=5.0,
            )
            item2 = Item(
                item_id=20,
                category_id=6,
                name_id=101,
                calories=150.0,
                protein_g=15.0,
                sodium_mcg=300.0,
                total_fat_g=8.0,
            )

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
            MockTrackedRepo.return_value.get_tracked_nutrients.return_value = [
                "Calories",
                "Protein",
            ]
            MockNamesRepo.return_value.get_product_name.side_effect = (
                lambda id: (
                    product_name1 if id == 100 else product_name2
                    if id == 101 else None
                )
            )
            MockDbPath.return_value = Path(tmpdir) / "foodlog.db"

            root = tk.Tk()
            try:
                window = NutritionSummaryWindow(root, order_id=456)
                window._export_csv()

                rows_arg = MockExport.call_args[0][2]

                assert len(rows_arg) == 5
                assert rows_arg[0][0] == "Produce"
                assert rows_arg[0][1] == "Apples"
                assert rows_arg[1][0] == "Produce"
                assert rows_arg[1][1] == "Subtotal"
                assert rows_arg[2][0] == "Meat"
                assert rows_arg[2][1] == "Chicken"
                assert rows_arg[3][0] == "Meat"
                assert rows_arg[3][1] == "Subtotal"
                assert rows_arg[4][0] == ""
                assert rows_arg[4][1] == "GRAND TOTAL"

                window.destroy()
            finally:
                root.destroy()


def test_nutrition_summary_window_csv_export_missing_product_name() -> None:
    """CSV export handles missing product names."""
    with tempfile.TemporaryDirectory() as tmpdir:
        with patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".OrderLinesRepository"
        ) as MockLinesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ItemsRepository"
        ) as MockItemsRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".CategoriesRepository"
        ) as MockCatRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".TrackedNutrientsRepository"
        ) as MockTrackedRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".ProductNamesRepository"
        ) as MockNamesRepo, patch(
            "foodlog.gui.windows.nutrition_summary_window"
            ".export_rows_to_csv"
        ) as MockExport, patch(
            "foodlog.gui.windows.nutrition_summary_window.messagebox"
        ), patch(
            "foodlog.gui.windows.nutrition_summary_window.get_database_path"
        ) as MockDbPath:

            line1 = OrderLine(
                line_id=1,
                order_id=456,
                item_id=10,
                actual_servings=1.0,
                stated_price=5.00,
                sale=0.0,
                discount=0.0,
                coupon=0.0,
                net_price=5.00,
            )

            item1 = Item(
                item_id=10,
                category_id=5,
                name_id=100,
                calories=100.0,
                protein_g=10.0,
            )

            category = Category(category_id=5, category_name="Produce")

            MockLinesRepo.return_value.get_order_lines.return_value = [line1]
            MockItemsRepo.return_value.get_item.return_value = item1
            MockCatRepo.return_value.get_category.return_value = category
            MockTrackedRepo.return_value.get_tracked_nutrients.return_value = [
                "Calories",
                "Protein",
            ]
            MockNamesRepo.return_value.get_product_name.return_value = None
            MockDbPath.return_value = Path(tmpdir) / "foodlog.db"

            root = tk.Tk()
            try:
                window = NutritionSummaryWindow(root, order_id=456)
                window._export_csv()

                rows_arg = MockExport.call_args[0][2]
                assert rows_arg[0][1] == "Item #10"

                window.destroy()
            finally:
                root.destroy()


def test_nutrition_summary_window_csv_export_error() -> None:
    """CSV export error shows error messagebox."""
    with patch(
        "foodlog.gui.windows.nutrition_summary_window"
        ".OrderLinesRepository"
    ) as MockLinesRepo, patch(
        "foodlog.gui.windows.nutrition_summary_window"
        ".ItemsRepository"
    ) as MockItemsRepo, patch(
        "foodlog.gui.windows.nutrition_summary_window"
        ".CategoriesRepository"
    ) as MockCatRepo, patch(
        "foodlog.gui.windows.nutrition_summary_window"
        ".TrackedNutrientsRepository"
    ) as MockTrackedRepo, patch(
        "foodlog.gui.windows.nutrition_summary_window"
        ".ProductNamesRepository"
    ) as MockNamesRepo, patch(
        "foodlog.gui.windows.nutrition_summary_window.messagebox"
    ) as MockMsgbox:

        line1 = OrderLine(
            line_id=1,
            order_id=456,
            item_id=10,
            actual_servings=1.0,
            stated_price=5.00,
            sale=0.0,
            discount=0.0,
            coupon=0.0,
            net_price=5.00,
        )

        item1 = Item(
            item_id=10,
            category_id=5,
            name_id=100,
            calories=100.0,
            protein_g=10.0,
        )

        category = Category(category_id=5, category_name="Produce")
        product_name = MagicMock(name_text="Apples")

        MockLinesRepo.return_value.get_order_lines.return_value = [line1]
        MockItemsRepo.return_value.get_item.return_value = item1
        MockCatRepo.return_value.get_category.return_value = category
        MockTrackedRepo.return_value.get_tracked_nutrients.return_value = [
            "calories",
            "protein",
        ]
        MockNamesRepo.return_value.get_product_name.return_value = (
            product_name
        )

        root = tk.Tk()
        try:
            window = NutritionSummaryWindow(root, order_id=456)

            with patch(
                "foodlog.gui.windows.nutrition_summary_window"
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
