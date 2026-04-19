# PROJECT ORION GAME
## Space Survival Simulator
### Master Design & Development Document
**Version 22.0 — April 2026**

> ⚠️ **IMPORTANT — DO NOT ASSUME ALL CONTENT IN THIS DOCUMENT IS CORRECT.** This document has evolved organically over many development sessions. Not all sections have been manually verified against the current codebase. Where the code and the document conflict, the code is authoritative. Treat this document as a guide and reference, not a specification.

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
- Fixed object data structure: terminals, storage units, surfaces, pallet containers, pallet platforms, engines ✅
- Description panel: markup parser, hover tooltips, click handlers, Layer 2/3 ✅
- Description panel: power state token injection system (`^power_state^`) ✅
- Description panel: powered/unpowered addendum rendered in italic ✅
- Description panel: new colour scheme — exits cyan, containers/surfaces amber, terminals violet, power junctions coral, portables purple ✅
- Description panel: power junction markup `?name?` ✅
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
- Electrical system: reactor, panels, breakers, cables, batteries, power tracing ✅
- Electrical integrated into gameplay: door panels and terminals check room power ✅
- Electrical service layer: `electrical_service.py` — `break_component()` / `fix_component()` callable from any backend code ✅
- Engineering terminal: Technical Data, Electrical sub-menu (Power Status map, Circuit Diagram placeholder) ✅
- Debug console: Ctrl+D, break/fix commands, live map refresh, room description reload on power change ✅
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
- Cargo manifest display: four columns (Container, Type, Item, Qty), item names resolved from registry ✅
- Propulsion bypass electrical path: `PWC-ENG-00` connects propulsion reactor to `PNL-ENG-MAIN` (starts broken) ✅
- Propulsion circuit panel `PNL-PRO-MAIN` with bypass, sub-light, and FTL breakers ✅
- Power tracer: any operational `FissionReactor` terminates trace, multiple inbound cables tried ✅
- Engine fixed objects: `Engine` class with `powered` and `online` flags, propulsion bay engines ✅
- SVG map: engine icons (sub-light pairs + FTL drive), reactor eject overlays, engine hover tooltips ✅
- SVG map: Share Tech Mono font, reduced room label size, dimension labels removed ✅
- Ship time multiplier: 40 real seconds = 1 ship minute ✅
- Event system: JSON-driven from `data/game/events.json`, frontend poll every 15 seconds ✅
- Event system: `impact_event` type breaks electrical components and door panels via `electrical_service` ✅
- Event system: `_break_component_by_id()` resolves IDs against electrical system then door panels ✅
- Impact event: fires 2 ship minutes after game start, breaks `PNL-REC-SUB-C` + two rec room door panels ✅
- Electrical repair parts: circuit breakers (6 sizes), HV wire (2 gauges), HV connectors, bus bars, logic boards, HV service kit ✅
- Storage facility quantity support: `{"id": "...", "quantity": N}` format in `initial_ship_items.json` ✅
- UI font: Share Tech Mono replacing Courier New across all player-facing UI (terminal panels excluded) ✅
- Room description style guide: separate document `Project_Orion_Room_Description_Style_v1.md` ✅
- PowerJunction FixedObject: class in interactable.py, JSON definitions, loader, object_states, tooltip ✅
- Power junction tooltip shows panel_id in coral — cross-reference with SVG circuit diagram ✅
- Panel_id in junction keywords — player can type diagnose PNL-REC-SUB-C directly ✅
- CircuitPanel: description field removed, id/type parameter shadowing fixed ✅
- ~ italic markup: atmospheric prose lines wrapped in ~ render italic, no markup parsing inside ✅
- Addendum flash animation: sharp orange fade-in, 8 second decay to normal grey on power state change ✅
- Room image swap: powered/unpowered variants via _unpowered suffix, selected in updateRoom() ✅
- Terminal auto-close on power cut: closes session, shows system response and Jack's monologue ✅
- Jack's internal monologue: appendMonologue() function, styled box with rounded corners ✅
- Corridor naming: Main Corridor CH-1 → Main Corridor, Sub Corridor CH-2 → Sub Corridor throughout ✅

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
- **Phase 17** — Electrical system integration ✅ (circuit diagram SVG pending — being built manually in Inkscape)
- **Phase 18** — Full repair system ✅
- **Post-18 session** — Diagnosis timing refactor, inventory improvements, floor source, progress counters, response format improvements ✅
- **Phase 19** — Storage room automated facility + cargo bay manifest system ✅
- **Codebase review (April 2026)** — dead code, silent fallbacks, door action logic, input locking, ship log structure ✅
- **Electrical expansion** — propulsion bypass, PNL-PRO-MAIN, power tracer improvements, engine fixed objects, SVG map engine icons, ship time multiplier ✅
- **Event system (bare minimum)** — EventSystem class, impact event, event strip, repairInProgress flag ✅
- **Electrical repair parts** — HV items, circuit breakers, wire gauges, storage quantity support ✅
- **File splits (April 2026)** — terminal.js → terminal_core/engineering/manifest.js; repair_handler.py → repair_handler/door_panel_repair/repair_utils.py ✅
- **Electrical service layer** — electrical_service.py extracted, systems.py thinned to HTTP wrappers ✅
- **Event system overhaul** — JSON-driven events.json, generic _break_component_by_id(), door panel damage via events ✅
- **Description system overhaul** — token injection, powered/unpowered addendum, new colour scheme, Share Tech Mono font, power junction markup ✅
- **Room description style guide** — Project_Orion_Room_Description_Style_v1.md created ✅
- **PowerJunction system** — class, JSON, loader, tooltip, panel_id keywords ✅
- **Visual polish** — ~ italic markup, addendum flash animation, unpowered room image swap ✅
- **Terminal power cut** — auto-close on power loss, Jack monologue box ✅
- **Corridor rename** — CH-1/CH-2 references removed throughout ✅

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
│   │   ├── room.py                ← description_powered, description_unpowered fields added
│   │   ├── door.py                ← panel_type, security_level resolved at load time
│   │   ├── interactable.py        ← StorageUnit, Surface, Terminal, Engine, PalletContainer, Pallet
│   │   ├── player.py
│   │   └── chronometer.py
│   │
│   ├── systems/
│   │   └── electrical/
│   │       ├── electrical_system.py
│   │       └── electrical_service.py  ← break_component(), fix_component() — shared service layer
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
│   │   ├── repair_utils.py        ← shared pure utilities (time calc, item_name, check_tools etc.)
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
│       ├── game.py
│       ├── command.py
│       ├── systems.py             ← thin HTTP wrappers calling electrical_service
│       └── events.py              ← /api/events/check endpoint
│
├── frontend/
│   ├── templates/
│   │   ├── splash.html
│   │   └── game.html
│   │
│   └── static/
│       ├── css/
│       │   ├── splash.css
│       │   ├── game.css           ← new colour variables, Share Tech Mono font
│       │   ├── description.css    ← markup classes, addendum flash animation, ~ italic class
│       │   ├── inventory.css
│       │   ├── response.css       ← monologue-box style
│       │   ├── terminal.css
│       │   ├── datapad.css
│       │   └── events.css         ← blink iterations increased to 7
│       ├── js/
│       │   ├── core/
│       │   │   ├── constants.js
│       │   │   ├── api.js
│       │   │   └── loop.js        ← event poll, repairInProgress flag, loadRoom() after events
│       │   └── screens/
│       │       ├── splash.js
│       │       ├── ui.js          ← appendMonologue() added
│       │       ├── commands.js
│       │       ├── description.js ← token injection, ?junction? markup, ~ markup, junction tooltip
│       │       ├── inventory.js
│       │       ├── terminal_core.js
│       │       ├── terminal_engineering.js
│       │       ├── terminal_manifest.js
│       │       ├── map.js
│       │       └── game.js        ← currentRoomPowered tracking, image swap, terminal power cut
│       └── images/
│           ├── rooms/
│           ├── doors/
│           └── ship_layout.svg    ← Share Tech Mono, reduced font size
│
└── data/
    ├── items/
    │   ├── tools.json
    │   ├── wearables.json
    │   ├── misc_items.json
    │   ├── consumables.json
    │   ├── trade_items.json
    │   ├── terminals.json
    │   ├── storage_units.json
    │   ├── surfaces.json
    │   ├── engines.json
    │   ├── power_junctions.json   ← NEW: five junction definitions with panel_id and keywords
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
        │   ├── ship_rooms.json    ← rec room: ~ italic markup, power junction, corridor names fixed
        │   ├── door_status.json
        │   ├── door_access_panel_types.json
        │   ├── initial_ship_state.json  ← panels array emptied (damage now via event system)
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
1. Instance ID direct match — if target matches any item's `instance_id`, returns immediately, no ambiguity possible
2. Preposition commands intercepted (`take from`, `put in`, `put on`) — clarified preposition commands routed directly, bypassing verb registry
3. Ambiguity check — `_check_ambiguity()` finds all matches, deduplicates by `display_name()`, returns `clarification_required` if multiple distinct items
4. Resolver — `_resolve_for_verb()` converts keywords to IDs using `_resolve_all()`
5. Handler receives resolved `instance_id`, type `id`, or original keyword — all handlers check all three

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
The `door_action` field passed through the card swipe flow has three distinct values:

