# PROJECT ORION GAME
## Session Handoff Document
### April 2026

---

## PURPOSE

This document provides context for a new chat session. Read the design document first, then this document. Upload the full codebase zip before making any changes.

**Upload current codebase zip at session start. Read files before touching them. One change at a time.**

---

## DESIGN DOCUMENTS

| Document | Purpose |
|----------|---------|
| `Project_Orion_Design_v20.md` | Master design and architecture document — read this first |
| `Project_Orion_Narrative_v4.md` | Narrative and events document |

---

## THE GAME

Project Orion Game is a Flask/Python backend + vanilla JS frontend space survival simulator. The player is Jack Harrow, an Enso VeilTech employee aboard the Tempus Fugit spacecraft, set in 2276. Core gameplay: move through the ship, diagnose and repair systems, manage inventory, survive.

**Key design philosophy:** Backend owns all game state. JS is display only. No silent fallbacks — missing data must crash loudly. One change at a time, verified before proceeding.

---

## CURRENT CODEBASE STATE

### What is complete and working
- 17-room ship structure with movement and door system
- Full electrical system — reactor, propulsion reactor, panels, breakers, cables, batteries, engines
- Propulsion bypass path — `PWC-ENG-00` connects propulsion reactor to `PNL-ENG-MAIN` (starts broken)
- Power tracer — any operational FissionReactor terminates trace, multiple inbound cables tried
- Engine fixed objects — `Engine` class with `powered` and `online` flags
- SVG ship map — engine icons, reactor eject overlays, colour state, hover tooltips
- Door panel repair system — diagnose, repair, scan tool, per-component, auto-chain
- Inventory system — carry, equip, drop, wear
- Terminal system — engineering, storage room, cargo bay terminals
- Datapad system — power map, ship's log, notes, messages stub
- Automated storage facility — store/retrieve via UI, quantity support in initial_ship_items.json
- Cargo bay — trade items in containers, four-column manifest display
- Ship time — 40 real seconds = 1 ship minute
- Event system — EventSystem class, frontend poll every 15 seconds, repairInProgress flag
- Impact event — fires 3 ship minutes after game start, damages cables and breaker
- Event strip — orange message, blinks 3 times, persists until resolved
- Electrical repair parts — HV service kit, circuit breakers (6 sizes), HV wire (2 gauges), connectors, bus bars, logic boards

### What is stubbed or incomplete
- Messages system — placeholder only
- Circuit diagram — SVG being built manually in Inkscape
- Electrical repair system — parts and design complete, profiles and handler not yet built
- Fixed object repair — engines and reactors not yet repairable
- Event system — impact event hardcoded, needs JSON-driven approach
- Save/load — not implemented
- Cargo movement — deferred
- Survival mechanics — deferred

---

## WHAT TO DO THIS SESSION

### Immediate priority — file splits
**Do piece by piece. Fully test each split before starting the next.**

**Split 1 — `repair_handler.py`**
Extract utility functions to `repair_utils.py`. The handler is over 600 lines. Utility functions (time calculations, parts checking, profile loading) belong in a separate file. The handler itself retains only the verb handlers and state machine logic.

**Split 2 — `terminal.js`**
Split into three files:
- `terminal_core.js` — shared terminal infrastructure (open, close, keypress, typewriter)
- `terminal_engineering.js` — engineering terminal specific rendering
- `terminal_manifest.js` — storage and cargo manifest rendering

**Split 3 — `command_handler.py`**
Review for split candidates after the above are complete.

### After file splits — electrical repair profiles
Build `data/repair/electrical_repair_profiles.json`.

**Structure** — keyed by panel ID, same pattern as `repair_profiles.json`:

```json
{
  "PNL-ENG-MAIN": {
    "diag_tools_required": ["hv_service_kit"],
    "repair_tools_required": ["hv_service_kit"],
    "components": [
      {"component_id": "PNL-ENG-MAIN", "type": "panel",   "diag_time_mins": 20, "repair_time_mins": 45},
      {"component_id": "FUS-ENG-01",   "type": "breaker", "diag_time_mins": 10, "repair_time_mins": 20},
      {"component_id": "PWC-ENG-00",   "type": "cable",   "diag_time_mins": 15, "repair_time_mins": 30},
      {"component_id": "PWC-ENG-01",   "type": "cable",   "diag_time_mins": 15, "repair_time_mins": 30}
    ]
  }
}
```

