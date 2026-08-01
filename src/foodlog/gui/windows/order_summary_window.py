import csv
import tkinter as tk
from datetime import datetime
from pathlib import Path

from foodlog.database.connection import get_database_path
from foodlog.repository.order_lines_repository import OrderLinesRepository
from foodlog.repository.product_names_repository import ProductNamesRepository


class OrderSummaryWindow(tk.Toplevel):
    """Order Summary (Money) — itemized by category."""

    def __init__(self, parent: tk.Widget, order_id: int) -> None:
        """Initialize order summary window."""
        super().__init__(parent)
        self.title(f"Order #{order_id} — Money Summary")
        self.geometry("700x600")
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
        lines = lines_repo.get_order_lines(self.order_id)

        total_cost = 0.0

        for line in lines:
            name_text = f"Item #{line.item_id}"
            text = (
                f"{name_text} x{line.actual_servings:.1f}: "
                f"${line.stated_price:.2f} → ${line.net_price:.2f}"
            )
            tk.Label(scrollable, text=text, justify=tk.LEFT).pack(
                anchor=tk.W, padx=10, pady=2
            )
            total_cost += line.net_price

        tk.Label(scrollable, text="", font=("Arial", 1)).pack()

        tk.Label(
            scrollable,
            text=f"Subtotal: ${total_cost:.2f}",
            font=("Arial", 10, "bold"),
        ).pack(anchor=tk.W, padx=10, pady=5)

        tk.Label(
            scrollable,
            text=f"Delivery: $0.00\nTip: $0.00\nTax: $0.00\nCoupon: $0.00",
            justify=tk.LEFT,
        ).pack(anchor=tk.W, padx=10, pady=5)

        tk.Label(
            scrollable,
            text=f"TOTAL: ${total_cost:.2f}",
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
            lines = lines_repo.get_order_lines(self.order_id)

            csv_path = (
                get_database_path().parent
                / f"order_{self.order_id}_money_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "Item ID",
                        "Servings",
                        "Stated Price",
                        "Sale",
                        "Discount",
                        "Coupon",
                        "Net Price",
                    ]
                )
                for line in lines:
                    writer.writerow(
                        [
                            line.item_id,
                            line.actual_servings,
                            line.stated_price,
                            line.sale,
                            line.discount,
                            line.coupon,
                            line.net_price,
                        ]
                    )

            tk.messagebox.showinfo("Export", f"Saved to {csv_path}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Export failed: {e}")