| Value | Behaviour |
|-------|-----------|
| `'open'` | Unlock and open the door — sent by `handle_open` when door is locked |
| `'unlock'` | Unlock only, door stays closed — sent by `handle_unlock` |
| `'lock'` | Lock the door — sent by `handle_lock` |

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
| `--col-text` | `#cecece` | Default prose text |
| `--col-title` | `#27e6ec` | Cyan — exits / doors |
| `--col-container` | `#c4a050` | Amber — containers + surfaces |
| `--col-terminal` | `#a06aa0` | Violet — terminals |
| `--col-junction` | `#b87560` | Coral — power junctions |
| `--col-portable` | `#b09abe` | Purple — portable items |
| `--col-alert` | `#ff8c00` | Orange — alerts, locked doors, offline state |
| `--col-prompt` | `#00ff00` | Green — command prompt, open doors |
| `--col-response` | `#7e97ae` | Muted blue — player input echo |
| `--col-term-bg` | `#000d00` | CRT phosphor background |
| `--col-term-text` | `#00ff41` | Phosphor green text |
| `--col-term-dim` | `#00801f` | Dimmer green — secondary terminal text |
| `--col-term-border` | `#004d10` | Dark green border |

### Font
Share Tech Mono is the primary UI font across all player-facing panels. Courier New remains as fallback. CRT terminal panels use a separate font (TBD — to be selected when terminal font is addressed).

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

All markup renders title case and bold. Colour distinguishes object type.

### Italic prose markup
Lines wrapped in `~text~` render in italic with no markup parsing inside. Used for atmospheric prose and set dressing — the player voice that describes the space rather than its interactables. Pure prose only, no interactive markup inside `~` lines.

### Power state token injection
The `description` array in `ship_rooms.json` is a mixed array of prose strings and state tokens. The renderer processes each element in order — prose strings render normally, state tokens resolve to the appropriate addendum and render in italic.

