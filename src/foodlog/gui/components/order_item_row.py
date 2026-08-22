import tkinter as tk

from foodlog.calculations.to_negative import to_negative
from foodlog.gui.components.live_ratio_calculator import compute_live_ratios
from foodlog.gui.dialogs.price_update_popup import PriceUpdatePopup
from foodlog.models.dim_items import Item
from foodlog.models.fact_order_lines import OrderLine
from foodlog.repository.product_names_repository import ProductNamesRepository
from foodlog.validation.constraints import (
    ValidationError, validate_integer_blocks, validate_price
)


class OrderItemRow:
    """Single order item row with live calculations."""

    def __init__(
        self,
        parent: tk.Widget,
        item: Item,
        existing_line: OrderLine | None = None
    ) -> None:
        """
        Initialize order item row.

        Args:
            parent: Parent widget
            item: Item to add to order
            existing_line: Optional existing order line for reopening/editing
        """
        self.item = item
        product_name = ProductNamesRepository().get_product_name(
            item.name_id
        )
        self.product_name = (
            product_name.name_text if product_name else ""
        )
        self.frame = tk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        self.on_change_callback = None
        self._updating = False
        self.servings_per_block = item.servings_per_block

        self.line_id = existing_line.line_id if existing_line else None

        if existing_line:
            self.price_var = tk.StringVar(
                value=str(existing_line.stated_price)
            )
            self.last_valid_price = str(existing_line.stated_price)
            blocks_value = (
                existing_line.actual_servings / self.servings_per_block
            )
            self.blocks_var = tk.StringVar(value=f"{blocks_value:.2f}")
            self.last_valid_blocks = f"{blocks_value:.2f}"
            self.servings_var = tk.StringVar(
                value=f"{existing_line.actual_servings:.2f}"
            )
            self.sale_var = tk.StringVar(
                value=f"{existing_line.sale:.2f}"
            )
            self.discount_var = tk.StringVar(
                value=f"{existing_line.discount:.2f}"
            )
            self.coupon_var = tk.StringVar(
                value=f"{existing_line.coupon:.2f}"
            )
        else:
            self.blocks_var = tk.StringVar(value="1")
            self.servings_var = tk.StringVar(
                value=str(item.servings_per_block)
            )
            self.sale_var = tk.StringVar(value="0.00")
            self.discount_var = tk.StringVar(value="0.00")
            self.coupon_var = tk.StringVar(value="0.00")
            self.price_var = tk.StringVar(value=str(item.price))
            self.last_valid_blocks = "1"
            self.last_valid_price = str(item.price)

        self.blocks_var.trace_add("write", self._on_blocks_change)
        self.servings_var.trace_add("write", self._on_servings_change)

        self.blocks_entry: tk.Entry | None = None
        self.servings_entry: tk.Entry | None = None
        self.price_entry: tk.Entry | None = None
        self.update_price_btn: tk.Button | None = None
        self.sale_entry: tk.Entry | None = None
        self.discount_entry: tk.Entry | None = None
        self.coupon_entry: tk.Entry | None = None
        self.delete_btn: tk.Button | None = None

        self._layout()

    def _layout(self) -> None:
        """Build row layout."""
        tk.Label(self.frame, text=self.product_name, width=20).pack(
            side=tk.LEFT, padx=5
        )

        tk.Label(self.frame, text="Blk:").pack(side=tk.LEFT, padx=2)
        self.blocks_entry = tk.Entry(self.frame, textvariable=self.blocks_var, width=5)
        self.blocks_entry.pack(side=tk.LEFT, padx=2)

        tk.Label(self.frame, text="Srv:").pack(side=tk.LEFT, padx=2)
        self.servings_entry = tk.Entry(self.frame, textvariable=self.servings_var, width=5)
        self.servings_entry.pack(side=tk.LEFT, padx=2)

        self.price_entry = tk.Entry(self.frame, textvariable=self.price_var,
                                    width=8)
        self.price_entry.pack(side=tk.LEFT, padx=10)
        self.price_entry.bind("<FocusOut>", self._on_price_change)

        self.update_price_btn = tk.Button(
            self.frame, text="🔧", command=self._on_update_price_click, width=2
        )
        self.update_price_btn.pack(side=tk.LEFT, padx=2)

        tk.Label(self.frame, text="Sale:").pack(side=tk.LEFT, padx=2)
        self.sale_entry = tk.Entry(self.frame, textvariable=self.sale_var,
                                   width=5)
        self.sale_entry.pack(side=tk.LEFT, padx=2)
        self.sale_entry.bind("<FocusOut>", self._on_amount_change)

        tk.Label(self.frame, text="Disc:").pack(side=tk.LEFT, padx=2)
        self.discount_entry = tk.Entry(
            self.frame, textvariable=self.discount_var, width=5
        )
        self.discount_entry.pack(side=tk.LEFT, padx=2)
        self.discount_entry.bind("<FocusOut>", self._on_amount_change)

        tk.Label(self.frame, text="Coup:").pack(side=tk.LEFT, padx=2)
        self.coupon_entry = tk.Entry(
            self.frame, textvariable=self.coupon_var, width=5
        )
        self.coupon_entry.pack(side=tk.LEFT, padx=2)
        self.coupon_entry.bind("<FocusOut>", self._on_amount_change)

        self.net_label = tk.Label(self.frame, text="$0.00", width=8)
        self.net_label.pack(side=tk.LEFT, padx=5)

        self.ratio_label = tk.Label(self.frame, text="0.0", width=6)
        self.ratio_label.pack(side=tk.LEFT, padx=5)

        self.ratio2_label = tk.Label(self.frame, text="0.0", width=6)
        self.ratio2_label.pack(side=tk.LEFT, padx=5)

        self.delete_btn = tk.Button(self.frame, text="X", command=self._delete)
        self.delete_btn.pack(side=tk.RIGHT, padx=5)

        self._update_display()

    def _on_blocks_change(self, *args) -> None:
        """Update servings when blocks change."""
        if self._updating:
            return
        self._updating = True
        try:
            blocks = float(self.blocks_var.get())
            validate_integer_blocks(blocks, self.item.blocks_must_be_integer)
            servings = blocks * self.servings_per_block
            self.servings_var.set(f"{servings:.2f}")
            self.last_valid_blocks = self.blocks_var.get()
        except (ValueError, ValidationError):
            self.blocks_var.set(self.last_valid_blocks)
        finally:
            self._updating = False

    def _on_servings_change(self, *args) -> None:
        """Update blocks when servings change."""
        if self._updating:
            return
        self._updating = True
        try:
            servings = float(self.servings_var.get())
            if self.servings_per_block > 0:
                blocks = servings / self.servings_per_block
                self.blocks_var.set(f"{blocks:.2f}")
        except ValueError:
            pass
        finally:
            self._updating = False

    def _on_amount_change(self, event) -> None:
        """Recalculate net price and ratios on focus-out."""
        self._update_display()
        if self.on_change_callback:
            self.on_change_callback()

    def _update_display(self) -> None:
        """Update net price and ratio display."""
        try:
            servings = float(self.servings_var.get())
            price = float(self.price_var.get())
            sale = to_negative(float(self.sale_var.get()))
            discount = to_negative(float(self.discount_var.get()))
            coupon = to_negative(float(self.coupon_var.get()))

            stated = (price / self.servings_per_block) * servings
            net = stated + sale + discount + coupon

            self.net_label.config(text=f"${net:.2f}")

            r1, r2 = compute_live_ratios(
                self.item.calories * servings,
                net,
                self.item.sodium_mcg * servings,
                self.item.total_fat_g * servings
            )
            self.ratio_label.config(text=f"{r1:.1f}")
            self.ratio2_label.config(text=f"{r2:.1f}")

        except ValueError:
            pass

    def _on_price_change(self, event) -> None:
        """Validate and update price on focus-out."""
        try:
            price = float(self.price_var.get())
            validate_price(price)
            self.last_valid_price = self.price_var.get()
            self._update_display()
            if self.on_change_callback:
                self.on_change_callback()
        except (ValueError, ValidationError):
            self.price_var.set(self.last_valid_price)

    def _on_update_price_click(self) -> None:
        """Open price update popup for dim_items.price."""
        def on_price_saved(new_price: float) -> None:
            self.item.price = new_price
            self.price_var.set(str(new_price))
            self.last_valid_price = str(new_price)
            self._update_display()
            if self.on_change_callback:
                self.on_change_callback()

        PriceUpdatePopup(
            self.frame,
            self.item.item_id,
            self.item.price,
            on_price_saved,
        )

    def _delete(self) -> None:
        """Delete this row."""
        self.frame.destroy()

    def get_frame(self) -> tk.Frame:
        """Return the frame widget."""
        return self.frame

    def get_values(self) -> dict:
        """Get row values for database."""
        try:
            servings_ordered = float(self.servings_var.get())
            stated_price = float(self.price_var.get())
            sale = to_negative(float(self.sale_var.get()))
            discount = to_negative(float(self.discount_var.get()))
            coupon = to_negative(float(self.coupon_var.get()))
            net = (stated_price / self.servings_per_block) * servings_ordered + sale + discount + coupon

            return {
                "item_id": self.item.item_id,
                "servings_ordered": servings_ordered,
                "actual_servings": servings_ordered,
                "stated_price": stated_price,
                "sale": sale,
                "discount": discount,
                "coupon": coupon,
                "net_price": net,
            }
        except ValueError:
            return {}

    def set_locked(self, locked: bool) -> None:
        """Disable/enable editable widgets.

        Parameters
        ----------
        locked : bool
            If True, disable all editable entry widgets and the delete
            button. If False, enable them.
        """
        state = tk.DISABLED if locked else tk.NORMAL

        if self.blocks_entry:
            self.blocks_entry.config(state=state)
        if self.servings_entry:
            self.servings_entry.config(state=state)
        if self.price_entry:
            self.price_entry.config(state=state)
        if self.update_price_btn:
            self.update_price_btn.config(state=state)
        if self.sale_entry:
            self.sale_entry.config(state=state)
        if self.discount_entry:
            self.discount_entry.config(state=state)
        if self.coupon_entry:
            self.coupon_entry.config(state=state)
        if self.delete_btn:
            self.delete_btn.config(state=state)
