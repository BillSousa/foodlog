import tkinter as tk
from tkinter import messagebox

from foodlog.gui.steps.wizard_step_welcome import WelcomeStep
from foodlog.gui.steps.wizard_step_nutrients import NutrientsStep
from foodlog.gui.steps.wizard_step_categories import CategoriesStep
from foodlog.gui.steps.wizard_step_cal_target import CalTargetStep
from foodlog.gui.steps.wizard_step_populate_items import PopulateItemsStep
from foodlog.repository.settings_repository import SettingsRepository


class SetupWizardWindow(tk.Tk):
    """Setup Wizard main window — 5-step flow."""

    def __init__(self) -> None:
        """Initialize wizard window."""
        super().__init__()
        self.title("FoodLog — Setup Wizard")
        self.geometry("600x500")

        self.steps = [
            WelcomeStep(self),
            NutrientsStep(self),
            CategoriesStep(self),
            CalTargetStep(self),
            PopulateItemsStep(self),
        ]

        self.current_step = 0

        for step in self.steps:
            step.layout()

        self._build_navigation()
        self._show_step(0)

    def _build_navigation(self) -> None:
        """Build back/next button frame."""
        nav_frame = tk.Frame(self)
        nav_frame.pack(fill=tk.X, padx=20, pady=10)

        self.back_btn = tk.Button(
            nav_frame,
            text="← Back",
            command=self._go_back,
            state=tk.DISABLED
        )
        self.back_btn.pack(side=tk.LEFT, padx=5)

        self.skip_btn = tk.Button(
            nav_frame,
            text="Skip →",
            command=self._skip_step
        )
        self.skip_btn.pack(side=tk.RIGHT, padx=5)

        self.next_btn = tk.Button(
            nav_frame,
            text="Next →",
            command=self._go_next
        )
        self.next_btn.pack(side=tk.RIGHT, padx=5)

    def _show_step(self, index: int) -> None:
        """Display step at given index."""
        for i, step in enumerate(self.steps):
            if i == index:
                step.show()
            else:
                step.hide()

        self.current_step = index

        title = f"Step {index + 1} of {len(self.steps)}"
        self.title(f"FoodLog — Setup Wizard — {title}")

        self.back_btn.config(state=tk.NORMAL if index > 0 else tk.DISABLED)

        if index == 1:
            self.skip_btn.config(state=tk.DISABLED)
        else:
            self.skip_btn.config(state=tk.NORMAL)

        if index == len(self.steps) - 1:
            self.next_btn.config(text="Finish")
        else:
            self.next_btn.config(text="Next →")

    def _go_back(self) -> None:
        """Go to previous step."""
        if self.current_step > 0:
            self._show_step(self.current_step - 1)

    def _skip_step(self) -> None:
        """Skip optional step."""
        if self.current_step == 1:
            self._go_next()

    def _go_next(self) -> None:
        """Validate current step and go to next."""
        step = self.steps[self.current_step]

        if not step.validate():
            return

        step.save()

        if self.current_step == len(self.steps) - 1:
            self._finish_wizard()
        else:
            self._show_step(self.current_step + 1)

    def _finish_wizard(self) -> None:
        """Complete wizard and set flag."""
        repo = SettingsRepository()
        repo.set_setting('wizard_completed', '1')

        messagebox.showinfo(
            "Welcome!",
            "Setup complete! Launching main GUI."
        )

        self.destroy()


def launch_setup_wizard() -> None:
    """Launch the setup wizard."""
    app = SetupWizardWindow()
    app.mainloop()
