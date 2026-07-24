# Settings

Not laid out in full pixel-level detail per SPEC.md §10 (left to iteration),
but must include the global cal/day target and the buried reset control.
Rough reference sketch below.

```
┌──────────────────────────────────────────────────────────┐
│  SETTINGS                                                │
├──────────────────────────────────────────────────────────┤
│  Target calories per day: [ 2000 ]                       │
│                                                          │
│  (other project-scope settings as added over time)       │
│                                                          │
├──────────────────────────────────────────────────────────┤
│  ▼ Danger Zone                                           │
│  ────────────────────────────────────────────────────────│
│  [ Reset This Project's Data... ]                        │
├──────────────────────────────────────────────────────────┤
│                     [ Save Changes ]                     │
└──────────────────────────────────────────────────────────┘
```

## Reset confirmation dialog

Opened by the "Reset This Project's Data..." button. Requires a typed
confirmation phrase, not just a click, to prevent accidental data loss.

```
┌────────────────────────────────────────────┐
│  ⚠ RESET PROJECT DATA — CANNOT BE UNDONE  │
├────────────────────────────────────────────┤
│  This will permanently erase all items,    │
│  orders, order lines, and consumption      │
│  history for this project file.            │
│                                            │
│  Type "RUMPELSTILTSKIN" to confirm:        │
│  [___________________]                     │
│                                            │
│    [ Cancel ]      [ Erase Everything ]    │
└────────────────────────────────────────────┘
```

Wipes `dim_items`, `fact_orders`, `fact_order_lines`, `fact_consumption`,
`dim_product_names`, and `dim_categories` for the current project file.
All the check boxes in the `tracked_nutrients` GUI are reset to the 
unchecked state (implicitly setting all `is_tracked` states in `ref_daily_values` 
to false). The Set-up Wizard toggle, a hidden implementation detail 
strictly handled by Claude Code, is set back to the "not set up" state (see 
`setup_wizard.md` for more discussion of the Set-up Wizard toggle.) This 
will cause the Set-up Wizard to trigger the next time that the FOODLOG 
program is run.

Does **not** wipe `ref_daily_values` — that table holds the FDA reference
defaults (nutrient names, daily values, tracked flags) and should survive a
project reset intact. `settings` (e.g. `cal_per_day_target`) is reset to the
system default (currently arbitrarily set at 2000).
