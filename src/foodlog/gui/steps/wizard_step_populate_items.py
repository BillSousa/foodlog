import tkinter as tk

from foodlog.gui.steps.base_step import BaseStep


class PopulateItemsStep(BaseStep):
    """Step 5: Populate items (optional, final step)."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize with choice variable."""
        super().__init__(parent)
        self.choice_var = tk.StringVar(value="skip")

    def layout(self) -> None:
        """Build items population screen."""
        title = tk.Label(
            self.frame,
            text="Populate Items",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=20)

        text = tk.Label(
            self.frame,
            text=(
                "Would you like to start entering food items now,\n"
                "or skip this and do it later from the main screen?"
            ),
            justify=tk.LEFT,
            wraplength=400
        )
        text.pack(pady=20)

        btn_skip = tk.Button(
            self.frame,
            text="Skip — Go to Main Screen",
            width=30
        )
        btn_skip.pack(pady=10)

        btn_items = tk.Button(
            self.frame,
            text="Start Entering Items →",
            width=30
        )
        btn_items.pack(pady=10)

    def validate(self) -> bool:
        """Items step is always valid (choice determines next action)."""
        return True

    def save(self) -> None:
        """No data to save for this step."""
        pass
