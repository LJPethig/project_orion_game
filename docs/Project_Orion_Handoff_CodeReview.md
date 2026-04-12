# PROJECT ORION GAME
## Session Handoff Document — Codebase Review
### April 2026

---

## PURPOSE

This session is a full codebase analysis. The goal is to identify dead code, problematic code, structural issues, and anything that needs cleaning up before Phase 19.5 (save/load) begins. Save/load will touch nearly every part of the codebase — a clean baseline now means fewer surprises later.

**No new features. No new phases. Analysis and cleanup only.**

---

## DESIGN DOCUMENTS

| Document | Purpose |
|----------|---------| 
| `Project_Orion_Design_v19.md` | Master design and architecture document — read this first |

The Phase 19 addendum has been retired. All content is now in the master design doc.

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
- Datapad system — PAD tab, power map, ship's log, notes, messages (stubs)
- Ship's log — structured entries written on diagnosis and repair completion
- Tablet notes — auto-created on diagnosis, deleted on repair complete
- Ship power map — live room colours, hover tooltips, pan/zoom/reset
- Automated storage facility — store/retrieve via UI, manifest on GameManager
- Cargo bay manifest — container/pallet instance data, read-only terminal display
- PalletContainer and Pallet classes in interactable.py
- cargo_containers.json and pallet_platforms.json type definitions
- initial_cargo.json with container/pallet instance data

### What is stubbed or incomplete
- Messages system — data structure exists, no content
- Circuit diagram — SVG being built manually in Inkscape, not yet integrated
- Event system — `check_for_event()` returns None, not implemented
- Save/load — not implemented
- Cargo movement — sack barrow and cargo handler mechanics deferred to Phase 25
- Cargo contents — initial_cargo.json containers are empty, to be authored in Phase 23

### Known deferred items
- Description panel click lockout during timed actions (Loop.isLocked() check needed in description.js)
- Examine command (`examine <item>` prints name, manufacturer, model, description)
- Terminal shutdown on power loss (implement when event system is built)
- Codebase size and structure analysis — this session
- repair_handler.py → repair_utils.py refactor before Phase 24
- terminal.js split plan before Phase 22 mainframe work
- cargo_handler_operational stub on GameManager before Phase 25

---

## WHAT TO DO THIS SESSION

### Full codebase analysis
Read every file in the codebase. Look for:

1. **Dead code** — functions, methods, variables, imports that are defined but never called or referenced anywhere
2. **Stale comments** — comments referencing old behaviour, deprecated approaches, or things that no longer exist
3. **Inconsistencies** — naming conventions violated, patterns not followed, things that work differently from how the rest of the codebase works
4. **Structural problems** — files doing things outside their domain, logic that belongs elsewhere, anything that will cause problems when save/load is built
5. **Silent fallbacks** — any place where missing data degrades silently instead of crashing loudly (violates rule 12)
6. **File size concerns** — files approaching the size where they need splitting, per the known targets already identified

### Known targets to examine closely
- `repair_handler.py` — 628 lines, largest file. Identify what should move to `repair_utils.py`.
- `command_handler.py` — 565 lines, growing verb registry. Flag any structural concerns.
- `terminal.js` — 434+ lines after Phase 19 additions. Split plan needed before Phase 22.
- `game.py` — API routes growing. Check for anything that should be split out.
- `game_manager.py` — now owns storage_manifest and cargo_manifest in addition to original responsibilities. Check cohesion.

### Output format
For each file, provide:
- File size / line count
- Assessment: Clean / Minor issues / Needs attention
- Specific issues found with line references where possible
- Recommended action

Produce a summary document at the end prioritised by urgency.

---

## KEY ARCHITECTURE RULES

1. **Upload current codebase zip at session start** — never work from memory
2. **Read files before changing them** — always
3. **One change at a time** — verify before proceeding
4. **No silent fallbacks** — missing data must crash loudly, not degrade silently
5. **Backend owns all game state** — JS is display only
6. **Minimal targeted changes** — no "while I'm in here" improvements without asking
7. **New files as downloads** — never inline only
8. **Push back on bad design** — don't silently accept wrong decisions
9. **All JSON fields have a use** — when creating instances from type definitions, load all fields
10. **Suggest before adding** — flag anything missing from spec before writing code or docs
11. **Never output complete game.html or game.js** — targeted changes only

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
      loop.js
      constants.js
    screens/
      game.js
      inventory.js
      terminal.js
      datapad.js
      map.js
      description.js
      commands.js
      ui.js
      splash.js
  css/
    game.css
    inventory.css
    terminal.css
    datapad.css
    response.css
    description.css
    splash.css

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

The game is at the boundary of Phase 19 complete and Phase 19.5 (save/load) pending.

---

*Project Orion Game — Session Handoff Document*
*Codebase Review — April 2026*
