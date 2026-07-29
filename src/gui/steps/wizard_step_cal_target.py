import tkinter as tk
from tkinter import messagebox

from src.gui.steps.base_step import BaseStep
from src.repository.settings_repository import SettingsRepository


class CalTargetStep(BaseStep):
    """Step 4: Set daily calorie target (default 2000)."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize with entry widget placeholder."""
        super().__init__(parent)
        self.entry: tk.Entry | None = None

    def layout(self) -> None:
        """Build calorie target screen."""
        title = tk.Label(
            self.frame,
            text="Daily Calorie Target",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=20)

        text = tk.Label(
            self.frame,
            text=(
                "This target is used to estimate order duration\n"
                "and drives per-day figures in Reporting.\n"
                "You can change this anytime later via Settings."
            ),
            justify=tk.LEFT,
            wraplength=400
        )
        text.pack(pady=10)

        frame = tk.Frame(self.frame)
        frame.pack(pady=20)

        label = tk.Label(frame, text="Target calories per day:")
        label.pack(side=tk.LEFT, padx=5)

        self.entry = tk.Entry(frame, width=10)
        self.entry.insert(0, "2000")
        self.entry.pack(side=tk.LEFT, padx=5)

    def validate(self) -> bool:
        """Validate calorie target is positive number."""
        if not self.entry:
            return False

        try:
            value = float(self.entry.get())
            if value <= 0:
                messagebox.showerror(
                    "Invalid",
                    "Target must be positive"
                )
                return False
            return True
        except ValueError:
            messagebox.showerror(
                "Invalid",
                "Please enter a number"
            )
            return False

    def save(self) -> None:
        """Save calorie target to settings."""
        if self.entry:
            repo = SettingsRepository()
            repo.set_setting(
                'cal_per_day_target',
                self.entry.get()
            )
