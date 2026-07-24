# Manage Items

Intentionally left loose per SPEC.md §9 — low architectural risk, standard
search/select/edit/save form, to be brute-forced with Claude Code. This
rough sketch exists as a starting reference point, not a locked design.

```
┌────────────────────────────────────────────────────────────────┐
│  MANAGE ITEMS                                                    │
├────────────────────────────────────────────────────────────────┤
│ Search: [___________]   Categories: [ ]Pasta [ ]Dairy [ ]Meat ... │
│                                                     [ + New Item ] │
├────────────────────────────────────────────────────────────────┤
│ ITEM                    CATEGORY   PRICE   ACTIVE   RATIO1  RATIO2│
│ ────────────────────────────────────────────────────────────────  │
│ Spaghetti, box          Pasta      $1.29    [X]      62.1    98.4 │
│ Giant Round-Top White 2 Baking     $2.49    [ ]      ...     ...  │
│ Giant Round-Top White 3 Baking     $2.59    [X]      ...     ...  │
│ ...                                                                │
├────────────────────────────────────────────────────────────────┤
│                          [ Edit Selected Item ]                   │
└────────────────────────────────────────────────────────────────┘
```

Selecting "Edit Selected Item" or "+ New Item" opens an edit form
containing:

```
┌────────────────────────────────────────────────────────────────┐
│  EDIT / CREATE ITEM                                              │
├────────────────────────────────────────────────────────────────┤
│  Name:              [__________________________]  (→ dim_product_names)│
│  Category:          [ Pasta          ▼ ]  (dropdown, from dim_categories)│
│  Price (per block):  [____.__]                                    │
│  Units:              [ g            ▼ ]  (shared by both fields below)│
│  Container Size:     [___] g   (total package size, from label)   │
│  Serving Size:       [___] g   (one serving size, from label)      │
│  Servings per block (computed): 6.25   (read-only — container ÷ serving)│
│  Blocks must be integer:  [X]                                     │
│  Active:                  [X]                                     │
│  Glycemic Index (optional): [___]                                 │
│                                                                    │
│  Nutrition panel (only tracked nutrients shown, per                │
│  "Manage Tracked Nutrients" settings):                              │
│    Calories: [___]   Protein (g): [___]   Sodium (mg): [___]       │
│    Total Fat (g): [___]   ... (all currently-tracked fields)        │
│                                                                    │
│              [ Save ]              [ Cancel ]                     │
└────────────────────────────────────────────────────────────────┘
```

Notes:
- **Servings per block is computed, not typed in.** It updates live as
  `Container Size` and `Serving Size` are filled in
  (`servings_per_block = container_size / serving_size`). `Units` applies 
  to both fields — no unit conversion is performed; the user must ensure 
  both figures share the same unit, exactly as they normally already do 
  on real packaging.
- Saving nutrition changes on an existing item does NOT overwrite — it
  should prompt "this looks like a nutrition change; create a new item
  version?" per the SCD2 rule, rather than silently mutating history.
  (Exact confirmation-flow wording left to iteration.)
- Nutrition fields shown are filtered to only whatever is currently
  `is_tracked = 1` in `ref_daily_values` — untracked nutrients are hidden
  from this form entirely.
