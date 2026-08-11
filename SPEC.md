# FoodLog — Product Specification

## 1. Purpose

FoodLog is a fully Python-based executable program that can run on Linux or 
Windows. Humans can populate a database with food purchase and consumption 
data that enables them to track, analyze, and report on their nutrition profile 
and food costs, including:
- Money spent on groceries
- Per-item nutrition and cost data on every purchase
- Running lifetime "servings consumed" totals per item

Food log also allows users to:
- Do pre-purchase "sandbox engineering" of orders to hit nutrition/cost targets
- Do post-purchase reconciliation of actual goods in-hand and prices paid
  against the actual invoice

The core goal of this program is to facilitate fast, convenient data entry and 
analysis via simple interfaces and a turnkey data storage mechanism.

## 2. Non-Goals

- No meal-by-meal / daily logging. Users do NOT need to log every meal.
  Consumption logging is "batch" granularity, with batch frequency determined 
  at the discretion of the user. Consumption entries are timestamped when the 
  user enters data.
- No multi-tenant / cloud / web-hosted architecture. No user accounts.
- No JavaScript, Electron, or web server. Pure Python.
- Not forcing category classification or nutrient tracking as mandatory —
  everything the user doesn't care about should be skippable, except the
  one-time nutrient Setup Wizard (see §8), which is intentionally mandatory
  at first run.

## 3. Technology Stack

- **Language:** Python only (no C++, no JavaScript, no Electron).
- **Database:** SQLite (`sqlite3` stdlib module). Single portable `.db` file.
- **GUI:** Tkinter (stdlib). No web server, no browser-based UI.
- **Charting:** `matplotlib` only, embedded in Tkinter via
  `matplotlib.backends.backend_tkagg.FigureCanvasTkAgg`.
  Do not use Plotly, as it is browser/JS-oriented and would require an embedded
  web-view, which introduces too much complexity.
- **Reporting/Analytics screens:** deliberately NOT specified in detail here —
  this is "cheap to iterate" territory, to be brute-forced with Claude Code
  and refined by reacting to a working prototype. CSV/Excel export is perhaps
  also a valid "poor man's" visualization path — dump to CSV and let Excel do it.

## 4. Packaging & Distribution

- **Goal:** Runs identically off a single thumb drive on both Windows and
  Linux, with the SAME database file, no installation required, distributable
  via GitHub.
- **No Python installation required for the end user.** Package via
  **PyInstaller**:
  - Windows: bundle to `foodlog_win.exe` (self-contained, no Python needed on
    host machine).
  - Linux: bundle to a `foodlog_linux` binary using PyInstaller run on Linux
    (does not cross-compile from Windows — must be built on an actual Linux
    machine). A plain `.py` script is a fallback for Linux (most distros ship
    Python 3 already) but the PyInstaller binary is preferred for a consistent
    double-click experience on both OSes with no terminal use.
  - Do NOT attempt to use the Windows "embeddable" Python package to run on
    Linux — it's Windows-only; Wine is not an acceptable workaround.
- **No Electron / local web server (Flask/Jupyter-style)** — evaluated and
  rejected: too heavy, introduces a second runtime/language, adds
  server/port/browser dependency complexity not justified for this tool.
- **Folder structure** (keeps thumb-drive root clean when coexisting with
  other files):

  ```
  /ThumbDrive/
    ├── (other unrelated stuff)
    ├── FoodLog/
    │     ├── foodlog_win.exe
    │     ├── foodlog_linux
    │     ├── foodlog.db          (shared SQLite file — same data, both OSes)
    │     └── (source .py files)
    ├── Run FoodLog (Windows).lnk   → FoodLog/foodlog_win.exe
    └── Run FoodLog (Linux)          → FoodLog/foodlog_linux
  ```

- **Critical implementation rule:** The executable must locate its own
  containing folder at runtime (e.g. via `sys.executable` per PyInstaller's
  documented pattern) and open `foodlog.db` **relative to that location** —
  never a hardcoded absolute path. This is required for the drive to work
  when plugged into different machines with different mount points/drive
  letters.
- **Multi-project support = file-level, not app-level.** No in-app project
  manager. To run a second independent project, the user copies the whole
  `FoodLog/` folder and renames it. The app must never hardcode its own
  folder/file name internally — all paths must be self-discovered/relative so
  renaming the folder doesn't break anything.
