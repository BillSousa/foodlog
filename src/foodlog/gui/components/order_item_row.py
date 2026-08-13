import tkinter as tk

from foodlog.calculations.ratios import ratio1, ratio2
from foodlog.calculations.to_negative import to_negative
from foodlog.models.dim_items import Item


class OrderItemRow:
    """Single order item row with live calculations."""

    def __init__(self, parent: tk.Widget, item: Item) -> None:
        """
        Initialize order item row.

        Args:
            parent: Parent widget
            item: Item to add to order
        """
        self.item = item
        self.frame = tk.Frame(parent, relief=tk.SUNKEN, borderwidth=1)
        self.on_change_callback = None

        self.blocks_var = tk.StringVar(value="1")
        self.servings_var = tk.StringVar(value=str(item.servings_per_block))
        self.sale_var = tk.StringVar(value="0")
        self.discount_var = tk.StringVar(value="0")
        self.coupon_var = tk.StringVar(value="0")

        self.servings_per_block = item.servings_per_block

        self.blocks_var.trace_add("write", self._on_blocks_change)
        self.servings_var.trace_add("write", self._on_servings_change)
        self.sale_var.trace_add("write", self._on_amount_change)
        self.discount_var.trace_add("write", self._on_amount_change)
        self.coupon_var.trace_add("write", self._on_amount_change)

        self._layout()

    def _layout(self) -> None:
        """Build row layout."""
        tk.Label(self.frame, text=self.item.units, width=20).pack(
            side=tk.LEFT, padx=5
        )

        tk.Label(self.frame, text="Blk:").pack(side=tk.LEFT, padx=2)
        tk.Entry(self.frame, textvariable=self.blocks_var, width=5).pack(
            side=tk.LEFT, padx=2
        )

        tk.Label(self.frame, text="Srv:").pack(side=tk.LEFT, padx=2)
        tk.Entry(self.frame, textvariable=self.servings_var, width=5).pack(
            side=tk.LEFT, padx=2
        )

        tk.Label(self.frame, text=f"${self.item.price:.2f}").pack(
            side=tk.LEFT, padx=10
        )

        tk.Label(self.frame, text="Sale:").pack(side=tk.LEFT, padx=2)
        tk.Entry(self.frame, textvariable=self.sale_var, width=5).pack(
            side=tk.LEFT, padx=2
        )

        tk.Label(self.frame, text="Disc:").pack(side=tk.LEFT, padx=2)
        tk.Entry(self.frame, textvariable=self.discount_var, width=5).pack(
            side=tk.LEFT, padx=2
        )

        tk.Label(self.frame, text="Coup:").pack(side=tk.LEFT, padx=2)
        tk.Entry(self.frame, textvariable=self.coupon_var, width=5).pack(
            side=tk.LEFT, padx=2
        )

        self.net_label = tk.Label(self.frame, text="$0.00", width=8)
        self.net_label.pack(side=tk.LEFT, padx=5)

        self.ratio_label = tk.Label(self.frame, text="0.0", width=6)
        self.ratio_label.pack(side=tk.LEFT, padx=5)

        delete_btn = tk.Button(self.frame, text="X", command=self._delete)
        delete_btn.pack(side=tk.RIGHT, padx=5)

    def _on_blocks_change(self, *args) -> None:
        """Update servings when blocks change."""
        try:
            blocks = float(self.blocks_var.get())
            servings = blocks * self.servings_per_block
            self.servings_var.set(f"{servings:.2f}")
        except ValueError:
            pass

    def _on_servings_change(self, *args) -> None:
        """Update blocks when servings change."""
        try:
            servings = float(self.servings_var.get())
            if self.servings_per_block > 0:
                blocks = servings / self.servings_per_block
                self.blocks_var.set(f"{blocks:.2f}")
        except ValueError:
            pass

    def _on_amount_change(self, *args) -> None:
        """Recalculate net price and ratios."""
        self._update_display()
        if self.on_change_callback:
            self.on_change_callback()

    def _update_display(self) -> None:
        """Update net price and ratio display."""
        try:
            servings = float(self.servings_var.get())
            price = self.item.price
            sale = to_negative(float(self.sale_var.get()))
            discount = to_negative(float(self.discount_var.get()))
            coupon = to_negative(float(self.coupon_var.get()))

            stated = price * servings
            net = stated + sale + discount + coupon

            self.net_label.config(text=f"${net:.2f}")

            r1 = ratio1(
                self.item.calories * servings,
                net,
                (self.item.sodium_mcg / 1000) * servings
            )
            self.ratio_label.config(text=f"{r1:.1f}")

        except ValueError:
            pass

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
            stated_price = self.item.price
            sale = to_negative(float(self.sale_var.get()))
            discount = to_negative(float(self.discount_var.get()))
            coupon = to_negative(float(self.coupon_var.get()))
            net = (stated_price * servings_ordered) + sale + discount + coupon

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