| Token | Resolves to | JSON fields required |
|-------|-------------|---------------------|
| `^power_state^` | Room power addendum | `description_powered`, `description_unpowered` |
| `@reactor_state@` | Reactor state addendum | Deferred — reserved |
| `&engine_state&` | Engine state addendum | Deferred — reserved |

Addendums render in italic, same default grey colour as prose. See `Project_Orion_Room_Description_Style_v1.md` for full authoring rules.

### Room description style
All room description authoring follows the rules in the separate style guide document:
**`docs/Project_Orion_Room_Description_Style_v1.md`**

Key rules:
- Neutral prose contains no power state references
- ISS directional convention throughout (forward, aft, port, starboard)
- All exits, interactables and fixed objects must appear in the description
- Powered/unpowered addendums mirror each other in structure
- Photoluminescent deck strips provide emergency lighting in all rooms — always present, always dim green, independent of electrical system

### Description layers
1. **Neutral prose** — authored JSON, no power state references
2. **Power state addendum** — italic, injected at `^power_state^` token position
3. **Layer 2** — open container contents (amber name, purple items)
4. **Layer 3** — expanded surface contents (purple, on demand)
5. **Floor line** — `Floor: item1, item2` (italic label, purple items, only when occupied)

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
- Store button visible on carried items when player is in the storage room

**Ship inventory** — automated storage facility in the storage room
- Accessed via storage room inventory terminal
- Store via inventory panel button, retrieve via terminal UI
- No typed commands for store/retrieve — UI only

---

## 11. ITEM SYSTEM

### Item registry
- `item_loader.py` stores raw data dicts — not instances
- `instantiate_item()` creates fresh `PortableItem` instance each call
- Every placed item is a unique Python object with independent state

### Object ID naming convention
`roomid_markuptext` — ensures unambiguous ID matching within a room.
Cargo container instances use descriptive IDs without room prefix since they are moveable: `small_container_001`, `pallet_single_001` etc.

### Item fields — all item types (tools, wearables, consumables)
Every item in the game must have:
- `manufacturer` — company name (e.g. "Enso VeilTech", "Tengu Cables", "SMC Nova")
- `model` — model or part number
- `description` — written with character, not generic

No generic descriptions anywhere. Every item must feel like it exists in the world of 2276.

### Wire consumables — special fields
Wire items use `mass_per_metre` instead of `mass` (mass is computed at runtime from `length_m`):
- `max_length_m` — maximum spool capacity, physical property of the item type
- `mass_per_metre` — used to compute instance mass at runtime

Wire instance attributes (set at runtime, not in JSON type definition):
- `length_m` — actual length of this spool, set from placement data, decremented on use
- `mass` — computed: `length_m * mass_per_metre`

Wire consumption during repair: one spool must have sufficient length — no combining across multiple spools. Repair consumes `length_m` from the spool and recomputes mass.

### Scan tool — special fields
- `installed_manuals` — list of human-readable panel model names the scan tool can service
- These strings must match the `model` field in `door_access_panel_types.json` exactly
- Expandable as new system manuals are added or purchased

### initial_ship_items.json — sections
- `storage_facility` — list of item IDs loaded into the automated storage facility at game init
- `room_floor` — items placed on room floors
- `containers` — items placed inside storage units
- `surfaces` — items placed on surfaces

---

## 12. TERMINAL SYSTEM (PHASE 16)

### Overview
Terminals are accessed via `access terminal` command or clicking terminal markup in the description. Once accessed, the player is locked to the terminal until they explicitly exit with `[X]`.

### Power check
Terminal access is blocked if the room has no power.

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

### Terminal types
| terminal_type | Location | Behaviour |
|---------------|----------|-----------|
| `engineering` | Engineering | Menu-driven, electrical sub-menu, power map |
| `storage_room` | Storage Room | Live manifest list, arrow nav, retrieve button, no menu |
| `cargo_bay` | Cargo Bay | Read-only manifest list, arrow nav, no menu |
| `personal` | Captain's Quarters | Stub |
| `mainframe` | Mainframe Room | Stub — future mainframe hack phase |
| `navigation` | Cockpit | Stub |
| `medical` | Med-Bay | Stub |

### Terminal content files
- `data/terminals/engineering.json` — engineering terminal content
- Storage room and cargo bay terminals load live data directly from GameManager — no JSON content file

### Key files
- `data/items/terminals.json` — terminal definitions, keywords, menu items with key bindings
- `backend/handlers/terminal_handler.py` — `access` verb handler, power check
- `backend/api/game.py` — terminal content, storage manifest, cargo manifest endpoints
- `frontend/static/js/screens/terminal_core.js` — session state, panel open/close, rendering, typewriter, keyboard
- `frontend/static/js/screens/terminal_engineering.js` — electrical sub-menu and power map
- `frontend/static/js/screens/terminal_manifest.js` — storage and cargo manifest rendering
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

