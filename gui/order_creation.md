# Order Creation / Planning

The most fully specified screen. Used for both new orders (status
`planning`) and re-opening existing ones at any later status (short of
`reconciled`, which soft-locks editing).

## Main grid

```
┌────────────────────────────────────────────────────────────────────────────────┐
│  ORDER CREATION / PLANNING                                    [Order #: --]    │
├────────────────────────────────────────────────────────────────────────────────┤
│ Order Date: [__________]   Delivery: [X]   Status: [Planning     ▼]           │
│ Delivery Charge: [____.__]   Tip: [____.__]                                    │
│ Tax: [____.__]              Order Coupon: [____.__]                            │
│                                    [ View Order Summary $ ]  [ View Nutrition ] │
├────────────────────────────────────────────────────────────────────────────────┤
│ Search: [bread___________]     Categories: [ ]Baking [X]Pasta [ ]Meat  ...     │
├────────────────────────────────────────────────────────────────────────────────┤
│ ITEM             BLOCKS  SERVINGS  PRICE      SALE     DISC    COUPON    NET      RATIO1  RATIO2 │
│ ────────────────────────────────────────────────────────────────────────────────────────────────│
│ Spaghetti, box   [2]  ⇄  [12]     $1.29 [✎]  [____]  [____]  [____]   $2.58     62.1    98.4    │
│ Linguine, box    [2]  ⇄  [12]     $1.39 [✎]  [____]  [____]  [____]   $2.78     59.8    95.0    │
│ Shells, box      [1]  ⇄  [6]      $1.29 [✎]  [-.50]  [____]  [____]   $0.79     71.3    112.2   │
│ ...                                                                                              │
├────────────────────────────────────────────────────────────────────────────────┤
│  RUNNING TOTALS (this order)                                                      │
│  Est. Net Cost: $46.33   Calories: 12,400   Sodium: 8,200mg                       │
│  Cal/Day target: 2000 (global)  →  Est. Days: 6.2                                 │
│  Sodium/Day: 1,058mg   Protein/Day: 62g   Ratio1: 60.2   Ratio2: 101.4            │
├────────────────────────────────────────────────────────────────────────────────┤
│                  [ Save Draft ]   [ Submit Order → "Ordered" ]                    │
└────────────────────────────────────────────────────────────────────────────────┘
```

Notes:
- **Header now includes `delivery_charge`, `tip`, `tax`, and
  `order_level_coupon`** as direct entry fields, alongside the fields
  already there (`order_date`, `is_delivery`/Delivery checkbox, `status`).
  All seven fields are `fact_orders` columns — grouping them together in
  the header (expanding it vertically rather than cramming them
  horizontally) keeps the header consistently "everything that's a
  property of the order itself," separate from the line-item grid below
  it. `order_level_coupon` is stored negative regardless of sign entered,
  same convention as the per-line sale/discount/coupon fields. These four
  fields remain also visible (read-only, rolled into the total) in the
  Order Summary ($) pop-out — editing happens here in the header, the
  pop-out just reflects the current values as part of the total.
- **BLOCKS ⇄ SERVINGS**: editing either box live-recalculates the other
  using `servings_per_block`. If `blocks_must_be_integer = 1` for that item,
  fractional blocks are rejected; if `0` (e.g. variable-weight chicken),
  fractional blocks are allowed.
- **RATIO1 / RATIO2 columns**: recalculate when the user exits a text box
  (not per keystroke), using live in-row qty/sale/discount/coupon values —
  not the static `dim_items.ratio1`/`ratio2` baseline.
- **Cal/Day target** shown here is read-only, pulled from the global
  `settings.cal_per_day_target` — not editable per-order (see SPEC.md
  §6/§10 edit history — this was originally sketched as a per-order input
  field, corrected to reference the global setting instead).
- Search box and category checkboxes work together (not either/or) — check
  "Pasta," then narrow further by typing, or vice versa.

## Price update popup

Opened via the `[✎]` icon next to any item's PRICE column.

```
┌───────────────────────────┐
│ Update Stated Price        │
│ Item: Spaghetti, box       │
│ New Price: [____.__]       │
│      [Save]  [Cancel]      │
└───────────────────────────┘
```
Writes directly to `dim_items.price` (SCD1 overwrite — no history kept).
Input must be 2-decimal currency format.

## "View Order Summary $" pop-out

