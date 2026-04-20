# PROJECT ORION GAME
## Space Survival Simulator
### Technical Reference & Current State
**Version 23.0 — April 2026**

> ⚠️ **IMPORTANT — DO NOT ASSUME ALL CONTENT IN THIS DOCUMENT IS CORRECT.** This document has evolved organically over many development sessions. Not all sections have been manually verified against the current codebase. Where the code and the document conflict, the code is authoritative. Treat this document as a guide and reference, not a specification.

> **Companion documents:**
> - `Project_Orion_Future_v1.md` — build plan, future system designs, narrative
> - `Project_Orion_Room_Description_Style_v1.md` — room description authoring rules

---

## 1. PROJECT OVERVIEW

### Concept
Project Orion Game is a space survival simulator set in 2276. The player operates a solo trader/explorer spacecraft named the **Tempus Fugit**, captained by **Jack Harrow** — an employee of the Enso VeilTech corporation. Core gameplay revolves around maintaining ship systems, repairing failures, and surviving deep space. This is a serious "slow burner" simulator — not an arcade game. Systems fail, cascade, and the player must diagnose and fix them before things get fatal.

### History
- **Project Dark Star** — previous iteration in Python/Arcade. Deprecated.
- **Project Orion (electrical reference project)** — standalone project used to design and validate the electrical system architecture. Now deprecated — all code and data merged into Project Orion Game.
- **Project Orion Game** — Flask backend + HTML/CSS/JS frontend. The active codebase.

### Core Philosophy
*"If the ship dies, you die."* Generous time windows. Thoughtful problem solving over frantic action. The player physically moves through the ship, gathers the right tools and parts, and repairs systems.

### Enso VeilTech — The Corporation
Jack Harrow is an Enso VeilTech employee. The Tempus Fugit is an Enso VeilTech vessel. The cargo is Enso VeilTech property. The mainframe runs Enso VeilTech software. The scan tool carries Enso VeilTech manuals and their legal disclaimers. Every aspect of Jack's working life is owned, controlled, and monitored by Enso VeilTech.

Enso VeilTech is not evil in a cartoonish sense — they are simply a corporation operating with complete indifference to the individual. Their systems are automated, their responses are templated, and Jack Harrow is employee number 7,341,892. When the bank hack destroys his finances and he is blacklisted, Enso VeilTech's automated compliance system flags him immediately. The response is swift, impersonal, and devastating — return the ship, report to the nearest office, face financial default proceedings. The fact that he is alone in deep space with a damaged ship is not a consideration their system is designed to handle.