### Power integration in gameplay
- **Door panels** — all doors require powered panel to operate. Unpowered: offline message, no door image shown.
- **Terminals** — terminal access blocked if room unpowered.
- **Hover tooltips** — exits show Offline state in orange when unpowered.

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/systems/electrical/status` | GET | Full system status including room_power map |
| `/api/systems/electrical/room/<id>` | GET | Single room power check |
| `/api/systems/electrical/break/<id>` | POST | Break any component by ID |
| `/api/systems/electrical/fix/<id>` | POST | Fix any component by ID |

### Debug console
- `Ctrl+D` toggles debug panel in game
- `break <component_id>` / `fix <component_id>` — electrical components only
- After break/fix, `loadRoom()` is called to update description addendum immediately

---

## 14. BUILD PLAN — FUTURE WORK

> ⚠️ **Phases below are not in strict order.** The sequence changes frequently. The suggested next order is listed but should be treated as a guide only.

### Suggested next order
1. **Room descriptions** — author powered/unpowered addendums and ~ italic prose for remaining 16 rooms. Generate unpowered images in Reve for each room alongside authoring.
2. **Power junction placement** — add junctions to the other four panel rooms in ship_rooms.json and their descriptions
3. **Electrical repair system** — diagnose/repair for cables, breakers, panels via power junction access
4. **Fixed object repair** — engines and reactors using same pattern as door panel repair
5. **Event system expansion** — add more event types, randomisation flags
6. **Codebase review** — before save/load, clean baseline
7. **Save/load system** — autosave only, JSON format, full state serialisation

### Future phases (not in order)

**Room descriptions** ⚠️ Do room by room, test each before moving to next
- Author `description_powered` and `description_unpowered` for all 17 rooms
- Follow `Project_Orion_Room_Description_Style_v1.md` strictly
- Recreation room complete — use as reference
- Rename Main Corridor and Sub Corridor throughout all rooms (remove CH-1/CH-2 suffixes)

**Power junction FixedObject** ⚠️ Needed before electrical repair
- New `PowerJunction` class in `interactable.py` — subclass of `FixedObject`
- `panel_id` field linking to electrical system `CircuitPanel` by ID
- JSON type definition file for power junctions
- Placement in `ship_rooms.json` for the five panel rooms
- Markup `?name?` already implemented in description renderer
- Bridge-by-ID pattern — same as doors. Electrical system untouched.

**Electrical repair system**
- Panel-based repair: each power junction is the physical access point
- `electrical_repair_profiles.json` keyed by panel ID
- HV test kit required, lockout/tagout assumed (not modelled)
- Diagnose/repair commands extended to cover electrical components
- `electrical_repair.py` handler — separate from `door_panel_repair.py`
- Both import shared utilities from `repair_utils.py`
- See Section 23 for full design

**Fixed object repair**
- Engines and reactors repairable using same profile-driven pattern
- `Engine` class extended with repair state
- Power sources (reactors) treated as fixed objects for repair purposes
- `fixed_object_repair.py` handler

**Event system expansion**
- Add more event types: `solar_flare_event`, `reactor_overload_event`, `message_event`
- `randomise_damage` flag — pick N random components from affected_components list
- `randomise_time` flag — fire anywhere within a time window
- `event_effects` list for future room description changes and atmosphere breaches
- `_break_component_by_id()` TODO stubs: engine resolution, fixed object resolution

**Save/load system** — see Section 20
- Autosave only, JSON format, `savegame.json` in project root
- Full state: player, items, doors, panels, electrical, chronometer, events, logs
- Event system fired/resolved flags must be serialised — events must not re-fire after load

**Life support** — see Phase 20 notes
- Binary operational states driven by electrical system
- Temperature modelling
- Dynamic room descriptions based on power state

**Player survival mechanics** — see Section 18
- Hunger, thirst, fatigue, atmospheric survival
- Auto-chain threshold for long repairs — pause between components above N minutes

**Events + opening narrative**
- Banking hack, compliance message, friend contact (after ship control)
- Mainframe navigation lock
- Message event type delivery to datapad messages system

**Mainframe hack objective**
- Mainframe terminal hack mechanic
- Mainframe AI personality post-hack

**Going dark** — see Section 24
- Cargo barter, transponder obfuscator, hull camouflage, EVA

**Cargo movement**
- Sack barrow, cargo handler operational flag
- `cargo_handler_operational` on GameManager before this phase

**Terminal font**
- CRT panels (engineering, storage, cargo terminals) need a distinct font
- Share Tech Mono is the main UI font — CRT panels currently inherit it
- A more appropriate CRT/retro font to be selected and applied via `terminal.css`

**`command_handler.py`**
- Review `process()` method — preposition command blocks partially duplicate `_resolve_for_verb()` logic
- Targeted cleanup pass, not a split

---

## 15. FULL REPAIR SYSTEM (PHASE 18)

### Overview
A realistic multi-step repair system. Phase 18 scope is door panels. The architecture is generic — the same profile-driven logic applies to any future repairable object.

### Door panel type system
Each door connection in `door_status.json` carries a `panel_type` field. The type is looked up in `door_access_panel_types.json` which defines:
- `security_level` — integer used by all game logic (0=none, 1=low card, 2=high card, 3=high card+PIN)
- `manufacturer`, `model`, `description` — display text

Security level is resolved at load time from the type registry. It is not stored directly in `door_status.json`.

### Security levels
| Level | Type | Behaviour |
|-------|------|-----------|
| 0 | NONE | No card required — instant open/lock/unlock |
| 1 | KEYCARD_LOW | Low or high security card required |
| 2 | KEYCARD_HIGH | High security card required |
| 3 | KEYCARD_HIGH_PIN | High security card + PIN required |

### Panel repair state
```python
panel.is_broken           = True/False
panel.broken_components   = []
panel.diagnosed_components = []
panel.repaired_components  = []
```

### State machine
```
is_broken = False
  → panel is operational

is_broken = True, broken_components empty
  → diagnose: check diag tools + scan tool manual, timed action

is_broken = True, broken_components populated, unrepaired components remain
  → repair: check repair tools + all parts upfront, per-component timed action

repaired_components == broken_components
  → post-repair failure roll (stub — always succeeds for now), panel restored
