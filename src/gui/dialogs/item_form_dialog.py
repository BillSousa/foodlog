import tkinter as tk
import tkinter.ttk
from tkinter import messagebox

from src.gui.components.nutrition_panel import NutritionPanel
from src.models.dim_items import Item
from src.models.dim_product_names import ProductName
from src.repository.categories_repository import CategoriesRepository
from src.repository.items_repository import ItemsRepository
from src.repository.product_names_repository import ProductNamesRepository


class ItemFormDialog(tk.Toplevel):
    """Dialog for creating/editing food items."""

    def __init__(
        self,
        parent: tk.Widget,
        item_id: int | None = None
    ) -> None:
        """
        Initialize item form dialog.

        Args:
            parent: Parent widget
            item_id: Item ID to edit (None for new item)
        """
        super().__init__(parent)
        self.title("Create Item" if not item_id else "Edit Item")
        self.geometry("600x700")
        self.item_id = item_id
        self.item: Item | None = None

        if item_id:
            repo = ItemsRepository()
            self.item = repo.get_item(item_id)

        self._layout()

    def _layout(self) -> None:
        """Build form layout."""
        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Name:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.name_entry = tk.Entry(frame, width=40)
        self.name_entry.grid(row=0, column=1, sticky=tk.EW, pady=5)

        tk.Label(frame, text="Category:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        self.category_var = tk.StringVar()
        cat_repo = CategoriesRepository()
        categories = [c.category_name for c in cat_repo.list_categories()]
        cat_combo = tk.ttk.Combobox(
            frame,
            textvariable=self.category_var,
            values=categories,
            width=37
        )
        cat_combo.grid(row=1, column=1, sticky=tk.EW, pady=5)

        tk.Label(frame, text="Price per block:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        self.price_entry = tk.Entry(frame, width=10)
        self.price_entry.grid(row=2, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Units:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.units_entry = tk.Entry(frame, width=10)
        self.units_entry.grid(row=3, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Container Size:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )
        self.container_entry = tk.Entry(frame, width=10)
        self.container_entry.grid(row=4, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Serving Size:").grid(
            row=5, column=0, sticky=tk.W, pady=5
        )
        self.serving_entry = tk.Entry(frame, width=10)
        self.serving_entry.grid(row=5, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Active:").grid(row=6, column=0, sticky=tk.W, pady=5)
        self.active_var = tk.BooleanVar(value=True)
        tk.Checkbutton(frame, variable=self.active_var).grid(
            row=6, column=1, sticky=tk.W, pady=5
        )

        self.nutrition_panel = NutritionPanel(frame)
        self.nutrition_panel.get_frame().grid(
            row=7, column=0, columnspan=2, sticky=tk.EW, pady=10
        )

        if self.item:
            self._populate_form()

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=20, pady=10)

        save_btn = tk.Button(btn_frame, text="Save", command=self._save)
        save_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(btn_frame, text="Cancel", command=self.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _populate_form(self) -> None:
        """Populate form with existing item data."""
        if not self.item:
            return

        self.name_entry.insert(0, "")
        self.price_entry.insert(0, str(self.item.price))
        self.units_entry.insert(0, self.item.units)
        self.container_entry.insert(0, str(self.item.container_size))
        self.serving_entry.insert(0, str(self.item.serving_size))
        self.active_var.set(self.item.active == 1)

        nutrition_values = {
            k: v for k, v in self.item.to_dict().items()
            if k.endswith(("_g", "_mg", "_mcg"))
        }
        self.nutrition_panel.set_values(nutrition_values)

    def _save(self) -> None:
        """Save item to database."""
        try:
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return

            price = float(self.price_entry.get())
            container = float(self.container_entry.get())
            serving = float(self.serving_entry.get())

            if container <= 0 or serving <= 0:
                messagebox.showerror(
                    "Error",
                    "Container and serving sizes must be positive"
                )
                return

            name_repo = ProductNamesRepository()
            name_id = name_repo.create_product_name(name)

            servings_per_block = container / serving

            item = Item(
                name_id=name_id,
                category_id=None,
                price=price,
                servings_per_block=servings_per_block,
                units=self.units_entry.get(),
                container_size=container,
                serving_size=serving,
                blocks_must_be_integer=0,
                active=1 if self.active_var.get() else 0,
            )

            nutrition = self.nutrition_panel.get_values()
            for key, value in nutrition.items():
                setattr(item, key, value)

            repo = ItemsRepository()
            if self.item_id:
                repo.update_item_price(self.item_id, price)
            else:
                repo.create_item(item)

            messagebox.showinfo("Success", "Item saved")
            self.destroy()

        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input")
