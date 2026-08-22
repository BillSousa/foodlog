import tkinter as tk
from tkinter import messagebox

from foodlog.gui.components.item_search_filter import ItemSearchFilter
from foodlog.gui.dialogs.item_form_dialog import ItemFormDialog
from foodlog.models.dim_product_names import ProductName
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.product_names_repository import ProductNamesRepository


class ItemManagementWindow(tk.Toplevel):
    """Item management screen — search, create, edit items."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize item management window."""
        super().__init__(parent)
        self.title("Manage Items")
        self.geometry("850x700")
        self._layout()

    def _layout(self) -> None:
        """Build item management layout."""
        self.search_filter = ItemSearchFilter(self)
        self.search_filter.get_frame().pack(fill=tk.X, padx=10, pady=10)

        list_frame = tk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.listbox = tk.Listbox(
            list_frame,
            yscrollcommand=scrollbar.set,
            height=15
        )
        self.listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.listbox.yview)

        self._load_items()

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        new_btn = tk.Button(btn_frame, text="+ New Item", command=self._new_item)
        new_btn.pack(side=tk.LEFT, padx=5)

        edit_btn = tk.Button(
            btn_frame,
            text="Edit Selected",
            command=self._edit_item
        )
        edit_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _load_items(self) -> None:
        """Load items into listbox."""
        self.listbox.delete(0, tk.END)

        repo = ItemsRepository()
        items = repo.list_active_items()

        for item in items:
            name_repo = ProductNamesRepository()
            names = name_repo.list_product_names()
            name_text = next(
                (n.name_text for n in names if n.name_id == item.name_id),
                f"(ID: {item.name_id})"
            )

            text = (
                f"{name_text} — ${item.price}/block "
                f"({item.servings_per_block} servings)"
            )
            self.listbox.insert(tk.END, text)

        self.item_ids = [item.item_id for item in items]

    def _new_item(self) -> None:
        """Create new item."""
        ItemFormDialog(self)
        self._load_items()

    def _edit_item(self) -> None:
        """Edit selected item."""
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Select", "Please select an item to edit")
            return

        index = selection[0]
        item_id = self.item_ids[index]
        ItemFormDialog(self, item_id=item_id)
        self._load_items()
