# PROJECT ORION GAME
## Space Survival Simulator
### Master Design & Development Document
**Version 9.0 — April 2026**

---

## 1. PROJECT OVERVIEW

### Concept
Project Orion Game is a space survival simulator set in 2276. The player operates a solo trader/explorer spacecraft named the **Tempus Fugit**, captained by **Jack Harrow**. Core gameplay revolves around maintaining ship systems, repairing failures, and surviving deep space. This is a serious "slow burner" simulator — not an arcade game. Systems fail, cascade, and the player must diagnose and fix them before things get fatal.

### History
- **Project Dark Star** — previous iteration in Python/Arcade. Deprecated — Project Orion Game has surpassed it in every area.
- **Project Orion (electrical reference project)** — standalone project used to design and validate the electrical system architecture. Now deprecated as a separate codebase — all relevant code and data has been merged into Project Orion Game.
- **Project Orion Game** — Flask backend + HTML/CSS/JS frontend. The active codebase.

### Core Philosophy
*"If the ship dies, you die."* Generous time windows. Thoughtful problem solving over frantic action. The player physically moves through the ship, gathers the right tools and parts, and repairs systems.

---

## 2. TECHNOLOGY STACK

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

## 3. CURRENT STATE — WHAT IS BUILT AND WORKING

### Core systems
- Rooms, doors, security panels, command system, chronometer ✅
- Player, inventory, items, basic repair ✅
- Fixed object data structure: terminals, storage units, surfaces ✅
- Description panel: markup parser, hover tooltips, click handlers, Layer 2/3 ✅
- Container commands: open, close, look in, take from, put in, put on ✅
- Equip/unequip commands: wear, equip, remove, take off, unequip ✅
- Floor fallback: items drop to floor when no surface available ✅
- Player inventory screen: slide-out panel, equipped slots, carried items, actions ✅
- Smart command parser: ID resolver, verb conflict resolution, clarification system ✅
- Item registry: unique instances per placement (foundation for consumables) ✅
- Dark Star feature parity: **complete** — Project Dark Star is now deprecated ✅

### Phase history
- **Phase 6** — Splash screen + game shell ✅
- **Phase 7** — Ship + room loading ✅
- **Phase 8** — Room description rendering ✅
- **Phase 9** — Movement ✅
- **Phase 10** — Door system ✅
- **Phase 11** — Damaged door panels + basic repair ✅
- **Phase 12** — Ship state, player, inventory ✅
- **Phase 13** — Description panel, containers, surfaces, equip ✅
- **Phase 14** — Player inventory screen ✅
- **Phase 15** — Smart command parser ✅
- **Phase 16** — Terminal system ✅
- **Phase 17** — Electrical system integration ✅ (in progress — map and debug complete, circuit diagram SVG pending)

---

## 4. FOLDER STRUCTURE (CURRENT)

```
project_orion_game/
│
├── main.py
├── config.py
├── requirements.txt
│
├── backend/
│   ├── models/
│   │   ├── game_manager.py        ← owns electrical_system instance
│   │   ├── ship.py
│   │   ├── room.py
│   │   ├── door.py
│   │   ├── interactable.py        ← StorageUnit, Surface, Terminal
│   │   ├── player.py
│   │   └── chronometer.py
│   │
│   ├── systems/
│   │   └── electrical/
│   │       └── electrical_system.py  ← ElectricalSystem, FissionReactor, BackupBattery,
│   │                                    CircuitPanel, Breaker, PowerCable
│   │
│   ├── handlers/
│   │   ├── base_handler.py
│   │   ├── command_handler.py
│   │   ├── movement_handler.py
│   │   ├── door_handler.py
│   │   ├── repair_handler.py
│   │   ├── item_handler.py
│   │   ├── container_handler.py
│   │   ├── equip_handler.py
│   │   └── terminal_handler.py
│   │
│   ├── loaders/
│   │   └── item_loader.py
│   │
│   └── api/
│       ├── game.py                ← includes /api/game/terminal/content
│       ├── command.py
│       └── systems.py             ← /api/systems/electrical/status, break, fix
│
├── frontend/
│   ├── templates/
│   │   ├── splash.html
│   │   └── game.html
│   │
│   └── static/
│       ├── css/
│       │   ├── splash.css
│       │   ├── game.css
│       │   ├── description.css
│       │   ├── inventory.css
│       │   ├── response.css
│       │   └── terminal.css
│       ├── js/
│       │   ├── core/
│       │   │   ├── constants.js
│       │   │   ├── api.js
│       │   │   └── loop.js
│       │   └── screens/
│       │       ├── splash.js
│       │       ├── ui.js
│       │       ├── commands.js
│       │       ├── description.js
│       │       ├── inventory.js
│       │       ├── terminal.js    ← terminal panel, map, typewriter, keypress nav
│       │       └── game.js        ← includes debug console (Ctrl+D)
│       └── images/
│           ├── rooms/
│           ├── doors/
│           └── ship_layout.svg    ← interactive room power map
│
└── data/
    ├── items/
    │   ├── tools.json
    │   ├── wearables.json
    │   ├── misc_items.json
    │   ├── consumables.json
    │   ├── terminals.json
    │   ├── storage_units.json
    │   └── surfaces.json
    ├── terminals/
    │   └── engineering.json       ← engineering terminal content
    └── ship/
        ├── structure/
        │   ├── ship_rooms.json
        │   ├── door_status.json
        │   ├── initial_ship_state.json
        │   ├── initial_ship_items.json
        │   └── player_items.json
        └── systems/
            └── electrical.json    ← full electrical system definition
```