```

### Repair profiles JSON
`data/repair/repair_profiles.json` — keyed by `panel_type`. Each profile defines `diag_tools_required`, `repair_tools_required`, and `components` with per-component `diag_time_mins` and `repair_time_mins`. Wire components use `length_m` instead of `qty`.

### Auto-chain
After each component repair, frontend automatically proceeds to next component after `REPAIR_COMPONENT_PAUSE_MS` pause. No player input required between components unless an event fires or parts/tools are missing.

### Post-repair failure roll
Hook exists — currently always succeeds. Future: probability-based failure, higher for complex repairs or missing manuals.

### Repair system architecture
The repair system is split across three files:

- `repair_handler.py` — thin dispatcher, routes `diagnose`/`repair` verbs to the correct sub-handler
- `door_panel_repair.py` — all door access panel logic (`DoorPanelRepairHandler`)
- `repair_utils.py` — shared pure utilities: `calc_repair_real_seconds`, `calc_diagnose_real_seconds`, `item_name`, `component_display_name`, `check_tools`, `format_duration`. Item registry loaded once at module import — no per-call disk I/O.

Future repair handlers (`electrical_repair.py`, `fixed_object_repair.py`) will follow the same pattern, importing from `repair_utils.py` and being routed from `repair_handler.py`.

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/command/diagnose_complete` | POST | Populates broken_components, returns diagnosis report |
| `/api/command/repair_complete` | POST | Consumes parts, marks component repaired |
| `/api/command/repair_next` | POST | Event check then next component repair |

---

## 16. KNOWN ISSUES / DEFERRED

- **PAM** — clips to utility belt. Dormant until life support phase.
- **Belt attachment mechanic** — utility belt accepts clipped attachments. Deferred until EVA phase.
- **Examine / look at command** — `examine <item>` prints name, manufacturer, model, and description to response panel. New verb in command handler. Deferred to quiet session. Note: examine on power junctions reads `description` from the `PowerJunction` object instance.
- **Terminal shutdown on power loss** — implemented for event-driven power cuts ✅. Edge case: power cut while mid-repair with terminal open — deferred.
- **Jack's internal monologue system** — currently hardcoded for terminal power cut only. Future: JSON-driven keyed response system (`monologue.json`) with keys like `terminal_power_failure`, `reactor_offline`, `hull_breach`. Ties into NPC dialogue tree system for mainframe AI, the friend, Ceres Base contact. Design considerations: tone variations based on game state, one-shot vs repeatable lines, character voice boxes with distinct colours per character.
- **Unpowered room images** — naming convention `roomname_unpowered.png` implemented and working. Recreation room complete. Remaining 16 rooms need unpowered variants generated in Reve alongside description authoring.
- **`^room_state^` token** — reserved for permanent room state changes triggered by events (hull breach visual etc.). Deferred until event effects system is built.
- **Dynamic room descriptions** — 16 rooms still need ~ italic prose, powered/unpowered addendums authored. Recreation room complete and is the reference example. Follow style guide.
- **Power junction placement** — recreation room complete. Four remaining rooms (engineering, main corridor, sub corridor, propulsion bay) need junctions added to fixed_objects and room descriptions.
- **Circuit diagram SVG** — being built manually in Inkscape. When complete, integrate into `[C] Circuit Diagram` in engineering terminal. Power junction tooltip panel_id provides the cross-reference link.
- **Repair post-repair failure roll** — hook exists, always succeeds. Future: probability-based failure chance.
- **Scan tool software updates** — future exotic systems require purchased scan tool updates.
- **Python built-in shadowing audit** — `id` and `type` used as parameter names in `__init__` methods, shadowing Python built-ins. Known affected: `electrical_system.py` (partially fixed on CircuitPanel), `interactable.py`, other model classes. Fix in dedicated cleanup pass.
- **CRT terminal font** — CRT panels currently inherit Share Tech Mono. A more appropriate retro/phosphor font to be selected and applied via `terminal.css`.
- **Event system save/load** — `GameEvent.fired` and `GameEvent.resolved` are in-memory only. Must be serialised in save file and restored after load to prevent events re-firing.
- **Event effects** — `event_effects` array in events.json is reserved but not implemented. Future: room description changes, atmosphere venting, narrative state changes.
- **Engine damage via events** — `_break_component_by_id()` has TODO stub for engine resolution.
- **`PalletContainer.pallet` flag** — purpose unclear, appears unused. Resolve before cargo movement phase.
- **Cargo contents** — `initial_cargo.json` containers currently empty.
- **Cargo handler operational flag** — `cargo_handler_operational` stub needed on GameManager before cargo movement phase.
- **Long repair auto-chain threshold** — repairs over N game minutes per component should pause. Implement when Phase 21 survival mechanics are built.
- **Repair failure mechanic** — when `panel_restored` is false, `Loop.setRepairInProgress(false)` must be called before presenting failure message.
- **`command_handler.py` process() cleanup** — preposition command blocks partially duplicate `_resolve_for_verb()` logic. Targeted cleanup pass deferred.
- **Room temperature** — deferred until life support is designed. Do not build on this.

### Input lockout behaviour — known inconsistency

**Terminal active** (`setTerminalMode`) — command input disabled, description panel
click handlers blocked via isTerminalSessionActive() checks, hover tooltips remain
active.

**Timed action active** (`Loop.lockInput`) — command input disabled, description
panel fully blocked via pointer-events: none, hover tooltips also disabled.

These behave differently as a result of how each was implemented rather than
intentional design. Whether they should be unified — and if so, which behaviour
is correct — is an open question for a future session.

