import tkinter as tk
from tkinter import messagebox

from src.repository.product_names_repository import ProductNamesRepository


class ProductNamesWindow(tk.Toplevel):
    """Edit product names."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize product names window."""
        super().__init__(parent)
        self.title("Edit Product Names")
        self.geometry("500x500")

        self.names_repo = ProductNamesRepository()
        self._layout()

    def _layout(self) -> None:
        """Build product names layout."""
        title = tk.Label(
            self,
            text="Edit Product Names",
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

        self.name_entries: dict[int, tk.StringVar] = {}

        for name in self.names_repo.list_product_names():
            self._add_name_row(scrollable, name)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        save_btn = tk.Button(
            btn_frame, text="Save", command=self._save
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _add_name_row(self, parent: tk.Widget, name) -> None:
        """Add a product name row."""
        row = tk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        row.pack(fill=tk.X, pady=2)

        name_id = name.name_id
        self.name_entries[name_id] = tk.StringVar(value=name.name_text)

        tk.Label(row, text=f"ID {name_id}", width=5).pack(side=tk.LEFT, padx=5)

        entry = tk.Entry(
            row,
            textvariable=self.name_entries[name_id],
            width=30
        )
        entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    def _save(self) -> None:
        """Save product name changes."""
        for name_id, var in self.name_entries.items():
            new_text = var.get().strip()
            if new_text:
                self.names_repo.update_product_name(name_id, new_text)

        messagebox.showinfo("Success", "Product names saved")
        self.destroy()
