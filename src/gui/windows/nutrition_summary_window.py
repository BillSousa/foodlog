import csv
import tkinter as tk
from datetime import datetime

from src.database.connection import get_database_path
from src.repository.items_repository import ItemsRepository
from src.repository.order_lines_repository import OrderLinesRepository
from src.repository.tracked_nutrients_repository import (
    TrackedNutrientsRepository,
)


class NutritionSummaryWindow(tk.Toplevel):
    """Order Nutrition Summary — nutrient matrix by item/category."""

    def __init__(self, parent: tk.Widget, order_id: int) -> None:
        """Initialize nutrition summary window."""
        super().__init__(parent)
        self.title(f"Order #{order_id} — Nutrition Summary")
        self.geometry("900x600")
        self.order_id = order_id
        self._layout()

    def _layout(self) -> None:
        """Build nutrition summary layout."""
        title = tk.Label(
            self,
            text=f"Order #{self.order_id} — Nutrition Summary",
            font=("Arial", 12, "bold"),
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

        lines_repo = OrderLinesRepository()
        items_repo = ItemsRepository()
        tracked_repo = TrackedNutrientsRepository()

        lines = lines_repo.get_order_lines(self.order_id)
        tracked = set(tracked_repo.get_tracked_nutrients())

        header = "Item | Servings | " + " | ".join(
            list(tracked)[:5]
        )
        tk.Label(scrollable, text=header, font=("Arial", 9)).pack(
            anchor=tk.W, padx=10, pady=5
        )

        total_calories = 0
        total_protein = 0
        total_sodium = 0

        for line in lines:
            item = items_repo.get_item(line.item_id)
            if not item:
                continue

            multiplier = line.actual_servings
            calories = item.calories * multiplier
            protein = item.protein_g * multiplier
            sodium = item.sodium_mg * multiplier

            total_calories += calories
            total_protein += protein
            total_sodium += sodium

            text = (
                f"Item #{item.item_id} x{multiplier:.1f} | "
                f"{calories:.0f}cal | {protein:.1f}g | {sodium:.0f}mg"
            )
            tk.Label(scrollable, text=text, justify=tk.LEFT).pack(
                anchor=tk.W, padx=10, pady=2
            )

        tk.Label(scrollable, text="", font=("Arial", 1)).pack()

        summary = (
            f"TOTALS: {total_calories:.0f} cal | "
            f"{total_protein:.1f}g protein | {total_sodium:.0f}mg sodium"
        )
        tk.Label(
            scrollable, text=summary, font=("Arial", 10, "bold")
        ).pack(anchor=tk.W, padx=10, pady=10)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        export_btn = tk.Button(
            btn_frame, text="Export to CSV", command=self._export_csv
        )
        export_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _export_csv(self) -> None:
        """Export nutrition summary to CSV."""
        try:
            lines_repo = OrderLinesRepository()
            items_repo = ItemsRepository()
            lines = lines_repo.get_order_lines(self.order_id)

            csv_path = (
                get_database_path().parent
                / f"order_{self.order_id}_nutrition_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            )

            with open(csv_path, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "Item ID",
                        "Servings",
                        "Calories",
                        "Protein (g)",
                        "Sodium (mg)",
                    ]
                )
                for line in lines:
                    item = items_repo.get_item(line.item_id)
                    if item:
                        writer.writerow(
                            [
                                item.item_id,
                                line.actual_servings,
                                item.calories * line.actual_servings,
                                item.protein_g * line.actual_servings,
                                item.sodium_mg * line.actual_servings,
                            ]
                        )

            tk.messagebox.showinfo("Export", f"Saved to {csv_path}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Export failed: {e}")
