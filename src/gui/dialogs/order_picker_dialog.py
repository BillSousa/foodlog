import tkinter as tk
from tkinter import messagebox

from src.repository.orders_repository import OrdersRepository


class OrderPickerDialog(tk.Toplevel):
    """Dialog for selecting an order or creating new."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize order picker dialog."""
        super().__init__(parent)
        self.title("Select an Order to Manage")
        self.geometry("500x400")
        self.selected_order_id: int | None = None
        self._layout()

    def _layout(self) -> None:
        """Build dialog layout."""
        new_btn = tk.Button(
            self,
            text="+ Create New Order",
            command=self._on_create_new
        )
        new_btn.pack(pady=10)

        tk.Label(self, text="Existing Orders:").pack(anchor=tk.W, padx=20)

        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        self._load_orders()

        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=10)

        open_btn = tk.Button(
            btn_frame,
            text="Open Selected Order",
            command=self._on_open
        )
        open_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=self.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _load_orders(self) -> None:
        """Load orders into listbox."""
        repo = OrdersRepository()
        orders = repo.list_orders()

        for order in orders:
            text = (
                f"Order #{order.order_id}: {order.order_date} "
                f"({'Delivery' if order.is_delivery else 'Pickup'}) "
                f"— {order.status}"
            )
            self.listbox.insert(tk.END, text)

    def _on_create_new(self) -> None:
        """Create new order."""
        messagebox.showinfo("TODO", "Order creation (Phase 8)")
        self.destroy()

    def _on_open(self) -> None:
        """Open selected order."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Select", "Please select an order")
            return

        index = selection[0]
        messagebox.showinfo("TODO", f"Open order {index + 1} (Phase 8)")
        self.destroy()