```
┌──────────────────────────────────────────────────────┐
│  ORDER #42 — MONEY SUMMARY                             │
├──────────────────────────────────────────────────────┤
│  PASTA                                                 │
│   Spaghetti x2      $1.29  sale:--  disc:--  = $2.58  │
│   Linguine  x2      $1.39  sale:--  disc:--  = $2.78  │
│   Shells    x1      $1.29  sale:-.50 disc:-- = $0.79  │
│  MEAT                                                  │
│   ...                                                  │
│  (UNCATEGORIZED)                                       │
│   Bottled Water x3  $0.89  sale:--  disc:-- = $2.67   │
├──────────────────────────────────────────────────────┤
│  Subtotal (net):        $46.33                         │
│  Delivery Charge:        $9.99                         │
│  Tip:                    $5.00                         │
│  Tax:                    $2.10                         │
│  Order Coupon:          -$5.00                         │
│  ─────────────────────────────                         │
│  TOTAL NET COST (calculated): $58.42                   │
│                                                        │
│  Compare this number manually against your             │
│  actual invoice.                                       │
│                                                        │
│                   [ DUMP TO CSV ]                      │
└──────────────────────────────────────────────────────┘
```
Money-only window — deliberately no ratio columns here (view the Nutrition
pop-out alongside if ratios are wanted next to cost). `TOTAL NET COST` is
`fact_orders.total_net_cost`, computed as SUM(line `net_price`) +
delivery_charge + tip + tax + order_level_coupon. There is no separate
manually-entered "invoice total" field — the user reconciles this computed
number directly against the real invoice/receipt off-screen.

Items with `category_id = NULL` are grouped under a display-only
**"(Uncategorized)"** heading, shown above. This label is generated at
display time only and is never written to `dim_categories`.

**CSV export button** (bottom of window): exports only this window's data
for the current order — a separate, self-contained feature, unrelated to
any future Reporting-screen CSV/Excel export (see `reporting.md`). The
file drops in the same folder as the FoodLog program itself (no
path-picker dialog). Filename convention: order number + a label
identifying it as the money summary + a date/time stamp (e.g.
`order_42_money_summary_2026-07-25_1830.csv`).

## "View Nutrition" pop-out

```
┌────────────────────────────────────────────────────────────────────────────┐
│  ORDER #42 — NUTRITION SUMMARY                                              │
├────────────────────────────────────────────────────────────────────────────┤
│ ITEM              CAL   PROTEIN  CARBS  FAT  SODIUM  ...  RATIO1  RATIO2   │
│ ── PASTA ──────────────────────────────────────────────────────────────    │
│  Spaghetti x2      400    14g     78g    2g   10mg          62.1   98.4    │
│  Linguine  x2      410    15g     80g    2g   12mg          59.8   95.0    │
│  Shells    x1      200     7g     40g    1g    5mg          71.3   112.2   │
│  » Subtotal:      1010    36g    198g    5g   27mg          63.4   101.1   │
│ ── MEAT ───────────────────────────────────────────────────────────────    │
│  Chicken Thighs x2 620    98g      0g   22g  340mg          40.2    55.9   │
│  » Subtotal:       620    98g      0g   22g  340mg          40.2    55.9   │
│ ── (UNCATEGORIZED) ─────────────────────────────────────────────────────   │
│  Bottled Water x3    0     0g      0g    0g    0mg           2.1     3.4   │
│  » Subtotal:         0     0g      0g    0g    0mg           2.1     3.4   │
├────────────────────────────────────────────────────────────────────────────┤
│  GRAND TOTAL:     12400  380g   ...g   ...g  8200mg   (all nutrients)       │
│                                                          RATIO1   RATIO2    │
│                                                           60.2     101.4    │
│  Cal/Day target: 2000 (global) → Days: 6.2                                 │
│  Per-Day:  Sodium 1,058mg | Protein 49g | ...                               │
│                                                                            │
│                                 [ DUMP TO CSV ]                            │
└────────────────────────────────────────────────────────────────────────────┘
```
Rows grouped by category, subtotal row after each group, grand total at
bottom. All figures (nutrients and ratios) computed live from actual order
quantities and current prices/discounts. Columns scroll/truncate
horizontally since there could be ~35 nutrient columns.

Items with `category_id = NULL` are grouped under the same display-only
**"(Uncategorized)"** heading described above.

**CSV export button** (bottom of window): exports only this window's data
for the current order, with the same file-location rule and filename
convention as the Order Summary ($) export above (order number + a label
identifying it as the nutrition summary + a date/time stamp) — again,
unrelated to any future Reporting-screen export.