---

## 5. CONFIG.PY — KEY CONSTANTS

```python
SHIP_NAME       = "Tempus Fugit"
PLAYER_NAME     = "Jack Harrow"
STARTING_ROOM   = "captains_quarters"
START_DATE_TIME = (2276, 1, 1, 0, 0)

REPAIR_PANEL_REAL_SECONDS  = 8
REPAIR_PANEL_GAME_MINUTES  = 30
CARD_SWIPE_REAL_SECONDS    = 5
DEBUG_HAS_REPAIR_TOOL      = True

ROOMS_JSON_PATH         = 'data/ship/structure/ship_rooms.json'
DOORS_JSON_PATH         = 'data/ship/structure/door_status.json'
INITIAL_STATE_JSON_PATH = 'data/ship/structure/initial_ship_state.json'
SHIP_ITEMS_JSON_PATH    = 'data/ship/structure/initial_ship_items.json'
PLAYER_ITEMS_JSON_PATH  = 'data/ship/structure/player_items.json'
TERMINALS_JSON_PATH     = 'data/items/terminals.json'
TERMINAL_CONTENT_PATH   = 'data/terminals'
STORAGE_UNITS_JSON_PATH = 'data/items/storage_units.json'
SURFACES_JSON_PATH      = 'data/items/surfaces.json'
ELECTRICAL_JSON_PATH    = 'data/ship/systems/electrical.json'
ITEM_FILES = [
    'data/items/tools.json',
    'data/items/wearables.json',
    'data/items/misc_items.json',
    'data/items/consumables.json',
]
```

---

## 6. THE GAME LOOP — ARCHITECTURE

**Instant actions** — no game time, immediate response, input stays unlocked.
**Timed actions** — backend returns `real_seconds`, frontend locks input, calls back to complete.

---

## 7. THE COMMAND SYSTEM

### Resolver architecture
All typed commands and UI clicks pass through `command_handler.process()`:
1. Preposition commands intercepted first (`take from`, `put in`, `put on`)
2. Ambiguity check — `_check_ambiguity()` finds all matches, returns `clarification_required` if multiple distinct items
3. Resolver — `_resolve_for_verb()` converts keywords to IDs using `_resolve_all()`
4. Handler receives resolved ID or original keyword

### Dual ID and keyword matching in handlers
Handlers retain both `item.id == target` and `item.matches(target)` checks. This is intentional — the resolver operates upstream but the preposition early-exit blocks in `process()` have their own resolution paths. Removing the keyword fallback was attempted and reverted.

### Fixed object keyword uniqueness
Fixed objects (containers, surfaces) must have unique keywords within a room.

### Clarification system
When multiple distinct matches found, returns `clarification_required` with clickable options rendered in response panel.

