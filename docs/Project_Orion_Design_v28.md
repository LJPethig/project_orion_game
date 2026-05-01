# PROJECT ORION GAME
## Space Survival Simulator
### Technical Reference & Current State
**Version 28.0 — May 2026**

> ⚠️ **IMPORTANT — DO NOT ASSUME ALL CONTENT IN THIS DOCUMENT IS CORRECT.** This document has evolved organically over many development sessions. Not all sections have been manually verified against the current codebase. Where the code and the document conflict, the code is authoritative. Treat this document as a guide and reference, not a specification.

> **Companion documents:**
> - `Project_Orion_Future_v6.md` — build plan and upcoming work
> - `Project_Orion_Door_System.md` — door security, panels, emergency release
> - `Project_Orion_Repair_System.md` — repair profiles, diagnosis architecture, electrical
> - `Project_Orion_Event_System.md` — event types, JSON format, randomisation
> - `docs/deferred_systems.md` — fully designed but not yet built
> - `Project_Orion_Room_Description_Style_v1.md` — room description authoring rules
> - `docs/narrative_notes.md` — narrative canon
> - `docs/archive/review_april_2026.md` — April 2026 codebase review

---

## 1. PROJECT OVERVIEW

### Concept
Project Orion Game is a space survival simulator set in 2276. The player operates a solo trader/explorer spacecraft named the **Tempus Fugit**, captained by **Jack Harrow** — an employee of the Enso VeilTech corporation. Core gameplay revolves around maintaining ship systems, repairing failures, and surviving deep space. This is a serious "slow burner" simulator — not an arcade game. Systems fail, cascade, and the player must diagnose and fix them before things get fatal.

### Core Philosophy
*"If the ship dies, you die."* Generous time windows. Thoughtful problem solving over frantic action. The player physically moves through the ship, gathers the right tools and parts, and repairs systems.

### Technology Stack
| Component | Technology |
|-----------|-----------|
| Game Logic | Python 3.14 |
| Web Server | Flask |
| UI | HTML / CSS / Vanilla JS |
| Ship Diagrams | SVG (interactive, live state) |
| Data | JSON files |
| Version Control | Git |

**No JS frameworks. No ORM. Keep it simple and maintainable.**

---

## 2. CURRENT STATE — WHAT IS BUILT AND WORKING

### Core systems
- Rooms, doors, security panels, command system, chronometer ✅
- Player, inventory, items ✅
- Fixed object data structure: terminals, storage units, surfaces, pallet containers, pallet platforms, engines, power junctions ✅
- Description panel: markup parser, hover tooltips, click handlers, Layer 2/3 ✅
- Description panel: token injection (`^power_state^`, `@reactor_state@`) ✅
- Description panel: powered/unpowered addendum with 8s flash animation ✅
- Description panel: colour scheme, Share Tech Mono font, power junction markup ✅
- Description panel: `~text~` italic markup, fixed room title, panel priority toggle ✅
- Description panel: stale tooltip hidden on room change ✅
- Description panel: items grouped by display_name with xN quantity suffix on surfaces, containers, floor ✅
- Container/equip/floor commands ✅
- Player inventory: grouped by display_name with quantity column, mass in detail panel ✅
- Inventory detail panel: model, manufacturer, mass shown. Store button in storage room ✅
- Smart command parser: ID resolver, verb conflict resolution, clarification system ✅
- Item registry: unique instances, instance_id per item ✅
- Item placement: quantity format `{"id": "x", "quantity": N}` supported in initial_ship_items.json ✅
- Terminal system: CRT styling, typewriter, keypress nav, sub-menus, terminal mode lockout ✅
- Terminal auto-close on power cut ✅
- Electrical system: reactor, panels, breakers, cables, batteries, power tracing ✅
- Electrical service layer: break/trip/fix/connect/disconnect/break_panel_component/eject/install ✅
- Breaker state: damaged + tripped flags, operational derived ✅
- CircuitPanel: 5 internal flags, operational derived ✅
- Cable fields: length_m, connected, emergency_bypass ✅
- Engineering terminal: technical data, electrical sub-menu, power map ✅
- Debug console: Ctrl+D, break/trip/fix/check/connect/disconnect/eject/install ✅
- Full door panel repair system — see `Project_Orion_Repair_System.md` ✅
- Full door security system — see `Project_Orion_Door_System.md` ✅
- Emergency release mechanic — see `Project_Orion_Door_System.md` ✅
- Full electrical junction repair system — see `Project_Orion_Repair_System.md` ✅
- Event system — see `Project_Orion_Event_System.md` ✅
- Automated storage facility: store/retrieve via UI, CRT terminal display ✅
- Cargo bay manifest: read-only CRT terminal display ✅
- Input locking during all timed actions ✅
- Ship log structured entries: timestamp, event, location, detail ✅
- SVG ship map: engine icons, reactor eject overlays, hover tooltips ✅
- Ship time multiplier: 40 real seconds = 1 ship minute ✅
- Jack's internal monologue: `appendMonologue()`, styled box ✅
- Reactor state system: `@reactor_state@` token, online/offline/ejected ✅
- Save/load system: Phase 19.5 — see Section 8 ✅
- Rest command: captain's quarters bunk or rec-room sofa ✅
- Start screen: New Game / Continue, two-step confirm ✅
- Chronometer: tracks elapsed minutes since commission date (17-03-2223 13:47) ✅
- Junction diagnosis state persisted in save/load ✅