### Recently completed deferred items
- ✅ **Wire length display** — `display_name()` method on `PortableItem` appends `(Xm)` for wire items.
- ✅ **Unique instance identifiers** — each placed item now receives a unique runtime `instance_id`.
- ✅ **`pick up <item> from <container>`** — preposition handling correctly routes `pick up` alongside `take`.
- ✅ **`take/pick up <item> from floor`** — floor now recognised as a valid source name.
- ✅ **Scan tool manual check** — missing manual shows corporate warning with Yes/No confirmation.
- ✅ **Inventory detail panel** — shows model + manufacturer. Store button in storage room.
- ✅ **Repair/diagnosis time scaling** — formula-based with config constants, 20s cap.
- ✅ **Progress counter on animations** — % counter on scan/repair/diagnosis animations.
- ✅ **Phase 19** — Storage room automated facility and cargo bay manifest fully implemented.
- ✅ **Codebase review and cleanup (April 2026)** — dead code removed, silent fallbacks eliminated, door action logic corrected, input locking hardened, ship log structured, messages stub fixed.
- ✅ **Electrical system expansion** — propulsion bypass, PNL-PRO-MAIN, power tracer multi-path, engine fixed objects, SVG map updates.
- ✅ **Event system (bare minimum)** — EventSystem, impact event, event strip, repairInProgress flag.
- ✅ **Electrical repair parts** — HV items authored, circuit breakers, wire gauges, storage quantity support.
- ✅ **File splits** — terminal.js → three files; repair_handler.py → three files.
- ✅ **Electrical service layer** — break_component/fix_component extracted to electrical_service.py.
- ✅ **Event system overhaul** — JSON-driven, generic component damage, door panel damage via events.
- ✅ **Description system overhaul** — token injection, colour scheme, Share Tech Mono, power junction markup.
- ✅ **Room description style guide** — Project_Orion_Room_Description_Style_v1.md.
- ✅ **PowerJunction FixedObject** — class, JSON, loader, tooltip, panel_id keywords, object_states.
- ✅ **~ italic markup** — atmospheric prose lines wrapped in ~ render italic, no markup parsing inside.
- ✅ **Addendum flash animation** — 8 second orange fade on power state change.
- ✅ **Unpowered room image swap** — currentRoomPowered tracking, _unpowered suffix image selection.
- ✅ **Terminal auto-close on power cut** — closes session, system response, Jack monologue box.
- ✅ **Jack's monologue box** — appendMonologue(), styled box, rounded corners, muted blue-grey italic.
- ✅ **Corridor rename** — CH-1/CH-2 references removed throughout all rooms and exits.
- ✅ **CircuitPanel description removed** — description field belongs on PowerJunction, not electrical component.

---

## 17. RULES FOR DEVELOPMENT

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
14. **All JSON fields have a use** — when creating instances from type definitions, load all fields. Never partially load type definitions.
15. **Suggest before adding** — if something seems missing from a spec, flag it as a suggestion before writing code or documentation
16. **Never output complete game.html or game.js — targeted changes only**

---

## 18. EVENT SYSTEM — DESIGN

### Overview
Two categories of events exist with different triggering mechanisms.

**Scheduled events** — triggered by game-time thresholds. Defined in `data/game/events.json`. Loaded at game start by `EventSystem.load_from_json()`. Currently implemented.

**Random events** — probability-based, checked periodically in the game loop. Not yet implemented.

### Event JSON structure
Events are defined in `data/game/events.json`. Each event has:

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
| `impact_event` | Breaks components in `affected_components` list | ✅ Implemented |
| `message_event` | Delivers message to datapad | Stub only |
| `solar_flare_event` | Future | Planned |
| `reactor_overload_event` | Future | Planned |

### Component damage resolution
`_break_component_by_id()` in `EventSystem` resolves each ID in `affected_components` in order:
1. Electrical components (cables, breakers, panels, power sources) via `electrical_service.break_component()`
2. Door panels — `panel.is_broken = True`
3. TODO: Engines — `engine.online = False` (when fixed object repair is built)
4. TODO: Fixed objects (when fixed object repair is built)
5. Not found — warning logged, no silent failure

### Event delivery
Events are delivered by the frontend poll — `loop.js` calls `/api/events/check` every 15 seconds when no timed action, repair chain, or PIN entry is in progress. After any event fires, `loadRoom()` is called to update the description addendum.

### Save/load consideration ⚠️
`GameEvent.fired` and `GameEvent.resolved` are in-memory only. Save/load must serialise these flags and restore them after `load_from_json()` — otherwise events re-fire after loading a save.

### Event effects (deferred)
The `event_effects` array is reserved for future side effects beyond component damage:
- Room description changes (hull breach visual)
- Atmosphere venting triggers
- Narrative state changes

### Technical implementation
- `EventSystem` in `backend/events/event_system.py`
- `electrical_service.py` in `backend/systems/electrical/`
- `/api/events/check` — frontend polls every 15 seconds
- Events loaded in `game_manager._init_events()` via `load_from_json()`

---

## 19. SHIP INVENTORY SYSTEM (PHASE 19)

### Storage room — automated storage facility

The storage room contains a single automated storage facility with integrated terminal. Stores repair consumables and crew consumables. No open/close state — items are logged to a manifest on GameManager, not physically placed in a room object.

**`game_manager.storage_manifest`** — dict keyed by `instance_id` → `PortableItem`. Populated at game init from the `storage_facility` section of `initial_ship_items.json`.

**Store** — contextual button on carried items in inventory panel, visible only when player is in the storage room. Calls `/api/game/storage/store`. No typed command.

**Retrieve** — button on highlighted item in storage terminal. Calls `/api/game/storage/retrieve`. Keyboard shortcut `[R]` also works. No typed command.

**Terminal display** — grouped by `display_name()`, showing quantity. Items with different wire lengths are listed separately. Sorted alphabetically. Arrow key navigation with auto-scroll.

**API endpoints:**
- `GET /api/game/storage/manifest` — returns grouped manifest for terminal display
- `POST /api/game/storage/store` — stores item by instance_id
- `POST /api/game/storage/retrieve` — retrieves single item by instance_id

### Cargo bay — freight space

