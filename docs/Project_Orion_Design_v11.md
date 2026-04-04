# PROJECT ORION GAME
## Space Survival Simulator
### Master Design & Development Document
**Version 11.0 — April 2026**

---

## 1. PROJECT OVERVIEW

### Concept
Project Orion Game is a space survival simulator set in 2276. The player operates a solo trader/explorer spacecraft named the **Tempus Fugit**, captained by **Jack Harrow**. Core gameplay revolves around maintaining ship systems, repairing failures, and surviving deep space. This is a serious "slow burner" simulator — not an arcade game. Systems fail, cascade, and the player must diagnose and fix them before things get fatal.

### History
- **Project Dark Star** — previous iteration in Python/Arcade. Deprecated.
- **Project Orion (electrical reference project)** — standalone project used to design and validate the electrical system architecture. Now deprecated — all code and data merged into Project Orion Game.
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
- Terminal system: CRT styling, typewriter, keypress nav, sub-menus, terminal mode lockout ✅
- Electrical system: reactor, panels, breakers, cables, batteries, power tracing ✅
- Electrical integrated into gameplay: door panels and terminals check room power ✅
- Engineering terminal: Technical Data, Electrical sub-menu (Power Status map, Circuit Diagram placeholder) ✅
- Debug console: Ctrl+D, break/fix commands, live map refresh ✅

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
- **Phase 17** — Electrical system integration ✅ (circuit diagram SVG pending — being built manually)

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
│   │   ├── base_handler.py        ← _check_room_power, _panel_offline_response
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
│   │   └── item_loader.py         ← handles mixed format in initial_ship_items.json,
│   │                                 computed mass for wire consumables
│   │
│   └── api/
│       ├── game.py                ← /api/game/terminal/content, room data includes panel_powered + terminal powered
│       ├── command.py
│       └── systems.py             ← /api/systems/electrical/status, break, fix
│
├── frontend/
│   ├── templates/
│   │   ├── splash.html
│   │   └── game.html              ← includes debug console panel
│   │
│   └── static/
│       ├── css/
│       │   ├── splash.css
│       │   ├── game.css           ← includes debug console styles
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
│       │       ├── commands.js    ← refreshExits() also updates currentObjects
│       │       ├── description.js ← exit/terminal tooltips show Offline state
│       │       ├── inventory.js
│       │       ├── terminal.js    ← terminal panel, map, typewriter, keypress nav
│       │       └── game.js        ← debug console (Ctrl+D), _debugBreakFix calls refreshExits
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
    │   ├── terminals.json         ← terminal definitions, keywords, menu items with key bindings
    │   ├── storage_units.json
    │   └── surfaces.json
    ├── terminals/
    │   └── engineering.json       ← engineering terminal content and sub-menus
    ├── repair/
    │   └── repair_profiles.json   ← repair profiles for all repairable objects (Phase 18)
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
REPAIR_PROFILES_PATH    = 'data/repair/repair_profiles.json'
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
| `repair`, `repair panel` | RepairHandler |
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
| `--col-alert` | `#ff8c00` | Orange — alerts, locked doors, offline state |
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
| `*exit*` | Exit | Cyan | Door state + Offline if unpowered | None |
| `%object%` | Container | Cyan | Open/Closed | Toggle open/close |
| `!terminal!` | Terminal | Cyan | Online / Offline | `access <terminal>` |
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

### Item fields — all item types (tools, wearables, consumables)
Every item in the game must have:
- `manufacturer` — company name (e.g. "Veridian Systems", "Axiom Systems", "Solaris Cable Co.")
- `model` — model or part number (e.g. "VS-900", "AX-7", "SC-OPT-2276")
- `description` — written with character, not generic. Include manufacturer, model, condition where appropriate.

No generic descriptions anywhere. Every item must feel like it exists in the world of 2276.

### Wire consumables — special fields
Wire items use `mass_per_metre` instead of `mass` (mass is computed at runtime from `length_m`):
- `max_length_m` — maximum spool capacity, physical property of the item type
- `mass_per_metre` — used to compute instance mass at runtime

Wire instance attributes (set at runtime, not in JSON type definition):
- `length_m` — actual length of this spool, set from placement data, decremented on use
- `mass` — computed: `length_m * mass_per_metre`

### Scan tool — special fields
- `installed_manuals` — list of repair profile keys the scan tool can service
  - Phase 18: `["door_panel_l1", "door_panel_l2", "door_panel_l3"]`
  - Expandable as new system manuals are added or purchased

### initial_ship_items.json — mixed placement format
Supports both simple string (standard instantiation) and dict (instance attribute overrides):

