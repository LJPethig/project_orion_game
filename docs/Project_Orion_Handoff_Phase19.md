# PROJECT ORION GAME
## Session Handoff Document — Phase 19
### April 2026

---

## PURPOSE

This document is the starting point for the next development session. It summarises the current state of the codebase, what was completed in the previous session, what is to be built next, and the rules that govern how we work.

The lead designer will upload the current codebase zip at the start of the new session. Read this document first, then read the relevant design documents before touching any code.

---

## DESIGN DOCUMENTS

| Document | Purpose |
|----------|---------|
| `Project_Orion_Design_v18.md` | Master design and architecture document |
| `Project_Orion_Addendum_Phase19.md` | Full implementation detail for Phase 19 ship inventory |
| `Project_Orion_Narrative_v3.md` | Narrative, events, dialogue, story beats |

**Read the Phase 19 addendum in full before writing any code.**

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
- Terminal system — engineering terminal, power map, circuit diagram placeholder
- Datapad system — PAD tab, power map, ship's log, notes, messages (stubs)
- Ship's log — structured entries written on diagnosis and repair completion
- Tablet notes — auto-created on diagnosis, deleted on repair complete
- Automated notes and log accessible from datapad
- Ship power map — live room colours, power source icon colours, hover tooltips, pan/zoom/reset
- PAD and TERM tabs mutually exclusive
- Debug console (Ctrl+D) — break/fix electrical components

### What is stubbed or incomplete
- Messages system — data structure exists, no content
- Notes archived state — not yet implemented
- Circuit diagram — SVG being built manually in Inkscape, not yet integrated
- Event system — `check_for_event()` returns None, not implemented
- Save/load — not implemented
- Ship inventory/cargo — Phase 19, to be built this session

### Known deferred items
- Description panel click lockout during timed actions (Loop.isLocked() check needed in description.js)
- Ship power map reset key on terminal (terminal.js [0] key — deferred, done on datapad only)
- Ship power map hover tooltips already done
- Codebase size analysis before Phase 23
- Examine command (`examine <item>` prints name, manufacturer, model, description)

---

## WHAT TO BUILD THIS SESSION — PHASE 19

Full detail in `Project_Orion_Addendum_Phase19.md`. Summary:

### The automated storage facility
A new fixed object type in the storage room only. Not a StorageUnit. One instance with its own independent manifest on GameManager. The cargo bay has no automated storage facility — it is a freight space with a pre-existing shipping manifest.

### New commands
- `store <item>` — removes item from carried inventory, logs it to the storage room facility manifest. Storage room only.
- `retrieve <item>` — removes item from facility manifest, adds to carried inventory. Storage room only.
- New verbs in command_handler.py routed to new StorageHandler

### Cargo bay
- Freight space. Cargo arrives pre-loaded with a shipping manifest transmitted to the mainframe at load time.
- Cargo handler (sit-on, forklift style) — moves large containers and pallet platforms
- Sack barrow — moves small containers only, through wider doors to engineering/propulsion
- Three container sizes — large (1200x800x900mm, standalone), medium (600x800x900mm, on platform), small (600x400x900mm, on platform/sack barrow)
- Pallet platform (1200x800x150mm) — base unit for medium and small containers, awkward items strap to it
- Operational capacity: ~70 large containers (all doors clear, handler can manoeuvre)
- Cargo bay terminal — read-only shipping manifest display only. No store/retrieve.

### Terminal integration
- Cargo bay terminal — shipping manifest read-only, cargo handler status
- Storage room terminal — stored items with retrieve option

### Inventory panel
- Contextual Store button on carried items when player is in storage room only

---

## FILES TO CREATE

- `backend/handlers/storage_handler.py`
- `data/terminals/cargo_bay.json`
- `data/terminals/storage_room.json`

---

## FILES TO MODIFY

