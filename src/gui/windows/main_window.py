import tkinter as tk
from tkinter import messagebox


class MainWindow(tk.Tk):
    """Main home screen with navigation buttons."""

    def __init__(self) -> None:
        """Initialize main window."""
        super().__init__()
        self.title("FoodLog — Main")
        self.geometry("400x600")
        self._layout()

    def _layout(self) -> None:
        """Build main screen layout."""
        title = tk.Label(
            self,
            text="FoodLog",
            font=("Arial", 18, "bold")
        )
        title.pack(pady=20)

        button_frame = tk.Frame(self)
        button_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        buttons = [
            ("New / Manage Orders", self._on_orders),
            ("Log Consumption", self._on_consumption),
            ("Manage Items", self._on_items),
            ("Edit Product Names", self._on_product_names),
            ("Manage Categories", self._on_categories),
            ("Manage Tracked Nutrients", self._on_nutrients),
            ("Reporting", self._on_reporting),
            ("Settings", self._on_settings),
        ]

        for label, command in buttons:
            btn = tk.Button(
                button_frame,
                text=label,
                command=command,
                width=30,
                height=2
            )
            btn.pack(pady=5)

    def _on_orders(self) -> None:
        """Open order picker dialog."""
        from src.gui.dialogs.order_picker_dialog import OrderPickerDialog
        OrderPickerDialog(self)

    def _on_consumption(self) -> None:
        """Open consumption logging screen."""
        tk.messagebox.showinfo("TODO", "Consumption screen (Phase 10)")

    def _on_items(self) -> None:
        """Open item management screen."""
        tk.messagebox.showinfo("TODO", "Item management screen (Phase 7)")

    def _on_product_names(self) -> None:
        """Open product names editor."""
        tk.messagebox.showinfo("TODO", "Product names screen (Phase 11)")

    def _on_categories(self) -> None:
        """Open category manager."""
        tk.messagebox.showinfo("TODO", "Categories screen (Phase 11)")

    def _on_nutrients(self) -> None:
        """Open nutrient tracking manager."""
        tk.messagebox.showinfo("TODO", "Nutrients screen (Phase 11)")

    def _on_reporting(self) -> None:
        """Open reporting/analytics."""
        tk.messagebox.showinfo("TODO", "Reporting screen (Phase 12)")

    def _on_settings(self) -> None:
        """Open settings."""
        tk.messagebox.showinfo("TODO", "Settings screen (Phase 11)")


def launch_main_gui() -> None:
    """Launch the main GUI."""
    app = MainWindow()
    app.mainloop()