```json
{
  "container_id": "engineering_large_parts_storage_unit",
  "items": [
    "electrical_service_kit",
    {"id": "wire_light_duty", "length_m": 12.5},
    {"id": "wire_optical", "length_m": 8.0}
  ]
}
```

`item_loader.py` handles both formats — string uses defaults, dict applies instance attribute overrides after instantiation.

---

## 12. TERMINAL SYSTEM (PHASE 16)

### Overview
Terminals are accessed via `access terminal` command or clicking terminal markup in the description. Once accessed, the player is locked to the terminal until they explicitly exit with `[X]`.

### Power check
Terminal access is blocked if the room has no power. Message: "The [terminal name] is unresponsive — it looks like it's offline." Tooltip shows "Offline" in orange.

### Terminal mode
- Command input disabled, `>` prompt hidden
- Global click refocus suppressed
- Description panel clicks blocked during active session
- INV tab still accessible
- TERM tab visible for duration of session
- Only `[X]` exits the terminal

### Terminal panel
- CRT styling: dark green phosphor background, scanlines, text glow
- Typewriter effect with jitter on sub-menu content text
- Blinking block cursor — solid during typing, blinking at rest
- Keypress navigation — single key, no Enter required
- Tab colour adapts — CRT green when terminal active

### Terminal menu structure (engineering terminal)
```
Main Menu
  [T] Technical Data
  [E] Electrical
  [X] Exit

Electrical Sub-Menu
  [P] Power Status      ← ship layout SVG, live room colours
  [C] Circuit Diagram   ← wiring diagram SVG (pending — being built manually in Inkscape)
  [R] Return
  [X] Exit
```

### Terminal content files
- `data/terminals/engineering.json` — engineering terminal content
- Terminal type maps to filename: `{terminal_type}.json`
- Content actions support `text` (typewriter), `view` (special rendering), or `view` + `menu` (sub-menu)
- View types: `electrical_map`, `electrical_menu`

### Key files
- `data/items/terminals.json` — terminal definitions, keywords, menu items with key bindings
- `backend/handlers/terminal_handler.py` — `access` verb handler, power check
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
Cables change ID at room boundaries. Junctions are not modelled as components — breaking either cable segment interrupts flow.

### Backup batteries
Both batteries monitor their room continuously and auto-activate on mains power loss. They provide power only to their designated room with no backfeed. `update_battery_states()` must be called after any component state change.

### Failure cascades
- **Reactor failure** — all rooms dark except Life Support and Mainframe (batteries)
- **PNL-ENG-MAIN failure** — all rooms dark except Life Support and Mainframe
- **FUS-MC-03 trips** — Mainframe loses mains, battery activates, other MC-SUB-A rooms unaffected
- **PWC-SC-02 break** — Cargo Bay only, other Sub Corridor rooms unaffected
- **PNL-REC-SUB-C failure** — Rec Room, Cockpit, Galley, Med Bay, Hypersleep all dark
- **PWC-MC-06 break** — entire Main Corridor branch dark