This corporation is the invisible antagonist of the entire game. The player never fights them directly — they simply have to survive in a world that Enso VeilTech has made very difficult for Jack Harrow to exist in.

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
- Player, inventory, items ✅
- Fixed object data structure: terminals, storage units, surfaces, pallet containers, pallet platforms, engines, power junctions ✅
- Description panel: markup parser, hover tooltips, click handlers, Layer 2/3 ✅
- Description panel: power state token injection system (`^power_state^`) ✅
- Description panel: reactor state token injection system (`@reactor_state@`) ✅
- Description panel: powered/unpowered addendum rendered in italic with 8s flash animation ✅
- Description panel: new colour scheme — exits cyan, containers/surfaces amber, terminals violet, power junctions coral, portables purple ✅
- Description panel: power junction markup `?name?` with panel_id tooltip ✅
- Description panel: `~text~` italic prose markup for atmospheric lines ✅
- Description panel: fixed room title — stays visible during scroll ✅
- Description panel: panel priority toggle — divider click flips description/response ratio ✅
- Container commands: open, close, look in, take from, put in, put on ✅
- Equip/unequip commands: wear, equip, remove, take off, unequip ✅
- Floor fallback: items drop to floor when no surface available ✅
- `take/pick up <item> from floor` — floor recognised as valid source ✅
- Player inventory screen: slide-out panel, equipped slots, carried items, actions ✅
- Inventory detail panel: model + manufacturer shown, Store button in storage room ✅
- Inventory selection preserved after drop/remove ✅
- Smart command parser: ID resolver, verb conflict resolution, clarification system ✅
- Item registry: unique instances per placement, unique runtime instance_id per item ✅
- Terminal system: CRT styling, typewriter, keypress nav, sub-menus, terminal mode lockout ✅
- Terminal system split: `terminal_core.js` + `terminal_engineering.js` + `terminal_manifest.js` ✅
- Terminal auto-close on power cut: closes session, system response, Jack's monologue ✅
- Electrical system: reactor, panels, breakers, cables, batteries, power tracing ✅
- Electrical integrated into gameplay: door panels and terminals check room power ✅
- Electrical service layer: `electrical_service.py` — `break_component()` / `fix_component()` / `eject_reactor()` / `install_reactor()` callable from any backend code ✅
- Engineering terminal: Technical Data, Electrical sub-menu (Power Status map, Circuit Diagram placeholder) ✅
- Debug console: Ctrl+D, break/fix/eject/install commands, live map refresh, room description reload on state change ✅
- Full repair system: diagnose + repair commands, scan tool manual validation, per-component repair, wire consumption by length, auto-chain, event hook ✅
- Repair handler split: `repair_handler.py` (dispatcher) + `door_panel_repair.py` + `repair_utils.py` ✅
- Repair/diagnosis real-time scaling: formula-based with config constants, 20s cap ✅
- Diagnosis timing: based on actual failed components + 25% access overhead + ±10% jitter ✅
- Diagnosis response: formatted duration, failed components, required tools, missing items ✅
- Progress counter (%) on all timed action animations ✅
- Door panel type system: panel_type field, door_access_panel_types.json, security level resolved at load time ✅
- Security level 0 panels: no card required, instant lock/unlock ✅
- Item manufacturer/model fields: all items carry manufacturer, model, description with character ✅
- Automated storage facility: store/retrieve via UI, manifest on GameManager, CRT terminal display ✅
- Cargo bay manifest: container/pallet instance data, read-only CRT terminal display ✅
- Door action distinction: `open` unlocks and opens, `unlock` unlocks only, `lock` locks ✅
- Input locking during door image display — all paths covered ✅
- Description panel click lockout during timed actions via pointer-events ✅
- Ship log structured entries: timestamp, event, location, detail fields ✅
- Messages system stub — datapad Messages menu functional, shows placeholder ✅
- Trade items: `trade_items.json` with 5 items, cargo containers populated ✅
- Propulsion bypass electrical path: `PWC-ENG-00` connects propulsion reactor to `PNL-ENG-MAIN` (starts broken) ✅
- Propulsion circuit panel `PNL-PRO-MAIN` with bypass, sub-light, and FTL breakers ✅
- Power tracer: any operational `FissionReactor` terminates trace, multiple inbound cables tried ✅
- Engine fixed objects: `Engine` class with `powered` and `online` flags, propulsion bay engines ✅
- SVG map: engine icons, reactor eject overlays, engine hover tooltips, Share Tech Mono font ✅
- Ship time multiplier: 40 real seconds = 1 ship minute ✅
- Event system: JSON-driven from `data/game/events.json`, frontend poll every 15 seconds ✅
- Event system: `impact_event` type breaks electrical components and door panels via `electrical_service` ✅
- Event system: `_break_component_by_id()` resolves IDs against electrical system then door panels ✅
- Impact event: fires 2 ship minutes after game start, breaks `PNL-REC-SUB-C` + two rec room door panels ✅
- Electrical repair parts: circuit breakers (6 sizes), HV wire (2 gauges), HV connectors, bus bars, logic boards, HV service kit ✅
- UI font: Share Tech Mono replacing Courier New across all player-facing UI (terminal panels excluded) ✅
- Room image swap: powered/unpowered and reactor on/off variants via suffix naming convention ✅
- Jack's internal monologue: `appendMonologue()` function, styled box with rounded corners ✅
- Reactor state system: `@reactor_state@` token, online/offline/ejected states, `_get_reactor_state()` helper ✅
- Eject/install reactor debug commands: `/api/systems/electrical/reactor/eject|install/<id>` ✅
- Engineering room: fully updated prose with all state tokens and image variants ✅
- Corridor naming: Main Corridor / Sub Corridor throughout ✅

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
- **Phase 17** — Electrical system integration ✅
- **Phase 18** — Full repair system ✅
- **Post-18** — Diagnosis timing refactor, inventory improvements, floor source, progress counters ✅
- **Phase 19** — Storage room automated facility + cargo bay manifest system ✅
- **Codebase review (April 2026)** — dead code, silent fallbacks, door action logic, input locking, ship log ✅
- **Electrical expansion** — propulsion bypass, PNL-PRO-MAIN, power tracer, engine fixed objects, SVG map ✅
- **Event system (bare minimum)** — EventSystem class, impact event, event strip, repairInProgress flag ✅
- **Electrical repair parts** — HV items, circuit breakers, wire gauges, storage quantity support ✅
- **File splits (April 2026)** — terminal.js → three files; repair_handler.py → three files ✅
- **Electrical service layer** — electrical_service.py extracted, systems.py thinned to HTTP wrappers ✅
- **Event system overhaul** — JSON-driven events.json, generic _break_component_by_id(), door panel damage ✅
- **Description system overhaul** — token injection, colour scheme, Share Tech Mono, power junction markup ✅
- **Room description style guide** — Project_Orion_Room_Description_Style_v1.md created ✅
- **PowerJunction system** — class, JSON, loader, tooltip, panel_id keywords ✅
- **Visual polish** — ~ italic markup, addendum flash animation, unpowered room image swap ✅
- **Terminal power cut** — auto-close on power loss, Jack monologue box ✅
- **Reactor state system** — @reactor_state@ token, eject/install debug commands, image variants ✅
- **Description panel UX** — fixed title, panel priority toggle, ghost divider ✅

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
│   │   ├── game_manager.py        ← owns all game state, event_system, storage_manifest, cargo_manifest
│   │   ├── ship.py
│   │   ├── room.py                ← description_powered/unpowered/reactor_online/offline/ejected fields
│   │   ├── door.py                ← panel_type, security_level resolved at load time
│   │   ├── interactable.py        ← StorageUnit, Surface, Terminal, Engine, PowerJunction, PalletContainer, Pallet
│   │   ├── player.py
│   │   └── chronometer.py
│   │
│   ├── systems/
│   │   └── electrical/
│   │       ├── electrical_system.py
│   │       └── electrical_service.py  ← break/fix/eject/install — shared service layer
│   │
│   ├── events/
│   │   ├── __init__.py
│   │   └── event_system.py        ← JSON-driven, _break_component_by_id(), handles electrical + door panels
│   │
│   ├── handlers/
│   │   ├── base_handler.py
│   │   ├── command_handler.py
│   │   ├── movement_handler.py
│   │   ├── door_handler.py
│   │   ├── repair_handler.py      ← thin dispatcher only
│   │   ├── door_panel_repair.py   ← door panel diagnosis and repair logic
│   │   ├── repair_utils.py        ← shared pure utilities, cached item registry
│   │   ├── item_handler.py
│   │   ├── container_handler.py
│   │   ├── equip_handler.py
│   │   ├── terminal_handler.py
│   │   └── storage_handler.py
│   │
│   ├── loaders/
│   │   └── item_loader.py
│   │
│   └── api/
│       ├── game.py                ← _get_reactor_state(), room response includes reactor state fields
│       ├── command.py
│       ├── systems.py             ← thin HTTP wrappers, eject/install reactor routes
│       └── events.py              ← /api/events/check endpoint
│
├── frontend/
│   ├── templates/
│   │   ├── splash.html
│   │   └── game.html              ← fixed description title, ghost divider, panel priority toggle
│   │
│   └── static/
│       ├── css/
│       │   ├── splash.css
│       │   ├── game.css           ← colour variables, Share Tech Mono, panel flex ratios, priority toggle
│       │   ├── description.css    ← markup classes, addendum flash, ~ italic, fixed title styles
│       │   ├── inventory.css
│       │   ├── response.css       ← monologue-box style
│       │   ├── terminal.css
│       │   ├── datapad.css
│       │   └── events.css         ← blink iterations 7
│       ├── js/
│       │   ├── core/
│       │   │   ├── constants.js
│       │   │   ├── api.js
│       │   │   └── loop.js        ← event poll, repairInProgress flag, loadRoom() after events
│       │   └── screens/
│       │       ├── splash.js
│       │       ├── ui.js          ← appendMonologue()
│       │       ├── commands.js
│       │       ├── description.js ← all token injection, markup parsing, tooltips
│       │       ├── inventory.js
│       │       ├── terminal_core.js
│       │       ├── terminal_engineering.js
│       │       ├── terminal_manifest.js
│       │       ├── map.js
│       │       └── game.js        ← room/reactor state tracking, image selection, debug console
│       └── images/
│           ├── rooms/             ← powered + _unpowered + _reactor_off + _unpowered_reactor_off variants
│           ├── doors/
│           └── ship_layout.svg
│
└── data/
    ├── items/
    │   ├── tools.json
    │   ├── wearables.json
    │   ├── misc_items.json
    │   ├── consumables.json       ← HV parts, circuit breakers, wire gauges
    │   ├── trade_items.json
    │   ├── terminals.json
    │   ├── storage_units.json
    │   ├── surfaces.json
    │   ├── engines.json
    │   ├── power_junctions.json   ← five junction definitions with panel_id and keywords
    │   ├── cargo_containers.json
    │   └── pallet_platforms.json
    ├── game/
    │   └── events.json            ← JSON-driven event definitions
    ├── terminals/
    │   └── engineering.json
    ├── repair/
    │   └── repair_profiles.json
    └── ship/
        ├── structure/
        │   ├── ship_rooms.json    ← rec room and engineering fully updated with new prose system
        │   ├── door_status.json
        │   ├── door_access_panel_types.json
        │   ├── initial_ship_state.json  ← panels array empty (damage via event system)
        │   ├── initial_ship_items.json
        │   ├── initial_cargo.json
        │   └── player_items.json
        └── systems/
            └── electrical.json    ← description field removed from panels
