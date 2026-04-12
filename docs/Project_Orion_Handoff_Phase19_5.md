# PROJECT ORION GAME
## Session Handoff Document — Phase 19.5 (Save/Load)
### April 2026

---

## PURPOSE

This session begins Phase 19.5 — the save/load system. The codebase has just completed a full review and cleanup session. It is in a clean, well-tested baseline state. No outstanding issues from the review remain except two deferred items (see below).

**Upload the codebase zip at the start of the session. Read files before touching them. One change at a time.**

---

## DESIGN DOCUMENTS

| Document | Purpose |
|----------|---------|
| `Project_Orion_Design_v19.md` | Master design and architecture document — read this first |

---

## THE GAME

Project Orion Game is a Flask/Python backend + vanilla JS frontend space survival simulator. The player is Jack Harrow, an Enso VeilTech employee aboard the Tempus Fugit spacecraft, set in 2276. Core gameplay: move through the ship, diagnose and repair systems, manage inventory, survive.

**Key design philosophy:** Backend owns all game state. JS is display only. No silent fallbacks — missing data must crash loudly. One change at a time, verified before proceeding.

---

## CURRENT CODEBASE STATE

### What is complete and working
- 17-room ship structure with movement and door system
- Electrical system — reactor, panels, breakers, cables, batteries, live power tracing
- Door panel repair system — diagnose, repair, scan tool, repair profiles
- Inventory system — carry, equip, drop, wear
- Terminal system — engineering terminal, power map, storage room terminal, cargo bay terminal
- Datapad system — power map, ship's log, notes, messages (stub — shows placeholder)
- Ship's log — structured entries (timestamp, event, location, detail fields)
- Tablet notes — auto-created on diagnosis, deleted on repair complete
- Ship power map — live room colours, hover tooltips, pan/zoom/reset
- Automated storage facility — store/retrieve via UI, manifest on GameManager
- Cargo bay manifest — container/pallet instance data, read-only terminal display
- Door action distinction — `open` unlocks and opens, `unlock` unlocks only, `lock` locks
- Input locking — command input and description panel both locked during timed actions
- Messages stub — datapad Messages menu opens and shows placeholder correctly

### What is stubbed or incomplete
- Messages system — placeholder only, no content
- Circuit diagram — SVG being built manually in Inkscape, not yet integrated
- Event system — `check_for_event()` returns None, not implemented
- Save/load — **this phase**
- Cargo movement — sack barrow and cargo handler mechanics deferred to Phase 25
- Cargo contents — initial_cargo.json containers are empty, to be authored in Phase 23

### Known deferred items (from codebase review)
- `terminal.js` split into terminal_core.js, terminal_engineering.js, terminal_manifest.js — **before Phase 22**
- `PalletContainer.pallet` flag — purpose unclear, to be resolved **before Phase 23**
- `repair_handler.py` → `repair_utils.py` refactor — **before Phase 24**
- `cargo_handler_operational` stub on GameManager — **before Phase 25**
- Input lockout behavioural inconsistency — terminal uses click guards, timed actions use pointer-events. Not yet unified. Documented in design doc Section 16.

---

## WHAT CHANGED IN THE LAST SESSION

The last session was a codebase review and cleanup. The following changes were made:

### Dead code removed
- `_check_parts()` in `repair_handler.py` — replaced by `_check_all_parts()`, never called
- `repair_progress` and `diagnosed_components` attributes on `SecurityPanel` in `door.py`
- `get_state_label()` method on `SecurityPanel` in `door.py`
- `DEBUG_HAS_REPAIR_TOOL` from `config.py`
- `CARD_SWIPE_GAME_MINUTES` from `config.py`
- Duplicate `Surface as SurfaceModel` import alias in `command_handler.py`
- Duplicate `_instant()` method in `storage_handler.py`
- Duplicate file header comment in `game.js`
- `init_systems()` injection pattern in `systems.py` — replaced with direct import

### Silent fallbacks removed
- `_load_player_items()` in `game_manager.py` — now crashes loudly on missing/corrupt file
- `_load_storage_facility()` in `game_manager.py` — now crashes loudly
- `_load_cargo()` in `game_manager.py` — now crashes loudly
- Type definition loading loop in `_load_cargo()` — now crashes loudly