### Verb registry
| Verb | Handler |
|------|---------|
| `go`, `enter`, `move` | MovementHandler |
| `open`, `close` | _route_open/_route_close |
| `lock`, `unlock` | DoorHandler |
| `repair panel`, `repair` | RepairHandler |
| `take`, `get`, `pick up` | ItemHandler |
| `drop` | ItemHandler |
| `look in` | ContainerHandler |
| `take from` | ContainerHandler |
| `put in`, `place in` | ContainerHandler |
| `put on`, `place on` | ContainerHandler / EquipHandler |
| `wear`, `equip` | EquipHandler |
| `remove`, `take off`, `unequip` | EquipHandler |
| `access` | TerminalHandler |

---

## 8. MAIN GAME SCREEN LAYOUT

```
┌────────────────────────────────────────────────────────────┐
│ [INV] [TERM]  ← horizontal tab strip                       │
├──────────────────────────────────┬─────────────────────────┤
│                                  │ DESCRIPTION (scrollable)│
│      ROOM IMAGE (45%)            ├─────────────────────────┤
│  ← slide-out panels cover this   │ RESPONSE (scrollable)   │
│                                  ├─────────────────────────┤
│                                  │ COMMAND INPUT           │
├──────────────────────────────────┴─────────────────────────┤
│ EVENT STRIP              [events]      [ship name + time]  │
└────────────────────────────────────────────────────────────┘
```

### Tab strip
Horizontal tabs at top of image panel. INV always visible. TERM tab appears only when a terminal session is active, hidden on exit.

### Colour palette
| Variable | Hex | Use |
|----------|-----|-----|
| `--col-text` | `#bababa` | Default text |
| `--col-title` | `#27e6ec` | Cyan — titles, exits, containers, terminals |
| `--col-portable` | `#bea5cd` | Purple — portable items, surfaces with items |
| `--col-alert` | `#ff8c00` | Orange — alerts, locked doors |
| `--col-prompt` | `#00ff00` | Green — command prompt, open doors |
| `--col-response` | `#7e97ae` | Muted blue — player input echo |
| `--col-term-bg` | `#000d00` | CRT phosphor background |
| `--col-term-text` | `#00ff41` | Phosphor green text |
| `--col-term-dim` | `#00801f` | Dimmer green — secondary terminal text |
| `--col-term-border` | `#004d10` | Dark green border |

---

## 9. DESCRIPTION PANEL — MARKUP SYSTEM

### Markup types
| Markup | Type | Colour | Hover | Click |
|--------|------|--------|-------|-------|
| `*exit*` | Exit | Cyan | Door state | None |
| `%object%` | Container | Cyan | Open/Closed | Toggle open/close |
| `!terminal!` | Terminal | Cyan | "Online" | `access <terminal>` |
| `#surface#` | Surface | Grey bold (empty) / Purple bold (has items) | "Empty"/"Has items" | Expand Layer 3 |

### Description layers
1. **Static prose** — authored JSON
2. **Layer 2** — open container contents (cyan name, purple items)
3. **Layer 3** — expanded surface contents (purple, on demand)
4. **Floor line** — `Floor: item1, item2` (italic label, purple items, only when occupied)

### Drop behaviour
- Drop lands on random surface, falls back to floor if none
- Multiple surfaces → clarification with surface names as options
- Floor is automatic fallback only — not a player-accessible drop target

---

## 10. INVENTORY SYSTEM

### Two distinct inventories
**Player inventory** — personal carried and worn items
- INV tab slide-out panel or `inventory` command
- Equipped slots + carried items, auto-selects first item on open

**Ship inventory** — managed manifest of tradeable/consumable stock
- Accessed via storage terminals only (Phase 19)

---

## 11. ITEM SYSTEM

### Item registry
- `item_loader.py` stores raw data dicts — not instances
- `instantiate_item()` creates fresh `PortableItem` instance each call
- Every placed item is a unique Python object with independent state

### Object ID naming convention
`roomid_markuptext` — ensures unambiguous ID matching within a room.

---

## 12. TERMINAL SYSTEM (PHASE 16)

### Overview
Terminals are accessed via `access terminal` command or clicking terminal markup in the description. Once accessed, the player is locked to the terminal until they explicitly exit with `[X]`.

