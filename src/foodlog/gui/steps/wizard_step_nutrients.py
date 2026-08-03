import tkinter as tk
from tkinter import messagebox

# TODO: "NUTRIENTS" NEEDS TO COME OUT.
from foodlog.database.seed_reference_data import NUTRIENTS
from foodlog.gui.steps.base_step import BaseStep
from foodlog.repository.tracked_nutrients_repository import (
    TrackedNutrientsRepository,
)


class NutrientsStep(BaseStep):
    """Step 2: Nutrient tracking (mandatory, no skip)."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize with nutrient checkboxes."""
        super().__init__(parent)
        self.check_vars: dict[str, tk.BooleanVar] = {}
        self.master_var = tk.BooleanVar(value=False)
        self.vitamin_vars: list[tk.BooleanVar] = []

    def layout(self) -> None:
        """Build nutrient selection screen."""
        title = tk.Label(
            self.frame,
            text="Nutrient Tracking",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=20)

        text = tk.Label(
            self.frame,
            text=(
                "Choose which nutrients you want to track.\n"
                "You can change this anytime later via "
                "'Manage Tracked Nutrients'.\n"
                "Not selecting any nutrients is allowed."
            ),
            justify=tk.LEFT,
            wraplength=400
        )
        text.pack(pady=10)

        canvas_frame = tk.Frame(self.frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        canvas = tk.Canvas(canvas_frame, height=250)
        scrollbar = tk.Scrollbar(
            canvas_frame,
            orient=tk.VERTICAL,
            command=canvas.yview
        )
        scrollable = tk.Frame(canvas)

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        self.master_var.trace(
            "w",
            lambda *args: self._toggle_all_vitamins()
        )

        master_check = tk.Checkbutton(
            scrollable,
            text="Track All Vitamins/Minerals",
            variable=self.master_var
        )
        master_check.pack(anchor=tk.W, padx=10, pady=5)

        tk.Label(scrollable, text="", font=("Arial", 1)).pack()

        # TODO: "NUTRIENTS" NEEDS TO COME OUT.
        # THIS NEEDS TO CHANGE TO PULL FROM ref_daily_values.
        for name, unit, dv, tracked, is_dv_percent in NUTRIENTS:
            var = tk.BooleanVar(value=False)
            self.check_vars[name] = var

            check = tk.Checkbutton(scrollable, text=name, variable=var)
            check.pack(anchor=tk.W, padx=20, pady=2)

            if "Vitamin" in name or "Calcium" in name or "Iron" in name:
                self.vitamin_vars.append(var)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _toggle_all_vitamins(self) -> None:
        """Toggle all vitamin checkboxes."""
        state = self.master_var.get()
        for var in self.vitamin_vars:
            var.set(state)

    def validate(self) -> bool:
        """Nutrients step is valid even if none selected."""
        return True

    def save(self) -> None:
        """Save nutrient tracking selections."""
        repo = TrackedNutrientsRepository()
        for name, var in self.check_vars.items():
            if var.get():
                repo.set_tracked(name, True)
