import tkinter as tk
from tkinter import messagebox

from foodlog.database.connection import get_connection
from foodlog.repository.settings_repository import SettingsRepository


class SettingsWindow(tk.Toplevel):
    """Settings screen with cal_per_day_target and reset button."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize settings window."""
        super().__init__(parent)
        self.title("Settings")
        self.geometry("700x500")

        self.settings_repo = SettingsRepository()
        self._layout()

    def _layout(self) -> None:
        """Build settings layout."""
        title = tk.Label(
            self,
            text="Settings",
            font=("Arial", 14, "bold")
        )
        title.pack(pady=10)

        frame = tk.Frame(self)
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        tk.Label(frame, text="Daily Calorie Target:").pack(anchor=tk.W)
        self.cal_var = tk.StringVar(
            value=self.settings_repo.get_setting("cal_per_day_target") or "2000"
        )
        cal_entry = tk.Entry(frame, textvariable=self.cal_var, width=10)
        cal_entry.pack(anchor=tk.W, pady=5)

        tk.Label(
            frame, text="", font=("Arial", 1)
        ).pack()

        danger_label = tk.Label(
            frame,
            text="⚠ Danger Zone",
            font=("Arial", 11, "bold"),
            fg="red"
        )
        danger_label.pack(anchor=tk.W, pady=(20, 10))

        reset_btn = tk.Button(
            frame,
            text="Reset All Data",
            bg="#ffcccc",
            command=self._show_reset_confirmation
        )
        reset_btn.pack(anchor=tk.W, pady=5)

        tk.Label(
            frame,
            text="(Deletes all orders, items, consumption entries)",
            font=("Arial", 9),
            fg="gray"
        ).pack(anchor=tk.W)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=20, pady=20)

        save_btn = tk.Button(btn_frame, text="Save", command=self._save)
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _save(self) -> None:
        """Save settings."""
        try:
            cal = float(self.cal_var.get())
            if cal <= 0:
                messagebox.showerror("Invalid", "Calorie target must be > 0")
                return

            self.settings_repo.set_setting("cal_per_day_target", str(cal))
            messagebox.showinfo("Success", "Settings saved")
            self.destroy()

        except ValueError:
            messagebox.showerror("Invalid", "Enter a valid number")

    def _show_reset_confirmation(self) -> None:
        """Show reset confirmation dialog."""
        dialog = tk.Toplevel(self)
        dialog.title("Confirm Reset")
        dialog.geometry("400x200")

        tk.Label(
            dialog,
            text="This will delete ALL data.",
            font=("Arial", 12, "bold"),
            fg="red"
        ).pack(pady=10)

        tk.Label(
            dialog,
            text='Type "I understand" to confirm:',
            justify=tk.CENTER
        ).pack(pady=10)

        confirm_var = tk.StringVar()
        confirm_entry = tk.Entry(dialog, textvariable=confirm_var, width=30)
        confirm_entry.pack(pady=10, padx=20)

        def do_reset():
            if confirm_var.get() == "I understand":
                self._reset_data()
                dialog.destroy()
                self.destroy()
            else:
                messagebox.showerror("Mismatch", "Confirmation text incorrect")

        btn_frame = tk.Frame(dialog)
        btn_frame.pack(pady=10)

        reset_btn = tk.Button(
            btn_frame,
            text="Reset",
            bg="red",
            fg="white",
            command=do_reset
        )
        reset_btn.pack(side=tk.LEFT, padx=5)

        cancel_btn = tk.Button(
            btn_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _reset_data(self) -> None:
        """Reset all data (except ref_daily_values)."""
        try:
            conn = get_connection()
            cursor = conn.cursor()

            tables_to_clear = [
                "fact_consumption",
                "fact_order_lines",
                "fact_orders",
                "dim_items",
                "dim_product_names",
                "dim_categories",
            ]

            for table in tables_to_clear:
                cursor.execute(f"DELETE FROM {table}")

            self.settings_repo.set_setting("cal_per_day_target", "2000")

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "All data reset. App will exit.")

        except Exception as e:
            messagebox.showerror("Error", f"Reset failed: {e}")
