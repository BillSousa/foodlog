import tkinter as tk
from tkinter import messagebox
from typing import Callable

from foodlog.repository.items_repository import ItemsRepository
from foodlog.validation.constraints import ValidationError, validate_price


class PriceUpdatePopup(tk.Toplevel):
    """Popup dialog for updating an item's price in dim_items."""

    def __init__(
        self,
        parent: tk.Widget,
        item_id: int,
        current_price: float,
        on_saved: Callable[[float], None],
    ) -> None:
        """
        Initialize price update popup.

        Parameters
        ----------
        parent : tk.Widget
            Parent widget
        item_id : int
            ID of the item whose price to update
        current_price : float
            Current price, used to pre-fill the entry
        on_saved : Callable[[float], None]
            Callback invoked with the new price after successful save
        """
        super().__init__(parent)
        self.title("Update Item Price")
        self.geometry("300x150")
        self.item_id = item_id
        self.current_price = current_price
        self.on_saved = on_saved

        self._layout()
        self.transient(parent)
        try:
            self.grab_set()
        except tk.TclError:
            # In headless/test environments, grab may fail if window
            # isn't fully viewable yet. Continue gracefully.
            pass

    def _layout(self) -> None:
        """Build dialog layout."""
        frame = tk.Frame(self, padx=10, pady=10)
        frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(frame, text="Current Price:").pack(anchor=tk.W, pady=5)
        self.price_label = tk.Label(
            frame, text=f"${self.current_price:.2f}"
        )
        self.price_label.pack(anchor=tk.W, pady=5)

        tk.Label(frame, text="New Price:").pack(anchor=tk.W, pady=5)
        self.price_entry = tk.Entry(frame, width=15)
        self.price_entry.insert(0, str(self.current_price))
        self.price_entry.pack(anchor=tk.W, pady=5)

        button_frame = tk.Frame(frame)
        button_frame.pack(pady=10)

        tk.Button(
            button_frame,
            text="Save",
            command=self._on_save,
            width=10,
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Cancel",
            command=self.destroy,
            width=10,
        ).pack(side=tk.LEFT, padx=5)

    def _on_save(self) -> None:
        """Validate, save, and close."""
        try:
            new_price = float(self.price_entry.get())
            validate_price(new_price)

            ItemsRepository().update_item_price(
                self.item_id, new_price
            )
            self.on_saved(new_price)
            self.destroy()
        except ValueError:
            messagebox.showerror(
                "Invalid Input", "Price must be a number."
            )
        except ValidationError as e:
            messagebox.showerror("Invalid Price", str(e))