### Power integration in gameplay
- **Door panels** — all doors require powered panel to operate. Unpowered: "The [room] door access panel is unresponsive — it looks like it's offline." No door image shown. Crowbar bypass still works.
- **Terminals** — terminal access blocked if room unpowered. Message: "The [terminal name] is unresponsive — it looks like it's offline."
- **Hover tooltips** — exits show "Open — Offline" / "Closed — Offline" in orange when unpowered. Terminals show "Offline" in orange.
- **Description refresh** — `refreshExits()` in `commands.js` updates both `currentExits` and `currentObjects` so tooltips reflect live state immediately after break/fix.
- **Active terminal on power loss** — if power is lost to a room while the player is using the terminal (via game events), the terminal should close immediately with an appropriate message. Not yet implemented — deferred to when event system is built.
- **Room description** — static prose descriptions have had all electrical atmosphere references removed (flickering lights, humming HVAC etc). A dynamic power-state description layer will be added later — powered rooms get atmospheric detail, unpowered rooms get darkness and silence.

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/systems/electrical/status` | GET | Full system status including room_power map |
| `/api/systems/electrical/room/<id>` | GET | Single room power check |
| `/api/systems/electrical/break/<id>` | POST | Break any component by ID |
| `/api/systems/electrical/fix/<id>` | POST | Fix any component by ID |

### Engineering terminal — electrical sub-menu
- **[P] Power Status** — ship layout SVG with live room colours (green=powered, red=unpowered). Pan with arrow keys, zoom with +/-. Pan constrained to keep map visible.
- **[C] Circuit Diagram** — wiring diagram SVG (being built manually in Inkscape). Shows reactor → panels → fuses → rooms topology. Hover on wire = cable ID/name. Hover on fuse = breaker ID/name. Static reference — no live power colouring.

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
- `break <component_id>` — breaks any electrical component, map and tooltips update immediately
- `fix <component_id>` — fixes any electrical component, map and tooltips update immediately
- Terminal keyhandler passes input through to debug console when debug input is focused

### Key files
- `data/ship/systems/electrical.json` — full electrical system definition
- `backend/systems/electrical/electrical_system.py` — ElectricalSystem and all component classes
- `backend/api/systems.py` — electrical API routes
- `backend/handlers/base_handler.py` — `_check_room_power()`, `_panel_offline_response()`
- `frontend/static/images/ship_layout.svg` — interactive ship layout map
- `frontend/static/js/screens/terminal.js` — map rendering and interaction
- `frontend/static/js/screens/commands.js` — `refreshExits()` updates both exits and object states

---

## 14. BUILD PLAN — NEXT PHASES

### Phase 17 — Electrical system integration (COMPLETE except circuit diagram SVG)
Remaining:
- Circuit diagram SVG being built manually in Inkscape — integrate into `[C] Circuit Diagram` when ready

### Phase 18 — Full repair system
- Scope: door panels first — designed to be fully generic for all future repairable objects
- See Section 15 for complete design

### Phase 19 — Ship inventory + cargo
- Ship inventory manifest via storage terminals
- Cargo bay trading items
- `PortableContainer` (moveable crate) — floor only

### Phase 20 — Life support
- Binary operational states driven by electrical system
- Temperature modelling — open/closed doors, room volume, HVAC
- Dynamic room descriptions based on power state

### Phase 21+ — Events, navigation, trading...

---

## 15. FULL REPAIR SYSTEM — DESIGN (PHASE 18)

### Overview
The repair system replaces the current magic repair with a realistic multi-step process. Phase 18 scope is door panels only, but the architecture is fully generic — the same code handles any future repairable object by reading its repair profile from JSON.

### The Scan Tool
The scan tool is the central diagnostic instrument — a jack-of-all-trades device equivalent to a high-end modern workshop tool. Capabilities:
- Fault code reading and bi-directional comms
- Coding, reset and initialisation procedures
- Built-in service manuals (door panels pre-installed; other exotic systems require scan tool updates purchased later)
- Built-in oscilloscope / multimeter
- Thermal imager
- Optical borescope
- WiFi link — can be used to view ship electrical systems SVG remotely

The scan tool has an `installed_manuals` attribute — a list of repair profile keys it can service. Phase 18: `["door_panel_l1", "door_panel_l2", "door_panel_l3"]`. Each security level has its own profile key with distinct fluff text (manufacturer, model, revision).

### Repair command — stateful and progressive
The single `repair <object>` command drives the entire process. The game determines what stage the player is at based on object state:

```
panel.is_broken = False
  → "The panel is operational."

panel.is_broken = True, panel.diagnosed_components = []
  → Run diagnosis (check tools, timed action, reveal broken components)

panel.is_broken = True, panel.diagnosed_components populated
  → Run repair (check tools + parts, timed action, restore panel)
