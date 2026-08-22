import tkinter as tk
from tkinter import messagebox


class MainWindow(tk.Tk):
    """Main home screen with navigation buttons."""

    def __init__(self) -> None:
        """Initialize main window."""
        super().__init__()
        self.title("FoodLog — Main")
        self.geometry("600x800")
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
        from foodlog.gui.dialogs.order_picker_dialog import OrderPickerDialog
        OrderPickerDialog(self)

    def _on_consumption(self) -> None:
        """Open consumption logging screen."""
        from foodlog.gui.windows.consumption_window import ConsumptionWindow
        ConsumptionWindow(self)

    def _on_items(self) -> None:
        """Open item management screen."""
        from foodlog.gui.windows.item_management_window import ItemManagementWindow
        ItemManagementWindow(self)

    def _on_product_names(self) -> None:
        """Open product names editor."""
        from foodlog.gui.windows.product_names_window import ProductNamesWindow
        ProductNamesWindow(self)

    def _on_categories(self) -> None:
        """Open category manager."""
        from foodlog.gui.windows.categories_window import CategoriesWindow
        CategoriesWindow(self)

    def _on_nutrients(self) -> None:
        """Open nutrient tracking manager."""
        from foodlog.gui.windows.nutrients_window import NutrientsWindow
        NutrientsWindow(self)

    def _on_reporting(self) -> None:
        """Open reporting/analytics."""
        from foodlog.gui.windows.reporting_window import ReportingWindow
        ReportingWindow(self)

    def _on_settings(self) -> None:
        """Open settings."""
        from foodlog.gui.windows.settings_window import SettingsWindow
        SettingsWindow(self)


def launch_main_gui() -> None:
    """Launch the main GUI."""
    app = MainWindow()
    app.mainloop()
