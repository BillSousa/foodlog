# Order Picker Dialog

Standalone dialog — not owned by any single screen. Triggered from the
Main GUI's "New / Manage Orders" button, always — regardless of how many
orders exist or what status they're in. There is no auto-jump/shortcut
that skips this dialog; it is the single, always-reachable entry point
into every order.

```
┌─────────────────────────────────────────────────┐
│  SELECT AN ORDER TO MANAGE                      │
├─────────────────────────────────────────────────┤
│  [ + Create New Order ]                         │
├─────────────────────────────────────────────────┤
│  ORDER #    DATE          DELIVERY   STATUS     │
│  ────────────────────────────────────────────── │
│  #43        2026-07-22    Yes        Planning   |
│  #42        2026-07-18    No         Ordered    │
│  #41        2026-07-10    Yes        Reconciled │
│  #40        2026-06-02    Yes        Reconciled │
│  ...                                            │
│                                                 │
│  ( select a row, then )                         │
│                                                 │
│              [ Open Selected Order ]            │
│              [ Cancel ]                         │
└─────────────────────────────────────────────────┘
```

Notes:

- "+ Create New Order" is a standing button, always present at the top —
  not conditional on the current order count or the status of orders.
  This button directs to the Order Creation / Planning screen, completely
  blank: no order_id yet (assigned on first save/commit), empty date field,
  delivery checkbox unchecked, status defaulting to planning, and an empty
  item grid ready for search/category-filter entry.
- Every `fact_orders` row is listed below it, **regardless of `status`**,
  including `reconciled` orders. Nothing is ever filtered out of this
  list. All orders are listed descending by date. 
- Every order remains reachable to reopen or change status, even after
  reconciliation. This is deliberate: `reconciled` is only a *soft* lock
  (editing of anything bearing that `order_id` is disabled while status
  is `reconciled`), and the only way to toggle an order's status back to
  something editable is to reopen it here — so a `reconciled` order must
  always remain reachable, or the soft lock effectively becomes permanent
  with no way back.
- Selecting a row and confirming opens that `order_id` directly in the
  Order Creation / Planning screen, in whatever state its `status`
  currently reflects (e.g. a `reconciled` order opens read-only/locked
  until the user flips its status dropdown away from `reconciled`).
