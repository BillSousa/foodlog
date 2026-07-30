import tkinter as tk
from tkinter import messagebox

from src.gui.components.report_date_range_picker import (
    ReportDateRangePicker,
)


class ReportingWindow(tk.Toplevel):
    """Reporting and analytics screen."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize reporting window."""
        super().__init__(parent)
        self.title("Reporting & Analytics")
        self.geometry("900x700")

        self._layout()

    def _layout(self) -> None:
        """Build reporting layout."""
        title = tk.Label(
            self,
            text="Reporting & Analytics",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        filter_frame = tk.Frame(self)
        filter_frame.pack(fill=tk.X, padx=10, pady=10)

        self.date_picker = ReportDateRangePicker(filter_frame)
        self.date_picker.get_frame().pack(fill=tk.X)

        chart_frame = tk.Frame(self)
        chart_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        tk.Label(
            chart_frame,
            text="Charts will be implemented in Phase 12",
            font=("Arial", 11),
            fg="gray"
        ).pack(pady=50)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        export_btn = tk.Button(
            btn_frame, text="Export to CSV", command=self._export_csv
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _export_csv(self) -> None:
        """Export reporting data to CSV."""
        messagebox.showinfo("TODO", "CSV export (Phase 12)")
