import tkinter as tk
from datetime import datetime
from pathlib import Path
from tkinter import messagebox

from foodlog.database.connection import get_database_path
from foodlog.gui.helpers.csv_exporter import export_rows_to_csv
from foodlog.gui.helpers.group_lines_by_category import (
    group_lines_by_category,
)
from foodlog.repository.categories_repository import CategoriesRepository
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.order_lines_repository import OrderLinesRepository
from foodlog.repository.orders_repository import OrdersRepository
from foodlog.repository.product_names_repository import ProductNamesRepository


class OrderSummaryWindow(tk.Toplevel):
    """Order Summary (Money) — itemized by category."""

    def __init__(self, parent: tk.Widget, order_id: int) -> None:
        """Initialize order summary window."""
        super().__init__(parent)
        self.title(f"Order #{order_id} — Money Summary")
        self.geometry("900x750")
        self.order_id = order_id
        self._layout()

    def _layout(self) -> None:
        """Build summary layout."""
        title = tk.Label(
            self,
            text=f"Order #{self.order_id} — Money Summary",
            font=("Arial", 24, "bold"),
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
        categories_repo = CategoriesRepository()
        orders_repo = OrdersRepository()
        product_names_repo = ProductNamesRepository()

        lines = lines_repo.get_order_lines(self.order_id)
        order = orders_repo.get_order(self.order_id)

        grouped = group_lines_by_category(
            lines, items_repo, categories_repo
        )

        grid_frame = tk.Frame(scrollable)
        grid_frame.pack(fill=tk.X, padx=10, pady=5)

        grid_frame.columnconfigure(0, minsize=240)
        grid_frame.columnconfigure(1, minsize=120)
        grid_frame.columnconfigure(2, minsize=120)
        grid_frame.columnconfigure(3, minsize=120)
        grid_frame.columnconfigure(4, minsize=100)
        grid_frame.columnconfigure(5, minsize=100)
        grid_frame.columnconfigure(6, minsize=100)
        grid_frame.columnconfigure(7, minsize=120)

        self.grid_row = 0

        header_cols = [
            "Item",
            "Blocks",
            "Servings",
            "Stated Price",
            "Sale",
            "Discount",
            "Coupon",
            "Net Price",
        ]
        self._build_table_header(grid_frame, header_cols)

        subtotal = 0.0
        for category_key in grouped:
            cat_label = tk.Label(
                grid_frame,
                text=category_key,
                font=("Arial", 20, "bold"),
                anchor=tk.W,
            )
            cat_label.grid(
                row=self.grid_row,
                column=0,
                columnspan=5,
                sticky="w",
                pady=(10, 5),
            )
            self.grid_row += 1

            category_subtotal = 0.0
            for line, item in grouped[category_key]:
                product_name = product_names_repo.get_product_name(
                    item.name_id
                )
                name_text = (
                    product_name.name_text
                    if product_name
                    else f"Item #{item.item_id}"
                )

                blocks = (
                    line.actual_servings / item.servings_per_block
                    if item.servings_per_block > 0
                    else 0.0
                )
                row_data = [
                    name_text,
                    f"{blocks:.2f}",
                    f"{line.actual_servings:.1f}",
                    f"${line.stated_price:.2f}",
                    f"${line.sale:.2f}",
                    f"${line.discount:.2f}",
                    f"${line.coupon:.2f}",
                    f"${line.net_price:.2f}",
                ]
                self._build_table_row(grid_frame, row_data)

                category_subtotal += line.net_price

            subtotal += category_subtotal
            cat_data = [
                "Subtotal",
                "",
                "",
                "",
                "",
                "",
                "",
                f"${category_subtotal:.2f}",
            ]
            self._build_table_row(grid_frame, cat_data, bold=True, pady=5)

        self.grid_row += 1

        subtotal_label = tk.Label(
            grid_frame,
            text="Subtotal",
            font=("Arial", 20, "bold"),
            anchor=tk.W,
        )
        subtotal_label.grid(
            row=self.grid_row,
            column=0,
            sticky="w",
            padx=2,
            pady=5,
        )
        subtotal_amount = tk.Label(
            grid_frame,
            text=f"${subtotal:.2f}",
            font=("Arial", 20, "bold"),
            anchor=tk.E,
        )
        subtotal_amount.grid(
            row=self.grid_row,
            column=7,
            sticky="e",
            padx=2,
            pady=5,
        )
        self.grid_row += 1

        delivery = order.delivery_charge if order else 0.0
        tip = order.tip if order else 0.0
        tax = order.tax if order else 0.0
        coupon = order.order_level_coupon if order else 0.0

        charges = [
            ["Delivery", "", "", "", "", "", "", f"${delivery:.2f}"],
            ["Tip", "", "", "", "", "", "", f"${tip:.2f}"],
            ["Tax", "", "", "", "", "", "", f"${tax:.2f}"],
            ["Coupon", "", "", "", "", "", "", f"${coupon:.2f}"],
        ]
        for charge_data in charges:
            self._build_table_row(grid_frame, charge_data, pady=2)

        grand_total = subtotal + delivery + tip + tax + coupon
        total_label = tk.Label(
            grid_frame,
            text="TOTAL",
            font=("Arial", 22, "bold"),
            anchor=tk.W,
        )
        total_label.grid(
            row=self.grid_row,
            column=0,
            sticky="w",
            padx=2,
            pady=10,
        )
        total_amount = tk.Label(
            grid_frame,
            text=f"${grand_total:.2f}",
            font=("Arial", 22, "bold"),
            anchor=tk.E,
        )
        total_amount.grid(
            row=self.grid_row,
            column=7,
            sticky="e",
            padx=2,
            pady=10,
        )
        self.grid_row += 1

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
        for i, col in enumerate(columns):
            label = tk.Label(
                parent,
                text=col,
                font=("Courier", 16, "bold"),
                anchor=tk.W if i == 0 else tk.E,
            )
            label.grid(
                row=self.grid_row,
                column=i,
                sticky="w" if i == 0 else "e",
                padx=2,
            )
        self.grid_row += 1

    def _build_table_row(
        self,
        parent: tk.Widget,
        row_data: list[str],
        bold: bool = False,
        pady: int | tuple[int, int] = 2,
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
        pady : int or tuple
            Y padding
        """
        font_style = ("Courier", 16, "bold") if bold else ("Courier", 16)

        for i, val in enumerate(row_data):
            is_first = i == 0
            label = tk.Label(
                parent,
                text=val,
                font=font_style,
                anchor=tk.W if is_first else tk.E,
            )
            label.grid(
                row=self.grid_row,
                column=i,
                sticky="w" if is_first else "e",
                padx=2,
                pady=pady,
            )
        self.grid_row += 1


    def _export_csv(self) -> None:
        """Export order summary to CSV."""
        try:
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()
            categories_repo = CategoriesRepository()
            orders_repo = OrdersRepository()
            product_names_repo = ProductNamesRepository()

            lines = lines_repo.get_order_lines(self.order_id)
            order = orders_repo.get_order(self.order_id)
            grouped = group_lines_by_category(
                lines, items_repo, categories_repo
            )

            csv_path = (
                get_database_path().parent
                / f"order_{self.order_id}_money_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            header = [
                "Item",
                "Blocks",
                "Servings",
                "Stated Price",
                "Sale",
                "Discount",
                "Coupon",
                "Net Price",
            ]
            rows = []
            subtotal = 0.0

            for category_key in grouped:
                rows.append([category_key, "", "", "", "", "", "", ""])
                category_subtotal = 0.0

                for line, item in grouped[category_key]:
                    product_name = product_names_repo.get_product_name(
                        item.name_id
                    )
                    name_text = (
                        product_name.name_text
                        if product_name
                        else f"Item #{item.item_id}"
                    )
                    blocks = (
                        line.actual_servings / item.servings_per_block
                        if item.servings_per_block > 0
                        else 0.0
                    )
                    rows.append(
                        [
                            name_text,
                            f"{blocks:.2f}",
                            f"{line.actual_servings:.1f}",
                            f"${line.stated_price:.2f}",
                            f"${line.sale:.2f}",
                            f"${line.discount:.2f}",
                            f"${line.coupon:.2f}",
                            f"${line.net_price:.2f}",
                        ]
                    )
                    category_subtotal += line.net_price

                subtotal += category_subtotal
                rows.append(
                    ["Subtotal", "", "", "", "", "", "", f"${category_subtotal:.2f}"]
                )

            rows.append(["Subtotal", "", "", "", "", "", "", f"${subtotal:.2f}"])
            rows.append(["", "", "", "", "", "", "", ""])

            delivery = order.delivery_charge if order else 0.0
            tip = order.tip if order else 0.0
            tax = order.tax if order else 0.0
            coupon = order.order_level_coupon if order else 0.0

            rows.append(["Delivery", "", "", "", "", "", "", f"${delivery:.2f}"])
            rows.append(["Tip", "", "", "", "", "", "", f"${tip:.2f}"])
            rows.append(["Tax", "", "", "", "", "", "", f"${tax:.2f}"])
            rows.append(["Coupon", "", "", "", "", "", "", f"${coupon:.2f}"])

            grand_total = subtotal + delivery + tip + tax + coupon
            rows.append(["TOTAL", "", "", "", "", "", "", f"${grand_total:.2f}"])

            export_rows_to_csv(csv_path, header, rows)

            messagebox.showinfo("Export", f"Saved to {csv_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
