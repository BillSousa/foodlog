import tkinter as tk
import tkinter.ttk
from datetime import datetime


class OrderHeader:
    """Order header with date, delivery, and status."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize order header."""
        self.frame = tk.Frame(parent)
        self.order_date_var = tk.StringVar(
            value=datetime.now().strftime("%Y-%m-%d")
        )
        self.is_delivery_var = tk.BooleanVar(value=False)
        self.status_var = tk.StringVar(value="planning")
        self._layout()

    def _layout(self) -> None:
        """Build header layout."""
        row = tk.Frame(self.frame)
        row.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(row, text="Order Date:").pack(side=tk.LEFT, padx=5)
        date_entry = tk.Entry(row, textvariable=self.order_date_var, width=12)
        date_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(row, text="Delivery:").pack(side=tk.LEFT, padx=20)
        tk.Checkbutton(row, variable=self.is_delivery_var).pack(
            side=tk.LEFT, padx=5
        )

        tk.Label(row, text="Status:").pack(side=tk.LEFT, padx=20)
        status_combo = tk.ttk.Combobox(
            row,
            textvariable=self.status_var,
            values=["planning", "ordered", "delivered", "reconciled"],
            width=12
        )
        status_combo.pack(side=tk.LEFT, padx=5)

    def get_frame(self) -> tk.Frame:
        """Return frame."""
        return self.frame

    def get_values(self) -> dict:
        """Get header values."""
        return {
            "order_date": self.order_date_var.get(),
            "is_delivery": 1 if self.is_delivery_var.get() else 0,
            "status": self.status_var.get(),
        }
