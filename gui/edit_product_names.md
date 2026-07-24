# Edit Product Names

Flat list, simple edit form. Fixes typos/punctuation in `dim_product_names`
without triggering a new `dim_items` SCD2 version (a name-text edit is
purely cosmetic, unrelated to nutrition-version changes).

```
┌──────────────────────────────────────────────────────────┐
│  EDIT PRODUCT NAMES                                      │
├──────────────────────────────────────────────────────────┤
│ Search: [___________]                                    │
├──────────────────────────────────────────────────────────┤
│ name_id    NAME TEXT                                     │
│ ─────────────────────────────────────────────────────────│
│ 1001       [Giant Round-Top White Sandwich Bread    ]    │
│ 1002       [Giant Sour Cream                        ]    │
│ 1003       [Barilla Spaghetti                       ]    │
│ ...                                                      │
├──────────────────────────────────────────────────────────┤
│                          [ Save Changes ]                │
└──────────────────────────────────────────────────────────┘
```

`name_id` is read-only (display only). `name_text` is directly editable
inline. Both this screen and the quick name-entry field on Manage Items
write to the same `dim_product_names.name_text` column.
