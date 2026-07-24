# Log Consumption

Batch data entry — the user logs consumed food items and enters as 
much as they want as often as they want. A data entry schedule, 
meal-wise, daily, weekly, etc., is not imposed on the user; they 
engage in this data entry component at their own discretion.
Additionally, strict recording of actual consumption date is not 
imposed, the entry is time stamped with "Entry Date", the date the 
data is entered into FOODLOG.

```
┌──────────────────────────────────────────────────────────────────┐
│  LOG CONSUMPTION                                                  │
├──────────────────────────────────────────────────────────────────┤
│ Entry Date: [__________]                                          │
│ Search: [___________]   Categories: [ ]Pasta [ ]Dairy [ ]Meat ... │
├──────────────────────────────────────────────────────────────────┤
│ ITEM                     ON HAND      CONSUMED NOW                │
│ ──────────────────────────────────────────────────────────────    │
│ Spaghetti, box              6          [___]                      │
│ Linguine, box                6          [___]                      │
│ Ketchup, bottle             1          [0.5]                      │
│ Eggs, carton                6          [___]                      │
│ ...                                                                │
├──────────────────────────────────────────────────────────────────┤
│                       [ Commit Consumption ]                      │
└──────────────────────────────────────────────────────────────────┘
```

Notes:
- Entry date is an editable field that defaults to today's date when the 
  consumption GUI is opened. The field is editable so that the user is 
  empowered to stamp the entry with another date. E.g., the user knows 
  the actual consumption date and wants to timestamp the entry with that 
  date instead of the data entry date.
- List is filtered to items where `on_hand > 0` only — keeps the visible
  list short and relevant.
- "ON HAND" is read-only, computed as
  `SUM(fact_order_lines.actual_servings) − SUM(fact_consumption.servings_consumed)`
  per item.
- "CONSUMED NOW" accepts decimals (fractional consumption, e.g. half a
  bottle of ketchup still in the fridge).
- **Hard validation**: any entry that would push computed on-hand negative
  for that item is rejected outright on commit — not merely flagged.
- Purely a data-entry screen — no ratio columns, no decision-making UI.
  If the item's name is ambiguous due to multiple SCD2 versions with the
  same product name, e.g. "Giant Round-Top White Sandwich Bread" after a
  reformulation, search results may show nutrition info alongside the name
  so the user can match against the empty package in hand — this detail is
  left to iteration with Claude Code.