```

---

## 5. CONFIG.PY — KEY CONSTANTS

```python
SHIP_NAME       = "Tempus Fugit"
PLAYER_NAME     = "Jack Harrow"
STARTING_ROOM   = "engineering"
START_DATE_TIME = (2276, 1, 1, 0, 0)

# Timed actions
CARD_SWIPE_REAL_SECONDS   = 5

# Repair/diagnosis real-time scaling
REPAIR_TIME_BASE_SECONDS  = 8
REPAIR_TIME_SCALE_SECONDS = 8
REPAIR_TIME_PIVOT_MINUTES = 30
REPAIR_TIME_CAP_SECONDS   = 20
DIAG_ACCESS_OVERHEAD      = 0.25
DIAG_TIME_JITTER          = 0.10

# Ship structure
ROOMS_JSON_PATH            = 'data/ship/structure/ship_rooms.json'
DOORS_JSON_PATH            = 'data/ship/structure/door_status.json'
DOOR_PANEL_TYPES_PATH      = 'data/ship/structure/door_access_panel_types.json'
INITIAL_STATE_JSON_PATH    = 'data/ship/structure/initial_ship_state.json'
SHIP_ITEMS_JSON_PATH       = 'data/ship/structure/initial_ship_items.json'
PLAYER_ITEMS_JSON_PATH     = 'data/ship/structure/player_items.json'
CARGO_JSON_PATH            = 'data/ship/structure/initial_cargo.json'
ELECTRICAL_JSON_PATH       = 'data/ship/systems/electrical.json'
EVENTS_JSON_PATH           = 'data/game/events.json'

