import tkinter as tk

from src.gui.steps.base_step import BaseStep


class WelcomeStep(BaseStep):
    """Step 1: Welcome introduction (informational only)."""

    def layout(self) -> None:
        """Build welcome screen layout."""
        title = tk.Label(
            self.frame,
            text="Welcome to FoodLog",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=20)

        text = tk.Label(
            self.frame,
            text=(
                "This wizard will help you set up a new FoodLog project.\n\n"
                "You'll choose which nutrients to track,\n"
                "optionally set up categories,\n"
                "set a daily calorie target,\n"
                "and optionally start entering items.\n\n"
                "Everything except nutrient tracking can be skipped\n"
                "and changed later."
            ),
            justify=tk.LEFT,
            wraplength=400
        )
        text.pack(pady=20)

    def validate(self) -> bool:
        """Welcome step has no validation."""
        return True

    def save(self) -> None:
        """Welcome step has no data to save."""
        pass
