import tkinter as tk
from tkinter import messagebox

from src.gui.steps.base_step import BaseStep
from src.repository.categories_repository import CategoriesRepository


class CategoriesStep(BaseStep):
    """Step 3: Create categories (optional)."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize with entry and listbox."""
        super().__init__(parent)
        self.entry: tk.Entry | None = None
        self.listbox: tk.Listbox | None = None
        self.categories: list[str] = []

    def layout(self) -> None:
        """Build categories screen."""
        title = tk.Label(
            self.frame,
            text="Categories (Optional)",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=20)

        text = tk.Label(
            self.frame,
            text=(
                "You can create categories now (e.g., 'Pasta', 'Meat')\n"
                "or skip this and do it later via 'Manage Categories'."
            ),
            justify=tk.LEFT,
            wraplength=400
        )
        text.pack(pady=10)

        frame = tk.Frame(self.frame)
        frame.pack(pady=10, padx=20, fill=tk.BOTH, expand=False)

        label = tk.Label(frame, text="New category:")
        label.pack(side=tk.LEFT, padx=5)

        self.entry = tk.Entry(frame, width=20)
        self.entry.pack(side=tk.LEFT, padx=5)

        btn = tk.Button(frame, text="Add", command=self._add_category)
        btn.pack(side=tk.LEFT, padx=5)

        self.listbox = tk.Listbox(self.frame, height=5, width=30)
        self.listbox.pack(pady=10, padx=20)

    def _add_category(self) -> None:
        """Add category to list."""
        if self.entry:
            text = self.entry.get().strip()
            if text and self.listbox:
                self.categories.append(text)
                self.listbox.insert(tk.END, text)
                self.entry.delete(0, tk.END)

    def validate(self) -> bool:
        """Categories step is always valid (optional)."""
        return True

    def save(self) -> None:
        """Save categories to database."""
        if self.categories:
            repo = CategoriesRepository()
            for cat in self.categories:
                repo.create_category(cat)
