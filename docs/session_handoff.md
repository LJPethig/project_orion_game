# PROJECT ORION — SESSION HANDOFF April 2026
## Next objective: Complete save/load system (Phase 19.5) then update docs

Attached is the complete current codebase as a zip. Read every file before doing anything.
Do not work from memory or assumptions — the code is the authority.

---

## What was completed this session

### Codebase review #2
Full review completed and all agreed fixes applied. See `docs/archive/review_april_2026.md`.

### Save system — all 8 stages complete
`backend/systems/save/save_manager.py` serialises and restores all game state.
The save file (`saves/save.json` + `saves/save_backup.json`) is tested and working.

**What is saved:**
- Player inventory and equipped slots
- Ship time (chronometer)
- All room state (floor items, container open/closed, container and surface contents)
- All door state (open/locked) and panel repair state
- Electrical system (reactors, batteries, panels, breakers, cables)
- Events (fired/resolved flags)
- Ship log and tablet notes
- Storage manifest and cargo manifest

**Save trigger:** Jack rests at captain's quarters bunk (or future: hypersleep pod).
No autosave timer — rest is the only save point. See `docs/save_load_design.md`.

### Rest command
`backend/handlers/rest_handler.py` — new handler.
`rest` command works. 8 second animation showing hours (1h–8h). Get up / Quit buttons.
Save fires on Get Up click via `/api/command/save`.

### Other fixes this session
- Chronometer now tracks elapsed minutes since ship commission date (17-03-2223 13:47)
  not since year 0. Game start: 08-09-2276 03:16.
- `ship._build_panel_index()` made public → `build_panel_index()`
- `player._inventory` access replaced with public `clear_inventory()` and
  `restore_inventory_item()` methods
- No-power diagnosis log entry moved to completion (correct timestamp)
- `PLAYER_MAX_CARRY_MASS` moved to `config.py`
- Narrative notes created: `docs/narrative_notes.md`

---

## What needs doing next session

### 1. Load game — wire up the splash screen (Priority 1)
The `load_game()` function exists in `save_manager.py` but nothing calls it yet.

**Load sequence:**
1. `new_game()` — initialises everything from JSON as normal
2. `load_game(game_manager)` — overlays save state on top
3. `reset_instance_counters_past(max_id)` — see instance ID section below

The splash screen needs:
- **Continue** button — calls new_game() then load_game(), redirects to game screen
- **New Game** button — if save exists, two-step confirmation warning before proceeding
- **Dead save** — if save file has `dead: true`, Continue shows death screen

The `dead` flag is not yet implemented in the save file — it needs adding to
`save_manager.py` as a meta field, and the splash screen must check for it.

### 2. Instance ID counter restoration (Critical — must do before load works)
**Why this is needed:** The load sequence calls `new_game()` first, which calls
`reset_instance_counters()` — resetting all counters to zero. `load_game()` then
restores all items from the save file with their existing `instance_id` values intact.
So far so good. But after loading, if anything creates a new item (player picks
something up, a cable spool is consumed and replaced etc.), the counter starts from
zero again and generates IDs like `cable_hv_standard_001` — which already exists in
the loaded game. Duplicate instance IDs break the item system.

Saving and restoring the counters means after loading, new items continue from where
they left off — `cable_hv_standard_004`, `cable_hv_standard_005` etc. — with no
risk of collision.

**The fix:** The instance ID counters in `item_loader.py` must be saved and restored
directly — not inferred by scanning the save file.

Read `item_loader.py` fully before touching anything. The counters dict must be:
- Added to the save file meta section in `save_manager.py`
- Restored after `new_game()` resets them, before anything creates new items

`reset_instance_counters()` is called by `new_game()` — the load sequence must
restore the saved counters immediately after.

### 3. Event strip restoration on load
When the game loads, the event strip must show any fired-but-unresolved events.
`event_system.get_active_events()` already returns these — the load sequence just
needs to call it and pass results to the frontend after loading.

### 4. Doc updates (do after save/load is complete and tested)
These docs are out of date and need rewriting:
- `docs/Project_Orion_Design_v25.md` — update phase history, add rest command,
  save/load system, commission date/start date changes, chronometer fix,
  narrative_notes.md reference. Increment to v26.
- `docs/Project_Orion_Future_v3.md` — Phase 19.5 is now complete, update build plan.
  Increment to v4.

Do NOT update these docs until save/load is fully working and tested.

---

## Key files changed this session

```
backend/systems/save/save_manager.py   ← new system, all 8 stages
backend/systems/save/__init__.py       ← new (empty package init)
backend/handlers/rest_handler.py       ← new handler
backend/api/command.py                 ← rest_complete + save endpoints
backend/models/player.py              ← clear_inventory(), restore_inventory_item()
backend/models/chronometer.py         ← commission date offset
backend/models/ship.py                ← build_panel_index() (was private)
backend/events/event_system.py        ← get_fired_state(), restore_fired_state(),
                                         build_panel_index() call fixed
backend/handlers/door_panel_repair.py ← log timestamp fix (no-power path)
config.py                             ← SHIP_COMMISSION_DATE, START_DATE_TIME updated,
                                         PLAYER_MAX_CARRY_MASS, REST_REAL_SECONDS,
                                         REST_SHIP_HOURS
frontend/static/js/core/api.js        ← saveGame(), completeRest()
frontend/static/js/screens/commands.js ← rest action handler, get up/quit buttons
frontend/static/js/core/constants.js  ← REST_SHIP_HOURS
frontend/static/js/screens/ui.js      ← _startHoursCounter(), showRestAnimation(),
                                         hideRestAnimation()
saves/save.json                        ← runtime generated (in .gitignore)
saves/save_backup.json                 ← runtime generated (in .gitignore)
docs/save_load_design.md              ← complete Phase 19.5 design
docs/narrative_notes.md               ← new, locked narrative canon
docs/archive/review_april_2026.md     ← new, completed codebase review
```

---

## Working rules — non-negotiable

- **Ask for files before making any changes** — never work from memory
- **Read every uploaded file completely before touching anything**
- **No lazy imports** unless there is a genuine circular import risk — document why
- **Never access private attributes or methods from outside their class**
- **One change at a time, verify before proceeding**
- **No silent fallbacks** — bad data must crash loudly
- **New files as downloads, existing file changes as inline find/replace**
- **No smelly code** — separation of concerns, no dead code
- **Push back on bad design** rather than silently accepting it

---

## Key documents to read before starting

1. `docs/save_load_design.md` — authoritative save/load design
2. `docs/narrative_notes.md` — locked narrative canon
3. `docs/archive/review_april_2026.md` — completed review for context