- **GitHub distribution:** source code (Python files, schema/init scripts) is
  committed to the repo. The user's actual `foodlog.db` (personal data) is
  `.gitignore`'d — never committed. Anyone cloning the repo gets a fresh,
  empty database via an init script.

## 5. Core Design Principles (carried through the whole schema)

- **SCD Type 1** (price): overwrite in place, no history kept in the
  dimension table.
- **SCD Type 2** (nutrition info): when a product's nutrition info changes
  (e.g. manufacturer reformulates), create a NEW `dim_items` row rather than
  overwriting. Old rows remain valid for historical `fact_order_lines` /
  `fact_consumption` rows that reference them. The product's display name can
  stay identical across new rows (e.g. "GIANT Round-Top White Sandwich
  Bread") — items are identified by surrogate key (`item_id`), never by name.
- **Fact table price snapshot:** `dim_items.price` (Type 1 SCD) gets
  **copied/locked into `fact_order_lines`** at the moment an item is added to
  an order. This preserves historical pricing on the fact table without
  needing SCD2 complexity on price in the dimension.
- **No store-of-purchase tracking.** A change of grocery store requires no
  special schema handling — it's absorbed naturally by the same "new item
  version" mechanism as any other product change, and cost/calorie aggregates
  are store-agnostic by design.
- **Servings, not blocks, are the fundamental persisted unit.** "Blocks"
  (e.g. "1 box of pasta") exist only as a data-entry convenience in the GUI
  (live-converting between "blocks" and "servings" via `servings_per_block`).
  Only `servings` values are stored in `fact_order_lines`. Rationale: all
  nutrition math is per-serving; blocks don't cleanly apply to variable-weight
  items (e.g. chicken) in the first place.
- **`net_price` and all downstream cost/nutrition math always derive from
  `actual_servings`, never `servings_ordered`.** `servings_ordered` is a
  frozen historical snapshot for audit/comparison only (e.g. "how often does
  a chicken order come up short").
- **`actual_servings` is editable on any line item, at any time, as long as
  the parent order's `status` is not `reconciled`.** This is a universal
  rule — NOT limited to variable-weight items. Any item can be shorted/out of
  stock, not just weight-variable ones. (Originally considered a
  `can_be_modified` flag to gate what products allow `actual_servings` to be
  modified — REJECTED; dropped from schema entirely. The `status` soft-lock is
  the only gate needed.)
- **A fully out-of-stock line item is NOT deleted from `fact_order_lines`.**
  The row stays, with `actual_servings` set to `0`. This was explicitly
  considered (deleting the row entirely) and rejected in favor of keeping
  it, because: (1) it preserves `servings_ordered` as an honest audit trail
  of what was originally attempted, consistent with how a *partial*
  shortfall is already handled; and (2) all downstream math already
  degrades gracefully to zero (`net_price`, nutrition totals) with no
  special-case logic needed — the line simply shows as $0 / 0 calories in
  the Order Summary and Nutrition Summary windows.
- **`fact_orders.status` values:** `planning → ordered → delivered →
  reconciled`. Set manually by the user via a dropdown — the program never
  infers status. In-store trips skip `ordered` and ultimately move to
  `reconciled` after post-purchase reconciliation of goods in-hand against the
  paper receipt.
  `reconciled` is a **soft lock only** — it disables editing of that
  `order_id`'s `fact_orders` header fields and `fact_order_lines` rows, but
  toggling `status` away from `reconciled` (to anything else) re-enables
  editing. This lock does NOT extend to `dim_items` or `fact_consumption` —
  those remain unaffected by any single order's status.
- **Sale/discount/coupon entered by the user in any sign are always stored
  as negative values** in `fact_order_lines` (so a user typing either `0.50`
  or `-0.50` both land as `-0.50`).
- **`fact_consumption` is fully independent of `fact_order_lines`** — no
  foreign key between them. They relate only implicitly through shared
  `item_id`. This is intentional: consumption is a pooled running total per
  item, not tied to which specific order/purchase it came from. "On-hand" is
  a derived, not stored, value:

  ```
  on_hand(item_id) = SUM(fact_order_lines.actual_servings WHERE item_id=X)
                    − SUM(fact_consumption.servings_consumed WHERE item_id=X)
  ```

- **Hard validation rule:** the `fact_consumption` GUI must block (not just
  warn on) any consumption entry that would cause `on_hand(item_id)` to go
  negative. This is a firm guardrail, not a soft warning.
- **All FDA-label nutrition columns in `dim_items` default to 0, not NULL**
  — this keeps aggregate SQL math simple and avoids NULL-propagation issues in
  arithmetic across columns. In this system, ALL nutrition/tracking fields
  (calories through trace minerals) are equally optional for the user to
  choose to track — there is no FDA "mandatory vs. voluntary" distinction
  enforced by the schema; that distinction is purely an FDA labeling
  convention, not a rule this system follows.
- **%DV (percent daily value) nutrients are converted to mass (mcg) at data
  entry time and stored as mass, never as raw percent.** This is because the
  FDA's daily value figures can change over time (as they did in 2016),
  which would silently invalidate historically-stored percentages. The GUI
  lets the user type the %DV straight off a label; the conversion (`mass_mcg
  = (percent / 100) * ref_daily_values.dv_amount`) happens in Python code
  before writing to `dim_items`. All %DV-based nutrients are stored in
  micrograms uniformly, and mg-based ones like Calcium get ×1000'd on entry, for
  apples-to-apples consistency. 
- **`glycemic_index` is the one nutrition-adjacent field that IS nullable**
  (no default). Rationale: it's not additive/summable across an order the way
  macros are, so 0 would be misleading (implies "no impact" rather than
  "unknown"). Expected range 0–200, validated at the application layer only
  (SQLite doesn't enforce numeric ranges) — low-stakes, self-correcting if
  entered wrong.
- **Naming convention:** tables prefixed `dim_` (dimension/lookup),
  `fact_` (transactional/event data), or `ref_` (static reference data not
  directly joined against, only referred to and used for computation).
  `settings` is left unprefixed as a pure config table (neither a dimension
  nor a fact).

## 6. Database Schema

### `dim_product_names`
| Column | Notes |
|---|---|
| `name_id` | PK |
| `name_text` | Editable. Decoupled from `dim_items` so a typo/punctuation fix doesn't require creating a whole new item version. |

### `dim_categories`
| Column | Notes |
|---|---|
| `category_id` | PK |
| `category_name` | Editable. |

Categories are entirely optional and never pre-populated — no default
category list is shipped, no forced classification. `dim_items.category_id`
is **nullable**; an item with no category is valid and simply won't appear
grouped in category-based reports (no "Uncategorized" placeholder row is
created and presented in reports).

### `ref_daily_values`
| Column                     | Notes                                                                               |
|----------------------------|-------------------------------------------------------------------------------------|
| `nutrient_id`              | PK                                                                                  |
| `nutrient_name`            | Editable (rare case: FDA renames a nutrient).                                       |
| `nutrient_fda_label_unit` | Read-only reference unit as printed on real FDA labels (e.g. "mg", "mcg", "g", "mL", "kcal"). Populated from seed data, not user-editable. |
| `nutrient_entry_unit` | Unit the item create/edit GUI asks the user to type in — either a mass or volume unit matching the label, or the literal string `"%"` for %DV-entered nutrients. `is_dv_percent_nutrient()` is derived from this (`== "%"`), not a separate stored flag. |
| `dv_amount`                | Editable. From the FDA, converted by user to nutrient_dim_items_unit at entry time. |
| `nutrient_dim_items_unit` | Unit the value is stored in on `dim_items` (mirrors each nutrient column's `_g`/`_mcg`/`_mL`/no-suffix convention; always "mcg" for %DV nutrients). |
| `is_tracked`               | Bool, editable via checkbox on "Manage Tracked Nutrients" screen. See §7.           |

Not directly joined against other tables in normal queries. `dv_amount` is 
referred to for %DV→mass conversion at `dim_items` entry time. `is_tracked` is 
fed by the "Manage Tracked Nutrients" screen and is consulted by reporting to 
decide which nutrient columns to display.

### `dim_items`
| Column | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
|---|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `item_id` | PK (surrogate key)                                                                                                                                                                                                                                                                                                                                                                                                                                                       |
| `name_id` | FK → `dim_product_names`                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| `category_id` | FK → `dim_categories`, **nullable**                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `price` | SCD Type 1 — current stated price, per block, overwritten in place                                                                                                                                                                                                                                                                                                                                                                                                       |
| `servings_per_block` | Computed: `container_size / serving_size` — see below                                                                                                                                                                                                                                                                                                                                                                                                                    |
| `units` | Dropdown — shared by both `container_size` and `serving_size` (e.g. units, g, oz, lb, kg, mL, L, fl oz, gal). The user must ensure both figures are expressed in this same unit; the app does not convert between units.                                                                                                                                                                                                                                                 |
| `container_size` | Float/int — total size of the package as printed on the label, in `units`                                                                                                                                                                                                                                                                                                                                                                                                |
| `serving_size` | Float/int — size of one serving as printed on the label, in `units`                                                                                                                                                                                                                                                                                                                                                                                                      |
| `blocks_must_be_integer` | Bool — gates whether the GUI allows fractional "blocks" for this item (e.g. pasta boxes = integer only; chicken thigh packages = fractional allowed)                                                                                                                                                                                                                                                                                                                     |
| `active` | Bool — hides retired/superseded item versions from picker/search UIs; historical fact rows still resolve correctly against inactive items                                                                                                                                                                                                                                                                                                                                |
| `glycemic_index` | Nullable int, expected range 0–200, app-layer validated only                                                                                                                                                                                                                                                                                                                                                                                                             |
| `ratio1` | Computed per-block value (see §9). Recalculated on item creation and whenever `price` is edited.                                                                                                                                                                                                                                                                                                                                                                         |
| `ratio2` | Computed per-block value (see §9). Same recalculation triggers as `ratio1`.                                                                                                                                                                                                                                                                                                                                                                                              |
| ~39 nutrition columns | All default 0, all equally optional/toggleable (see §7 and §5). Includes calories, total/saturated/trans fat, cholesterol, sodium, total carb, fiber, total/added sugars, protein, and the full FDA label vitamin/mineral list (vitamin D/A/C/E/K, calcium, iron, potassium, thiamin, riboflavin, niacin, B6, folate, B12, biotin, pantothenic acid, phosphorus, iodine, magnesium, zinc, selenium, copper, manganese, chromium, molybdenum, chloride, choline) plus ethanol. |

Note on `servings_per_block`: this value is not typed in directly by
the user. It's derived automatically from `container_size / serving_size`,
letting the GUI compute it live as those two fields are filled in (e.g.
container_size 250, serving_size 40 → servings_per_block 6.25), rather than
requiring the user to do that division by hand with a calculator first.
**No unit conversion is performed.** `container_size` and `serving_size`
share a single `units` dropdown — the user is responsible for making sure
both figures are expressed in the same unit (as they almost always already
are on real packaging). If a label happens to print them in different
units (a rare exception), the user must convert one of the two numbers
themselves before entering it; the app will not detect or correct a
unit mismatch.

Note: nutrition-changing events (e.g. manufacturer reformulation) always
create a **new** `dim_items` row (SCD2) — they never overwrite an existing
row's nutrition columns. Editing `dim_items.name_id`'s underlying text (a
typo fix) does NOT trigger a new row — that's handled via
`dim_product_names` directly.

### `fact_orders`
| Column | Notes |
|---|---|
| `order_id` | PK |
| `order_date` | |
| `is_delivery` | Bool |
| `status` | `planning` / `ordered` / `delivered` / `reconciled` — user-set via dropdown; soft lock on `reconciled` (see §5) |
| `delivery_charge` | Not nullable, defaults to 0 |
| `tip` | Not nullable, defaults to 0 — driver tip, sometimes given, sometimes not |
| `tax` | Not nullable, defaults to 0 |
| `order_level_coupon` | Not nullable, defaults to 0 — whole-order coupon, distinct from per-line coupons; stored negative regardless of sign entered, same as sale/discount/coupon on `fact_order_lines` |
| `total_net_cost` | Not nullable, defaults to 0 — computed: SUM(`net_price` from all `fact_order_lines` on this order) + `delivery_charge` + `tip` + `tax` + `order_level_coupon`. This is the figure the human manually compares against the invoice. |
| `total_calories` | Whole-order aggregate |
| `total_protein_g` | Whole-order aggregate |
| `total_carbs_g` | Whole-order aggregate |
| `total_fat_g` | Whole-order aggregate |
| `total_sodium_mg` | Whole-order aggregate |
| `ratio1` | Whole-order ratio, computed from actual net cost/servings (see §9) |
| `ratio2` | Whole-order ratio, same basis |

Note: `invoice_total` was explicitly considered and REJECTED as redundant
with `total_net_cost` — the computed `total_net_cost` is what the user
compares against the real invoice/receipt; no separate manually-entered
invoice-total column is needed.
Per-day-normalized figures (e.g. sodium/day) are deliberately NOT stored
here — they're computed at reporting time against whatever daily target the
user feels like using that day, rather than baking in one assumption.

### `fact_order_lines`
| Column | Notes |
|---|---|
| `line_id` | PK |
| `order_id` | FK → `fact_orders` |
| `item_id` | FK → `dim_items` (locks in which SCD2 nutrition-version applies) |
| `servings_ordered` | Frozen snapshot at order creation — historical/audit only, never used in calculations |
| `actual_servings` | Starts equal to `servings_ordered`; freely editable (any item, not just variable-weight ones) until order `status = reconciled`; drives ALL downstream math (net_price, nutrition totals, ratios) throughout the order's life |
| `stated_price` | Snapshot of `dim_items.price` at time of logging |
| `sale` | Not nullable, defaults to 0, stored negative |
| `discount` | Not nullable, defaults to 0, stored negative |
| `coupon` | Not nullable, defaults to 0, stored negative |
| `net_price` | Computed: `stated_price` (× actual_servings basis) + sale + discount + coupon (sale/discount/coupon are already stored as negative values, so addition is correct here) |

No per-line ratio1/ratio2 snapshot is stored here — considered and rejected;
whole-order aggregate ratios on `fact_orders` are sufficient for historical
reference, while live per-line ratios matter only during the planning/
engineering phase (computed live in the GUI, not persisted).

### `fact_consumption`
| Column | Notes |
|---|---|
| `consumption_id` | PK |
| `item_id` | FK → `dim_items` |
| `entry_date` | Date of the logging session |
| `servings_consumed` | Decimal — fractional entries allowed (e.g. half a bottle of ketchup still in the fridge) |

No FK to `fact_orders`/`fact_order_lines` (see §5). Validated against
on-hand at entry time (hard block on negative on-hand).

### `settings`
| Column | Notes |
|---|---|
| `setting_key` | PK, text |
| `setting_value` | cast as needed in application code |

Simple key-value store. Known settings include `cal_per_day_target`
(default 2000). Nutrient tracking flags do NOT live here — they live in
`ref_daily_values.is_tracked` (see §7) via a dedicated screen, not the
generic Settings screen.

## 7. Nutrient Tracking Setup

- **First-run Setup Wizard (mandatory, one-time nudge):** On first launch,
  presents checkboxes for every possible tracked field — calories, cost,
  every macro, every vitamin/mineral — with a master "Vitamins" toggle
  (checking/unchecking it toggles all ~21 vitamin/mineral rows at once)
  alongside individual overrides. An all-unchecked configuration is valid
  (bare-bones "what did I buy and when" log). This is intentionally the one
  forced decision point in the app, to make the user deliberately think
  about what they want to capture — everything else in the app avoids
  forcing choices.
- **"Manage Tracked Nutrients" screen (permanent, always accessible):** A
  button on the main GUI leads to a screen listing every FDA nutrient
  (populated from `ref_daily_values`), each row inline-editable for
  `nutrient_name` and `dv_amount` (rare edits — an FDA rename or
  daily-value revision), plus an editable checkbox bound to `is_tracked`.
  There is no separate screen for editing name/daily-value — everything
  lives on this one screen. The Setup Wizard is really just a friendlier
  first-touch entry point into this same underlying data (specifically its
  `is_tracked` column) — not a separate one-time-only mechanism. The user
  can return here anytime to turn tracking on/off or correct a name/value.
- **Adding or deleting a nutrient row is explicitly out of scope** for this
  screen and for the app generally — see §11 for the full reasoning.
- **`is_tracked` is a pure visibility/reporting filter — it never alters the
  schema.** Unchecking a nutrient does NOT drop its column from `dim_items`
  and does NOT destroy historical data. It only hides that column from GUI
  entry forms and reporting output going forward. Reporting determines which
  nutrient columns to display by checking `ref_daily_values.is_tracked`, not
  by inspecting `dim_items` columns directly or any text-matching scheme.

## 8. Setup Wizard

A multi-step, installer-style flow shown on first launch of a new project
(i.e. against a fresh, empty `foodlog.db`). It runs exactly once per
project file and does not reappear on subsequent launches once completed.
See @/gui/setup_wizard.md for the full ASCII mockup of every step.

Only the Nutrient Tracking step is mandatory — every other step can be
skipped and revisited later via the corresponding screen on the Main GUI.
The steps, in order:

1. **Welcome** — brief orientation screen, explains what the wizard covers
   and that everything except nutrient tracking is optional/revisitable.
2. **Nutrient Tracking (mandatory, no skip option)** — the same checkbox UI
   as the permanent "Manage Tracked Nutrients" screen (§7): every possible
   tracked field (calories, cost, every macro, every vitamin/mineral) with
   a master "Vitamins" toggle plus individual overrides. An all-unchecked
   configuration is valid. This is the one forced decision point in the
   entire app — everywhere else deliberately avoids forcing a choice.
3. **Categories (optional)** — lets the user create/name categories now via
   the same underlying mechanism as the "Manage Categories" screen, or skip
   entirely and leave `dim_categories` empty for now.
4. **Cal/Day Target** — sets `settings.cal_per_day_target`, pre-filled with
   a default of **2000**, which the user may override. Not skippable in
   the sense of being blank — it always has a value — but the default is
   sensible enough that the user can simply click through without typing
   anything if they don't care to change it. Cannot be blank, cannot be 
   negative, cannot be zero. User must enter a postive definite float/int.
5. **Populate Items (optional, final step)** — offers a choice: "Start
   Entering Items" or "Skip." Choosing "Start Entering Items" exits the
   wizard directly into the Manage Items screen (create-new-item form).
   Choosing "Skip" exits directly into the Main GUI. Either choice
   permanently ends the wizard for this project file.

## 9. Ratio Calculations

Two hand-tuned "value scoring" ratios that are used to engineer orders
against calorie-efficiency vs. sodium/fat tradeoffs. Higher is always
better. Constants are fudge factors calibrated by feel, not derived
mathematically — treat as fixed constants in code, not configurable.

```
Ratio1 = Total_Calories / (4 × Total_Cost + Total_Sodium_mg/100 + 0.00001)
Ratio2 = Total_Calories / (1.333 × Total_Cost + Total_Sodium_mg/300 + Total_Fat_g/6.6 + 0.00001)
```

- The `+0.00001` exists purely to avoid divide-by-zero.
- Ratio1 is the primary/preferred tool.
- Ratio2 is a secondary/reference tool. Kept around for reference, not primary
  focus.
- **Two calculation contexts, both needed:**
  1. **Per-item, per-block basis** (stored as `dim_items.ratio1`/`ratio2`) —
     lets the user compare arbitrary items head-to-head (e.g. rice vs.
     anchovies) outside the context of any specific order. Computed from
     `price` (per block) and nutrition columns × `servings_per_block`.
     Recalculated whenever `price` changes or a new item version is
     created.
  2. **Live, per-order basis** (computed live in the Order Creation GUI, and
     snapshotted to `fact_orders.ratio1`/`ratio2` once the order is
     finalized) — uses ACTUAL net cost (post sale/discount/coupon) and
     actual servings for the whole order or any subgroup. This is the
     figure that actually drives real-time engineering decisions (e.g.
     "should I drop a bottle of hot sauce"), and must recalculate live as
     quantities/discounts are edited in the GUI.
- Sale/discount/coupon values are reliably known at order-placement time in
  ~95% of cases (coupons are known, website sale price is shown, itemized
  discounts available under a link) — only genuinely weight-variable items
  (e.g. a per-pound chicken sale) cause the actual discount total to shift
  post-purchase, which is already handled because `net_price` derives from
  `actual_servings`, which is itself editable post-delivery. No special-
  casing needed elsewhere.

## 10. GUI / Screen Inventory

### Main / Project-Level GUI (home screen, launched after first-run wizard)
Simple launcher exposing:
- New / Manage Orders — always opens the Order Picker dialog. The dialog
  offers "Create New Order" as a standing option, plus a list of every
  existing order regardless of status (including `reconciled`), so any
  order remains reachable to reopen or change status even after
  reconciliation. There is no auto-jump shortcut that skips this dialog.
- Log Consumption
- Manage Items
- Edit Product Names
- Manage Categories (manage category names — NOT item-to-category
  assignment, which happens via dropdown in the Items screen)
- Manage Tracked Nutrients
- Reporting
- Settings (includes `cal_per_day_target` and a hidden/buried "Danger Zone"
  reset control — see below)

### Order Creation / Planning
The most fully specified screen. Layout:
- Header: order date, delivery checkbox, status dropdown
- Search box + category-filter checkboxes to narrow the item picker (supports
  both free-text search AND category-checkbox filtering simultaneously, e.g.
  checking "Pasta" then entering quantities across several matching items in
  one pass). The search box may need an item-name-disambiguation component,
  which may show nutrition info alongside search results so the user can select 
  the correct SCD2 item version when multiple similarly-named versions exist
  (but this may not be applicable if retired/superseded items are culled from
  the search pool.)
- Per-item row: item name, **Blocks** entry box ⇄ **Servings** entry box
  (live bidirectional auto-calculation using `servings_per_block` — editing
  either box recalculates the other instantly), stated price with an
  inline shortcut icon/button opening a small "Update Stated Price" popup
  that overwrites `dim_items.price` (SCD1), then Sale/Discount/Coupon entry
  boxes (any sign accepted, stored negative), a computed Net column, and
  live **Ratio1**/**Ratio2** columns recalculating when the user exits a
  text box (not per keystroke)
- Footer: running totals (est. net cost, calories, sodium, etc.), an
  estimated-days-of-supply figure driven by the global `cal_per_day_target`
  (from `settings` — not a per-order input field), and live whole-order
  Ratio1/Ratio2
- Buttons: Save Draft, Submit Order (transitions status to `ordered`)
- Two pop-out windows, opened via buttons/links from this screen:
  - **Order Summary ($)** — itemized by category, showing qty/base price/
    discounts/net price per line, subtotaled by category, with delivery
    charge, tip, tax, and order coupon rolled into a grand estimated total.
    This window deliberately shows money only — no ratios (view side-by-side
    with the Nutrition window if ratios are wanted alongside cost). Items
    with `category_id = NULL` are grouped under a display-only
    `(Uncategorized)` heading — this label is generated at display time
    only and is never written to `dim_categories`. Includes its own CSV
    export button, scoped only to this window's data for the current
    order — separate and unrelated to any future Reporting-screen CSV/
    Excel export (see §3/§10 Reporting). The exported file drops in the
    same folder as the FoodLog program itself, with an auto-generated
    filename combining the order number, a label identifying it as the
    money summary, and a date/time stamp.
  - **Nutrition Summary** — a matrix: nutrient columns across the top
    (truncated/scrollable given ~35 possible columns), items down the left
    grouped by category, a subtotal row after each category group, a grand
    total row at the bottom, plus per-item/per-category/per-order Ratio1
    and Ratio2 columns on the far right, all computed live from actual
    order quantities and prices. Items with `category_id = NULL` are
    grouped under the same display-only `(Uncategorized)` heading
    described above. Includes its own CSV export button, scoped only to
    this window's data for the current order, with the same file-location
    rule and filename convention (order number, a label identifying it as
    the nutrition summary, and a date/time stamp) as the Order Summary ($)
    export above — again, unrelated to any future Reporting-screen export.
- Blocks-entry validation: if `dim_items.blocks_must_be_integer = 1`, only
  whole-number block entries are accepted; fractional blocks are allowed
  for items where it's `0` (e.g. variable-weight chicken).

### Log Consumption
- Entry date field
- Search box + category-filter checkboxes (same pattern as Order Creation)
- Full-width scrollable list, filtered to items where `on_hand > 0` (so the
  visible list is always short and relevant.
- Per-item row: item name, read-only "On Hand" figure, editable "Consumed
  Now" entry box (decimal allowed for fractional consumption)
- Hard validation: any entry causing computed on-hand to go negative is
  rejected outright (not merely flagged)
- Purely a data-entry screen — no decisions being made here, so it carries
  no ratio columns.
- The items may need an item-name-disambiguation display, which may show
  nutrition info alongside the available items so the user can select the
  correct SCD2 item version when multiple similarly-named versions exist.

### Manage Items
Intentionally left to be brute-forced with Claude Code rather than fully
specified here — low architectural risk, standard search/select/edit/save
form. Should reuse the same search + category-filter pattern as the other
screens. Needs to support both creating brand-new items (meaning entry of all 
`dim_items` fields including the nutrition panel, plus a `name_text` entry 
that writes to `dim_product_names`) and editing existing ones.

### Edit Product Names
Flat list: read-only `name_id`, editable `name_text` text box.

### Manage Categories
Simple screen to create/rename/delete category names only (text boxes,
`category_id` auto-assigned). Does NOT handle item-to-category assignment —
that's done via a dropdown (populated from this table) inside the Manage
Items screen. Deleting a category currently in use by one or more
`dim_items` rows must be hard blocked — the user must first reassign or
clear that category off every item using it before the category itself can
be deleted. No silent orphaning, no automatic reassignment.

### Manage Tracked Nutrients
See §7. Editable nutrient name list (from `ref_daily_values`), a read-only 
`nutrient_fda_label_unit` display column showing the respective units used on 
food labels, a read-only `nutrient_entry_unit` display column showing the 
units of entry in the item create/edit GUI (most likely identical to 
`nutrient_fda_label_unit`), editable daily value fields, a read-only 
`nutrient_dim_items_unit` display column showing the units of display in this 
GUI (which is equal to the units of storage in `dim_items`), and an editable 
tracked/untracked checkbox per row.

### Settings
Not laid out in pixel-level detail (left to iteration with Claude Code), but
must include: an editable `cal_per_day_target` value that has a system default 
value of 2000, and a hidden/buried reset button (e.g. under a "Danger Zone" 
label) requiring a typed confirmation phrase (not just a click) to fully reset 
the FoodLog program. Resetting the program deletes all entries from the 
`dim_items`, `fact_orders`, `fact_order_lines`, `fact_consumption`, 
`dim_product_names`, and `dim_categories` tables, and resets the `cal_per_day_target` 
to the system default. This reset does NOT change editable fields in 
`ref_daily_values`, which hold FDA reference defaults — nutrient names, daily 
values — which should survive a reset.

### Reporting
Deliberately NOT specified beyond the mechanism decision (§3: matplotlib
embedded in Tkinter, plus CSV/Excel export as a lower-effort fallback path).
Content/layout to be iterated on directly with Claude Code once a working
prototype exists.

## 11. Explicitly Rejected / Considered-and-Discarded Ideas

Recorded so these don't get re-litigated or re-discovered later:

- Storing store-of-purchase per item — rejected, unnecessary (see §5).
- `dim_items.can_be_modified` flag to gate `actual_servings` editability —
  rejected and removed; editability is universal, gated only by order
  `status`.
- Deleting `fact_order_lines` rows for fully out-of-stock items — rejected;
  the row stays with `actual_servings = 0` to preserve the audit trail (see
  §5).
- Storing a locked-in per-line ratio1/ratio2 snapshot on `fact_order_lines`
  — rejected; whole-order aggregates on `fact_orders` are sufficient.
- Adding ratio columns to the Order Summary ($) money window — rejected;
  keep that window money-only, view Nutrition window alongside if needed.
- Pre-populating `dim_categories` with a default list, or forcing item
  classification — rejected; fully optional, nullable FK, no imposed data.
- `invoice_total` on `fact_orders` — rejected as redundant with
  `total_net_cost`.
- Multi-project management inside the app (a `projects` table/UI) —
  rejected in favor of simple file/folder-copy-based multi-project support.
- Electron and local-web-server (Flask/Jupyter-style) architectures for the
  GUI — rejected; adds unjustified complexity/dependencies for this tool.
- A separate `dim_tracked_nutrients` table — rejected; folded `is_tracked`
  directly into `ref_daily_values` instead.
- A GUI mechanism to add or delete a nutrient row in `ref_daily_values` —
  rejected. Each nutrient corresponds to a named column in `dim_items`;
  adding a genuinely new nutrient would require an actual schema change (a
  new `dim_items` column), not a data edit, and there's nowhere to store
  per-item values for a nutrient with no corresponding column.
- Reserving blank spare columns in `dim_items` ahead of time for future
  nutrients — rejected as not worth the schema clutter, given how rare
  this event is (the FDA's last full add/drop of label nutrients was the
  2016 label overhaul, phased in through 2020/2021 — roughly once-per-
  decade-or-longer). If the FDA adds or drops a label nutrient in the
  future, that should be handled as a deliberate one-off schema migration,
  not a runtime GUI action.
