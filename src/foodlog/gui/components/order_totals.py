import tkinter as tk


class OrderTotals:
    """Running totals display for order."""

    def __init__(self, parent: tk.Widget, cal_per_day: float = 2000) -> None:
        """Initialize totals display."""
        self.frame = tk.LabelFrame(parent, text="Running Totals")
        self.cal_per_day = cal_per_day
        self.labels: dict[str, tk.Label] = {}
        self._layout()
        self.update(0, 0, 0, 0, 0, 0)

    def _layout(self) -> None:
        """Build totals display."""
        row1 = tk.Frame(self.frame)
        row1.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(row1, text="Cost:").pack(side=tk.LEFT, padx=10)
        self.labels["cost"] = tk.Label(row1, text="$0.00", width=10)
        self.labels["cost"].pack(side=tk.LEFT, padx=5)

        tk.Label(row1, text="Calories:").pack(side=tk.LEFT, padx=10)
        self.labels["calories"] = tk.Label(row1, text="0", width=10)
        self.labels["calories"].pack(side=tk.LEFT, padx=5)

        tk.Label(row1, text="Days:").pack(side=tk.LEFT, padx=10)
        self.labels["days"] = tk.Label(row1, text="0", width=10)
        self.labels["days"].pack(side=tk.LEFT, padx=5)

        row2 = tk.Frame(self.frame)
        row2.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(row2, text="Protein:").pack(side=tk.LEFT, padx=10)
        self.labels["protein"] = tk.Label(row2, text="0g", width=10)
        self.labels["protein"].pack(side=tk.LEFT, padx=5)

        tk.Label(row2, text="Sodium:").pack(side=tk.LEFT, padx=10)
        self.labels["sodium"] = tk.Label(row2, text="0mg", width=10)
        self.labels["sodium"].pack(side=tk.LEFT, padx=5)

        tk.Label(row2, text="Ratio1:").pack(side=tk.LEFT, padx=10)
        self.labels["ratio1"] = tk.Label(row2, text="0", width=10)
        self.labels["ratio1"].pack(side=tk.LEFT, padx=5)

    def update(
        self,
        cost: float,
        calories: float,
        protein_g: float,
        sodium_mg: float,
        ratio1: float,
        ratio2: float
    ) -> None:
        """Update totals display."""
        self.labels["cost"].config(text=f"${cost:.2f}")
        self.labels["calories"].config(text=f"{int(calories)}")

        days = calories / self.cal_per_day if calories > 0 else 0
        self.labels["days"].config(text=f"{days:.1f}")

        self.labels["protein"].config(text=f"{protein_g:.1f}g")
        self.labels["sodium"].config(text=f"{sodium_mg:.0f}mg")
        self.labels["ratio1"].config(text=f"{ratio1:.1f}")

    def get_frame(self) -> tk.Frame:
        """Return frame."""
        return self.frame
