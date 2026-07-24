# Reporting

Deliberately NOT specified in detail — this is cheap-to-iterate territory,
per SPEC.md §3/§10. No mockup drawn here yet; content and layout are meant
to be built with Claude Code directly against a working prototype and
refined by reaction, not designed blind in advance.

Known constraints carried over from earlier discussion (see SPEC.md §3):
- Charting mechanism: `matplotlib` embedded in Tkinter via
  `FigureCanvasTkAgg` — not Plotly, not a browser/web-based approach.
- A CSV/Excel export option is a valid lower-effort fallback/complement —
  dump data out and let Excel handle any charting the user may be 
  comfortable doing there.
- Likely candidates for what this screen eventually shows (not yet
  decided/designed): calories/sodium/protein trends over time, Ratio1/
  Ratio2 trends across orders, lifetime aggregate ratios based on total
  actual consumption and total actual cost (mentioned in passing during
  ratio discussion, explicitly deferred to here rather than designed then).

This file exists as a placeholder/reminder — expect it to be filled in
after a prototype exists, not before.