The cargo bay is a freight space. Cargo is pre-loaded by Enso VeilTech logistics before the game starts. The manifest is read-only. There is no automated storage facility in the cargo bay.

**`game_manager.cargo_manifest`** — dict with `containers` and `pallets` lists. Loaded at game init from `initial_cargo.json`. Type definitions from `cargo_containers.json` and `pallet_platforms.json` are merged into each instance at load time.

**Cargo bay terminal** — read-only manifest display. Columns: Container (EVT reference), Type, Contents. Sorted small → medium → large → pallet. Arrow key navigation. No retrieve button.

**Manifest display rules:**
- All containers shown (empty or not)
- Pallets shown only if they have `attached_items` (items strapped directly, not stacked containers)
- Pallets with only stacked containers — not shown

**API endpoint:**
- `GET /api/game/cargo/manifest` — returns full cargo_manifest dict

### Interactable class hierarchy (Phase 19 additions)

```
Interactable
├── PortableItem
│   └── UtilityBelt
├── FixedObject
│   ├── StorageUnit
│   │   └── PalletContainer  ← moveable cargo container
│   ├── Surface
│   │   └── Pallet           ← moveable pallet platform
│   └── Terminal
```

**PalletContainer** — subclass of StorageUnit. Moveable by equipment. Not player-carriable. Attributes: `container_size` (small/medium/large), `movement_equipment`, `stacks_on`, `moveable = True`.

**Pallet** — subclass of Surface. Moveable by cargo handler only. Items strap directly to it (`attached_items`). Attributes: `movement_equipment = 'cargo_handler'`, `stacks_on = []`, `moveable = True`.

### Container and pallet type definitions

**`cargo_containers.json`** — type definitions for `PalletContainer`. Key fields: `id`, `type_name`, `description`, `keywords`, `container_size`, `movement_equipment`, `capacity_mass`, `stacks_on`.

**`pallet_platforms.json`** — type definitions for `Pallet`. Key fields: `id`, `type_name`, `description`, `keywords`, `movement_equipment`, `stacks_on`.

Note: `type_name` is distinct from the instance `name` field (EVT reference). Both exist without collision. All type definition fields are merged into instances at load time — no fields are discarded.

### Container dimensions

| Type | Dimensions | Movement | Stacking |
|------|-----------|----------|---------|
| Small container | 750x600x900mm | Sack barrow or cargo handler | Stacks on pallets and other containers |
| Medium container | 750x1200x900mm | Cargo handler only | Stacks on pallets and large containers |
| Large container | 1500x1200x900mm | Cargo handler only | Does not stack |
| Single pallet | 1500x1200x150mm | Cargo handler only | Base unit |
| Double pallet | 3000x1200x150mm | Cargo handler only | Base unit |

4 small containers or 2 medium containers fit on a single pallet. 8 small or 4 medium on a double pallet.

### Instance data — initial_cargo.json

Each container instance carries: `instance_id`, `name` (EVT reference), `type_id`, `room_id`, `stacked_on`, `contents`.
Each pallet instance carries: `instance_id`, `name`, `type_id`, `room_id`, `attached_items`.

`stacked_on` references either a pallet `instance_id` (accessible) or another container `instance_id` (requires cargo handler). `room_id` tracks current location — updated when Jack moves a container.

### Deferred to Phase 25 — cargo movement
- Sack barrow mechanic for moving small containers between rooms
- `cargo_handler_operational` flag on GameManager
- Stacking accessibility check: stacked on pallet → accessible; stacked on container → cargo handler required

### Deferred to Phase 23 — cargo contents
- Cargo contents in `initial_cargo.json` containers currently empty
- Narrative cargo manifest to be authored when trading phase is designed
- Cargo handler item definition and repair profile

---

## 20. SAVE / LOAD SYSTEM — DESIGN ⚠️ NEEDS FURTHER DISCUSSION

### Philosophy
No scum saving. No reloading. When you die, you are dead.

### Splash screen
- **New Game** — greyed out if a save file exists
- **Continue** — greyed out if no save file exists

### Save triggers — autosave only
- Room change
- After any timed action completes
- On clean quit

### Death state
Save file written with `dead: true` flag. Continue shows death screen. Only New Game available.

### Self-termination ⚠️ NEEDS FURTHER DISCUSSION
Multi-step auto-destruct sequence spread across multiple rooms. Airlock spacing as an alternative method. Both write the dead save state identically.

### Save file scope
Player state, portable item positions, door states, panel states, electrical system state, ship time, instance ID counters, cargo manifest state, storage manifest state, dead flag.

---

## 21. TABLET, SHIP'S LOG AND MESSAGES — DESIGN

### The Tablet
Portable handheld device. When in inventory, TAB tab appears. Shows: ship power map, circuit diagram, diagnostic/repair notes, ship's log, messages. Works on own battery — functions in unpowered rooms.

### Diagnostic/Repair Notes
Auto-created when diagnosis completes and tablet is in inventory. Snapshot in time — does not update dynamically. Replaced if panel re-diagnosed. Marked ARCHIVED when repair completes.

### Ship's Log
Permanent timestamped record. Logs: game start, diagnosis, repairs, events, power changes, security events, player death.

Log entries are structured dicts with the following fields:
- `timestamp` — ship time string at time of entry
- `event` — short event label (e.g. "Diagnosis complete", "Repair complete")
- `location` — location string, present on diagnosis and repair entries only (e.g. "Location: Crew Cabin | Main Corridor door panel Model Name")
- `detail` — detail string (e.g. "Faults: component1, component2" or "Components Replaced: component1")

The `location` field is optional — future log entry types that have no location simply omit it. The frontend renderer checks for its presence before rendering.

### Messages System
Narrative delivery mechanism. Distinct from ship's log. Types: automated ship alerts, external communications, narrative events.