**Parts per component type:**
- Breaker: 1x matching amp-rated breaker item
- Cable (standard): `wire_hv_standard` by `length_m` + 2x `hv_connect_standard`
- Cable (heavy duty): `wire_hv_heavy_duty` by `length_m` + 2x `hv_connect_heavy`
- Panel: 1x `hv_logic_board` + 1x `hv_bus_bar`

**Heavy duty cables** (use `wire_hv_heavy_duty`):
`PWC-ENG-01`, `PWC-PRO-01`, `PWC-PRO-04`, `PWC-ENG-00`, `PWC-PRO-02`, `PWC-PRO-03`

**NOTE:** `length_m` needs adding to each cable in `electrical.json` before profiles can be completed. Estimated values are acceptable for now.

---

## KEY ARCHITECTURE RULES

1. **Upload current files at start of every session** — never work from memory
2. **Read the code before changing it** — always
3. **One change at a time** — verify before proceeding
4. **No silent fallbacks** — missing data must crash loudly
5. **Backend owns all game state** — JS is display only
6. **Minimal targeted changes** — no "while I'm in here" improvements without asking
7. **New files as downloads** — never inline only
8. **Push back on bad design** — don't silently accept wrong decisions
9. **All JSON fields have a use** — load all fields, never partially load
10. **Suggest before adding** — flag missing spec items before writing code
11. **Never output complete files** — targeted find/replace only
12. **File splits — piece by piece, fully tested before next split**

---

## KEY FILE LOCATIONS

```
backend/
  api/
    game.py
    command.py
    systems.py
    events.py              ← /api/events/check
  events/
    __init__.py
    event_system.py        ← EventSystem class
  handlers/
    command_handler.py     ← verb registry and routing
    repair_handler.py      ← door panel diagnosis and repair (SPLIT CANDIDATE)
    terminal_handler.py
    storage_handler.py
    item_handler.py
    container_handler.py
    equip_handler.py
    movement_handler.py
    door_handler.py
    base_handler.py
  models/
    game_manager.py        ← central coordinator, event_system attribute
    interactable.py        ← full hierarchy including Engine
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
      loop.js              ← repairInProgress flag, 40s tick, event poll
      constants.js
    screens/
      game.js
      inventory.js
      terminal.js          ← SPLIT CANDIDATE
      datapad.js
      map.js               ← engine icons, eject state
      description.js
      commands.js
      ui.js                ← appendEventStrip, clearEventStrip
      splash.js
  css/
    game.css
    inventory.css
    terminal.css
    datapad.css
    response.css
    description.css
    events.css             ← event strip styling
    splash.css

data/
  items/
    tools.json             ← hv_service_kit
    consumables.json       ← HV parts, circuit breakers, wire gauges
    trade_items.json
    engines.json
    cargo_containers.json
    pallet_platforms.json
    terminals.json
    storage_units.json
    surfaces.json
    misc_items.json
    wearables.json
  ship/
    structure/
      ship_rooms.json      ← engines in propulsion_bay
      door_status.json
      door_access_panel_types.json
      initial_ship_state.json   ← PWC-ENG-00 intact:false
      initial_ship_items.json   ← HV parts in storage, quantity support
      initial_cargo.json        ← trade items in containers
      player_items.json
    systems/
      electrical.json      ← propulsion bypass, corrected amp ratings
  repair/
    repair_profiles.json   ← door panel profiles
  terminals/
    engineering.json
```

---

## IMPORTANT NAMING CONVENTIONS

- Fixed object IDs: `roomid_objectdescription`
- Cargo container instance IDs: descriptive without room prefix (`small_container_001`)
- Panel IDs: `roomid_roomid_panel_side`
- Electrical components: `PNL-`, `FUS-`, `PWC-`, `BAT-` prefixes
- Instance IDs on portable items: `itemid_NNN` assigned at runtime
- Breaker item IDs: `10A_breaker`, `32A_breaker`, `63A_breaker`, `250A_breaker`, `600A_breaker`, `1200A_breaker`
- Wire item IDs: `wire_low_voltage`, `wire_hv_standard`, `wire_hv_heavy_duty`
- HV connector IDs: `hv_connect_standard`, `hv_connect_heavy`

---

## NARRATIVE CONTEXT (brief)

Jack Harrow is an Enso VeilTech employee. The Tempus Fugit is company property. Jack is broke and blacklisted. The mainframe runs Enso VeilTech software. The full narrative is in `Project_Orion_Narrative_v4.md` — the opening sequence involves a Robo Pet AI, reactor ejection, and escape. The impact event at game start is the inciting incident.

---

*Project Orion Game — Session Handoff Document*
*April 2026*