### Bug fixes
- `_openMessages()` in `datapad.js` — called undefined `_renderStubView()`, now correctly implemented using `_renderDataView()`
- Stray backslash on `if not profile:\` in `repair_handler.py`
- `containers.sort()` in `terminal.js` now runs before `_cargoManifestData` assignment

### Logic corrections
- Door action distinction — `unlock` now correctly unlocks only (does not open). `open` unlocks and opens. `_complete_door_action()` in `command.py` now has explicit branches for each.
- `Loop.lockInput()` in `loop.js` — `unlockInput()` now fires **before** the callback, not after. This allows callbacks to chain a new `lockInput()` without it being immediately cancelled.
- Input locking during door image display — all three paths (non-PIN swipe, PIN swipe, instant open/close) now correctly lock input for the display duration.
- Description panel clicks blocked during timed actions — `Loop.lockInput()` and `Loop.unlockInput()` now set `pointer-events: none` on `description-content`.

### Structural improvements
- `StorageHandler` converted to module-level singleton — consistent with all other handlers
- `systems.py` — replaced `init_systems()` injection with direct `game_manager` import
- `container_handler.py` — `open_description` now accessed via `getattr` guard

### Formatting improvements
- Ship log entries now have separate `location` and `detail` fields (previously concatenated into one string)
- Repair log: "Components Replaced:" label (was "Components:")
- Between-component repair message: "Preparing next component." (was "N components remaining.")

### Comments added
- `calc_diagnose_real_seconds()` — note that it is currently identical to `calc_repair_real_seconds()`, kept separate for anticipated Phase 24 divergence
- Design doc — input lockout behavioural inconsistency documented

---

## PHASE 19.5 — SAVE/LOAD SYSTEM

### Design (from design doc Section 20)

**Philosophy:** No scum saving. No reloading. When you die, you are dead.

**Splash screen:**
- New Game — greyed out if a save file exists
- Continue — greyed out if no save file exists

**Save triggers — autosave only:**
- Room change
- After any timed action completes
- On clean quit

**Death state:** Save file written with `dead: true` flag. Continue shows death screen. Only New Game available.

**Save file scope:**
- Player state (inventory, equipped slots)
- Portable item positions (room floors, container contents, surface contents)
- Door states (open, locked)
- Panel states (is_broken, broken_components, repaired_components, pin, pin_attempts)
- Electrical system state
- Ship time (chronometer state)
- Instance ID counters (so resumed game does not re-use instance IDs)
- Storage manifest state
- Cargo manifest state
- Ship log entries
- Tablet notes
- `dead` flag

### Key design questions still open ⚠️
- Save file format — JSON recommended for simplicity and debuggability
- Save file location — alongside the game, or in a user data directory?
- Self-termination mechanic — multi-step auto-destruct or airlock spacing, needs further discussion

---

## KEY ARCHITECTURE RULES

1. **Upload current codebase zip at session start** — never work from memory
2. **Read files before changing them** — always, upload current versions
3. **One change at a time** — verify before proceeding
4. **No silent fallbacks** — missing data must crash loudly, not degrade silently
5. **Backend owns all game state** — JS is display only
6. **Minimal targeted changes** — no "while I'm in here" improvements without asking
7. **New files as downloads** — never inline only
8. **Push back on bad design** — don't silently accept wrong decisions
9. **All JSON fields have a use** — when creating instances from type definitions, load all fields
10. **Suggest before adding** — flag anything missing from spec before writing code or docs
11. **Never output complete files** — targeted inline changes only, with explicit find/replace
12. **Never work from memory** — if a file has changed since it was last uploaded, ask for the current version

---

## KEY FILE LOCATIONS

```
backend/
  api/
    game.py          — game state, inventory, room, terminal, storage, cargo endpoints
    command.py       — command processing endpoints
    systems.py       — electrical system endpoints
  handlers/
    command_handler.py   — verb registry and routing
    repair_handler.py    — door panel diagnosis and repair
    terminal_handler.py  — terminal access
    storage_handler.py   — store and retrieve for automated storage facility
    item_handler.py
    container_handler.py
    equip_handler.py
    movement_handler.py
    door_handler.py
    base_handler.py
  models/
    game_manager.py  — central game state coordinator
    interactable.py  — full object hierarchy including PalletContainer and Pallet
    player.py
    door.py
    room.py
    ship.py
    chronometer.py
  loaders/
    item_loader.py
  systems/
    electrical/
      electrical_system.py

frontend/static/
  js/
    core/
      api.js
      loop.js        — lockInput/unlockInput manage both command input and description panel
      constants.js
    screens/
      game.js
      inventory.js
      terminal.js
      datapad.js
      map.js
      description.js
      commands.js    — handleResult, door action handling, swipe flow
      ui.js
      splash.js

data/
  items/
    tools.json
    misc_items.json
    wearables.json
    consumables.json
    terminals.json
    storage_units.json
    surfaces.json
    cargo_containers.json
    pallet_platforms.json
  ship/
    structure/
      initial_ship_items.json
      initial_cargo.json
      ship_rooms.json
      door_status.json
      door_access_panel_types.json
      initial_ship_state.json
      player_items.json
    systems/
      electrical.json
  repair/
    repair_profiles.json
  terminals/
    engineering.json
```

---

## IMPORTANT NAMING CONVENTIONS

- Fixed object IDs: `roomid_objectdescription` (e.g. `cargo_bay_inventory_terminal`)
- Cargo container instance IDs: descriptive without room prefix (e.g. `small_container_001`, `pallet_single_001`) — these are moveable
- Panel IDs: `roomid_roomid_panel_side`
- Electrical components: `PNL-`, `FUS-`, `PWC-`, `BAT-` prefixes
- Instance IDs on portable items: assigned at runtime, format `itemid_NNN`

---

## NARRATIVE CONTEXT (brief)

Jack Harrow is an Enso VeilTech employee. The Tempus Fugit is company property. Jack is broke and blacklisted due to a bank hack. Enso VeilTech has issued a compliance order requiring him to return the ship. The mainframe is running Enso VeilTech software.

The game is at Phase 19.5 — save/load implementation.

---

*Project Orion Game — Session Handoff Document*
*Phase 19.5 (Save/Load) — April 2026*