# Items
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

# Repair
REPAIR_PROFILES_PATH       = 'data/repair/repair_profiles.json'

# Terminal content
TERMINAL_CONTENT_PATH      = 'data/terminals'
```

---

## 6. THE GAME LOOP — ARCHITECTURE

**Instant actions** — no game time, immediate response, input stays unlocked.
**Timed actions** — backend returns `real_seconds`, frontend locks input, calls back to complete.

---

## 7. THE COMMAND SYSTEM

### Resolver architecture
All typed commands and UI clicks pass through `command_handler.process()`:
1. Instance ID direct match — if target matches any item's `instance_id`, returns immediately
2. Preposition commands intercepted (`take from`, `put in`, `put on`) — routed directly, bypassing verb registry
3. Ambiguity check — `_check_ambiguity()` finds all matches, returns `clarification_required` if multiple distinct items
4. Resolver — `_resolve_for_verb()` converts keywords to IDs using `_resolve_all()`
5. Handler receives resolved `instance_id`, type `id`, or original keyword — all handlers check all three

### Verb registry
| Verb | Handler |
|------|---------|
| `go`, `enter`, `move` | MovementHandler |
| `open`, `close` | _route_open/_route_close |
| `lock`, `unlock` | DoorHandler |
| `diagnose`, `diagnose panel` | RepairHandler.handle_diagnose |
| `repair`, `repair panel` | RepairHandler.handle_repair |
| `take`, `get`, `pick up` | ItemHandler |
| `drop` | ItemHandler |
| `look in` | ContainerHandler |
| `take from` | ContainerHandler |
| `put in`, `place in` | ContainerHandler |
| `put on`, `place on` | ContainerHandler / EquipHandler |
| `wear`, `equip` | EquipHandler |
| `remove`, `take off`, `unequip` | EquipHandler |
| `access` | TerminalHandler |

### Door action values
| Value | Behaviour |
|-------|-----------|
| `'open'` | Unlock and open the door |
| `'unlock'` | Unlock only, door stays closed |
| `'lock'` | Lock the door |

---

## 8. MAIN GAME SCREEN LAYOUT

```
┌────────────────────────────────────────────────────────────┐
│ [INV] [TERM]  ← horizontal tab strip                       │
├──────────────────────────────────┬─────────────────────────┤
│                                  │ ROOM TITLE (fixed)      │
│      ROOM IMAGE (45%)            ├─────────────────────────┤
│  ← slide-out panels cover this   │ DESCRIPTION (scrollable)│
│                                  ├──── divider (toggle) ───┤
│                                  │ RESPONSE (scrollable)   │
│                                  ├─────────────────────────┤
│                                  │ COMMAND INPUT           │
├──────────────────────────────────┴─────────────────────────┤
│ EVENT STRIP              [events]      [ship name + time]  │
└────────────────────────────────────────────────────────────┘
```

### Panel priority toggle
Clicking the divider between description and response flips the flex ratios:
- Default: description flex 5, response flex 2
- Toggled: description flex 2, response flex 5

Useful when dialogue trees or long repair sequences fill the response panel.

### Colour palette
| Variable | Hex | Use |
|----------|-----|-----|
| `--col-text` | `#cecece` | Default prose text |
| `--col-title` | `#27e6ec` | Cyan — exits / doors |
| `--col-container` | `#c4a050` | Amber — containers + surfaces |
| `--col-terminal` | `#a06aa0` | Violet — terminals |
| `--col-junction` | `#b87560` | Coral — power junctions |
| `--col-portable` | `#b09abe` | Purple — portable items |
| `--col-alert` | `#ff8c00` | Orange — alerts |
| `--col-prompt` | `#00ff00` | Green — command prompt |
| `--col-response` | `#7e97ae` | Muted blue — player input echo |
| `--col-term-bg` | `#000d00` | CRT phosphor background |
| `--col-term-text` | `#00ff41` | Phosphor green text |
| `--col-term-dim` | `#00801f` | Dimmer green — secondary |
| `--col-term-border` | `#004d10` | Dark green border |