### Phase history (summary)
- **Phases 6–15** — core game shell, rooms, movement, doors, inventory, description panel, terminal, parser ✅
- **Phase 16** — terminal system ✅
- **Phase 17** — electrical system integration ✅
- **Phase 18** — full repair system ✅
- **Phase 19** — storage facility + cargo manifest ✅
- **Phase 19.5** — save/load, rest, start screen ✅
- **Post-19.5** — electrical expansion, event system, electrical repair, description overhaul, visual polish ✅
- **Codebase reviews #1 and #2 (2026)** — dead code, silent fallbacks, DRY refactor ✅
- **May 2026** — inventory/description grouping, door system overhaul, emergency release, diagnosis architecture refactor, event randomisation ✅

---

## 3. FOLDER STRUCTURE

```
project_orion_game/
│
├── main.py
├── config.py
├── requirements.txt
│
├── backend/
│   ├── models/
│   │   ├── game_manager.py
│   │   ├── ship.py
│   │   ├── room.py
│   │   ├── door.py                ← per-side panel_type; emergency_released on Door; is_diagnosed on SecurityPanel
│   │   ├── interactable.py        ← PowerJunction carries broken_components, repaired_components
│   │   ├── player.py
│   │   └── chronometer.py
│   │
│   ├── systems/
│   │   ├── electrical/
│   │   │   ├── electrical_system.py
│   │   │   └── electrical_service.py
│   │   └── save/
│   │       └── save_manager.py    ← PowerJunction repair state now persisted per room
│   │
│   ├── events/
│   │   └── event_system.py        ← loads repair_profiles.json at init; randomise_damage implemented
│   │
│   ├── handlers/
│   │   ├── base_handler.py        ← emergency release prompt and released response helpers
│   │   ├── command_handler.py
│   │   ├── movement_handler.py    ← emergency release prompt on go/enter
│   │   ├── door_handler.py        ← allow_emergency flag on _check_panel
│   │   ├── repair_handler.py
│   │   ├── door_panel_repair.py   ← repair_tools_override support; is_diagnosed checks
│   │   ├── electrical_repair.py
│   │   ├── repair_utils.py        ← component_display_name handles actuator_reset
│   │   ├── item_handler.py
│   │   ├── container_handler.py
│   │   ├── equip_handler.py
│   │   ├── terminal_handler.py
│   │   ├── storage_handler.py
│   │   └── rest_handler.py
│   │
│   ├── loaders/
│   │   └── item_loader.py
│   │
│   └── api/
│       ├── game.py                ← panel_damaged includes emergency_released for tooltip
│       ├── command.py             ← emergency_release_complete endpoint; pending_move support
│       ├── systems.py
│       └── events.py
│
├── frontend/
│   └── static/
│       ├── css/
│       │   ├── start-screen.css
│       │   ├── game.css
│       │   ├── description.css
│       │   ├── inventory.css
│       │   ├── response.css
│       │   ├── terminal.css
│       │   ├── datapad.css
│       │   └── events.css
│       └── js/
│           ├── core/
│           │   ├── constants.js
│           │   ├── api.js         ← completeEmergencyRelease() added
│           │   └── loop.js
│           └── screens/
│               ├── start-screen.js
│               ├── ui.js          ← showLeverAnimation() added
│               ├── commands.js    ← emergency release handlers
│               ├── description.js ← item grouping with xN suffix
│               ├── inventory.js   ← qty column, mass in detail panel
│               ├── terminal_core.js
│               ├── terminal_engineering.js
│               ├── terminal_manifest.js
│               ├── map.js
│               └── game.js        ← tooltip hidden on room change
│
├── data/
│   ├── items/
│   │   ├── tools.json
│   │   ├── wearables.json
│   │   ├── misc_items.json
│   │   ├── consumables.json
│   │   ├── trade_items.json
│   │   ├── terminals.json
│   │   ├── storage_units.json
│   │   ├── surfaces.json
│   │   ├── engines.json
│   │   ├── power_junctions.json
│   │   ├── cargo_containers.json
│   │   └── pallet_platforms.json
│   ├── game/
│   │   └── events.json            ← random_selection_count added; randomise_damage implemented
│   ├── terminals/
│   │   └── engineering.json
│   ├── repair/
│   │   ├── repair_profiles.json   ← actuator_reset entry on vesper_ulock with repair_tools_override
│   │   └── electrical_repair_profiles.json
│   └── ship/
│       ├── structure/
│       │   ├── ship_rooms.json
│       │   ├── door_status.json   ← panel_type per panel entry; all 16 doors updated
│       │   ├── door_access_panel_types.json
│       │   ├── initial_ship_state.json
│       │   ├── initial_ship_items.json  ← quantity format supported
│       │   ├── initial_cargo.json
│       │   └── player_items.json
│       └── systems/
│           └── electrical.json
│
├── saves/
│   ├── save.json
│   └── save_backup.json
│
└── docs/
    ├── Project_Orion_Design_v28.md
    ├── Project_Orion_Future_v6.md
    ├── Project_Orion_Door_System.md
    ├── Project_Orion_Repair_System.md
    ├── Project_Orion_Event_System.md
    ├── Project_Orion_Room_Description_Style_v1.md
    ├── deferred_systems.md
    ├── narrative_notes.md
    └── archive/
        └── review_april_2026.md
```