### Terminal mode
- Command input disabled, `>` prompt hidden
- Global click refocus suppressed
- Description panel clicks blocked (except terminal markup, which is also blocked during active session)
- INV tab still accessible
- TERM tab visible for duration of session, switches between panels without closing session
- Only `[X]` exits the terminal — no other mechanism

### Terminal panel
- CRT styling: dark green phosphor background, scanlines, text glow
- Typewriter effect with jitter on sub-menu content text
- Blinking block cursor — solid during typing, blinking at rest
- Keypress navigation — single key, no Enter required, unrecognised keys silently ignored
- Tab colour adapts — CRT green when terminal active

### Terminal menu structure (engineering terminal)
```
Main Menu
  [T] Technical Data
  [E] Electrical
  [X] Exit

Electrical Sub-Menu
  [P] Power Status      ← ship layout SVG, live room colours
  [C] Circuit Diagram   ← wiring diagram SVG (pending — being built manually)
  [R] Return
  [X] Exit
```

### Terminal content files
- `data/terminals/engineering.json` — engineering terminal content
- Terminal type maps to filename: `{terminal_type}.json`
- Content actions support `text` (typewriter) or `view` (special rendering)
- View types: `electrical_map`, `electrical_menu`

### Key files
- `data/items/terminals.json` — terminal definitions, keywords, menu items with key bindings
- `backend/handlers/terminal_handler.py` — `access` verb handler
- `backend/api/game.py` — `/api/game/terminal/content` POST route
- `frontend/static/js/screens/terminal.js` — all terminal rendering and interaction
- `frontend/static/css/terminal.css` — CRT styling

---

## 13. ELECTRICAL SYSTEM (PHASE 17)

### Overview
The Tempus Fugit electrical system provides 25kW continuous power via a thermionic fission reactor. Power is distributed through a hierarchical network of circuit panels, breakers, and cables to all 17 ship compartments. Two backup battery systems provide emergency power to Life Support and Mainframe rooms.

### Component naming convention
| Code | Type | Example |
|------|------|---------|
| `PNL-` | Panel | `PNL-ENG-MAIN` |
| `FUS-` | Breaker | `FUS-MC-01` |
| `PWC-` | Cable | `PWC-ENG-03` |
| `BAT-` | Battery | `BAT-LS-01` |

### Location codes
| Code | Location |
|------|---------|
| ENG | Engineering |
| MC | Main Corridor |
| SC | Sub Corridor |
| REC | Recreation Room |
| LS | Life Support |
| MF | Mainframe |

### Architecture summary
```
reactor_core (25kW)
└── PWC-ENG-01
    └── PNL-ENG-MAIN (Main Circuit Panel, Engineering)
        ├── FUS-ENG-01 → PWC-ENG-02 → life_support + BAT-LS-01 (backup)
        ├── FUS-ENG-02 → PWC-ENG-03/PWC-MC-06 → PNL-MC-SUB-A (Main Corridor)
        │   ├── FUS-MC-01 → PWC-MC-01 → crew_cabin
        │   ├── FUS-MC-02 → PWC-MC-02 → captains_quarters
        │   ├── FUS-MC-03 → PWC-MC-03 → mainframe_room + BAT-MF-01 (backup)
        │   └── PWC-MC-04 → main_corridor (local)
        ├── FUS-ENG-03 → PWC-ENG-04/PWC-MC-07/PWC-SC-05 → PNL-SC-SUB-B (Sub Corridor)
        │   ├── FUS-SC-01 → PWC-SC-01 → head
        │   ├── FUS-SC-02 → PWC-SC-02 → cargo_bay
        │   ├── FUS-SC-03 → PWC-SC-03 → storage_room
        │   ├── FUS-SC-04 → PWC-SC-04 → airlock
        │   └── PWC-SC-06 → sub_corridor (local)
        ├── FUS-ENG-04 → PWC-ENG-05/PWC-MC-08/PWC-REC-05 → PNL-REC-SUB-C (Rec Room)
        │   ├── FUS-REC-01 → PWC-REC-01 → med_bay
        │   ├── FUS-REC-02 → PWC-REC-02 → hypersleep_chamber
        │   ├── FUS-REC-03 → PWC-REC-03 → galley
        │   ├── FUS-REC-04 → PWC-REC-04 → cockpit
        │   └── PWC-REC-06 → recreation_room (local)
        ├── FUS-ENG-05 → PWC-ENG-06 → engineering (local)
        └── FUS-ENG-06 → PWC-ENG-07 → propulsion_bay

propulsion_reactor (120kW) — independent tree
├── PWC-PROP-01 → sublight_engines
└── PWC-PROP-02 → ftl_drive
```

