import tkinter as tk
from tkinter import messagebox, ttk

from foodlog.gui.components.item_search_filter import ItemSearchFilter
from foodlog.gui.components.live_ratio_calculator import compute_live_ratios
from foodlog.gui.components.order_header import OrderHeader
from foodlog.gui.components.order_item_row import OrderItemRow
from foodlog.gui.components.order_totals import OrderTotals
from foodlog.models.fact_order_lines import OrderLine
from foodlog.models.fact_orders import Order
from foodlog.repository.items_repository import ItemsRepository
from foodlog.repository.orders_repository import OrdersRepository
from foodlog.repository.settings_repository import SettingsRepository
from foodlog.validation.constraints import ValidationError


class OrderCreationWindow(tk.Toplevel):
    """Order creation and planning screen."""

    def __init__(self, parent: tk.Widget) -> None:
        """Initialize order creation window."""
        super().__init__(parent)
        self.title("Create Order")
        self.geometry("900x700")

        self.order_items: list[dict] = []
        self.order_id: int | None = None

        settings_repo = SettingsRepository()
        cal_target = float(
            settings_repo.get_setting("cal_per_day_target") or "2000"
        )

        self._layout(cal_target)

    def _layout(self, cal_target: float) -> None:
        """Build order creation layout."""
        self.header = OrderHeader(self)
        self.header.get_frame().pack(fill=tk.X)

        self.search_filter = ItemSearchFilter(self)
        self.search_filter.get_frame().pack(fill=tk.X, padx=10, pady=10)

        grid_frame = tk.LabelFrame(self, text="Order Items")
        grid_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.items_frame = tk.Frame(grid_frame)
        self.items_frame.pack(fill=tk.BOTH, expand=True)

        btn_row = tk.Frame(self)
        btn_row.pack(pady=5)

        self.add_item_btn = tk.Button(
            btn_row,
            text="Add Item to Order",
            command=self._show_item_picker
        )
        self.add_item_btn.pack(side=tk.LEFT, padx=5)

        summary_btn = tk.Button(
            btn_row,
            text="View Order Summary $",
            command=self._view_money_summary
        )
        summary_btn.pack(side=tk.LEFT, padx=5)

        nutrition_btn = tk.Button(
            btn_row,
            text="View Nutrition",
            command=self._view_nutrition_summary
        )
        nutrition_btn.pack(side=tk.LEFT, padx=5)

        self.totals = OrderTotals(self, cal_target)
        self.totals.get_frame().pack(fill=tk.X, padx=10, pady=10)

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill=tk.X, padx=10, pady=10)

        save_btn = tk.Button(btn_frame, text="Save Draft", command=self._save)
        save_btn.pack(side=tk.LEFT, padx=5)

        close_btn = tk.Button(btn_frame, text="Close", command=self.destroy)
        close_btn.pack(side=tk.RIGHT, padx=5)

    def _show_item_picker(self) -> None:
        """Show item picker dialog."""
        search_text = self.search_filter.get_search_text()
        repo = ItemsRepository()

        if search_text:
            items = repo.search_items(search_text)
        else:
            items = repo.list_active_items()

        if not items:
            messagebox.showwarning("No items", "No items found")
            return

        dialog = tk.Toplevel(self)
        dialog.title("Select Item")
        dialog.geometry("400x300")

        listbox = tk.Listbox(dialog, height=12)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for item in items:
            text = f"{item.units} — ${item.price:.2f}"
            listbox.insert(tk.END, text)

        def add_selected():
            selection = listbox.curselection()
            if selection:
                item = items[selection[0]]
                self._add_item_row(item)
                dialog.destroy()

        btn = tk.Button(dialog, text="Add Item", command=add_selected)
        btn.pack(pady=10)

    def _add_item_row(self, item) -> None:
        """Add item row to order grid."""
        row = OrderItemRow(self.items_frame, item)
        row.on_change_callback = self._update_totals
        row.get_frame().pack(fill=tk.X, pady=2)

        self.order_items.append({"row": row, "item": item})
        self._update_totals()

    def _update_totals(self) -> None:
        """Recalculate order totals."""
        total_cost = 0.0
        total_calories = 0.0
        total_protein = 0.0
        total_sodium_mcg = 0.0
        total_fat_g = 0.0

        for entry in self.order_items:
            values = entry["row"].get_values()
            if values:
                total_cost += values["net_price"]
                item = entry["item"]
                multiplier = values["actual_servings"]
                total_calories += item.calories * multiplier
                total_protein += item.protein_g * multiplier
                total_sodium_mcg += item.sodium_mcg * multiplier
                total_fat_g += item.total_fat_g * multiplier

        total_sodium_mg = total_sodium_mcg / 1000
        r1, r2 = compute_live_ratios(
            total_calories, total_cost, total_sodium_mcg, total_fat_g
        )
        self.totals.update(
            total_cost, total_calories, total_protein, total_sodium_mg,
            r1, r2
        )

    def _view_money_summary(self) -> None:
        """View order summary (money) pop-out."""
        if not self.order_id:
            messagebox.showwarning("Save first", "Save order before viewing summary")
            return

        from foodlog.gui.windows.order_summary_window import OrderSummaryWindow
        OrderSummaryWindow(self, self.order_id)

    def _view_nutrition_summary(self) -> None:
        """View nutrition summary pop-out."""
        if not self.order_id:
            messagebox.showwarning("Save first", "Save order before viewing summary")
            return

        from foodlog.gui.windows.nutrition_summary_window import NutritionSummaryWindow
        NutritionSummaryWindow(self, self.order_id)

    def _save(self) -> None:
        """Save order as draft with line items."""
        if not self.order_items:
            messagebox.showwarning("Empty", "Add at least one item")
            return

        header = self.header.get_values()
        order = Order(
            order_date=header["order_date"],
            is_delivery=header["is_delivery"],
            status="planning"
        )

        try:
            orders_repo = OrdersRepository()
            self.order_id = orders_repo.create_order(order)

            for entry in self.order_items:
                values = entry["row"].get_values()
                if values:
                    line = OrderLine(
                        order_id=self.order_id,
                        item_id=values["item_id"],
                        servings_ordered=values["servings_ordered"],
                        actual_servings=values["actual_servings"],
                        stated_price=values["stated_price"],
                        sale=values["sale"],
                        discount=values["discount"],
                        coupon=values["coupon"],
                        net_price=values["net_price"],
                    )
                    from foodlog.repository.order_lines_repository import (
                        OrderLinesRepository,
                    )
                    lines_repo = OrderLinesRepository()
                    lines_repo.create_order_line(line)

            # Calculate and update order-level totals from all line items
            total_cost = 0.0
            total_calories = 0.0
            total_protein = 0.0
            total_carbs = 0.0
            total_fat = 0.0
            total_sodium_mg = 0.0

            for entry in self.order_items:
                values = entry["row"].get_values()
                if values:
                    total_cost += values["net_price"]
                    item = entry["item"]
                    multiplier = values["actual_servings"]
                    total_calories += item.calories * multiplier
                    total_protein += item.protein_g * multiplier
                    total_carbs += item.total_carbs_g * multiplier
                    total_fat += item.total_fat_g * multiplier
                    total_sodium_mg += item.sodium_mcg * multiplier / 1000

            # Add header-level amounts to net cost
            header_values = self.header.get_values()
            total_cost += header_values["delivery_charge"]
            total_cost += header_values["tip"]
            total_cost += header_values["tax"]
            total_cost += header_values["order_level_coupon"]

            # Calculate ratios
            r1, r2 = compute_live_ratios(
                total_calories, total_cost,
                total_sodium_mg * 1000,
                total_fat
            )

            # Update database with calculated totals
            orders_repo.update_order_totals(
                self.order_id,
                total_net_cost=total_cost,
                total_calories=total_calories,
                total_protein_g=total_protein,
                total_carbs_g=total_carbs,
                total_fat_g=total_fat,
                total_sodium_mg=total_sodium_mg,
                ratio1=r1,
                ratio2=r2
            )

            messagebox.showinfo("Success", f"Order #{self.order_id} saved")
            self.destroy()
        except ValidationError as e:
            messagebox.showerror("Save failed", str(e))

    def _set_locked(self, locked: bool) -> None:
        """Disable/enable every editable widget except the status field.

        Called with locked=True right after loading an order whose
        status is 'reconciled', and locked=False whenever the status
        dropdown is changed away from 'reconciled'.

        Parameters
        ----------
        locked : bool
            If True, disable all editable widgets except status Combobox.
            If False, enable them.
        """
        self.header.set_locked(locked)

        for entry in self.order_items:
            entry["row"].set_locked(locked)

        self.add_item_btn.config(state=tk.DISABLED if locked else tk.NORMAL)