### Font
Share Tech Mono is the primary UI font. CRT terminal panels use a separate font (TBD).

---

## 9. DESCRIPTION PANEL — MARKUP SYSTEM

### Markup types
| Markup | Type | Colour | Hover | Click |
|--------|------|--------|-------|-------|
| `*exit*` | Exit | Cyan bold | Door state + Offline if unpowered | None |
| `%container%` | Container | Amber bold | Open/Closed | Toggle open/close |
| `!terminal!` | Terminal | Violet bold | Online / Offline | `access <terminal>` |
| `#surface#` | Surface | Amber bold | Empty/Has items | Expand Layer 3 |
| `?junction?` | Power junction | Coral bold | Panel ID (e.g. PNL-REC-SUB-C) | None |

### Italic prose markup
Lines wrapped in `~text~` render in italic. Pure prose only — no interactive markup inside `~` lines.

### Token injection system
The `description` array is a mixed array of prose strings and state tokens:

| Token | Resolves to | JSON fields required |
|-------|-------------|---------------------|
| `^power_state^` | Room power addendum | `description_powered`, `description_unpowered` |
| `@reactor_state@` | Reactor state addendum | `description_reactor_online`, `description_reactor_offline`, `description_reactor_ejected` |
| `&engine_state&` | Engine state addendum | Reserved — not yet implemented |

Addendums render in italic with 8-second orange flash animation on state change.

### Room image selection
Images use suffix naming convention — the frontend builds the path from current state:
- Powered + reactor online → `roomname.png`
- Powered + reactor offline/ejected → `roomname_reactor_off.png`
- Unpowered + reactor online → `roomname_unpowered.png`
- Unpowered + reactor offline/ejected → `roomname_unpowered_reactor_off.png`

Missing image variants fall back gracefully via `img.onerror`.

### Description layers
1. **Room title** — fixed, does not scroll
2. **Neutral prose** — authored JSON, no state references, `~italic~` for atmosphere
3. **State addendums** — italic, injected at token positions
4. **Layer 2** — open container contents (amber name, purple items)
5. **Layer 3** — expanded surface contents (purple, on demand)
6. **Floor line** — italic label, purple items, only when occupied

### Room description authoring
See `Project_Orion_Room_Description_Style_v1.md` for full authoring rules.

---

## 10. INVENTORY SYSTEM

**Player inventory** — INV tab slide-out panel. Equipped slots + carried items. Store button visible in storage room.

**Ship inventory** — automated storage facility in storage room. Store via inventory panel, retrieve via terminal UI. No typed commands.

---

## 11. ITEM SYSTEM

### Item registry
- `item_loader.py` stores raw data dicts — not instances
- `instantiate_item()` creates fresh `PortableItem` instance each call
- Every placed item is a unique Python object with independent state

### Object ID naming convention
`roomid_markuptext` — ensures unambiguous ID matching within a room.

### Item fields — required on all items
- `manufacturer` — company name
- `model` — model or part number
- `description` — written with character, not generic

### Wire consumables — special fields
- `mass_per_metre` instead of `mass`
- `max_length_m` — maximum spool capacity
- `length_m` — actual instance length, decremented on use
- One spool must have sufficient length — no combining across spools

### Scan tool — special fields
- `installed_manuals` — list of panel model names the scan tool can service
- Must match `model` field in `door_access_panel_types.json` exactly

---

## 12. TERMINAL SYSTEM

### Overview
Accessed via `access terminal` command or clicking terminal markup. Player locked to terminal until `[X]` exit.

