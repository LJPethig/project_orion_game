# Project Orion — Codebase Review
**April 2026 — Pre-save/load clean baseline**

---

## How to read this document

Issues are split into two groups:

**GROUP A — Fix before save/load work begins.** These are genuine bugs or things that will cause real problems when the save/load system is built. There are 3 of them.

**GROUP B — Quality issues.** Dead code, duplication, and things that are just slightly untidy. None of these will break anything right now, but cleaning them up keeps the codebase healthy. There are 5 of them.

Each issue says: what the file is, what the problem is in plain language, why it matters, and what to do about it.

Fix them one at a time. Verify each one before moving to the next.

---

## GROUP A — Fix before save/load

---

### A1 — `backend/api/command.py` and `backend/handlers/electrical_repair.py` — One file reaching inside another file's private workings

**The problem in plain language:**
The `command.py` file (which handles API routes) reaches inside `electrical_repair_handler` and reads a private variable called `_profiles` directly. The underscore prefix on `_profiles` is Python's way of saying "this is internal, don't touch it from outside." This is sloppy coding — private functions and variables should never be accessed outside of the class they belong to.

This creates a hidden dependency: if the electrical repair handler ever changes how it stores profiles internally, `command.py` will break — and it won't be obvious why, because the connection isn't visible.

**Why it matters:** It's the kind of thing that causes confusing bugs later. It also means a piece of "how do I look up a profile?" logic has leaked into the wrong file.

**What to fix:** Add a small public method to `electrical_repair.py` called `get_profile(panel_id)` that returns the profile. Then `command.py` calls that method instead of reaching in directly.

---

### A2 — `backend/api/game.py` — Dead code

**The problem in plain language:**
The function `_build_room_data()` builds a list called `portable_objects` and sends it to the frontend on every room load. This list is **always empty** — portable items live on room floors, surfaces, and inside containers — never directly in `room.objects`. Floor items are already correctly handled by the separate `floor_items` key lower down in the same function.

Confirmed by global search in PyCharm: `portable_objects` appears only in `game.py`. It is never read by any JS file.

**Why it matters:** Dead code should be removed. It will also confuse the save/load implementation.

**What to fix:** Remove the `portable_objects` list and its key from `_build_room_data()`.

---

### A3 — `backend/api/game.py` — Reading item files from disk on every cargo manifest request

**The problem in plain language:**
Every time the player opens the cargo manifest terminal, the code calls `load_item_registry()` — this opens and reads multiple JSON files from disk just to look up item names for display. Item definitions never change while the game is running, so reading them fresh from disk every time is unnecessary work.

There is already a correct solution in the codebase — `repair_utils.py` has a function called `item_name()` that does exactly this lookup using a pre-loaded cache. The cargo manifest should use that instead.

**What to fix:** Replace the `load_item_registry()` call and its inline `resolve_contents()` logic in the cargo manifest route with calls to `item_name()` from `repair_utils`.

---

## GROUP B — Quality issues

---

### B1 — `backend/events/event_system.py` — Silent failure and duplicate log entry

**The problem in plain language:**
In `_break_component_by_id()`, when a component ID from `events.json` cannot be found in any damageable system, the code currently prints a warning to the console and carries on. This violates the no-silent-fallbacks rule — if a component ID can't be found it means the data is wrong and the game should crash immediately with a clear error message.

The same function also writes a ship log entry in this error path, identical to the one already written by the outer `_handle_impact_event()` function. This means the player's ship log would show the same event twice.

**What to fix:**
1. Replace the silent `print` warning with a loud crash (`raise ValueError` or similar) so bad data in `events.json` is caught immediately.
2. Remove the `add_log_entry` call from inside `_break_component_by_id()`. One log entry per event is enough — the outer function handles it.

---

### B2 — `backend/handlers/equip_handler.py` — Lazy import

**The problem in plain language:**
The file imports the `random` module inside a function body (`import random` on line 67 inside `handle_remove()`), instead of at the top of the file where all imports belong. The only valid reason for an import inside a function is to avoid a circular import — `random` is a Python standard library module and cannot cause a circular import under any circumstances. This is sloppy coding.

**What to fix:** Move `import random` to the top of the file with the other imports.

---

### B4 — `backend/models/interactable.py` — Same code written twice (not DRY)

