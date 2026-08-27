import tkinter as tk
from datetime import datetime
from tkinter import messagebox

from foodlog.calculations.on_hand import calculate_on_hand
from foodlog.gui.components.item_search_filter import ItemSearchFilter
from foodlog.gui.helpers.item_filter import filter_items
from foodlog.models.fact_consumption import Consumption
from foodlog.repository.categories_repository import CategoriesRepository
from foodlog.repository.consumption_repository import ConsumptionRepository
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.product_names_repository import ProductNamesRepository
from foodlog.validation.constraints import (
    validate_consumption_on_hand,
    ValidationError,
)


class ConsumptionWindow(tk.Toplevel):
    """Log consumption with on-hand validation."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize consumption logging window."""
        super().__init__(parent)
        self.title("Log Consumption")
        self.geometry("900x750")

        self.entry_date = datetime.today()
        self.consumption_entries: dict[int, dict] = {}

        self._layout()

    def _layout(self) -> None:
        """Build consumption window layout."""
        header = tk.Frame(self)
        header.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(header, text="Entry Date:").pack(side=tk.LEFT)

        date_str = self.entry_date.strftime("%Y-%m-%d")
        date_entry = tk.Entry(header, width=12)
        date_entry.insert(0, date_str)

        def on_date_change(*args):
            try:
                self.entry_date = datetime.strptime(
                    date_entry.get(), "%Y-%m-%d"
                )
            except ValueError:
                messagebox.showerror("Invalid date", "Use YYYY-MM-DD")

        date_entry.pack(side=tk.LEFT, padx=5)
        date_entry.bind('<FocusOut>', on_date_change)

        self.search_filter = ItemSearchFilter(self)
        self.search_filter.get_frame().pack(fill=tk.X, padx=10, pady=10)

        items_frame = tk.LabelFrame(self, text="Items (on-hand > 0)")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.items_container = tk.Frame(items_frame)
        self.items_container.pack(fill=tk.BOTH, expand=True)

        self._populate_items()

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        save_btn = tk.Button(btn_frame, text="Log Consumption", command=self._save)
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _populate_items(self) -> None:
        """Populate list of items with on-hand > 0, filtered by search."""
        for widget in self.items_container.winfo_children():
            widget.destroy()

        items_repo = ItemsRepository()
        all_items = items_repo.list_active_items()

        search_text = self.search_filter.get_search_text()
        selected_cat_names = self.search_filter.get_selected_categories()

        cat_repo = CategoriesRepository()
        all_cats = cat_repo.list_categories()
        cat_map = {c.category_name: c.category_id for c in all_cats}
        selected_cat_ids = [
            cat_map[name] for name in selected_cat_names
            if name in cat_map
        ]

        product_names_repo = ProductNamesRepository()
        filtered_items = filter_items(
            all_items,
            search_text,
            selected_cat_ids,
            product_names_repo,
        )

        visible_count = 0
        for item in filtered_items:
            on_hand = calculate_on_hand(item.item_id)
            if on_hand <= 0:
                continue

            visible_count += 1
            self._add_item_row(item, on_hand)

        if visible_count == 0:
            tk.Label(
                self.items_container,
                text="No items with on-hand > 0",
                fg="gray"
            ).pack(pady=20)

    def _add_item_row(self, item, on_hand: float) -> None:
        """Add item row to consumption grid."""
        row = tk.Frame(self.items_container, relief=tk.SUNKEN, borderwidth=1)
        row.pack(fill=tk.X, pady=2, padx=5)

        product_names_repo = ProductNamesRepository()
        product_name = product_names_repo.get_product_name(item.name_id)
        name_text = product_name.name_text if product_name else "Unknown"

        tk.Label(row, text=name_text, width=30).pack(side=tk.LEFT, padx=5)

        tk.Label(row, text=f"On-hand: {on_hand:.2f}").pack(
            side=tk.LEFT, padx=10
        )

        tk.Label(row, text="Consumed:").pack(side=tk.LEFT, padx=2)

        consumed_var = tk.StringVar(value="0")
        entry = tk.Entry(row, textvariable=consumed_var, width=8)
        entry.pack(side=tk.LEFT, padx=2)

        self.consumption_entries[item.item_id] = {
            "var": consumed_var,
            "item": item,
            "on_hand": on_hand,
        }

    def _save(self) -> None:
        """Log all consumption entries."""
        consumption_repo = ConsumptionRepository()

        for item_id, entry_data in self.consumption_entries.items():
            consumed_str = entry_data["var"].get().strip()
            if not consumed_str or consumed_str == "0":
                continue

            try:
                consumed = float(consumed_str)
                if consumed < 0:
                    messagebox.showerror("Invalid", "Negative consumption")
                    return

                validate_consumption_on_hand(item_id, consumed)

                entry = Consumption(
                    item_id=item_id,
                    entry_date=self.entry_date,
                    servings_consumed=consumed,
                )
                consumption_repo.log_consumption(entry)

            except ValidationError as e:
                messagebox.showerror("Invalid consumption", str(e))
                return
            except ValueError:
                messagebox.showerror("Invalid value", f"Item {item_id}")
                return

        messagebox.showinfo("Success", "Consumption logged")
        self.destroy()
