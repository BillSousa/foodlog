import tkinter as tk
from tkinter import messagebox

from src.calculations.ratios import ratio1, ratio2
from src.gui.components.item_search_filter import ItemSearchFilter
from src.gui.components.order_header import OrderHeader
from src.gui.components.order_totals import OrderTotals
from src.models.fact_orders import Order
from src.repository.items_repository import ItemsRepository
from src.repository.orders_repository import OrdersRepository
from src.repository.settings_repository import SettingsRepository


class OrderCreationWindow(tk.Toplevel):
    """Order creation and planning screen."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize order creation window."""
        super().__init__(parent)
        self.title("Create Order")
        self.geometry("900x700")

        self.order_items: list[dict] = []
        self.order_id: int | None = None

        settings_repo = SettingsRepository()
        cal_target = float(
            settings_repo.get_setting("cal_per_day_target") or "2000"
        )

        self._layout(cal_target)

    def _layout(self, cal_target: float) -> None:
        """Build order creation layout."""
        self.header = OrderHeader(self)
        self.header.get_frame().pack(fill=tk.X)

        self.search_filter = ItemSearchFilter(self)
        self.search_filter.get_frame().pack(fill=tk.X, padx=10, pady=10)

        grid_frame = tk.LabelFrame(self, text="Order Items")
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.listbox = tk.Listbox(grid_frame, height=10)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        add_btn = tk.Button(
            self,
            text="Add Item",
            command=self._add_item
        )
        add_btn.pack(pady=5)

        self.totals = OrderTotals(self, cal_target)
        self.totals.get_frame().pack(fill=tk.X, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        save_btn = tk.Button(btn_frame, text="Save Draft", command=self._save)
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _add_item(self) -> None:
        """Add item to order (placeholder for full implementation)."""
        messagebox.showinfo(
            "TODO",
            "Item picker implementation (Phase 8 Part 2)"
        )

    def _save(self) -> None:
        """Save order as draft."""
        if not self.order_items:
            messagebox.showwarning("Empty", "Add at least one item")
            return

        header = self.header.get_values()
        order = Order(
            order_date=header["order_date"],
            is_delivery=header["is_delivery"],
            status="planning"
        )

        repo = OrdersRepository()
        self.order_id = repo.create_order(order)

        messagebox.showinfo("Success", f"Order #{self.order_id} saved")
        self.destroy()
