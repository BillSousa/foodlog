import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from foodlog.calculations.ratios import ratio1, ratio2
from foodlog.database.connection import get_database_path
from foodlog.gui.helpers.csv_exporter import export_rows_to_csv
from foodlog.gui.helpers.group_lines_by_category import (
    group_lines_by_category,
)
from foodlog.repository.categories_repository import CategoriesRepository
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.order_lines_repository import OrderLinesRepository
from foodlog.repository.product_names_repository import ProductNamesRepository
from foodlog.repository.tracked_nutrients_repository import (
    TrackedNutrientsRepository,
)


class NutritionSummaryWindow(tk.Toplevel):
    """Order Nutrition Summary — nutrient matrix by item/category."""

    def __init__(self, parent: tk.Widget, order_id: int) -> None:
        """Initialize nutrition summary window."""
        super().__init__(parent)
        self.title(f"Order #{order_id} — Nutrition Summary")
        self.geometry("1000x750")
        self.order_id = order_id
        self._layout()

    def _layout(self) -> None:
        """Build nutrition summary layout."""
        title = tk.Label(
            self,
            text=f"Order #{self.order_id} — Nutrition Summary",
            font=("Arial", 12, "bold"),
        )
        title.pack(pady=10)

        canvas_frame = tk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(
            canvas_frame, orient=tk.VERTICAL, command=canvas.yview
        )
        scrollable = tk.Frame(canvas)

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        lines_repo = OrderLinesRepository()
        items_repo = ItemsRepository()
        tracked_repo = TrackedNutrientsRepository()
        categories_repo = CategoriesRepository()
        product_names_repo = ProductNamesRepository()

        lines = lines_repo.get_order_lines(self.order_id)
        tracked_list = tracked_repo.get_tracked_nutrients()
        grouped = group_lines_by_category(
            lines, items_repo, categories_repo
        )

        header_cols = ["Item", "Servings"] + tracked_list + [
            "Ratio1",
            "Ratio2",
        ]

        self._build_table_header(scrollable, header_cols)

        order_totals = {nutrient: 0.0 for nutrient in tracked_list}
        order_totals["cost"] = 0.0

        for category_key in grouped:
            tk.Label(
                scrollable,
                text=category_key,
                font=("Arial", 10, "bold"),
            ).pack(anchor=tk.W, padx=10, pady=(10, 5))

            category_totals = {nutrient: 0.0 for nutrient in tracked_list}
            category_totals["cost"] = 0.0

            for line, item in grouped[category_key]:
                product_name = product_names_repo.get_product_name(
                    item.name_id
                )
                name_text = (
                    product_name.name_text
                    if product_name
                    else f"Item #{item.item_id}"
                )

                nutrient_vals = {}
                for nutrient in tracked_list:
                    attr = f"{nutrient.lower().replace(' ', '_')}"
                    val = getattr(item, attr, 0.0)
                    computed = val * line.actual_servings
                    nutrient_vals[nutrient] = computed
                    category_totals[nutrient] += computed
                    order_totals[nutrient] += computed

                category_totals["cost"] += line.net_price
                order_totals["cost"] += line.net_price

                item_calories = nutrient_vals.get("calories", 0.0)
                item_cost = line.net_price
                item_sodium = nutrient_vals.get("sodium", 0.0)
                item_fat = nutrient_vals.get("total_fat", 0.0)
                item_ratio1 = (
                    ratio1(item_calories, item_cost, item_sodium)
                    if item_cost > 0
                    else 0.0
                )
                item_ratio2 = (
                    ratio2(
                        item_calories,
                        item_cost,
                        item_sodium,
                        item_fat,
                    )
                    if item_cost > 0
                    else 0.0
                )

                row_data = [
                    f"  {name_text}",
                    f"{line.actual_servings:.1f}",
                ]
                for nutrient in tracked_list:
                    row_data.append(f"{nutrient_vals[nutrient]:.1f}")
                row_data.extend([f"{item_ratio1:.2f}", f"{item_ratio2:.2f}"])

                self._build_table_row(scrollable, row_data)

            cat_calories = category_totals.get("calories", 0.0)
            cat_cost = category_totals["cost"]
            cat_sodium = category_totals.get("sodium", 0.0)
            cat_fat = category_totals.get("total_fat", 0.0)
            cat_ratio1 = (
                ratio1(cat_calories, cat_cost, cat_sodium)
                if cat_cost > 0
                else 0.0
            )
            cat_ratio2 = (
                ratio2(cat_calories, cat_cost, cat_sodium, cat_fat)
                if cat_cost > 0
                else 0.0
            )

            cat_data = ["  Subtotal", ""]
            for nutrient in tracked_list:
                cat_data.append(f"{category_totals[nutrient]:.1f}")
            cat_data.extend([f"{cat_ratio1:.2f}", f"{cat_ratio2:.2f}"])

            self._build_table_row(
                scrollable, cat_data, bold=True, pady=(0, 5)
            )

        tk.Label(scrollable, text="", font=("Arial", 1)).pack()

        ord_calories = order_totals.get("calories", 0.0)
        ord_cost = order_totals["cost"]
        ord_sodium = order_totals.get("sodium", 0.0)
        ord_fat = order_totals.get("total_fat", 0.0)
        ord_ratio1 = (
            ratio1(ord_calories, ord_cost, ord_sodium)
            if ord_cost > 0
            else 0.0
        )
        ord_ratio2 = (
            ratio2(ord_calories, ord_cost, ord_sodium, ord_fat)
            if ord_cost > 0
            else 0.0
        )

        grand_data = ["GRAND TOTAL", ""]
        for nutrient in tracked_list:
            grand_data.append(f"{order_totals[nutrient]:.1f}")
        grand_data.extend([f"{ord_ratio1:.2f}", f"{ord_ratio2:.2f}"])

        self._build_table_row(scrollable, grand_data, bold=True, pady=10)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        export_btn = tk.Button(
            btn_frame, text="Export to CSV", command=self._export_csv
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _build_table_header(
        self, parent: tk.Widget, columns: list[str]
    ) -> None:
        """Build table header with column names.

        Parameters
        ----------
        parent : tk.Widget
            Parent widget
        columns : list[str]
            Column header names
        """
        header_frame = tk.Frame(parent)
        header_frame.pack(anchor=tk.W, padx=10, pady=5)

        col_widths = self._get_column_widths(columns)
        for i, col in enumerate(columns):
            label = tk.Label(
                header_frame,
                text=col,
                font=("Courier", 8, "bold"),
                width=col_widths[i],
                anchor=tk.W if i == 0 else tk.E,
            )
            label.pack(side=tk.LEFT, padx=2)

    def _build_table_row(
        self,
        parent: tk.Widget,
        row_data: list[str],
        bold: bool = False,
        pady: tuple[int, int] | int = 2,
    ) -> None:
        """Build table row with aligned columns.

        Parameters
        ----------
        parent : tk.Widget
            Parent widget
        row_data : list[str]
            Column values
        bold : bool
            If True, use bold font
        pady : tuple or int
            Y padding
        """
        row_frame = tk.Frame(parent)
        row_frame.pack(anchor=tk.W, padx=10, pady=pady)

        col_widths = self._get_column_widths(
            ["Item"] + ["Servings"] + ["Col"] * (len(row_data) - 2)
        )

        font_style = ("Courier", 8, "bold") if bold else ("Courier", 8)

        for i, val in enumerate(row_data):
            is_first = i == 0
            label = tk.Label(
                row_frame,
                text=val,
                font=font_style,
                width=col_widths[i],
                anchor=tk.W if is_first else tk.E,
            )
            label.pack(side=tk.LEFT, padx=2)

    def _get_column_widths(self, columns: list[str]) -> list[int]:
        """Calculate reasonable column widths.

        Parameters
        ----------
        columns : list[str]
            Column headers

        Returns
        -------
        list[int]
            Width for each column
        """
        widths = []
        for i, col in enumerate(columns):
            if i == 0:
                widths.append(20)
            else:
                widths.append(12)
        return widths

    def _export_csv(self) -> None:
        """Export nutrition summary to CSV."""
        try:
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()
            tracked_repo = TrackedNutrientsRepository()
            categories_repo = CategoriesRepository()
            product_names_repo = ProductNamesRepository()

            lines = lines_repo.get_order_lines(self.order_id)
            tracked_list = tracked_repo.get_tracked_nutrients()
            grouped = group_lines_by_category(
                lines, items_repo, categories_repo
            )

            csv_path = (
                get_database_path().parent
                / f"order_{self.order_id}_nutrition_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            header = [
                "Category",
                "Item",
                "Servings",
            ] + tracked_list + ["Ratio1", "Ratio2"]

            rows = []
            order_totals = {nutrient: 0.0 for nutrient in tracked_list}
            order_totals["cost"] = 0.0

            for category_key in grouped:
                category_totals = {
                    nutrient: 0.0 for nutrient in tracked_list
                }
                category_totals["cost"] = 0.0

                for line, item in grouped[category_key]:
                    product_name = product_names_repo.get_product_name(
                        item.name_id
                    )
                    name_text = (
                        product_name.name_text
                        if product_name
                        else f"Item #{item.item_id}"
                    )

                    nutrient_vals = {}
                    for nutrient in tracked_list:
                        attr = f"{nutrient.lower().replace(' ', '_')}"
                        val = getattr(item, attr, 0.0)
                        computed = val * line.actual_servings
                        nutrient_vals[nutrient] = computed
                        category_totals[nutrient] += computed
                        order_totals[nutrient] += computed

                    category_totals["cost"] += line.net_price
                    order_totals["cost"] += line.net_price

                    item_calories = nutrient_vals.get("calories", 0.0)
                    item_cost = line.net_price
                    item_sodium = nutrient_vals.get("sodium", 0.0)
                    item_fat = nutrient_vals.get("total_fat", 0.0)
                    item_ratio1 = (
                        ratio1(item_calories, item_cost, item_sodium)
                        if item_cost > 0
                        else 0.0
                    )
                    item_ratio2 = (
                        ratio2(
                            item_calories,
                            item_cost,
                            item_sodium,
                            item_fat,
                        )
                        if item_cost > 0
                        else 0.0
                    )

                    row = [
                        category_key,
                        name_text,
                        line.actual_servings,
                    ]
                    for nutrient in tracked_list:
                        row.append(nutrient_vals[nutrient])
                    row.extend([item_ratio1, item_ratio2])
                    rows.append(row)

                cat_calories = category_totals.get("calories", 0.0)
                cat_cost = category_totals["cost"]
                cat_sodium = category_totals.get("sodium", 0.0)
                cat_fat = category_totals.get("total_fat", 0.0)
                cat_ratio1 = (
                    ratio1(cat_calories, cat_cost, cat_sodium)
                    if cat_cost > 0
                    else 0.0
                )
                cat_ratio2 = (
                    ratio2(cat_calories, cat_cost, cat_sodium, cat_fat)
                    if cat_cost > 0
                    else 0.0
                )

                cat_row = [
                    category_key,
                    "Subtotal",
                    "",
                ]
                for nutrient in tracked_list:
                    cat_row.append(category_totals[nutrient])
                cat_row.extend([cat_ratio1, cat_ratio2])
                rows.append(cat_row)

            ord_calories = order_totals.get("calories", 0.0)
            ord_cost = order_totals["cost"]
            ord_sodium = order_totals.get("sodium", 0.0)
            ord_fat = order_totals.get("total_fat", 0.0)
            ord_ratio1 = (
                ratio1(ord_calories, ord_cost, ord_sodium)
                if ord_cost > 0
                else 0.0
            )
            ord_ratio2 = (
                ratio2(ord_calories, ord_cost, ord_sodium, ord_fat)
                if ord_cost > 0
                else 0.0
            )

            grand_row = [
                "",
                "GRAND TOTAL",
                "",
            ]
            for nutrient in tracked_list:
                grand_row.append(order_totals[nutrient])
            grand_row.extend([ord_ratio1, ord_ratio2])
            rows.append(grand_row)

            export_rows_to_csv(csv_path, header, rows)

            messagebox.showinfo("Export", f"Saved to {csv_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