**The problem in plain language:**
The `StorageUnit` class and the `Surface` class both have a method called `contents_str()` — and both are word-for-word identical. If the formatting of item lists ever needs to change, it will need to be changed in two places. Code should not be repeated — if it exists in two places, eventually one will be updated and the other forgotten.

**What to fix:** Pull the shared logic into a small private helper function at the top of `interactable.py` (e.g. `_format_item_list(items)`), and have both classes call it.

---

### B5 — `backend/handlers/repair_utils.py` — Cache assumption not documented

**The problem in plain language:**
`repair_utils.py` loads the item registry once when the file is first imported and caches it permanently. This is correct — the registry stores read-only item definition templates (names, descriptions, mass etc.) that never change at runtime. Each time an item is placed in the world, a fresh instance is created from the template.

However there is nothing in the code explaining this. An AI in a future session, or anyone reading the code cold, might mistake it for a bug or try to reset it unnecessarily.

**What to fix:** Add a short comment above `_item_registry` explaining that it is a read-only template cache, intentionally loaded once at import, and does not need to be included in save/load serialisation.

---

### B7 — `backend/systems/electrical/electrical_system.py` — Docstrings not up to project standard

**The problem in plain language:**
The description at the top of `electrical_system.py` is very brief and the class descriptions inside it are single-line, where other files in the project use properly formatted multi-line descriptions. This file was ported from an earlier project and the documentation was never brought up to standard.

**Why it matters:** Style consistency. Not a bug.

**What to fix:** Expand the module and class docstrings to match the style of files like `electrical_repair.py` and `door_panel_repair.py`. No functional change needed.

---

## Skipped items — reasons recorded

| Item | Reason skipped |
|------|---------------|
| B3 — `[STUB]` text in `repair_handler.py` | Game is deep in development. The stub is a valid reminder of unbuilt code and will not be seen by a real player for a long time. Leave it. |
| B6 — `datapad_suppressed` comment in `game_manager.py` | Save/load will only trigger at idle moments — not mid-terminal, mid-repair, or during any timed action. `datapad_suppressed` will always be `False` at save time by design. No comment needed. |

---

## Save/load readiness notes

The Future doc (Section 7) already has the core list of what needs to be serialised. The following are additions and clarifications from this review session:

- **`game_manager.tablet_notes`** — the entire dict must be saved and restored. Multiple notes can exist simultaneously — one per diagnosed but not-yet-repaired panel (both door panels and electrical junctions). Repair completion reads the note for log labels and then deletes it. If a note is missing after loading, repair completion will crash. Notes are written at diagnosis time and deleted on repair completion — this is intentional design, not a bug.

- **`PowerJunction.broken_components` and `repaired_components`** — mid-repair state. Must be saved and restored. If a junction is mid-repair when the game saves, it must resume correctly on load. These fields must be restored in sync with the corresponding tablet note.

- **`SecurityPanel.broken_components` and `repaired_components`** — same requirement as above but for door panels.

- **`_item_registry` in `repair_utils`** — does NOT need to be serialised. It is a read-only template cache of item definitions. Static data, intentional, never changes at runtime.

- **Save triggers** — autosave only, at idle moments: room change, after any timed action completes, on clean quit. The game will never save mid-repair, mid-diagnosis, mid-timed-action, or while a terminal/datapad/inventory panel is open. This constraint simplifies serialisation significantly — many transient states (e.g. `datapad_suppressed`, `repairInProgress`) will always be at their default values at save time.

- **Frontend globals** (`pendingPin`, `currentRoomId`, `currentRoomPowered`, etc.) — reset automatically on page load, which covers all current save/load paths. No explicit reset needed unless in-game load (without a page reload) is ever added.

---

## Fix order

Work through A1–A3 first, then B1, B2, B4, B5, B7 in order. One at a time, verify after each.

| # | File | Group | One-line description |
|---|------|-------|----------------------|
| A1 | `command.py` + `electrical_repair.py` | Must fix | Private `_profiles` access |
| A2 | `api/game.py` | Must fix | Dead `portable_objects` list |
| A3 | `api/game.py` | Must fix | Unnecessary disk reads on cargo manifest |
| B1 | `event_system.py` | Quality | Silent failure + duplicate log entry |
| B2 | `equip_handler.py` | Quality | Lazy import |
| B4 | `interactable.py` | Quality | Duplicated `contents_str()` — not DRY |
| B5 | `repair_utils.py` | Quality | Add cache explanation comment |
| B7 | `electrical_system.py` | Quality | Docstrings not up to standard |
