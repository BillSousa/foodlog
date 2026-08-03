import tkinter as tk

# TODO: "NUTRIENTS" NEEDS TO COME OUT.
from foodlog.database.seed_reference_data import NUTRIENTS
from foodlog.nutrients.metadata import get_nutrient_unit
from foodlog.repository.tracked_nutrients_repository import (
    TrackedNutrientsRepository,
)


# TODO: UNITS OF ENTRY FOR EACH NUTRIENT (e.g., calcium, magnesium, etc.) MUST BE PULLED FROM 
# ref_daily_values.nutrient_entry_unit FOR DISPLAY HERE.
# TODO: CALCULATIONS DRIVING NUTRIENT QUANTITY UNIT CONVERSIONS (FOR FILLING THE CORRESPONDING COLUMNS 
# IN dim_items FROM VALUES ENTERED HERE) MUST BE UPDATED TO PERFORM CONDITIONAL CONVERSIONS BASED ON 
# ref_daily_values.nutrient_entry_unit.


class NutritionPanel:
    """Nutrition entry fields for tracked nutrients."""

    def __init__(self, parent: tk.Widget) -> None:
        """
        Initialize nutrition panel.

        Args:
            parent: Parent widget
        """
        self.parent = parent
        self.frame = tk.LabelFrame(parent, text="Nutrition")
        self.entries: dict[str, tk.Entry] = {}
        self._layout()

    def _layout(self) -> None:
        """Build nutrition fields from tracked nutrients."""
        repo = TrackedNutrientsRepository()
        tracked = set(repo.get_tracked_nutrients())

        if not tracked:
            tk.Label(
                self.frame,
                text="No nutrients tracked"
            ).pack()
            return

        canvas_frame = tk.Frame(self.frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(canvas_frame, height=200)
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

        # TODO: NUTRIENTS WILL HAVE TO COME OUT, USE ref_daily_values COLUMNS DIRECTLY.
        for name, _, _, _, _ in NUTRIENTS:
            if name not in tracked:
                continue

            row = tk.Frame(scrollable)
            row.pack(fill=tk.X, padx=5, pady=2)

            display_unit = get_nutrient_unit(name)
            label = tk.Label(row, text=f"{name} ({display_unit}):", width=25)
            label.pack(side=tk.LEFT)

            entry = tk.Entry(row, width=10)
            entry.insert(0, "0")
            entry.pack(side=tk.LEFT, padx=5)

            self.entries[name] = entry

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def get_values(self) -> dict[str, float]:
        """Get nutrition values from entries."""
        result = {}
        for name, entry in self.entries.items():
            try:
                result[name] = float(entry.get())
            except ValueError:
                result[name] = 0.0
        return result

    def set_values(self, values: dict[str, float]) -> None:
        """Populate entries with values."""
        for name, entry in self.entries.items():
            if name in values:
                entry.delete(0, tk.END)
                entry.insert(0, str(values[name]))

    def get_frame(self) -> tk.Frame:
        """Return the frame widget."""
        return self.frame