---

## 4. CONFIG.PY — KEY CONSTANTS

```python
SHIP_NAME             = "Tempus Fugit"
PLAYER_NAME           = "Jack Harrow"
PLAYER_MAX_CARRY_MASS = 40.0          # kg — temporary, sack barrow not yet implemented
STARTING_ROOM         = "engineering"

SHIP_COMMISSION_DATE  = (2223, 3, 17, 13, 47)
START_DATE_TIME       = (2276, 9, 8, 3, 16)

CARD_SWIPE_REAL_SECONDS   = 5
REST_REAL_SECONDS         = 8
REST_SHIP_HOURS           = 8

REPAIR_TIME_BASE_SECONDS  = 8
REPAIR_TIME_SCALE_SECONDS = 8
REPAIR_TIME_PIVOT_MINUTES = 30
REPAIR_TIME_CAP_SECONDS   = 20
DIAG_ACCESS_OVERHEAD      = 0.25
DIAG_TIME_JITTER          = 0.10

ROOMS_JSON_PATH            = 'data/ship/structure/ship_rooms.json'
DOORS_JSON_PATH            = 'data/ship/structure/door_status.json'
DOOR_PANEL_TYPES_PATH      = 'data/ship/structure/door_access_panel_types.json'
INITIAL_STATE_JSON_PATH    = 'data/ship/structure/initial_ship_state.json'
SHIP_ITEMS_JSON_PATH       = 'data/ship/structure/initial_ship_items.json'
PLAYER_ITEMS_JSON_PATH     = 'data/ship/structure/player_items.json'
CARGO_JSON_PATH            = 'data/ship/structure/initial_cargo.json'
ELECTRICAL_JSON_PATH       = 'data/ship/systems/electrical.json'
EVENTS_JSON_PATH           = 'data/game/events.json'

ITEM_FILES = [
    'data/items/tools.json',
    'data/items/wearables.json',
    'data/items/misc_items.json',
    'data/items/consumables.json',
    'data/items/trade_items.json',
]
TERMINALS_JSON_PATH        = 'data/items/terminals.json'
STORAGE_UNITS_JSON_PATH    = 'data/items/storage_units.json'
SURFACES_JSON_PATH         = 'data/items/surfaces.json'
ENGINES_JSON_PATH          = 'data/items/engines.json'
POWER_JUNCTIONS_JSON_PATH  = 'data/items/power_junctions.json'
CARGO_CONTAINERS_JSON_PATH = 'data/items/cargo_containers.json'
PALLET_PLATFORMS_JSON_PATH = 'data/items/pallet_platforms.json'

REPAIR_PROFILES_PATH            = 'data/repair/repair_profiles.json'
ELECTRICAL_REPAIR_PROFILES_PATH = 'data/repair/electrical_repair_profiles.json'
TERMINAL_CONTENT_PATH           = 'data/terminals'
```

