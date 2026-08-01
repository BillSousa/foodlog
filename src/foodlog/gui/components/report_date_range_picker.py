import tkinter as tk
from datetime import datetime, timedelta


class ReportDateRangePicker:
    """Date range picker component for reporting screens."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize date range picker."""
        self.frame = tk.Frame(parent)
        self.on_change_callback = None

        today = datetime.today()
        thirty_days_ago = today - timedelta(days=30)

        self.start_var = tk.StringVar(value=thirty_days_ago.strftime("%Y-%m-%d"))
        self.end_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))

        self._layout()

    def _layout(self) -> None:
        """Build date picker layout."""
        tk.Label(self.frame, text="From:").pack(side=tk.LEFT, padx=5)
        start_entry = tk.Entry(
            self.frame, textvariable=self.start_var, width=12
        )
        start_entry.pack(side=tk.LEFT, padx=5)

        tk.Label(self.frame, text="To:").pack(side=tk.LEFT, padx=5)
        end_entry = tk.Entry(
            self.frame, textvariable=self.end_var, width=12
        )
        end_entry.pack(side=tk.LEFT, padx=5)

        self.start_var.trace("w", self._on_change)
        self.end_var.trace("w", self._on_change)

    def _on_change(self, *args) -> None:
        """Notify on date change."""
        if self.on_change_callback:
            self.on_change_callback()

    def get_frame(self) -> tk.Frame:
        """Return the frame widget."""
        return self.frame

    def get_dates(self) -> tuple[str, str]:
        """Get start and end dates (YYYY-MM-DD format)."""
        return (self.start_var.get(), self.end_var.get())
