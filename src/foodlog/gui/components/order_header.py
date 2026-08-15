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
        self.date_entry: tk.Entry | None = None
        self.is_delivery_check: tk.Checkbutton | None = None
        self.status_combo: tk.ttk.Combobox | None = None
        self._layout()

    def _layout(self) -> None:
        """Build header layout."""
        row = tk.Frame(self.frame)
        row.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(row, text="Order Date:").pack(side=tk.LEFT, padx=5)
        self.date_entry = tk.Entry(row, textvariable=self.order_date_var, width=12)
        self.date_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(row, text="Delivery:").pack(side=tk.LEFT, padx=20)
        self.is_delivery_check = tk.Checkbutton(row, variable=self.is_delivery_var)
        self.is_delivery_check.pack(side=tk.LEFT, padx=5)

        tk.Label(row, text="Status:").pack(side=tk.LEFT, padx=20)
        self.status_combo = tk.ttk.Combobox(
            row,
            textvariable=self.status_var,
            values=["planning", "ordered", "delivered", "reconciled"],
            width=12
        )
        self.status_combo.pack(side=tk.LEFT, padx=5)

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

    def set_locked(self, locked: bool) -> None:
        """Disable/enable editable widgets (except status).

        Parameters
        ----------
        locked : bool
            If True, disable all editable widgets except the status
            Combobox. If False, enable them.
        """
        state = tk.DISABLED if locked else tk.NORMAL

        if self.date_entry:
            self.date_entry.config(state=state)
        if self.is_delivery_check:
            self.is_delivery_check.config(state=state)
