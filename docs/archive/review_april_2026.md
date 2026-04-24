# Project Orion — Codebase Review (April 2026)
**Status: Complete**

Commits:
- `fix: codebase review fixes — A1, A2, A3, B1`
- `fix: resolve lazy imports across codebase`
- `fix: codebase review fixes — B2, B4, B5, B7`

---

## GROUP A — Fix before save/load

---

### A1 — ✅ DONE — `backend/api/command.py` and `backend/handlers/electrical_repair.py` — One file reaching inside another file's private workings

**The problem:**
`command.py` reached inside `electrical_repair_handler` and read a private variable called
`_profiles` directly. The underscore prefix is Python's convention for "internal — do not
touch from outside." Private variables and functions should never be accessed outside the
class they belong to. This creates a hidden dependency — if the handler ever changes how
it stores profiles internally, `command.py` breaks silently.

**Fix:** Added a public `get_profile(panel_id)` method to `ElectricalRepairHandler`.
`command.py` calls that instead of accessing `_profiles` directly.

---

### A2 — ✅ DONE — `backend/api/game.py` — Dead code

**The problem:**
`_build_room_data()` built a list called `portable_objects` and sent it to the frontend
on every room load. The list was always empty — portable items live on floors, surfaces,
and in containers, never directly in `room.objects`. Confirmed by global PyCharm search:
`portable_objects` was never read by any JS file. Floor items were already correctly
handled by the separate `floor_items` key.

**Fix:** Removed the `portable_objects` list and its key from `_build_room_data()`.

---

### A3 — ✅ DONE — `backend/api/game.py` — Reading item files from disk on every cargo manifest request

**The problem:**
The cargo manifest route called `load_item_registry()` on every request — opening and
reading multiple JSON files from disk just to look up item display names. Item definitions
never change at runtime. `repair_utils.py` already had a cached `item_name()` function
that does exactly this lookup. Also removed a function-level lazy import
(`from backend.loaders.item_loader import load_item_registry`) that was inside the route
function body.

**Fix:** Replaced `load_item_registry()` and the inline `resolve_contents()` helper with
calls to `item_name()` from `repair_utils`. Added `item_name` to the top-level imports.

---

## GROUP B — Quality issues

---

### B1 — ✅ DONE — `backend/events/event_system.py` — Silent failures and duplicate log entry

**The problem:**
Two silent failure paths existed in the event system — both violating the no-silent-
fallbacks rule:

1. Unknown event type in `check()` — printed a console warning and carried on. The
   docstring even claimed "no silent failures" while doing exactly that.
2. Component ID not found in `_break_component_by_id()` — also printed a warning and
   carried on. Additionally wrote a duplicate ship log entry on this error path, identical
   to the one already written by the outer `_handle_impact_event()`.

**Fix:**
- Both silent `print` warnings replaced with `raise ValueError` — bad data in
  `events.json` now crashes immediately with a clear message.
- Duplicate `add_log_entry` call removed from the error path in `_break_component_by_id()`.
- Module docstring updated to accurately reflect the no-silent-failures behaviour.

---

### B2 — ✅ DONE — Lazy imports across multiple files

**The problem:**
Several files had imports inside function bodies instead of at the top of the file.
The only legitimate reason for a function-level import is to avoid a circular import.
Most of these had no such justification.

Files corrected:
- `equip_handler.py` — `import random` moved to top (standard library, zero circular
  import risk). PEP 8 import order also corrected (`import` before `from` imports).
- `game.py` — `import json` moved to top. `from config import TERMINAL_CONTENT_PATH`
  merged into the existing top-level config import (config was already imported at the
  top of the file, proving no circular import risk). `from backend.systems.electrical.
  electrical_system import FissionReactor` moved to top after testing confirmed no
  circular import.

---

### B4 — ✅ DONE — `backend/models/interactable.py` — Duplicated `contents_str()` method

**The problem:**
`StorageUnit` and `Surface` both had a `contents_str()` method that was word-for-word
identical. Not DRY — a future change would need to be made in two places.

**Fix:** Extracted shared logic into a module-level private helper `_format_contents(items)`.
Both classes now call it.

---

### B5 — ✅ DONE — `backend/handlers/repair_utils.py` — Cache assumption not documented

**The problem:**
`_item_registry` is loaded once at module import and cached permanently. This is correct
and intentional — the registry is a read-only template store that never changes at runtime.
Nothing in the code explained this, which could cause confusion during save/load work.

**Fix:** Added a comment above `_item_registry` clarifying it is a read-only template
cache and does not need to be serialised for save/load.

---

### B7 — ✅ DONE — `backend/systems/electrical/electrical_system.py` — Docstrings not up to project standard

**The problem:**
`electrical_system.py` was ported from an earlier project. The module docstring was a
single brief line and all class docstrings were single-line, inconsistent with the rest
of the project.

**Fix:** Expanded module docstring and all class docstrings to project standard. Key
additions include: circular import warning in the module docstring, full explanation of
`PowerCable.intact` vs `connected` states including emergency bypass cable behaviour,
`BackupBattery` ship context (two installed — Mainframe Room and Life Support), and
`CircuitPanel.operational` derivation from internal component flags.

---

## Skipped items

| Item | Reason |
|------|--------|
| B3 — `[STUB]` text in `repair_handler.py` | Valid developer marker for unbuilt code. Game is deep in development — no real player will see it for a long time. |
| B6 — `datapad_suppressed` comment in `game_manager.py` | Save triggers never capture a mid-terminal state. `datapad_suppressed` will always be `False` at save time by design. No comment needed. |