---

## 22. NARRATIVE — JACK HARROW AND ENSO VEILTECH

### Jack Harrow — starting situation
Jack Harrow is an Enso VeilTech employee operating the Tempus Fugit as a solo trader/courier. He is currently in deep space, returning from a long haul run, in hypersleep.

### The opening sequence
1. Impact event wakes Jack early. Ship has damage.
2. Three messages waiting: bank (account terminated, blacklisted), Enso VeilTech compliance (return ship, 72 hours), the friend (don't comply, hack the mainframe, Ceres Base contact).
3. Mainframe processes compliance order, locks navigation course.
4. Player must hack the mainframe. First major non-repair objective.

### Enso VeilTech — the invisible antagonist
Never a villain in the traditional sense. Complete institutional indifference. Automated systems. Templated responses. Employee 7,341,892 is a line item.

### Key decisions still to make ⚠️
- The friend's identity, backstory, and name
- The Ceres Base contact's name and personality
- The mainframe AI's name and personality post-hack
- Exact wording of the bank email and Enso VeilTech compliance message
- The 72-hour countdown mechanic in gameplay terms

---

## 23. ELECTRICAL SYSTEM REPAIR — DESIGN

### Overview
The same diagnose/repair gameplay used for door panels extends to the ship's electrical system. Key differences: HV test kit required, lockout/tagout safety assumed (not modelled), electrical components accessed via their owning circuit panel.

### Fault causes
Electrical faults are always caused by game events — never random at diagnosis time. Events: micrometeorite impact (severs cables), power surge (trips/destroys breakers), age/general failure.

### The HV Test Kit
Specialist tool for all electrical diagnosis and repair. Cannot be substituted with scan tool. Contains HV rated PPE, HV multimeter, megohmmeter, lockout tags. Item ID: `hv_service_kit`.

### Lockout / Tagout procedure
800V DC is lethal. Lockout/tagout is assumed to be performed correctly — not modelled as a gameplay mechanic. The HV service kit description references lockout hardware. Attempting to work on live systems is not currently modelled — future consideration.

### Panel-based repair access
Each circuit panel is a physical repair location. Jack must be in the panel's room to diagnose and repair. Each panel owns:
- The panel itself
- All breakers in that panel
- All cables on either side up to the next panel or power source

### Repair profiles
`data/repair/electrical_repair_profiles.json` — keyed by panel ID. Each profile lists all owned components with diagnosis/repair times and required parts.

**Component types and parts:**

| Type | Parts required |
|------|---------------|
| Breaker | 1x matching amp-rated circuit breaker |
| Cable (standard) | `wire_hv_standard` by length + 2x `hv_connect_standard` |
| Cable (heavy duty) | `wire_hv_heavy_duty` by length + 2x `hv_connect_heavy` |
| Panel | 1x `hv_logic_board` + 1x `hv_bus_bar` (+ possible breakers for severe failure) |
| Power sources | Out of scope — handled by fixed object repair system |

**Heavy duty cables** (reactor feeds and bypass path):
`PWC-ENG-01`, `PWC-PRO-01`, `PWC-PRO-04`, `PWC-ENG-00`, `PWC-PRO-02`, `PWC-PRO-03`

**Circuit breaker sizes:**
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
- Panel failure severity randomisation — event sets damage level, profile defines max parts
- Repair profiles need cable length_m added to electrical.json first

---

## 24. GOING DARK — SHIP DISGUISE AND BARTER (PHASE 23)

### Two layers of disguise
**Physical hull camouflage** — bolt-on external modifications. Requires EVA to install — unlocks EVA gameplay phase.

**Transponder obfuscator** — spoofs ship identification signal. Illegal. Underground source only. Requires barter.

### Paying for it — the cargo
The cargo represents Jack's only negotiating currency. Some items easily moved, some dangerous or sensitive, some of questionable origin. The cargo manifest is a narrative device.

### Key design decisions still to make ⚠️
- The cargo manifest contents — what is Jack actually carrying, and what secrets does it contain?
- The new ship name and identity
- EVA mechanics detail — suit duration, oxygen limits, hull attachment

---

## 25. PROJECT BACKGROUND — HOW THIS CAME TO BE

*The following was written by the lead designer during a development session in April 2026.*

"I have limited coding knowledge, mainly Python, with a little exposure to javascript, html, css but I am no accomplished programmer. My skills are in logical thought processes, multiple years of real life mechanical repair/diagnosis and an ability to look into what future changes could impact the current codebase which enables a certain amount of 'if we do this, we may need to make allowances for what a future phase may require'.

The development process has been organic, some has been planned for, but certainly not from day one. This is where the design docs are vital.

I am the lead designer, however virtually all coding is done by AI, my coding input has been minimal. The project started from several small projects aka feature experiments eg the electrical system and the typewriter terminal effects. Some experiments didn't work out such as the life support logic so this will need revisiting until I am happy with the result.

This project would never have got to this state without the various AI's (starting with Grok, the SuperGrok, then Sonnet 4.5 and now Sonnet 4.6) and of course it also would not have got to this state without my input, design ideas and constant questions and debates between myself and the AI's such as yourself."

### Summary
- Started as a series of feature experiments
- Development has been organic rather than fully planned from day one
- The lead designer has limited formal programming background, strong logical thinking, real-world mechanical diagnosis and repair experience, and a particular ability to anticipate how current decisions affect future phases
- Virtually all code is AI-generated, directed and reviewed by the lead designer
- Development has progressed through several AI collaborators: Grok, SuperGrok, Claude Sonnet 4.5, Claude Sonnet 4.6

---

*Project Orion Game Design Document v22.0*
*April 2026*