```

The player never needs to think about which sub-command to use. Typing `repair panel` repeatedly walks them through the process naturally. Once diagnosis is complete, re-typing `repair panel` jumps straight to the repair stage — diagnosis is never repeated unnecessarily.

### Game state per repairable object
```python
panel.is_broken = True/False
panel.broken_components = ["logic_circuit", "wiring_optical"]   # ground truth — set at break time
panel.diagnosed_components = []                                   # what player has discovered — set by diagnosis
```

The separation between `broken_components` and `diagnosed_components` is intentional. The repair handler checks `broken_components` to determine actual success, but the player can only act on `diagnosed_components`. This is the hook for future difficulty scaling — a missed diagnosis means a repair appears to succeed but the panel stays broken, forcing the player to diagnose again.

### Repair profiles JSON
`data/repair/repair_profiles.json` — one profile per repairable object type, keyed by security level for door panels.

```json
{
  "door_panel_l1": {
    "display_name": "Door Access Panel (Level 1)",
    "diag_tools_required": ["scan_tool", "power_screwdriver_set"],
    "repair_tools_required": ["scan_tool", "power_screwdriver_set", "electrical_service_kit"],
    "components": [
      {
        "id": "logic_circuit",
        "name": "Logic Circuit",
        "diag_time_mins": 5,
        "repair_time_mins": 15,
        "parts_required": [
          {"item_id": "logic_circuit_board", "qty": 1}
        ]
      },
      {
        "id": "interface",
        "name": "Interface Module",
        "diag_time_mins": 5,
        "repair_time_mins": 10,
        "parts_required": [
          {"item_id": "interface_module", "qty": 1}
        ]
      },
      {
        "id": "screen",
        "name": "Panel Screen",
        "diag_time_mins": 5,
        "repair_time_mins": 10,
        "parts_required": [
          {"item_id": "panel_screen", "qty": 1}
        ]
      },
      {
        "id": "wiring_light",
        "name": "Light Duty Wiring",
        "diag_time_mins": 3,
        "repair_time_mins": 8,
        "parts_required": [
          {"item_id": "wire_light_duty", "qty": 1}
        ]
      },
      {
        "id": "wiring_optical",
        "name": "Optical Wiring",
        "diag_time_mins": 3,
        "repair_time_mins": 8,
        "parts_required": [
          {"item_id": "wire_optical", "qty": 1}
        ]
      }
    ]
  },
  "door_panel_l2": { ... },
  "door_panel_l3": { ... }
}
```

### Repair flow — detailed
**Step 1 — Player types `repair panel`**
- Handler finds the broken panel in the current room
- Checks `diagnosed_components` — if empty, proceeds to diagnosis
- Checks `diag_tools_required` — if any missing, lists what's needed and stops
- Checks scan tool `installed_manuals` includes profile key — if not, informs player scan tool lacks the required manual
- All tools and manual present → timed diagnosis action begins (sum of `diag_time_mins` for all broken components)

**Step 2 — Diagnosis complete**
- `diagnosed_components` populated with broken component IDs
- Response panel lists what was found: "Scan complete. Faults found: Logic Circuit, Optical Wiring."
- Parts required listed: "Parts needed: 1x Logic Circuit Board, 1x Optical Wire"
- Tools required for repair listed

**Step 3 — Player gathers parts and returns, types `repair panel` again**
- `diagnosed_components` already populated → skip to repair stage
- Checks `repair_tools_required` — if any missing, lists what's needed and stops
- Checks player inventory for all parts required across all diagnosed components — if any missing, lists what's needed and stops
- All tools and parts present → timed repair action begins (sum of `repair_time_mins` for diagnosed components)

**Step 4 — Repair complete**
- Parts consumed from player inventory
- Handler checks if `diagnosed_components` covers all `broken_components`
  - If yes → panel restored, `is_broken = False`, door operational
  - If no (missed diagnosis) → panel still broken, message: "The panel powers up briefly then fails again. Further diagnosis required."
- `diagnosed_components` cleared regardless, ready for next diagnosis attempt

### Diagnosis timing
Total diagnosis time = sum of `diag_time_mins` for all actually broken components. Converted to real seconds via existing timed action system.

### Repair timing
Total repair time = sum of `repair_time_mins` for all diagnosed components. Only diagnosed components are repaired.

### Breaking a panel — component selection
When a panel breaks (game event or debug), one or more components are selected randomly from the profile's component list. Number and selection tunable per event type.

### Future scope (not Phase 18)
- Incorrect diagnosis chance based on difficulty setting
- Scan tool software updates for exotic systems (purchasable)
- Crowbar bypass — force open door, damages panel further
- Visual pre-diagnosis — obvious burnt components visible without scan tool
- Salvageable components — scan tool determines which broken parts can be reused

---

## 16. KNOWN ISSUES / DEFERRED

- **PAM** — clips to utility belt. Dormant until life support phase.
- **Belt attachment mechanic** — utility belt accepts clipped items. Deferred until EVA phase.
- **Examine / look at command** — deferred. To be discussed.
- **Wire `length_m` and computed mass** — fully designed (see Section 11) but not yet implemented. Implement in Phase 18 when repair parts are built out.
- **Clarification display for items with same name but different state** — e.g. `Optical Wire (5m)` vs `Optical Wire (10m)`. Implement alongside `length_m`.
- **`refreshExits()` rename** — function now updates both `currentExits` and `currentObjects`. Should be renamed `refreshDescription()` but touches many call sites — defer to a quiet refactor session.
- **Terminal shutdown on power loss** — if power is lost to a room while the terminal is active (via game events), the terminal should close immediately. Not implemented — no crash risk, purely a gameplay/immersion issue. Implement when event system is built.
- **Dynamic room descriptions** — static prose has had electrical atmosphere removed. A power-state description layer (dark/silent when unpowered, atmospheric when powered) is planned for Phase 20.
- **resolver_debug.log** — logging added during Phase 15 to investigate whether keyword fallback could be safely removed from handlers. Conclusion: keep dual matching (see Section 7). Log is now redundant — remove logger setup from `main.py` and delete the log file during a tidy-up session.

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

*Project Orion Game Design Document v11.0*
*April 2026*
