import tkinter as tk

from src.repository.categories_repository import CategoriesRepository


class ItemSearchFilter:
    """Reusable search + category filter component."""

    def __init__(self, parent: tk.Widget) -> None:
        """
        Initialize search/filter frame.

        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.frame = tk.Frame(parent)
        self.search_var = tk.StringVar()
        self.category_vars: dict[str, tk.BooleanVar] = {}
        self._layout()

    def _layout(self) -> None:
        """Build search and filter UI."""
        search_frame = tk.Frame(self.frame)
        search_frame.pack(fill=tk.X, padx=10, pady=10)

        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)

        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            width=30
        )
        search_entry.pack(side=tk.LEFT, padx=5)

        category_frame = tk.Frame(self.frame)
        category_frame.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(category_frame, text="Categories:").pack(side=tk.LEFT, padx=5)

        repo = CategoriesRepository()
        categories = repo.list_categories()

        for cat in categories:
            var = tk.BooleanVar(value=False)
            self.category_vars[cat.category_name] = var
            check = tk.Checkbutton(
                category_frame,
                text=cat.category_name,
                variable=var
            )
            check.pack(side=tk.LEFT, padx=5)

    def get_search_text(self) -> str:
        """Get search text (lowercase)."""
        return self.search_var.get().lower()

    def get_selected_categories(self) -> list[str]:
        """Get list of selected category names."""
        return [
            name for name, var in self.category_vars.items()
            if var.get()
        ]

    def get_frame(self) -> tk.Frame:
        """Return the frame widget."""
        return self.frame
