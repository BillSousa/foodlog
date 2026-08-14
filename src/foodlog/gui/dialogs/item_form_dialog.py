import tkinter as tk
import tkinter.ttk
from tkinter import messagebox

from foodlog.conversion.nutrition_converter import (
    convert_nutrition_for_storage,
    get_column_name,
)
from foodlog.gui.components.nutrition_panel import NutritionPanel
from foodlog.gui.helpers.item_form_populator import (
    populate_item_form_data,
)
from foodlog.gui.helpers.should_create_new_version import (
    should_create_new_version,
)
from foodlog.models.dim_items import Item
from foodlog.repository.categories_repository import CategoriesRepository
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.product_names_repository import ProductNamesRepository


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

        tk.Label(frame, text="Blocks Must Be Integer:").grid(
            row=7, column=0, sticky=tk.W, pady=5
        )
        self.blocks_must_be_integer_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            frame, variable=self.blocks_must_be_integer_var
        ).grid(row=7, column=1, sticky=tk.W, pady=5)

        tk.Label(frame, text="Glycemic Index:").grid(
            row=8, column=0, sticky=tk.W, pady=5
        )
        self.glycemic_index_entry = tk.Entry(frame, width=10)
        self.glycemic_index_entry.grid(row=8, column=1, sticky=tk.W, pady=5)

        self.nutrition_panel = NutritionPanel(frame)
        self.nutrition_panel.get_frame().grid(
            row=9, column=0, columnspan=2, sticky=tk.EW, pady=10
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

        name_repo = ProductNamesRepository()
        data = populate_item_form_data(self.item, name_repo)

        self.name_entry.insert(0, data['name_text'])
        self.price_entry.insert(0, data['price'])
        self.units_entry.insert(0, data['units'])
        self.container_entry.insert(0, data['container_size'])
        self.serving_entry.insert(0, data['serving_size'])
        self.active_var.set(data['active'])
        self.blocks_must_be_integer_var.set(
            data['blocks_must_be_integer']
        )
        if data['glycemic_index'] is not None:
            self.glycemic_index_entry.insert(0, data['glycemic_index'])

        self.nutrition_panel.set_values(data['nutrition_values'])

    def _save(self) -> None:
        """Save item to database."""
        try:
            name = self.name_entry.get().strip()
            if not name:
                messagebox.showerror("Error", "Name is required")
                return

            units = self.units_entry.get().strip()
            if not units:
                messagebox.showerror("Error", "Units is required")
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

            category_id = None
            selected_category_name = self.category_var.get().strip()
            if selected_category_name:
                cat_repo = CategoriesRepository()
                categories = cat_repo.list_categories()
                category_map = {
                    c.category_name: c.category_id for c in categories
                }
                category_id = category_map.get(selected_category_name)

            servings_per_block = container / serving

            blocks_must_be_integer = (
                1 if self.blocks_must_be_integer_var.get() else 0
            )

            active = 1 if self.active_var.get() else 0

            glycemic_index = None
            gi_str = self.glycemic_index_entry.get().strip()
            if gi_str:
                try:
                    glycemic_index = int(gi_str)
                except ValueError:
                    messagebox.showerror(
                        "Error", "Glycemic Index must be a whole number"
                    )
                    return

            item = Item(
                name_id=name_id,
                category_id=category_id,
                price=price,
                servings_per_block=servings_per_block,
                units=units,
                container_size=container,
                serving_size=serving,
                blocks_must_be_integer=blocks_must_be_integer,
                active=active,
                glycemic_index=glycemic_index,
            )

            nutrition = self.nutrition_panel.get_values()
            nutrition_dict = {}
            nutrition_dict['units'] = units
            nutrition_dict['container_size'] = container
            nutrition_dict['serving_size'] = serving

            for nutrient_name, user_value in nutrition.items():
                column_name = get_column_name(nutrient_name)
                if column_name:
                    converted_value = convert_nutrition_for_storage(
                        nutrient_name, user_value
                    )
                    setattr(item, column_name, converted_value)
                    nutrition_dict[column_name] = converted_value

            repo = ItemsRepository()
            if self.item_id:
                if should_create_new_version(self.item, nutrition_dict):
                    repo.create_item_version(item)
                else:
                    repo.update_item_price(self.item_id, price)
                    repo.update_item_metadata(
                        self.item_id,
                        category_id,
                        glycemic_index,
                        blocks_must_be_integer,
                        active,
                    )
            else:
                repo.create_item(item)

            messagebox.showinfo("Success", "Item saved")
            self.destroy()

        except ValueError:
            messagebox.showerror("Error", "Invalid numeric input")