### Terminal types
| terminal_type | Location | Behaviour |
|---------------|----------|-----------|
| `engineering` | Engineering | Menu-driven, electrical sub-menu, power map |
| `storage_room` | Storage Room | Live manifest, arrow nav, retrieve button |
| `cargo_bay` | Cargo Bay | Read-only manifest, arrow nav |
| `personal` | Captain's Quarters | Stub |
| `mainframe` | Mainframe Room | Stub |
| `navigation` | Cockpit | Stub |
| `medical` | Med-Bay | Stub |

### Power cut behaviour
If room loses power while terminal is active, terminal closes automatically. System response shown, Jack's monologue appended.

### Key files
- `terminal_core.js` — session state, panel, rendering, typewriter, keyboard
- `terminal_engineering.js` — electrical sub-menu and power map
- `terminal_manifest.js` — storage and cargo manifest rendering

---

## 13. ELECTRICAL SYSTEM

### Overview
25kW thermionic fission reactor. Power distributed through hierarchical network of circuit panels, breakers, and cables to all 17 compartments. Two backup batteries for Life Support and Mainframe.

### Component naming convention
| Code | Type | Example |
|------|------|---------|
| `PNL-` | Panel | `PNL-ENG-MAIN` |
| `FUS-` | Breaker | `FUS-MC-01` |
| `PWC-` | Cable | `PWC-ENG-03` |
| `BAT-` | Battery | `BAT-LS-01` |

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

PWC-ENG-00 — bypass path: propulsion_reactor → PNL-ENG-MAIN (starts broken)
```

### Reactor ejection
The main reactor core can be ejected via explosive bolts. The reactor shell remains in place and maintains hull integrity — it is rated to contain fission, so vacuum is not a concern. The ejection port goes with the core, leaving the shell as the hull seal. Through the crystalline alumina casing, space is visible where the core used to be.

**Ejection is irreversible in deep space.** The propulsion reactor takes over via the bypass path (`PWC-ENG-00`). See Future doc Section 3 for full dual-reactor design.

### Reactor state values
| State | Condition |
|-------|-----------|
| `online` | Reactor operational |
| `offline` | Reactor present but not operational |
| `ejected` | Core ejected, shell present |

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/systems/electrical/status` | GET | Full system status |
| `/api/systems/electrical/room/<id>` | GET | Single room power check |
| `/api/systems/electrical/break/<id>` | POST | Break any component |
| `/api/systems/electrical/fix/<id>` | POST | Fix any component |
| `/api/systems/electrical/reactor/eject/<id>` | POST | Eject reactor core (debug) |
| `/api/systems/electrical/reactor/install/<id>` | POST | Install reactor core (debug) |

### Debug console
- `Ctrl+D` toggles debug panel
- `break <id>` / `fix <id>` — electrical components
- `eject <id>` / `install <id>` — reactor cores (debug only)

---

## 14. REPAIR SYSTEM (PHASE 18)

### Overview
Profile-driven multi-step repair. Phase 18 scope is door panels. Architecture is generic — same pattern applies to electrical repair and future fixed object repair.

### Door panel state machine
```
is_broken = False → operational
is_broken = True, broken_components empty → diagnose
is_broken = True, components populated → repair per-component
repaired_components == broken_components → panel restored
```

### Security levels
| Level | Type | Behaviour |
|-------|------|-----------|
| 0 | NONE | No card required |
| 1 | KEYCARD_LOW | Low or high security card |
| 2 | KEYCARD_HIGH | High security card |
| 3 | KEYCARD_HIGH_PIN | High security card + PIN |