---

## 5. GAME LOOP & COMMAND SYSTEM

### Game loop
**Instant actions** — no game time, immediate response, input stays unlocked.
**Timed actions** — backend returns `real_seconds`, frontend locks input, calls back to complete.

Frontend polling: poll every 10s, tick every 40s (1 ship minute), event check every 15s.

### Verb registry
| Verb | Handler |
|------|---------|
| `go`, `enter`, `move` | MovementHandler |
| `open`, `close` | _route_open/_route_close |
| `lock`, `unlock` | DoorHandler |
| `diagnose`, `diagnose panel` | RepairHandler |
| `repair`, `repair panel` | RepairHandler |
| `take`, `get`, `pick up` | ItemHandler |
| `drop` | ItemHandler |
| `look in` | ContainerHandler |
| `take from` | ContainerHandler |
| `put in`, `place in`, `put on`, `place on` | ContainerHandler / EquipHandler |
| `wear`, `equip`, `remove`, `take off` | EquipHandler |
| `access` | TerminalHandler |
| `rest` | RestHandler |

---

## 6. DESCRIPTION PANEL

### Markup types
| Markup | Colour | Hover | Click |
|--------|--------|-------|-------|
| `*exit*` | Cyan | Door state + Offline suffix if unpowered/broken/emergency released | None |
| `%container%` | Amber | Open/Closed | Toggle |
| `!terminal!` | Violet | Online/Offline | `access` |
| `#surface#` | Amber | Empty/Has items | Expand Layer 3 |
| `?junction?` | Coral | Panel ID | None |

### Colour palette
| Variable | Hex | Use |
|----------|-----|-----|
| `--col-text` | `#cecece` | Default prose |
| `--col-title` | `#27e6ec` | Cyan — exits |
| `--col-container` | `#c4a050` | Amber — containers/surfaces |
| `--col-terminal` | `#a06aa0` | Violet — terminals |
| `--col-junction` | `#b87560` | Coral — power junctions |
| `--col-portable` | `#b09abe` | Purple — portable items |
| `--col-alert` | `#ff8c00` | Orange — alerts |
| `--col-prompt` | `#00ff00` | Green — command prompt |
| `--col-response` | `#7e97ae` | Muted blue — input echo |

### Token injection
| Token | Fields required |
|-------|----------------|
| `^power_state^` | `description_powered`, `description_unpowered` |
| `@reactor_state@` | `description_reactor_online`, `description_reactor_offline`, `description_reactor_ejected` |

### Room image naming
`roomname.png` / `roomname_unpowered.png` / `roomname_reactor_off.png` / `roomname_unpowered_reactor_off.png`

---

## 7. ELECTRICAL SYSTEM

### Architecture summary
Two fission reactors. Main (25kW) → ship systems. Propulsion (120kW) → engines. Distributed via circuit panels, breakers, cables to all 17 rooms. Two backup batteries (Life Support, Mainframe).

See `docs/archive/` for full circuit diagram. Key naming: `PNL-` panels, `FUS-` breakers, `PWC-` cables, `BAT-` batteries.

