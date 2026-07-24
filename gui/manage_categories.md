# Manage Categories

Simple screen to create, rename, or delete category names only. Does NOT
handle item-to-category assignment — that happens via a dropdown
(populated from this same table) inside the Manage Items edit form.

```
┌──────────────────────────────────────────────────────────┐
│  MANAGE CATEGORIES                                          │
├──────────────────────────────────────────────────────────┤
│  New category name: [______________]  [ Add ]               │
├──────────────────────────────────────────────────────────┤
│  category_id   CATEGORY NAME                                │
│  ────────────────────────────────────────────────────────   │
│  1             [Pasta          ]              [ Delete ]     │
│  2             [Baking         ]              [ Delete ]     │
│  3             [Meat           ]              [ Delete ]     │
│  ...                                                          │
├──────────────────────────────────────────────────────────┤
│                          [ Save Changes ]                    │
└──────────────────────────────────────────────────────────┘
```

Entirely optional — no categories are pre-populated at project creation,
and `dim_items.category_id` is nullable, so an item can remain uncategorized
indefinitely with no penalty in reporting (it simply won't appear grouped
under any category).

Note: attempting to delete a category currently in use by one or more
`dim_items` rows must be **hard blocked** — the deletion is refused, and
the user is notified they must first reassign or clear the category off
every item using it before the category itself can be deleted. No silent
orphaning, no automatic reassignment.