### Component summary
| Type | Count |
|------|-------|
| Reactors | 2 (main 25kW, propulsion 120kW) |
| Backup batteries | 2 (Life Support, Mainframe — 150kWh each, auto-activate) |
| Circuit panels | 4 |
| Breakers | 17 |
| Cables | 28 |
| Rooms powered | 17 |

### Cable junctions
Cables change ID at room boundaries. Junctions are not modelled as components — breaking either cable segment interrupts flow. Example: Engineering→Main Corridor power travels via `PWC-ENG-03` then continues as `PWC-MC-06`.

### Backup batteries
Both batteries monitor their room continuously and auto-activate on mains power loss. They provide power only to their designated room with no backfeed. `update_battery_states()` must be called after any component state change.

### Failure cascades
- **Reactor failure** — all rooms dark except Life Support and Mainframe (batteries)
- **PNL-ENG-MAIN failure** — all rooms dark except Life Support and Mainframe
- **FUS-MC-03 trips** — Mainframe loses mains, battery activates, other MC-SUB-A rooms unaffected
- **PWC-SC-02 break** — Cargo Bay only, other Sub Corridor rooms unaffected
- **PNL-REC-SUB-C failure** — Rec Room, Cockpit, Galley, Med Bay, Hypersleep all dark
- **PWC-MC-06 break** — entire Main Corridor branch dark (Crew Cabin, Captains Quarters, Mainframe on battery, Main Corridor)

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/systems/electrical/status` | GET | Full system status including room_power map |
| `/api/systems/electrical/room/<id>` | GET | Single room power check |
| `/api/systems/electrical/break/<id>` | POST | Break any component by ID |
| `/api/systems/electrical/fix/<id>` | POST | Fix any component by ID |

### Engineering terminal — electrical sub-menu
- **[P] Power Status** — ship layout SVG (`ship_layout.svg`) with live room colours (green=powered, red=unpowered). Pan with arrow keys, zoom with +/-. Colours fetched from `/api/systems/electrical/status` on open.
- **[C] Circuit Diagram** — wiring diagram SVG (being built manually in Inkscape from `skeleton.svg` skeleton). Shows reactor → panels → fuses → rooms topology. Hover on wire = cable ID/name. Hover on fuse = breaker ID/name. Static reference — no live power colouring.

### SVG room ID mapping (ship_layout.svg → backend)
| SVG ID | Backend room ID |
|--------|----------------|
| `rec-room-fill` | `recreation_room` |
| `cockpit-fill` | `cockpit` |
| `storage-fill` | `storage_room` |
| `medbay-fill` | `med_bay` |
| `stasis-room-fill` | `hypersleep_chamber` |
| `galley-fill` | `galley` |
| `corridor-main-fill` | `main_corridor` |
| `corridor-sub-fill` | `sub_corridor` |
| `bathroom-sub-fill` | `head` |
| `mainframe-sub-fill` | `mainframe_room` |
| `cargo-bay-sub-fill` | `cargo_bay` |
| `airlock-sub-fill` | `airlock` |
| `engineering-sub-fill` | `engineering` |
| `propulsion-sub-fill` | `propulsion_bay` |
| `captains-cabin-sub-fill` | `captains_quarters` |
| `crew-quarters-sub-fill` | `crew_cabin` |
| `life-support-sub-fill` | `life_support` |

### Circuit diagram SVG — skeleton classes
| Class | Element |
|-------|---------|
| `.reactor` | Power source box |
| `.panel` | Circuit panel box (tall, fuses inside) |
| `.fuse` + `.fuse-bar` | Fuse circle with horizontal bar |
| `.cable` | Solid wire |
| `.cable-dash` | Dashed backup feed |
| `.endpoint` | Room power socket |
| `.battery` | Backup battery |

### Debug console
- `Ctrl+D` toggles debug panel in game
- `break <component_id>` — breaks any electrical component, map updates immediately
- `fix <component_id>` — fixes any electrical component, map updates immediately
- Terminal keyhandler passes input through to debug console when debug input is focused

### Key files
- `data/ship/systems/electrical.json` — full electrical system definition
- `backend/systems/electrical/electrical_system.py` — ElectricalSystem and all component classes
- `backend/api/systems.py` — electrical API routes
- `frontend/static/images/ship_layout.svg` — interactive ship layout map
- `frontend/static/js/screens/terminal.js` — map rendering and interaction (SVG_ROOM_MAP, `_openElectricalMap`, `_updateRoomColours`)

---

## 14. BUILD PLAN — NEXT PHASES

### Phase 17 — Electrical system integration (CURRENT)
Remaining:
- Circuit diagram SVG being built manually in Inkscape
- Wire circuit diagram into `[C] Circuit Diagram` terminal option
- Remove placeholder x/y coordinates from `electrical.json` and `ElectricalSystem` classes
- Room power affecting doors, terminals (later in phase)

### Phase 18 — Full repair system
- Diagnosis, repair, verification flow
- Real tool and parts checks
- See Section 15 for complete design

### Phase 19 — Ship inventory + cargo
- Ship inventory manifest via storage terminals
- Cargo bay trading items
- `PortableContainer` (moveable crate) — floor only

### Phase 20 — Life support
- Binary operational states driven by electrical system
- Temperature modelling — open/closed doors, room volume, HVAC

### Phase 21+ — Events, navigation, trading...

---

## 15. FULL REPAIR SYSTEM — TARGET DESIGN (PHASE 18)

**Step 1 — Diagnose** using Scan Tool + basic access tools + workshop manuals (optional)
**Step 2 — Repair/Replace** correct parts and tools at component location
**Step 3 — Verify** using Scan Tool again
**Step 4 — Operational** or return to Step 2

Without correct manual: diagnosis less precise, chance of incorrect repair.
Bypass mechanic: force open frozen door with crowbar, damages door further.

Repair procedure (electrical):
1. Diagnose: Use scan tool on failed component to identify fault
2. Navigate: Travel to component location
3. Gather Tools: Insulated gloves, powered bit driver, multimeter, wire cutters
4. Gather Parts: Replacement breakers, wire segments, circuit boards (as needed)
5. Perform Repair: Replace failed component (game time advances 15-60 minutes)
6. Test: Verify power restoration, check downstream systems

Breaker reset vs replacement:
- **Tripped breaker** — quick reset (2 minutes). Trips again immediately = fault downstream.
- **Failed breaker** — requires replacement (15 minutes).

---

## 16. KNOWN ISSUES / DEFERRED

- **PAM** — clips to utility belt. Dormant until life support phase.
- **Belt attachment mechanic** — utility belt accepts clipped items. Deferred until EVA phase.
- **Examine / look at command** — deferred. To be discussed.
- **Consumable `length_m`** — wire instances need `length_m` attribute in consumables.json. Add when repair system built.
- **Clarification display for items with same name but different state** — e.g. `Optical Wire (5m)` vs `Optical Wire (10m)`. Fix when `length_m` attribute exists.
- **Storage room wiring** — logical bug fixed in `electrical.json` (storage_room now correctly mapped to `PNL-SC-SUB-B` via `FUS-SC-03`).

---

## 17. RULES FOR DEVELOPMENT

1. **Upload current files at start of every session** — never work from memory
2. **Read the code before changing it** — ask to see files before editing
3. **Complete files for large changes, inline instructions for small ones**
4. **Minimal targeted changes** — no "while I'm in here" improvements without asking
5. **Only create what we need right now**
6. **No god files** — grouped logically by domain
7. **Backend owns all game state** — JS is display only
8. **All colours in CSS variables**
9. **All JS timeouts in `constants.js`**
10. **All Python durations in `config.py`**
11. **Debate bad ideas** — push back if something seems wrong
12. **Never add "type X to fix it" hints** — immersive messages only
13. **Small changes — show inline instructions, not complete files**
14. **Never output complete game.html or game.js — targeted changes only**
15. **One change at a time — verify before proceeding**

---

*Project Orion Game Design Document v9.0*
*April 2026*
