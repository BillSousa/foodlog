import tkinter as tk
from tkinter import messagebox

from foodlog.repository.tracked_nutrients_repository import (
    TrackedNutrientsRepository,
)


class NutrientsWindow(tk.Toplevel):
    """Manage tracked nutrients and daily values."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize nutrients window."""
        super().__init__(parent)
        self.title("Manage Tracked Nutrients")
        self.geometry("700x600")

        self.nutrients_repo = TrackedNutrientsRepository()
        self.nutrient_rows: dict[int, dict] = {}

        self._layout()

    def _layout(self) -> None:
        """Build nutrients layout."""
        title = tk.Label(
            self,
            text="Manage Tracked Nutrients",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        canvas_frame = tk.Frame(self)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        canvas = tk.Canvas(canvas_frame)
        scrollbar = tk.Scrollbar(
            canvas_frame, orient=tk.VERTICAL, command=canvas.yview
        )
        scrollable = tk.Frame(canvas)

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")),
        )

        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        for nutrient in self.nutrients_repo.list_all_nutrients():
            self._add_nutrient_row(scrollable, nutrient)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        save_btn = tk.Button(
            btn_frame, text="Save", command=self._save
        )
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _add_nutrient_row(self, parent: tk.Widget, nutrient) -> None:
        """Add a nutrient row."""
        row = tk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        row.pack(fill=tk.X, pady=2)

        nutrient_id = nutrient.nutrient_id
        self.nutrient_rows[nutrient_id] = {
            "name_var": tk.StringVar(value=nutrient.nutrient_name),
            "dv_var": tk.StringVar(value=str(nutrient.dv_amount)),
            "tracked_var": tk.BooleanVar(value=bool(nutrient.is_tracked)),
            "row": row,
        }

        tk.Label(row, text=f"ID {nutrient_id}", width=3).pack(
            side=tk.LEFT, padx=5
        )

        name_entry = tk.Entry(
            row,
            textvariable=self.nutrient_rows[nutrient_id]["name_var"],
            width=25
        )
        name_entry.pack(side=tk.LEFT, padx=2)

        dv_entry = tk.Entry(
            row,
            textvariable=self.nutrient_rows[nutrient_id]["dv_var"],
            width=12
        )
        dv_entry.pack(side=tk.LEFT, padx=2)

        tk.Label(row, text="mcg").pack(side=tk.LEFT, padx=2)

        tracked_checkbox = tk.Checkbutton(
            row,
            variable=self.nutrient_rows[nutrient_id]["tracked_var"]
        )
        tracked_checkbox.pack(side=tk.RIGHT, padx=5)

        tk.Label(row, text="Tracked", font=("Arial", 8)).pack(
            side=tk.RIGHT, padx=2
        )

    def _save(self) -> None:
        """Save all nutrient changes."""
        try:
            for nutrient_id, row_data in self.nutrient_rows.items():
                name = row_data["name_var"].get().strip()
                dv_str = row_data["dv_var"].get().strip()
                is_tracked = row_data["tracked_var"].get()

                if not name or not dv_str:
                    messagebox.showerror("Invalid", "Name/DV cannot be blank")
                    return

                dv = float(dv_str)
                if dv < 0:
                    messagebox.showerror("Invalid", "DV cannot be negative")
                    return

                self.nutrients_repo.update_nutrient(
                    nutrient_id, name, dv, 1 if is_tracked else 0
                )

            messagebox.showinfo("Success", "Nutrients saved")
            self.destroy()

        except ValueError:
            messagebox.showerror("Invalid", "DV must be a number")
