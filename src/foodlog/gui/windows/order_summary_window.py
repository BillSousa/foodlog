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
        categories_repo = CategoriesRepository()
        orders_repo = OrdersRepository()
        product_names_repo = ProductNamesRepository()

        lines = lines_repo.get_order_lines(self.order_id)
        order = orders_repo.get_order(self.order_id)

        grouped = group_lines_by_category(
            lines, items_repo, categories_repo
        )

        subtotal = 0.0
        for category_key in grouped:
            tk.Label(
                scrollable,
                text=category_key,
                font=("Arial", 10, "bold"),
            ).pack(anchor=tk.W, padx=10, pady=(10, 5))

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

                text = (
                    f"  {name_text} x{line.actual_servings:.1f}: "
                    f"${line.stated_price:.2f} → "
                    f"${line.net_price:.2f}"
                )
                tk.Label(scrollable, text=text, justify=tk.LEFT).pack(
                    anchor=tk.W, padx=10, pady=2
                )

                category_subtotal += line.net_price

            subtotal += category_subtotal
            tk.Label(
                scrollable,
                text=f"  Subtotal: ${category_subtotal:.2f}",
                font=("Arial", 9, "bold"),
            ).pack(anchor=tk.W, padx=10, pady=(0, 5))

        tk.Label(scrollable, text="", font=("Arial", 1)).pack()

        tk.Label(
            scrollable,
            text=f"Subtotal: ${subtotal:.2f}",
            font=("Arial", 10, "bold"),
        ).pack(anchor=tk.W, padx=10, pady=5)

        delivery = order.delivery_charge if order else 0.0
        tip = order.tip if order else 0.0
        tax = order.tax if order else 0.0
        coupon = order.order_level_coupon if order else 0.0

        tk.Label(
            scrollable,
            text=(
                f"Delivery: ${delivery:.2f}\nTip: ${tip:.2f}\n"
                f"Tax: ${tax:.2f}\nCoupon: ${coupon:.2f}"
            ),
            justify=tk.LEFT,
        ).pack(anchor=tk.W, padx=10, pady=5)

        grand_total = subtotal + delivery + tip + tax + coupon
        tk.Label(
            scrollable,
            text=f"TOTAL: ${grand_total:.2f}",
            font=("Arial", 11, "bold"),
        ).pack(anchor=tk.W, padx=10, pady=10)

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

    def _export_csv(self) -> None:
        """Export order summary to CSV."""
        try:
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()
            categories_repo = CategoriesRepository()
            product_names_repo = ProductNamesRepository()

            lines = lines_repo.get_order_lines(self.order_id)
            grouped = group_lines_by_category(
                lines, items_repo, categories_repo
            )

            csv_path = (
                get_database_path().parent
                / f"order_{self.order_id}_money_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            header = [
                "Category",
                "Item",
                "Servings",
                "Stated Price",
                "Sale",
                "Discount",
                "Coupon",
                "Net Price",
            ]
            rows = []
            for category_key in grouped:
                for line, item in grouped[category_key]:
                    product_name = product_names_repo.get_product_name(
                        item.name_id
                    )
                    name_text = (
                        product_name.name_text
                        if product_name
                        else f"Item #{item.item_id}"
                    )
                    rows.append(
                        [
                            category_key,
                            name_text,
                            line.actual_servings,
                            line.stated_price,
                            line.sale,
                            line.discount,
                            line.coupon,
                            line.net_price,
                        ]
                    )

            export_rows_to_csv(csv_path, header, rows)

            messagebox.showinfo("Export", f"Saved to {csv_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
