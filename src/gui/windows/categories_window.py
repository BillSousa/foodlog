import tkinter as tk
from tkinter import messagebox

from src.repository.categories_repository import CategoriesRepository
from src.repository.items_repository import ItemsRepository


class CategoriesWindow(tk.Toplevel):
    """Manage category names."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize categories window."""
        super().__init__(parent)
        self.title("Manage Categories")
        self.geometry("400x500")

        self.categories_repo = CategoriesRepository()
        self.items_repo = ItemsRepository()

        self._layout()

    def _layout(self) -> None:
        """Build categories layout."""
        title = tk.Label(
            self,
            text="Manage Categories",
            font=("Arial", 14, "bold")
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

        self.category_entries: dict[int, dict] = {}

        for cat in self.categories_repo.list_categories():
            self._add_category_row(scrollable, cat)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        add_btn = tk.Button(
            btn_frame, text="Add Category", command=self._add_new_category
        )
        add_btn.pack(side=tk.LEFT, padx=5)

        save_btn = tk.Button(
            btn_frame, text="Save", command=self._save
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _add_category_row(self, parent: tk.Widget, category) -> None:
        """Add a category row."""
        row = tk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        row.pack(fill=tk.X, pady=2)

        cat_id = category.category_id
        self.category_entries[cat_id] = {
            "var": tk.StringVar(value=category.category_name),
            "row": row,
        }

        tk.Label(row, text=f"ID {cat_id}", width=5).pack(side=tk.LEFT, padx=5)

        entry = tk.Entry(
            row,
            textvariable=self.category_entries[cat_id]["var"],
            width=25
        )
        entry.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(
            row,
            text="Delete",
            command=lambda: self._delete_category(cat_id)
        )
        delete_btn.pack(side=tk.RIGHT, padx=5)

    def _add_new_category(self) -> None:
        """Add a new category (temporary, saved on Save button)."""
        new_cat = self.categories_repo.create_category("New Category")
        if new_cat and hasattr(new_cat, "category_id"):
            # Refresh the list
            for widget in self.winfo_children():
                widget.destroy()
            self._layout()

    def _delete_category(self, cat_id: int) -> None:
        """Delete a category."""
        items = self.items_repo.list_active_items()
        in_use = any(item.category_id == cat_id for item in items)

        if in_use:
            messagebox.showerror(
                "In use",
                "Cannot delete category currently used by items"
            )
            return

        if messagebox.askyesno("Confirm", "Delete this category?"):
            self.categories_repo.delete_category(cat_id)
            self.category_entries.pop(cat_id, None)
            for widget in self.winfo_children():
                widget.destroy()
            self._layout()

    def _save(self) -> None:
        """Save category name changes."""
        for cat_id, entry_data in self.category_entries.items():
            new_name = entry_data["var"].get().strip()
            if new_name:
                self.categories_repo.update_category(cat_id, new_name)

        messagebox.showinfo("Success", "Categories saved")
        self.destroy()