### Component state models
- **Breaker:** `damaged` + `tripped` flags, `operational` derived
- **CircuitPanel:** 5 internal flags (`logic_board_intact`, `bus_bar_intact`, `surge_protector_intact`, `smoothing_capacitor_intact`, `isolation_switch_intact`), `operational` derived
- **PowerCable:** `intact`, `connected`, `emergency_bypass`, `length_m`
- **Reactor:** `online` / `offline` / `ejected`

---

## 8. SAVE/LOAD SYSTEM

### Philosophy
No autosave. No manual save. Save only on rest. One slot. Death is permanent.

### What is saved
- Meta: `dead` flag, `instance_counters`
- Player: current room, inventory, equipped slots
- Rooms: floor items, container state/contents, surface contents, PowerJunction broken/repaired components
- Doors: open/locked/emergency_released per door; is_broken/is_diagnosed/broken_components/repaired_components per panel
- Electrical: reactor, battery, panel flags, breaker state, cable state
- Events: fired/resolved flags
- Ship log, tablet notes, storage and cargo manifests

### Rest locations
Captain's quarters bunk, rec-room sofa. Hypersleep pod deferred.

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/game/save_status` | GET | `{exists, dead}` |
| `/api/game/load` | POST | new_game() + load_game() |
| `DELETE /api/game/save` | DELETE | Delete both save files |
| `/api/command/save` | POST | Save current state |
| `/api/command/rest_complete` | POST | Advance time after rest |

---

## 9. KNOWN ISSUES / DEFERRED

- **PAM** — clips to utility belt. Dormant until life support phase.
- **Examine command** — `examine <item>` deferred.
- **Unpowered room images** — 15 rooms still need Reve generation.
- **Dynamic room descriptions** — 15 rooms need prose, powered/unpowered addendums.
- **Power junction placement** — main corridor, sub corridor, propulsion bay pending.
- **Circuit diagram SVG** — in progress in Inkscape.
- **Post-repair failure roll** — always succeeds. Future: probability-based.
- **CRT terminal font** — Share Tech Mono inherited. Separate font TBD.
- **Engine damage via events** — `_break_component_by_id()` TODO stub.
- **Cargo contents** — `initial_cargo.json` containers empty.
- **Long repair auto-chain threshold** — deferred until survival mechanics.
- **Room temperature** — deferred until life support.
- **Sack barrow** — `PLAYER_MAX_CARRY_MASS` 40kg temporary. Deferred.
- **Jury-rigging system** — deferred. See `docs/deferred_systems.md`.
- **Death screen UI** — dead flag in place, UI not built.
- **Hypersleep pod** — deferred rest/save location.
- **diagnosed_components list** — future replacement for `is_diagnosed` flag to support misdiagnosis mechanic.
- **Emergency release test groups 5 & 6** — not yet completed.
- **Reactor image bug** — debug reactor break incorrectly appends `_reactor_off` to all rooms. Deferred.

### Input lockout inconsistency
Terminal active — tooltips remain active. Timed action active — full pointer-events block. Whether to unify is an open question.

---

## 10. RULES FOR DEVELOPMENT

1. **Upload current files at start of every session** — never work from memory
2. **Read the code before changing it** — ask to see files before editing
3. **One change at a time — verify before proceeding**
4. **No silent fallbacks** — missing data must crash loudly
5. **Backend owns all game state** — JS is display only
6. **Minimal targeted changes** — no unrequested improvements
7. **No god files** — grouped logically by domain
8. **All colours in CSS variables**
9. **All JS timeouts in `constants.js`**
10. **All Python durations in `config.py`**
11. **All Python player/ship constants in `config.py`**
12. **Debate bad ideas** — push back if something seems wrong
13. **Never add "type X to fix it" hints** — immersive messages only
14. **Inline find/replace for existing files — complete files for new files**
15. **All JSON fields have a use** — never partially load type definitions
16. **Suggest before adding** — flag missing spec items before writing code
17. **No smelly code** — no dead code, no unnecessary fallbacks
18. **Never work from stale files** — always ask for uploads before writing instructions

---

*Project Orion Game — Technical Reference v28.0 — May 2026*
