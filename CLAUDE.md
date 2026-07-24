# FoodLog — Instructions for Claude Code

**Read `SPEC.md` in full before doing any work on this project.** It contains
the complete, deliberated product specification — database schema, business
rules, packaging strategy, and GUI/screen inventory. It reflects roughly 20
hours of design discussion and should be treated as authoritative for
anything it covers.

# Project Overview
This project builds a fully Python-based executable program called "FoodLog" 
that can run on Linux or Windows. Humans can populate a database with food 
purchase and consumption data that enables them to track, analyze, and report 
on their nutrition profile and food costs.

## Claude API
Model: claude-haiku-4-5-20251001 ONLY. Never upgrade to Sonnet, Opus, or Fable 
for ANY reason without explicit permission from the human.
Do not waste the human's tokens.
Only try to complete a task twice. If you cannot complete the task after 2 
tries, stop and ask the human for help. Report what you are trying to do, 
what steps you have tried, how those attempts have failed, and ask for help 
instead of wasting tokens by hopelessly retrying the same things.

## Token Hygiene
Do not read entire files unless necessary — read only relevant sections.
Do not repeat back large chunks of code unless asked.
Keep responses concise — Be non-verbose and do not use lengthy preambles 
or summaries.
Go step-by-step to solve problems. Do not return long, multi-step procedures 
to the human.

## Claude Code Config
- Do not use /home for project-level configurations, only use /home for 
user-level config.
- Do not touch /home (user-level config) unless specifically instructed by 
the user!
- For project-level config, use a .claude folder at the root of the project 
folder with a settings.json file in it.

## Python Standards
- Python 3.13
- Type hints on all functions and method signatures
- Docstrings on all public functions (numpydoc style).
- Max line length: 79 characters.
- Use f-strings, not `.format()` or `%`.
- Prefer `pathlib.Path` over `os.path`.

## Environment
- Package manager: `uv` with `pyproject.toml`.
- Virtual environment: `.venv/` in project root (never modify system Python)
- NEVER use the system python, only use the .venv in the project root.
- Never use `sudo pip`.
- Update `pyproject.toml` immediately if you make dependency changes.

## Git
- Never commit: `.venv/`, `__pycache__/`, `.env`, `*.pyc`
- Never push directly to main

## Maintaining CLAUDE.md (this document)
Change rules for CLAUDE.md --- Do not modify CLAUDE.md unless you have 
explicit approval from the human. If you would like to make changes to 
CLAUDE.md, present your proposed changes to the human and explicitly ask for 
permission to make the changes. When presenting your changes, if you are 
deleting information, present what is being deleted. If you are adding 
information, present what you are adding. If you are editing information, 
present both the original text and the edited text to the human. If the 
human approves any or all of the changes, then modify CLAUDE.md with only 
the approved changes.

## Quick facts
- Language: Python only. No JavaScript, no Electron, no web server.
- Database: SQLite, single portable file (`foodlog.db`).
- GUI: Tkinter (stdlib). Plain/default styling is acceptable; polish is a
  later, low-priority concern.
- Packaging: PyInstaller, producing a Windows `.exe` and a Linux binary
  (built on Linux), both reading the same `foodlog.db` from a shared folder.
  See SPEC.md §4 for exact folder layout and the path-resolution rule
  (locate the executable's own folder at runtime — never hardcode paths).
- Charting (future): matplotlib embedded in Tkinter, not Plotly/web-based.

## What's firm vs. what's flexible
- The schema (all 8 tables, keys, SCD1/SCD2 rules, nullability, the ratio
  formulas, the order lifecycle/status rules) is **settled** — don't
  redesign it without checking with the human first.
- GUI pixel-level layout, the Manage Items screen, the Settings screen
  layout, and all Reporting/Analytics screens are **intentionally left
  open** for iterative, trial-and-error development. Build a first pass,
  show the user, refine based on reaction — don't over-engineer these
  up front.

## Maintaining SPEC.md
Change rules for SPEC.md --- Do not modify SPEC.md unless you have explicit 
approval from the human. If you would like to make changes to SPEC.md, 
including in those cases discussed immediately below, present your proposed 
changes to the human and explicitly ask for permission to make the changes. 
When presenting your changes, if you are deleting information, present what 
is being deleted. If you are adding information, present what you are adding. 
If you are editing information, present both the original text and the edited 
text to the human. If the human approves any or all of the changes, then 
modify SPEC.md only with the approved changes.
Causes to change SPEC.md --- If a design decision changes during development 
(schema tweak, rejected approach, new rule discovered), 
**update SPEC.md to reflect it** — If something gets tried and discarded, 
add it to the "Explicitly Rejected" section (§11) so it doesn't get re-proposed 
later. Treat SPEC.md as a living document, not a one-time handoff.

## The /gui Folder
The `/gui` folder at the project root contains one markdown file per screen
(plus a couple of standalone dialog files not tied to any single screen),
each holding ASCII-art mockups of that screen's layout. These are reference
diagrams, not authoritative pixel-perfect specs — exact widget placement,
spacing, and styling are left to Claude Code's judgment. What the diagrams
DO fix are: which fields/columns exist on a screen, which pop-outs/dialogs
belong to it, and any behavior notes written alongside the diagram (e.g.
validation rules, what triggers a recalculation). Treat those behavior
notes with the same weight as SPEC.md itself.

## Maintaining /gui and its md files
Change rules for `/gui` --- Do not modify any file inside `/gui` unless you
have explicit approval from the human. If you would like to make changes to
a file in `/gui`, present your proposed changes to the human and explicitly
ask for permission to make the changes. When presenting your changes, if
you are deleting information, present what is being deleted. If you are
adding information, present what you are adding. If you are editing
information, present both the original text and the edited text to the
human. If the human approves any or all of the changes, then modify the
file with only the approved changes.
Causes to change a `/gui` file --- If a screen's design changes during
development (a field gets added/removed, a behavior rule changes, a new
dialog gets introduced), update the relevant `/gui/*.md` file to reflect
it. If a brand-new screen or dialog gets created that isn't in this
inventory yet, create a new file for it here rather than letting the design
exist only in code. Treat `/gui` as a living set of documents, not a
one-time handoff.
