# Manage Tracked Nutrients

Permanent, always-accessible screen backing all of `ref_daily_values`. The
first-run Setup Wizard's nutrient step is really just a friendlier
first-touch entry point into the `is_tracked` column of this same
underlying data — this screen lets the user revisit and change their mind
anytime (e.g. dropping a nutrient a year later after noticing it's always
zero).

```
┌────────────────────────────────────────────────────────────────┐
│  MANAGE TRACKED NUTRIENTS                                        │
├────────────────────────────────────────────────────────────────┤
│  [ ] Track All Vitamins/Minerals (master toggle)                 │
├────────────────────────────────────────────────────────────────┤
│  NUTRIENT NAME          DAILY VALUE    UNITS    TRACKED          │
│  ──────────────────────────────────────────────────────────────  │
│  [Calories            ]  (n/a)         kcal      [X]             │
│  [Total Fat           ]  (n/a)         g         [X]             │
│  [Sodium              ]  (n/a)         mg        [X]             │
│  [Vitamin D           ]  [20      ]    mcg       [X]             │
│  [Vitamin A           ]  [900000  ]    mcg       [ ]             │
│  [Folate              ]  [400     ]    mcg       [ ]             │
│  [Biotin              ]  [30      ]    mcg       [ ]             │
│  ...  (scrollable, ~35 rows total)                                │
├────────────────────────────────────────────────────────────────┤
│                             [ Save Changes ]                      │
└────────────────────────────────────────────────────────────────┘
```

Notes:
- `nutrient_name` and `dv_amount` are directly editable inline (text
  boxes), alongside the `is_tracked` checkbox, matching what SPEC.md §6 
  already declares editable for `ref_daily_values`.
- `nutrient_name` edits are expected to be extremely rare (the FDA
  renaming a nutrient) — SCD-style rationale: editable in place because 
  the underlying identity (`nutrient_id`) doesn't change, just the label.
- `dv_amount` edits are similarly rare (the FDA revising a daily
  value) but the mechanism is the same simple inline edit — no history is
  kept on this table; it's a small reference table the user can correct
  directly if the FDA changes a number.
- **UNITS column** is read-only and displays the unit of measurement for
  that nutrient (e.g., "g", "mcg", "kcal"). This is derived from the
  internal NUTRIENTS reference list and is for display/clarity only — it
  is not stored in `ref_daily_values`.
- Nutrients without an FDA daily-value number (e.g. calories) show "(n/a)"
  in the Daily Value column and have no edit box there.
- `is_tracked` is a pure visibility/reporting filter. Unchecking a nutrient
  never drops its column from `dim_items` or destroys historical data; it
  only hides that column from GUI entry forms and reporting output going
  forward.

## Explicitly out of scope: adding or removing a nutrient row

This screen supports **editing** existing `ref_daily_values` rows
(name, daily value, tracked flag) — it does NOT support adding a brand-new
nutrient row or deleting one outright. This was deliberately considered and
rejected:

- Each nutrient in `ref_daily_values` corresponds to a specific, named
  column in `dim_items` (e.g. `niacin_mcg`). Adding a genuinely new
  nutrient would require adding a new column to `dim_items` — a real
  schema change, not a data edit — and there is nowhere to actually store
  per-item values for a nutrient that has no corresponding `dim_items`
  column.
- A "pre-provision a handful of blank/reserved spare columns in
  `dim_items` for future nutrients" approach was considered and rejected
  as not worth the schema clutter, given the low frequency of this event
  (the FDA's last full add/drop of label nutrients was the 2016 label
  overhaul, phased in through 2020/2021 — a roughly once-per-decade-or-
  longer event, not something to design self-service tooling around).
- If the FDA ever does add or drop a nutrient from the label in the
  future, that should be treated as a deliberate one-off schema migration
  project (new `dim_items` column added, `ref_daily_values` row added,
  historical data backfilled or left null as appropriate) — not a runtime
  GUI action.
