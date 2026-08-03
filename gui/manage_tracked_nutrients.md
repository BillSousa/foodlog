# Manage Tracked Nutrients

Permanent, always-accessible screen backing all of `ref_daily_values`. The
first-run Setup Wizard's nutrient step is really just a friendlier
first-touch entry point into the `is_tracked` column of this same
underlying data — this screen lets the user revisit and change their mind
anytime (e.g. dropping a nutrient a year later after noticing it's always
zero).

# TODO: UPDATE THE COLUMNS IN THE IS DIAGRAM
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
│  [Sodium              ]  (n/a)         mcg       [X]             │
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
  Nutrient names as entered here must automatically propagate to all displayed 
  nutrient names in all other GUIs.
- TODO: ADD `nutrient_fda_label_unit`, read-only and displays the unit of
  measurement for that nutrient (e.g., "g", "mg", "kcal") that is displayed
  on actual food labels. This is from ref_daily_values.nutrient_fda_label_unit 
  and is for display/clarity only.
- TODO: ADD `nutrient_entry_unit` (MOST LIKELY THE SAME AS nutrient_fda_label_unit),
  read-only and displays the unit of measurement for that nutrient (e.g., "g",
  "mg", "kcal") that is displayed on the item create/edit GUI. This from
  ref_daily_values.nutrient_entry_unit and is for display/clarity only.
- `dv_amount` edits are similarly rare (the FDA revising a daily value) but
  the mechanism is the same simple inline edit — no history is kept on this
  table; it's a small reference table the user can correct directly if the
  FDA changes a number.
- Nutrients without an FDA daily-value number (e.g. calories) show "(n/a)"
  in the Daily Value column and have no edit box there.
- TODO: ADD `nutrient_dim_items_unit`, read-only and displays the unit of
  measurement for that nutrient (e.g., "g", "mcg", "kcal") that is used 
  when storing amount-per-serving quantities to `dim_items`. This is also
  the `dv_amount` unit of entry for this GUI. This is from
  ref_daily_values.nutrient_dim_items_unit and is for display/clarity only.
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