- `backend/models/game_manager.py` — storage_manifests, cargo_manifest, helper methods
- `backend/handlers/command_handler.py` — register store, retrieve verbs
- `backend/loaders/item_loader.py` — handle pallet flag, auto-log to cargo_manifest
- `backend/api/game.py` — new storage endpoint
- `frontend/static/js/screens/inventory.js` — contextual Store button
- `data/ship/structure/initial_ship_items.json` — pallet cargo, coffee container

---

## KEY ARCHITECTURE RULES

1. **Upload current codebase zip at session start** — never work from memory
2. **Read files before changing them** — always
3. **One change at a time** — verify before proceeding
4. **No silent fallbacks** — missing data must crash loudly, not degrade silently
5. **Backend owns all game state** — JS is display only
6. **Minimal targeted changes** — no "while I'm in here" improvements without asking
7. **New files delivered as downloads** — never inline only
8. **Push back on bad design** — don't silently accept wrong decisions
9. **Never output complete game.html or game.js** — targeted changes only

---

## KEY FILE LOCATIONS

```
backend/
  api/
    game.py          — game state, inventory, room, terminal, datapad endpoints
    command.py       — command processing endpoints
    systems.py       — electrical system endpoints
  handlers/
    command_handler.py   — verb registry and routing
    repair_handler.py    — door panel diagnosis and repair
    terminal_handler.py  — terminal access
    storage_handler.py   — NEW: store and retrieve commands
  models/
    game_manager.py  — central game state coordinator
    interactable.py  — item hierarchy
    player.py        — player state
    door.py          — door and security panel
  loaders/
    item_loader.py   — item registry and instantiation
  systems/
    electrical/
      electrical_system.py  — power distribution logic

frontend/static/
  js/
    core/
      api.js         — all fetch calls
      loop.js        — polling loop and input locking
      constants.js   — frontend constants
    screens/
      game.js        — main orchestrator
      inventory.js   — inventory panel
      terminal.js    — terminal panel
      datapad.js     — datapad panel
      map.js         — shared ship power map logic
      description.js — room description rendering
      commands.js    — command handling and result routing
      ui.js          — UI utilities
  css/
    game.css         — main layout
    inventory.css    — inventory panel
    terminal.css     — terminal and map tooltip
    datapad.css      — datapad panel
    response.css     — response panel

data/
  items/
    tools.json       — scan tool, HV kit, screwdrivers etc
    misc_items.json  — datapad, ID cards
    wearables.json   — EVA suit, coveralls, boots
    consumables.json — food, water (future)
  ship/
    structure/
      initial_ship_items.json  — item placement at game start
      ship_rooms.json          — room definitions
      door_status.json         — door connections and panel types
      door_access_panel_types.json — panel type registry
      player_items.json        — player starting items
    systems/
      electrical.json          — electrical component definitions
  repair/
    repair_profiles.json       — per-panel-type diagnosis and repair data
  terminals/
    engineering.json           — engineering terminal content
    cargo_bay.json             — NEW: cargo bay terminal content
    storage_room.json          — NEW: storage room terminal content
```

---

## IMPORTANT NAMING CONVENTIONS

- Object IDs: `roomid_objectdescription` (e.g. `cargo_bay_auto_storage`)
- Instance IDs: assigned at runtime, format `itemid_NNN`
- Panel IDs: `roomid_roomid_panel_side` (e.g. `crew_cabin_main_corridor_panel_crew`)
- Electrical components: `PNL-`, `FUS-`, `PWC-`, `BAT-` prefixes

---

## NARRATIVE CONTEXT (brief)

Jack Harrow is an Enso VeilTech employee. The Tempus Fugit is company property. Jack is currently broke and blacklisted due to a bank hack that destroyed his finances. Enso VeilTech has issued a compliance order requiring him to return the ship. The mainframe is running Enso VeilTech software and has locked the navigation.

The game is at the boundary of Phase 18 complete and Phase 19 beginning.

---

*Project Orion Game — Session Handoff Document*
*April 2026*