### Repair system architecture
- `repair_handler.py` — thin dispatcher
- `door_panel_repair.py` — door panel logic
- `repair_utils.py` — shared utilities, cached item registry
- Future: `electrical_repair.py`, `fixed_object_repair.py` — same pattern

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/command/diagnose_complete` | POST | Populates broken_components |
| `/api/command/repair_complete` | POST | Consumes parts, marks repaired |
| `/api/command/repair_next` | POST | Event check then next component |

---

## 15. EVENT SYSTEM

### Overview
Scheduled events triggered by game-time thresholds. Defined in `data/game/events.json`.

### Event JSON structure
```json
{
  "id": "micrometeorite_impact",
  "type": "impact_event",
  "trigger_minutes": 2,
  "event_message": "⚠ IMPACT EVENT — Electrical faults detected — Run diagnostics",
  "affected_components": ["PNL-REC-SUB-C", "recreation_room_cockpit_panel_rec"],
  "event_effects": [],
  "randomise_damage": false,
  "randomise_time": false
}
```

### Supported event types
| Type | Behaviour | Status |
|------|-----------|--------|
| `impact_event` | Breaks components in `affected_components` | ✅ Implemented |
| `message_event` | Delivers message to datapad | Stub only |
| `solar_flare_event` | Future | Planned |
| `reactor_overload_event` | Future | Planned |

### Component damage resolution
`_break_component_by_id()` resolves each ID in order:
1. Electrical components via `electrical_service.break_component()`
2. Door panels — `panel.is_broken = True`
3. TODO: Engines, fixed objects

### `event_effects` array
Reserved for future side effects — room description changes, atmosphere venting, narrative state changes. Currently always empty.

---

## 16. SHIP INVENTORY SYSTEM

### Storage room — automated storage facility
- `game_manager.storage_manifest` — dict keyed by `instance_id` → `PortableItem`
- Store via inventory panel button (storage room only)
- Retrieve via storage terminal `[R]` key
- API: `GET /api/game/storage/manifest`, `POST /api/game/storage/store`, `POST /api/game/storage/retrieve`

### Cargo bay — freight space
- `game_manager.cargo_manifest` — containers and pallets lists
- Read-only terminal display
- API: `GET /api/game/cargo/manifest`

### Interactable class hierarchy
```
Interactable
├── PortableItem
│   └── UtilityBelt
├── FixedObject
│   ├── StorageUnit
│   │   └── PalletContainer
│   ├── Surface
│   │   └── Pallet
│   ├── Terminal
│   ├── Engine
│   └── PowerJunction         ← panel_id links to electrical CircuitPanel
```

### Container dimensions
| Type | Dimensions | Movement |
|------|-----------|----------|
| Small | 750x600x900mm | Sack barrow or cargo handler |
| Medium | 750x1200x900mm | Cargo handler only |
| Large | 1500x1200x900mm | Cargo handler only |
| Single pallet | 1500x1200x150mm | Cargo handler only |
| Double pallet | 3000x1200x150mm | Cargo handler only |

---

## 17. TABLET, SHIP'S LOG AND MESSAGES

### The Tablet
Portable handheld device. When in inventory, PAD tab appears. Shows: ship power map, circuit diagram, diagnostic/repair notes, ship's log, messages. Works on own battery — functions in unpowered rooms.

### Ship's Log
Structured dicts: `timestamp`, `event`, `location` (optional), `detail`.

### Messages System
Narrative delivery mechanism. Types: automated ship alerts, external communications, narrative events. Distinct from ship's log.

---

## 18. JACK'S MONOLOGUE SYSTEM

### Current state
Hardcoded for one trigger only — terminal power cut. `appendMonologue(text)` renders text in a styled box (dark background, muted blue-grey italic, rounded corners).

### Future
JSON-driven keyed response system (`monologue.json`). Keys: `terminal_power_failure`, `reactor_offline`, `hull_breach` etc. Ties into NPC dialogue tree system. Design: tone variations by game state, one-shot vs repeatable lines, per-character voice box colours.

---

## 19. ELECTRICAL REPAIR — DESIGN

### Overview
Same diagnose/repair gameplay as door panels. HV test kit required instead of scan tool. Access point is the PowerJunction fixed object. Each junction owns its panel, breakers, and adjacent cables.

### Repair scope boundary
Jack can repair: cables, breakers, circuit panels, door access panels.
Jack cannot repair without port: reactor cores, engine internals, major structural damage.

Reactor ejection is irreversible in deep space. See Future doc Section 3.

### Component types and parts
| Type | Parts required |
|------|---------------|
| Breaker | 1x matching amp-rated circuit breaker |
| Cable (standard) | `wire_hv_standard` by length + 2x `hv_connect_standard` |
| Cable (heavy duty) | `wire_hv_heavy_duty` by length + 2x `hv_connect_heavy` |
| Panel | 1x `hv_logic_board` + 1x `hv_bus_bar` |

### Heavy duty cables
`PWC-ENG-01`, `PWC-PRO-01`, `PWC-PRO-04`, `PWC-ENG-00`, `PWC-PRO-02`, `PWC-PRO-03`

### Circuit breaker sizes
| Item ID | Rating | Used for |
|---------|--------|---------|
| `10A_breaker` | 10A | Small rooms |
| `32A_breaker` | 32A | Medium rooms |
| `63A_breaker` | 63A | Sub-panel branch feeds |
| `250A_breaker` | 250A | Bypass breaker FUS-PRO-00 |
| `600A_breaker` | 600A | Sub-light engine FUS-PRO-01 |
| `1200A_breaker` | 1200A | FTL engine FUS-PRO-02 |

### Key design decisions still to make ⚠️
- Exact command syntax for electrical diagnose/repair
- Panel failure severity randomisation
- Repair profiles need cable length_m added to electrical.json first
- Junction panel images needed: `junction_closed.png`, `junction_open.png`

---

## 20. KNOWN ISSUES / DEFERRED

- **PAM** — clips to utility belt. Dormant until life support phase.
- **Examine command** — `examine <item>` prints name, manufacturer, model, description. New verb, deferred.
- **Terminal shutdown edge case** — power cut while mid-repair with terminal open. Deferred.
- **Unpowered room images** — naming convention implemented. Recreation room and engineering complete. Remaining 15 rooms need Reve generation alongside description authoring.
- **`^room_state^` token** — reserved for permanent room state changes (hull breach etc.). Deferred.
- **Dynamic room descriptions** — 15 rooms still need ~ italic prose, powered/unpowered addendums. Recreation room and engineering complete.
- **Power junction placement** — recreation room and engineering complete. Three remaining rooms (main corridor, sub corridor, propulsion bay) need junctions added.
- **Circuit diagram SVG** — being built manually in Inkscape. Integrate into engineering terminal when complete.
- **Repair post-repair failure roll** — always succeeds. Future: probability-based.
- **Scan tool software updates** — future exotic systems require purchased updates.
- **Python built-in shadowing** — `id` and `type` used as parameter names throughout. Dedicated cleanup pass needed.
- **CRT terminal font** — Share Tech Mono inherited by CRT panels. Separate font TBD.
- **Event system save/load** — `GameEvent.fired` and `GameEvent.resolved` in-memory only. Must be serialised.
- **Event effects** — `event_effects` reserved but not implemented.
- **Engine damage via events** — `_break_component_by_id()` TODO stub for engine resolution.
- **`PalletContainer.pallet` flag** — purpose unclear, appears unused.
- **Cargo contents** — `initial_cargo.json` containers empty.
- **Cargo handler operational flag** — stub needed before cargo movement phase.
- **Long repair auto-chain threshold** — pause for survival mechanics. Phase 21.
- **Repair failure mechanic** — `Loop.setRepairInProgress(false)` needed on failure path.
- **`command_handler.py` process() cleanup** — preposition blocks duplicate `_resolve_for_verb()` logic.
- **Room temperature** — deferred until life support is designed.
- **Description panel priority toggle** — future: auto-flip when dialogue tree is active.
- **`reactor_offline` monologue** — Jack's reaction to finding the reactor cold. First candidate for monologue JSON system.

### Input lockout behaviour — known inconsistency
Terminal active (`setTerminalMode`) — tooltips remain active.
Timed action active (`Loop.lockInput`) — full pointer-events block, tooltips disabled.
Whether to unify these is an open question.

### Recently completed deferred items
- ✅ Terminal auto-close on power cut
- ✅ Jack's monologue box
- ✅ Corridor rename throughout
- ✅ PowerJunction FixedObject system
- ✅ ~ italic markup
- ✅ Addendum flash animation
- ✅ Unpowered room image swap
- ✅ Reactor state token system
- ✅ Eject/install debug commands
- ✅ Engineering room fully described with all state variants
- ✅ Description panel fixed title
- ✅ Panel priority toggle
- ✅ Ghost divider padding

---

## 21. RULES FOR DEVELOPMENT

1. **Upload current files at start of every session** — never work from memory
2. **Read the code before changing it** — ask to see files before editing
3. **One change at a time — verify before proceeding**
4. **No silent fallbacks** — missing data must crash loudly, not degrade silently
5. **Backend owns all game state** — JS is display only
6. **Minimal targeted changes** — no "while I'm in here" improvements without asking
7. **No god files** — grouped logically by domain
8. **All colours in CSS variables**
9. **All JS timeouts in `constants.js`**
10. **All Python durations in `config.py`**
11. **Debate bad ideas** — push back if something seems wrong
12. **Never add "type X to fix it" hints** — immersive messages only
13. **New files as downloads** — never inline only
14. **All JSON fields have a use** — never partially load type definitions
15. **Suggest before adding** — flag missing spec items before writing code
16. **Never output complete game.html or game.js — targeted changes only**

---

## 22. PROJECT BACKGROUND

*Written by the lead designer, April 2026.*

"I have limited coding knowledge, mainly Python, with a little exposure to javascript, html, css but I am no accomplished programmer. My skills are in logical thought processes, multiple years of real life mechanical repair/diagnosis and an ability to look into what future changes could impact the current codebase which enables a certain amount of 'if we do this, we may need to make allowances for what a future phase may require'.

The development process has been organic, some has been planned for, but certainly not from day one. This is where the design docs are vital.

I am the lead designer, however virtually all coding is done by AI, my coding input has been minimal. The project started from several small projects aka feature experiments eg the electrical system and the typewriter terminal effects. Some experiments didn't work out such as the life support logic so this will need revisiting until I am happy with the result.

This project would never have got to this state without the various AI's (starting with Grok, the SuperGrok, then Sonnet 4.5 and now Sonnet 4.6) and of course it also would not have got to this state without my input, design ideas and constant questions and debates between myself and the AI's such as yourself."

---

*Project Orion Game — Technical Reference v23.0 — April 2026*
