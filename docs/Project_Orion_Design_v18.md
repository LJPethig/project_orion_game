# PROJECT ORION GAME
## Space Survival Simulator
### Master Design & Development Document
**Version 18.0 — April 2026**

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
- Fixed object data structure: terminals, storage units, surfaces ✅
- Description panel: markup parser, hover tooltips, click handlers, Layer 2/3 ✅
- Container commands: open, close, look in, take from, put in, put on ✅
- Equip/unequip commands: wear, equip, remove, take off, unequip ✅
- Floor fallback: items drop to floor when no surface available ✅
- `take/pick up <item> from floor` — floor recognised as valid source ✅
- Player inventory screen: slide-out panel, equipped slots, carried items, actions ✅
- Inventory detail panel: model + manufacturer shown instead of name + weight ✅
- Inventory selection preserved after drop/remove ✅
- Smart command parser: ID resolver, verb conflict resolution, clarification system ✅
- Item registry: unique instances per placement, unique runtime instance_id per item ✅
- Terminal system: CRT styling, typewriter, keypress nav, sub-menus, terminal mode lockout ✅
- Electrical system: reactor, panels, breakers, cables, batteries, power tracing ✅
- Electrical integrated into gameplay: door panels and terminals check room power ✅
- Engineering terminal: Technical Data, Electrical sub-menu (Power Status map, Circuit Diagram placeholder) ✅
- Debug console: Ctrl+D, break/fix commands, live map refresh ✅
- Full repair system: diagnose + repair commands, scan tool manual validation, per-component repair, wire consumption by length, auto-chain, event hook ✅
- Repair/diagnosis real-time scaling: formula-based with config constants, 20s cap ✅
- Diagnosis timing: based on actual failed components + 25% access overhead + ±10% jitter ✅
- Diagnosis response: formatted duration, failed components, required tools, missing items ✅
- Progress counter (%) on all timed action animations ✅
- Door panel type system: panel_type field, door_access_panel_types.json, security level resolved at load time ✅
- Security level 0 panels: no card required, instant lock/unlock ✅
- Item manufacturer/model fields: all items carry manufacturer, model, description with character ✅

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
│   │   ├── game_manager.py        ← owns electrical_system instance, check_for_event() stub
│   │   ├── ship.py
│   │   ├── room.py
│   │   ├── door.py                ← panel_type, security_level resolved at load time
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
│   │   ├── door_handler.py        ← security level 0 instant open/lock/unlock
│   │   ├── repair_handler.py      ← diagnose + repair, profile-driven, per-component
│   │   ├── item_handler.py
│   │   ├── container_handler.py
│   │   ├── equip_handler.py
│   │   └── terminal_handler.py
│   │
│   ├── loaders/
│   │   └── item_loader.py         ← mixed format placements, computed wire mass
│   │
│   └── api/
│       ├── game.py
│       ├── command.py             ← diagnose_complete, repair_complete, repair_next endpoints
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
│       │   │   ├── constants.js   ← DOOR_IMAGE_DISPLAY_MS, REPAIR_COMPONENT_PAUSE_MS
│       │   │   ├── api.js
│       │   │   └── loop.js
│       │   └── screens/
│       │       ├── splash.js
│       │       ├── ui.js          ← appendRepairMessage(), showDiagnosisAnimation()
│       │       ├── commands.js    ← diagnose_panel, repair_component, repair_complete handlers
│       │       ├── description.js
│       │       ├── inventory.js
│       │       ├── terminal.js
│       │       └── game.js        ← debug console (Ctrl+D)
│       └── images/
│           ├── rooms/
│           ├── doors/
│           └── ship_layout.svg
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
    │   └── engineering.json
    ├── repair/
    │   └── repair_profiles.json   ← repair profiles keyed by panel_type
    └── ship/
        ├── structure/
        │   ├── ship_rooms.json
        │   ├── door_status.json               ← panel_type per connection
        │   ├── door_access_panel_types.json   ← panel type registry, security levels
        │   ├── initial_ship_state.json
        │   ├── initial_ship_items.json
        │   └── player_items.json
        └── systems/
            └── electrical.json
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
CARD_SWIPE_GAME_MINUTES   = 0

# Repair/diagnosis real-time scaling
# real_seconds = REPAIR_TIME_BASE + (game_minutes / REPAIR_TIME_PIVOT) * REPAIR_TIME_SCALE
# capped at REPAIR_TIME_CAP
REPAIR_TIME_BASE_SECONDS  = 8
REPAIR_TIME_SCALE_SECONDS = 8
REPAIR_TIME_PIVOT_MINUTES = 30
REPAIR_TIME_CAP_SECONDS   = 20

# Diagnosis time modifiers
DIAG_ACCESS_OVERHEAD      = 0.25  # 25% of component diag time added for panel access
DIAG_TIME_JITTER          = 0.10  # ±10% random variation on diagnosis time

ROOMS_JSON_PATH           = 'data/ship/structure/ship_rooms.json'
DOORS_JSON_PATH           = 'data/ship/structure/door_status.json'
DOOR_PANEL_TYPES_PATH     = 'data/ship/structure/door_access_panel_types.json'
INITIAL_STATE_JSON_PATH   = 'data/ship/structure/initial_ship_state.json'
SHIP_ITEMS_JSON_PATH      = 'data/ship/structure/initial_ship_items.json'
PLAYER_ITEMS_JSON_PATH    = 'data/ship/structure/player_items.json'
REPAIR_PROFILES_PATH      = 'data/repair/repair_profiles.json'
ITEM_FILES = [
    'data/items/tools.json',
    'data/items/wearables.json',
    'data/items/misc_items.json',
    'data/items/consumables.json',
]
TERMINALS_JSON_PATH     = 'data/items/terminals.json'
STORAGE_UNITS_JSON_PATH = 'data/items/storage_units.json'
SURFACES_JSON_PATH      = 'data/items/surfaces.json'
TERMINAL_CONTENT_PATH   = 'data/terminals'
ELECTRICAL_JSON_PATH    = 'data/ship/systems/electrical.json'
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
| `--col-portable` | `#bea5cd` | Purple — portable items, surfaces with items, repair components/tools |
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

### Deferred inventory improvements
- Item display in inventory screen needs `manufacturer` and `model` shown alongside description
- Inventory screen should auto-close when player initiates a door action (swipe, PIN, repair) so door/panel imagery is visible

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
- `manufacturer` — company name (e.g. "Enso VeilTech", "Tengu Cables", "SMC Nova")
- `model` — model or part number (e.g. "VT-7 SmartDiag PLUS", "H05V-K", "TS1500")
- `description` — written with character, not generic. Include manufacturer, model, condition where appropriate.

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
- Phase 18: `["Vesper Control U-LOCK Access Panel", "SMC Nova TS1500 Security Door Panel", "SMC Nova Q-Emerald Security Door Panel"]`
- These strings must match the `model` field in `door_access_panel_types.json` exactly
- Expandable as new system manuals are added or purchased

### initial_ship_items.json — mixed placement format
Supports both simple string (standard instantiation) and dict (instance attribute overrides):

```json
{
  "container_id": "engineering_large_parts_storage_unit",
  "items": [
    "electrical_service_kit",
    {"id": "wire_low_voltage", "length_m": 12.5},
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

### Power integration in gameplay
- **Door panels** — all doors require powered panel to operate. Unpowered: offline message, no door image shown.
- **Terminals** — terminal access blocked if room unpowered.
- **Hover tooltips** — exits show Offline state in orange when unpowered.
- **Description refresh** — `refreshDescription()` updates both `currentExits` and `currentObjects` immediately after break/fix.

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/systems/electrical/status` | GET | Full system status including room_power map |
| `/api/systems/electrical/room/<id>` | GET | Single room power check |
| `/api/systems/electrical/break/<id>` | POST | Break any component by ID |
| `/api/systems/electrical/fix/<id>` | POST | Fix any component by ID |

### Engineering terminal — electrical sub-menu
- **[P] Power Status** — ship layout SVG with live room colours (green=powered, red=unpowered).
- **[C] Circuit Diagram** — wiring diagram SVG (being built manually in Inkscape). Static reference — no live power colouring.

### Debug console
- `Ctrl+D` toggles debug panel in game
- `break <component_id>` / `fix <component_id>` — electrical components only
- Door panel breaking for testing is done via `initial_ship_state.json`

### Key files
- `data/ship/systems/electrical.json`
- `backend/systems/electrical/electrical_system.py`
- `backend/api/systems.py`
- `backend/handlers/base_handler.py`
- `frontend/static/images/ship_layout.svg`
- `frontend/static/js/screens/terminal.js`

---

## 14. BUILD PLAN — NEXT PHASES

### Phase 18 — Full repair system (COMPLETE)
See Section 15.

### Phase 19 — Ship inventory + cargo
- Ship inventory manifest via storage terminals
- Cargo bay trading items
- `PortableContainer` (moveable crate) — floor only
- Note: ship inventory is NOT a global item manifest. Terminal-managed cataloguing specific to cargo bay and storage room only.

### Phase 19.5 — Save / Load system (see Section 20)
- Single autosave, no player-controlled saving
- Autosave triggers: room change, timed action complete, clean quit
- Splash screen: New Game / Continue — mutually exclusive based on save state
- Death permanently flags the save — Continue shows death screen, only New Game available

### Phase 19.6 — Tablet + Ship's Log + Messages system (see Section 21)
- Portable tablet tool — TAB tab visible when in inventory
- Ship power map and circuit diagram accessible from tablet
- Automatic diagnostic/repair notes with timestamp and location
- Notes archived automatically when repair is complete
- Ship's log — events, diagnosis, repairs
- Messages system — narrative delivery, accessible from terminals and tablet

### Phase 20 — Life support
- Binary operational states driven by electrical system
- Temperature modelling — open/closed doors, room volume, HVAC
- Dynamic room descriptions based on power state

### Phase 21 — Events system + opening narrative (see Sections 18 and 22)
- Banking hack opening event — delivered via messages system
- Enso VeilTech compliance message
- Friend's warning message
- Mainframe navigation lock event
- Random and scheduled event architecture
- Player survival mechanics

### Phase 22 — Mainframe hack objective
- Mainframe terminal hack mechanic
- Mainframe AI personality post-hack
- Ceres Base navigation objective

### Phase 23 — Going dark (see Section 24)
- Cargo inventory and barter — liquidate Enso VeilTech cargo through underground contacts
- Ship transponder obfuscator — illegal device, underground source only
- Physical hull camouflage — bolt-on parts changing the Tempus Fugit's visual profile
- EVA required for external hull work — unlocks EVA gameplay phase
- New ship identity established

### Phase 24 — Electrical system repair (see Section 23)
- HV test kit — specialist tool for electrical diagnosis
- Lockout/tagout procedure using breaker locked_out attribute
- diagnose/repair commands extended to cover electrical components
- Reactor integral main isolator breaker

### Phase 25+ — Navigation, trading, further narrative...

---

## 15. FULL REPAIR SYSTEM (PHASE 18)

### Overview
A realistic multi-step repair system. Phase 18 scope is door panels. The architecture is generic — the same profile-driven logic applies to any future repairable object.

### Door panel type system
Each door connection in `door_status.json` carries a `panel_type` field (e.g. `vesper_ulock`, `smc_ts1500`, `smc_q_emerald`). The type is looked up in `door_access_panel_types.json` which defines:
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

### The Scan Tool
Central diagnostic instrument. Key special field:
- `installed_manuals` — list of human-readable panel model names the scan tool can service
- Must match `model` field in `door_access_panel_types.json` exactly
- Expandable — future exotic systems require purchased scan tool updates

### Repair commands
Two separate commands. Diagnosis and repair are distinct activities:
- `diagnose <panel>` — runs diagnosis stage only. Fails if already diagnosed.
- `repair <panel>` — runs repair stage only. Fails if not yet diagnosed.

### Panel repair state (on SecurityPanel)
```python
panel.is_broken           = True/False
panel.broken_components   = []   # component item_ids — set by scan tool diagnosis
panel.diagnosed_components = []  # electrical only — scan tool verification
panel.repaired_components  = []  # component item_ids successfully replaced
```

For door panels: `broken_components` is populated by the scan tool during diagnosis (not at break time). The player does not know what is broken until they diagnose.

For electrical components: `broken_components` is set by the event that caused the failure. The scan tool verifies (confirmatory, not investigative).

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
`data/repair/repair_profiles.json` — keyed by `panel_type`. Each profile:

```json
{
  "vesper_ulock": {
    "diag_tools_required": ["scan_tool", "power_screwdriver_set"],
    "repair_tools_required": ["scan_tool", "power_screwdriver_set", "electrical_service_kit", "laser_solderer"],
    "components": [
      {"item_id": "u-lock_door_logic_board", "qty": 1, "diag_time_mins": 5, "repair_time_mins": 15},
      {"item_id": "wire_low_voltage", "length_m": 0.5, "diag_time_mins": 3, "repair_time_mins": 8}
    ]
  }
}
```

Wire components use `length_m` instead of `qty`. All other components use `qty`.

### Repair flow — detailed

**Diagnosis (`diagnose <panel>`)**
1. Check `diag_tools_required` — if missing, return structured response listing missing tools
2. Check scan tool `installed_manuals` contains panel `model` — if not, display corporate warning message in orange with Yes/No confirmation. Player may proceed without correct manual but risks higher post-repair failure probability (future).
3. Timed action begins (sum of `diag_time_mins` for all profile components)
4. On complete: randomly select 1–3 broken components (weighted toward fewer), populate `broken_components`
5. Return structured response: panel model, failed components (purple), repair tools required (purple)

**Repair (`repair <panel>`)**
1. Check all missing tools and all missing parts across all remaining unrepaired components upfront
2. If anything missing — return single structured response listing all missing tools and parts
3. If everything present — begin timed action for next unrepaired component only
4. On complete — consume parts, mark component repaired, auto-chain to next component after `REPAIR_COMPONENT_PAUSE_MS`
5. Between components — `check_for_event()` is called. If event fires, return event instead of next repair
6. When `repaired_components == broken_components` — post-repair failure roll (stub), panel restored

### Wire consumption
One spool must have sufficient `length_m` — no combining across multiple spools. On consumption: `spool.length_m` decremented, `spool.mass` recomputed from `length_m * mass_per_metre`.

### Auto-chain
After each component repair, frontend automatically proceeds to next component after `REPAIR_COMPONENT_PAUSE_MS` pause (configurable in `constants.js`). No player input required between components unless an event fires or parts/tools are missing.

### Post-repair failure roll
Hook exists in `complete_component_repair()` — currently always succeeds. Future: probability-based failure, higher for complex repairs or missing manuals. On failure: panel powers up briefly then dies, `is_broken` stays `True`, all repair state cleared, fresh diagnosis required.

### Repair system architecture — future refactor
When a second repairable type is added (machinery, life support):
- Common logic (`_check_tools`, `_check_all_parts`, `_consume_parts`, `_item_name`, calc functions) extracted to `repair_utils.py`
- `repair_handler.py` stays as door panel handler, imports from `repair_utils.py`
- New handler (e.g. `machinery_repair_handler.py`) also imports from `repair_utils.py`
- `repair` verb in `command_handler.py` routes to correct handler based on what's in the room

### Repair timing — future work
`REPAIR_REAL_SECONDS` and `DIAGNOSE_REAL_SECONDS` in `config.py` are temporary stubs returning fixed values. When properly implemented:
- `calc_repair_real_seconds(game_minutes)` and `calc_diagnose_real_seconds(game_minutes)` in `repair_handler.py` implement proper scaling with a cap
- Very long repairs (48hrs game time) should not require proportionally long real-time waits
- Delete the config stubs when real scaling is implemented

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/command/diagnose_complete` | POST | Populates broken_components, returns diagnosis report |
| `/api/command/repair_complete` | POST | Consumes parts, marks component repaired |
| `/api/command/repair_next` | POST | Event check then next component repair |

### Key files
- `data/repair/repair_profiles.json`
- `data/ship/structure/door_access_panel_types.json`
- `data/ship/structure/door_status.json`
- `backend/handlers/repair_handler.py`
- `backend/models/door.py`
- `backend/api/command.py`
- `frontend/static/js/screens/ui.js` — `appendRepairMessage()`
- `frontend/static/js/screens/commands.js` — action type handlers
- `frontend/static/js/core/constants.js` — `REPAIR_COMPONENT_PAUSE_MS`

---

## 16. KNOWN ISSUES / DEFERRED

- **PAM** — clips to utility belt. Dormant until life support phase.
- **Belt attachment mechanic** — utility belt accepts clipped items. Deferred until EVA phase.
- **Examine / look at command** — `examine <item>` prints name, manufacturer, model, and description to response panel. New verb in command handler. Deferred to quiet session.
- **Terminal shutdown on power loss** — if power is lost to a room while the terminal is active (via game events), the terminal should close immediately. Implement when event system is built.
- **Dynamic room descriptions** — static prose needs electrical atmosphere removed. A power-state description layer (dark/silent when unpowered, atmospheric when powered) is planned for Phase 20.
- **Circuit diagram SVG** — being built manually in Inkscape. When complete, integrate into `[C] Circuit Diagram` in engineering terminal.
- **Repair post-repair failure roll** — hook exists, always succeeds. Future: probability-based failure chance, higher for complex repairs or missing manuals.
- **Scan tool software updates** — future exotic systems require purchased scan tool updates. Not yet implemented.
- **Description panel click lockout during timed actions** — container, surface, terminal and floor item clicks in the description panel should be suppressed when Loop.isLocked() is true (during diagnosis, repair, card swipe). Currently only isTerminalSessionActive() is checked. Add Loop.isLocked() check to all click handlers in description.js.
- **Ship power map reset key** — add a key (e.g. [0]) that resets the map to initial zoom and position (_mapPanX = 0, _mapPanY = 0, _mapScale = 0.35). Apply to both the datapad power map and the engineering terminal power map.
- **Ship power map hover tooltips** — hovering over rooms, reactors, and batteries on the SVG map should show status information (powered/unpowered, reactor output, battery charge percentage). Applies to both terminal and datapad map views.
- **Codebase size and structure analysis** — before Phase 23 (electrical system repair), do a full review of all backend and frontend files for size, cohesion, and split candidates. Known targets: repair_handler.py (shared utilities → repair_utils.py), command_handler.py (growing verb registry), game.py (API routes may need splitting as endpoints multiply). Frontend: terminal.js is already large and will grow when mainframe terminal is built.

### Recently completed deferred items
- ✅ **Wire length display** — `display_name()` method on `PortableItem` appends `(Xm)` for wire items.
- ✅ **Unique instance identifiers** — each placed item now receives a unique runtime `instance_id`.
- ✅ **`pick up <item> from <container>`** — preposition handling correctly routes `pick up` alongside `take`.
- ✅ **`take/pick up <item> from floor`** — floor now recognised as a valid source name.
- ✅ **Scan tool manual check** — missing manual shows corporate warning with Yes/No confirmation.
- ✅ **`display_name()` in all response messages** — wire length shown correctly everywhere.
- ✅ **resolver_debug.log** — logger removed, log file deleted.
- ✅ **Inventory screen auto-close** — closes when door/panel imagery is shown.
- ✅ **Inventory detail panel** — shows model + manufacturer instead of name + weight. Model styled as headline.
- ✅ **Inventory selection preservation** — selection moves to next logical item after drop/remove.
- ✅ **`refreshExits()` renamed** — to `refreshDescription()` across all call sites.
- ✅ **Repair/diagnosis time scaling** — formula-based with config constants, 20s cap. Stubs removed.
- ✅ **Diagnosis timing refactor** — broken components selected before timer starts. Time based on actual faults + 25% access overhead + ±10% jitter.
- ✅ **Diagnosis response format** — formatted duration, failed components, required tools, missing items listed separately.
- ✅ **Progress counter on animations** — % counter on scan/repair/diagnosis animations.

---

## 17. RULES FOR DEVELOPMENT

1. **Upload current files at start of every session** — never work from memory
2. **Read the code before changing it** — ask to see files before editing
3. **Complete files for large changes, inline instructions for small ones**
4. **New functions — give as instructions to append, not complete files**
5. **Minimal targeted changes** — no "while I'm in here" improvements without asking
6. **Only create what we need right now**
7. **No god files** — grouped logically by domain
8. **Backend owns all game state** — JS is display only
9. **All colours in CSS variables**
10. **All JS timeouts in `constants.js`**
11. **All Python durations in `config.py`**
12. **No silent fallbacks** — missing data must crash loudly, not degrade silently
13. **Debate bad ideas** — push back if something seems wrong
14. **Never add "type X to fix it" hints** — immersive messages only
15. **One change at a time — verify before proceeding**
16. **Never output complete game.html or game.js — targeted changes only**

---

## 18. EVENT SYSTEM — DESIGN (PHASE 21)

### Overview
The event system introduces in-game occurrences that interrupt normal play, advance narrative, and enforce survival mechanics. Two categories of events exist with different triggering mechanisms.

### Event categories

**Random events** — probability-based, checked periodically in the game loop. Examples: micrometeorite impacts causing ship damage, electrical faults, system failures. Probability tunable per event type. These can fire at any time.

**Scheduled events** — triggered by game-time thresholds. Examples: hunger, thirst, fatigue, atmospheric exposure. These fire at predictable intervals regardless of what the player is doing. Long repairs (48hrs+ of game time) will be interrupted multiple times by survival needs.

### Event interruption during repairs
`check_for_event()` is called in `game_manager.py` between each component repair via the `/api/command/repair_next` endpoint. If an event fires, it is returned instead of the next repair action. The player deals with the event and then resumes repair by typing `repair <panel>` again.

Diagnosis is atomic — events cannot interrupt mid-diagnosis. Events can only interrupt between component replacements during repair.

### Player survival mechanics (to be implemented in Phase 21)
The player class will be expanded with persistent survival state, all ticking against game time:
- **Hunger** — must eat at regular intervals. Failure: degrading performance, eventually death.
- **Thirst** — must drink at regular intervals. Failure: degrading performance, eventually death.
- **Fatigue** — must rest/sleep. Sleep deprivation causes errors, hallucinations, death.
- **Atmospheric survival** — when life support is built: breathable air, correct temperature range, correct pressure all required. Failure at any point is fatal.

These are not optional inconveniences — they are core to the "if the ship dies, you die" philosophy, extended to "if Jack dies, you die."

### Opening sequence event — "Account Terminated"
Fires shortly after game start. The player is woken early from hypersleep by an impact event (ship damage — serious but not immediately critical). Upon accessing the ship's message system, they discover messages waiting from while they were in stasis.

**Message 1 — The bank (3 months old):**
The bank's quantum encryption system was hacked. The email is written in pure corporate indifference — no apology, no explanation, no recourse. Key details:
- Account balance set to zero by the hack
- Bank treats zero balance as a breach of contract
- Account terminated forthwith
- Player's quantum ID blacklisted across all financial institutions (effectively permanent)
- Compounded interest has been accruing on the account closure fee for the 90 days since termination
- The blacklist was already ancient history in the bank's system by the time the player reads it

**Message 2 — Enso VeilTech Compliance (recent, triggered by the blacklist):**
Automated. Terse. The compliance system has flagged Jack Harrow as financially blacklisted. Per Enso VeilTech employment contract Section 4 subsection 2a, continued operation of company assets requires a clean financial record. Jack is instructed to set course for the nearest Enso VeilTech authorised facility, surrender the Tempus Fugit, and report in person to face financial default proceedings. Failure to comply within 72 hours will result in remote lockdown of the vessel and escalation to Enso VeilTech Security Division.

**Message 3 — The friend (recent, urgent):**
Informal. Worried. They've heard what happened — news travels fast even in deep space. Do NOT go to Enso VeilTech. Do NOT let the mainframe set that course. The mainframe is running Enso VeilTech navigation compliance software — it will lock the course automatically if it processes the compliance order. Hack the mainframe first. There's someone on Ceres Base who can install clean software — ask for [Name TBD]. They can also help with parts and supplies, no questions asked, no financial record required. Get there before the 72 hours are up.

**The mainframe's response:**
Shortly after the compliance message is processed, the mainframe (running Enso VeilTech software) logs a navigation compliance event and attempts to set course for the nearest Enso VeilTech facility. The player receives a ship's log entry and a mainframe alert. The ship is trying to take itself home.

**The hack objective:**
The player must reach the mainframe terminal and hack it — installing replacement software provided by the contact on Ceres Base (or obtained by other means). Until the hack is complete, the mainframe is an obstacle. After the hack, the mainframe becomes an ally — a ship AI that is now loyal to Jack rather than Enso VeilTech. Its personality and capabilities expand as the game progresses.

This event permanently removes the player's financial safety net and sets the entire game's narrative in motion. Scavenging, salvage, and barter become the only options. Enso VeilTech becomes the background threat. The mainframe hack is the first major non-repair objective.

The bank email and the Enso VeilTech compliance message are to be written carefully — masterpieces of corporate indifference that set the tone for the entire game world.

### Technical implementation (deferred)
- `check_for_event()` in `game_manager.py` — stub currently returns `None`
- Random events: probability checked in game loop tick
- Scheduled events: game-time threshold comparison against `chronometer` state
- Event response format: standard response dict, handled by frontend `handleResult()`
- Pending events cleared after delivery to prevent repeat firing


---

## 20. SAVE / LOAD SYSTEM — DESIGN ⚠️ NEEDS FURTHER DISCUSSION

### Philosophy
The save system reflects the game's core philosophy — unforgiving, like real life. There is no scum saving. There is no reloading because you didn't like an outcome. When you die, you are dead.

### Splash screen
- **New Game** — greyed out if a save file exists
- **Continue** — greyed out if no save file exists
- Only one path is ever available at a time, except when no save exists (New Game only)

### Save triggers — autosave only
No player-controlled saving. The game saves automatically on:
- Room change
- After any timed action completes (repair component, diagnosis, card swipe)
- On clean quit (player confirms quit at the quit prompt)

Saves never occur mid-action. If the browser closes during a repair timer, on Continue the player resumes from just before the repair started.

### Death state
On player death (any cause — system failure, survival mechanics, self-termination):
- Save file is written with a `dead: true` flag
- Continue screen displays a death message — immersive, in-world
- Only New Game is available
- No reload, no second chance

### Self-termination ⚠️ NEEDS FURTHER DISCUSSION
The player can choose to end their run deliberately, but it must require significant effort — not an exit button. Current thinking:
- Multi-step ship auto-destruct sequence spread across multiple rooms
- Requires visiting Engineering terminal, Mainframe terminal, and Cockpit — in sequence
- Requires high security card and PIN at one or more steps
- Ship's computer responds to each step with in-world terminal text
- Countdown once initiated — player can abort before expiry
- Takes approximately 15-20 minutes of game time to complete
- Airlock spacing as an alternative quieter method — requires EVA suit absent, airlock cycling deliberately without suit
- Both methods write the dead save state identically

### Save file scope
The save file is a JSON snapshot of all mutable game state:
- **Player state** — room, inventory (with instance_ids and wire lengths), equipped slots, survival stats (future)
- **Portable item positions** — room floors, container contents, surface contents, with instance_ids and all instance attributes
- **Door states** — open, locked, pin_attempts per door
- **Panel states** — is_broken, broken_components, diagnosed_components, repaired_components per panel
- **Electrical system state** — operational state of all cables, breakers, panels, power sources
- **Ship time** — total_minutes from chronometer
- **Instance ID counters** — restored on load to avoid collisions (not regenerated)
- **Dead flag** — true if the run ended in death

### Technical notes
- `instance_id` must be persisted and restored — not regenerated on load
- On load: restore instance counters from max existing suffix per type to avoid collisions
- All major entities already have stable IDs (doors, panels, electrical components, rooms)
- Portable items are the only entities that previously lacked stable unique identifiers — fixed by `instance_id`
- Recommended save file location: `data/save/save.json`
- Save/load functions belong in `game_manager.py`

### Key decisions still to make ⚠️
- Exact self-termination sequence and terminal content
- Whether airlock spacing requires any preconditions beyond suit absence
- Abort window duration for auto-destruct countdown
- Death screen content and presentation on the splash screen

---

## 21. TABLET, SHIP'S LOG AND MESSAGES — DESIGN

### The Tablet
A portable handheld device — think future iPad, rugged industrial build. Carried in player inventory. When in inventory, a TAB tab appears in the tab strip alongside INV and TERM, always visible regardless of whether there are active notes.

**What it shows:**
- Ship power map (live, same as engineering terminal Power Status view)
- Circuit diagram (same as engineering terminal Circuit Diagram view)
- Diagnostic/repair notes (see below)
- Ship's log
- Messages

**Key design rules:**
- The tablet is NOT read-only — it is a full interface device
- The tablet cannot reset or operate breakers — physical presence at the panel is always required
- The tablet works on its own battery — functions even in unpowered rooms, allowing the player to consult the map while standing in a dark room
- The tablet is on the ship's network but the network is not modelled as a separate system
- Tablet access command: `access tablet` or clicking the TAB tab

**Item definition:**
- Single inventory item, carried loose
- Manufacturer/model TBD — rugged industrial device, not a consumer product

### Diagnostic/Repair Notes
When the player receives a diagnosis result and the tablet is in inventory, a note is automatically created and stored on the tablet. The note is a snapshot in time — it does not update dynamically. If the player re-diagnoses the same panel, the note is replaced with a fresh one.

**Note format:**
```
01-01-2276  14:32
Location: Recreation Room
Panel: SMC Nova TS1500 Security Door Panel

Faulty components:
  TS1500 Logic Board, Relay Switch Array

Tools required:
  Scan Tool, Power Screwdriver Set,
  Electrical Service Tool Kit, Laser Solderer

Missing from inventory at time of diagnosis:
  Electrical Service Tool Kit, TS1500 Logic Board
```

**Note behaviour:**
- Missing items reflect inventory state at time of diagnosis only — not updated dynamically
- Player re-runs diagnosis to get a fresh note with updated missing items
- Re-diagnosing the same panel replaces the existing note for that panel
- When a panel/component is fully repaired, its note is automatically marked ARCHIVED
- Archived notes are kept for reference — player can manually dismiss them
- Notes list is ordered most recent first, archived notes shown separately at bottom

### Ship's Log
Accessible from any terminal and from the tablet. A permanent timestamped record of the run. Starts fresh on New Game. Survives across saves.

**Logged automatically:**
- Game start / hypersleep exit
- Diagnosis initiated and completed (what, where, outcome)
- Repair completed (component, system, location)
- Game events (micrometeorite impact, power surge, system failure, etc.)
- Power loss / restoration to rooms
- Significant security events (card invalidation, PIN failure lockout)
- Player death (cause recorded)

**Format** — terse, functional, one line per entry:
```
01-01-2276  00:00  ENGINEERING       Game started. Hypersleep exit.
01-01-2276  14:32  RECREATION ROOM   Diagnosis initiated: Cockpit access panel
01-01-2276  14:51  RECREATION ROOM   Diagnosis complete: TS1500 Logic Board, Relay Switch Array
01-01-2276  15:47  MAIN CORRIDOR     Power restored: Crew Cabin, Captains Quarters
```

### Messages System
Accessible from terminals and the tablet. Narrative delivery mechanism for the game world. Called "Messages" in-game, not "email".

**Message types:**
- Automated ship alerts (system failures, critical warnings)
- External communications — from the friend, from Enso VeilTech, from contacts
- Narrative events — the opening sequence messages fire here

**Key design rule:** Messages and the ship's log are distinct. The log is automated and factual. Messages are communications addressed to Jack Harrow.

**The friend:**
Jack has at least one person on the outside who cares whether he lives. Messages from this person are informal, human, and urgent. They provide tips, contacts, and narrative hooks — directing the player toward underground contacts, useful locations, and information Enso VeilTech doesn't want Jack to have. The friend operates in grey areas and is not above pointing Jack toward people who operate outside the law. Identity and backstory TBD — scope deferred.

**The mainframe as eventual ally:**
Before the mainframe hack, the mainframe terminal runs Enso VeilTech compliance software and is an obstacle. After the hack, the mainframe AI becomes a ship companion — accessible via the mainframe terminal, capable of providing ship status, advice, and eventually expanded capabilities as the game progresses. Its personality develops over time. Scope deferred to mainframe hack phase.

---

## 22. NARRATIVE — JACK HARROW AND ENSO VEILTECH

### Jack Harrow — starting situation
Jack Harrow is an Enso VeilTech employee operating the Tempus Fugit as a solo trader/courier. The ship is company property. The cargo is company property. His tools carry company software and company legal warnings. He is employee number 7,341,892 in a corporation that does not know his name.

He is currently in deep space, returning from a long haul run, in hypersleep.

### The opening sequence — what happens
1. **Impact event** — something hits the ship during hypersleep. Jack is woken early. The ship has damage — serious but not immediately fatal. He has repairs to make. This is the tutorial period — the player learns the game systems.

2. **Messages waiting** — when Jack accesses a terminal or the tablet, three messages are waiting:

   **Message 1 — The bank (3 months old):**
   The bank's quantum encryption system was hacked by an unknown third party. Jack's account balance was set to zero. The bank treats a zero balance as a breach of contract under their terms. His account has been terminated. His quantum ID has been blacklisted across all affiliated financial institutions. This blacklist is effectively permanent. Compounded interest on the account closure fee has been accruing for 90 days. The email is a masterpiece of corporate indifference — no apology, no acknowledgement that Jack is a victim, no recourse offered. To be written with great care — it sets the tone for the entire game world.

   **Message 2 — Enso VeilTech Compliance (recent, automated):**
   The Enso VeilTech compliance system has flagged Jack Harrow. Per employment contract Section 4 subsection 2a, continued operation of company assets requires a clean financial record. Jack is instructed to set course immediately for the nearest Enso VeilTech authorised facility, surrender the Tempus Fugit, and report in person. Financial default proceedings will be initiated. Failure to comply within 72 hours will result in remote lockdown of the vessel and escalation to Enso VeilTech Security Division. Also a masterpiece of corporate indifference — automated, impersonal, devastating.

   **Message 3 — The friend (recent, urgent):**
   Informal. Worried. They've heard what happened. Do NOT comply with Enso VeilTech. Do NOT let the mainframe set a course for their facility. The mainframe is running Enso VeilTech navigation compliance software — it will lock the course automatically when it processes the compliance order. Hack the mainframe first. There is someone on Ceres Base — ask for [Name TBD] — who can install clean software and help with parts and supplies, no financial record required. Get there before 72 hours are up.

3. **The mainframe acts** — shortly after the compliance message is processed, the mainframe logs a navigation compliance event in the ship's log and attempts to lock a course for the nearest Enso VeilTech facility. The ship is trying to take itself home. The player receives a ship's log entry and a mainframe alert.

4. **The hack objective** — the player must reach the mainframe terminal and perform the hack. Until this is done, the mainframe is an obstacle. After the hack, the mainframe AI is freed from Enso VeilTech's software and becomes loyal to Jack. This is the first major non-repair objective in the game.

### Enso VeilTech — the invisible antagonist
Enso VeilTech is never a villain in the traditional sense. They simply operate with complete institutional indifference. Their systems are automated, their responses are templated, and the individual human being does not register. The scan tool warning message — threatening dismissal and punitive damages for using incorrect manuals — is not malicious. It is just how Enso VeilTech's legal department writes every document.

This makes them more unsettling than a conventional antagonist. They are not pursuing Jack. They have simply set their compliance processes in motion and moved on. Employee 7,341,892 is a line item.

### Key decisions still to make ⚠️
- The friend's identity, backstory, and name
- The Ceres Base contact's name and personality
- The mainframe AI's name and personality post-hack
- Exact wording of the bank email and Enso VeilTech compliance message — to be drafted carefully
- The 72-hour countdown mechanic — does it actually lock the ship, and what does that mean in gameplay terms?
- Whether there are other messages in the system from before the hypersleep that give context to Jack's life

---

## 23. ELECTRICAL SYSTEM REPAIR — DESIGN

### Overview
The same diagnose/repair gameplay used for door panels extends to the ship's electrical system. The key differences are the tools required, the lockout/tagout safety procedure that must precede any work, and the fact that electrical components are not visible — the player must reason from symptoms to fault location using the power map and circuit diagram.

### Fault causes
Electrical faults are always caused by game events — never random at diagnosis time (unlike door panels). Events that cause electrical faults:
- **Micrometeorite impact** — most likely to sever cables
- **Power surge** (external origin) — most likely to trip or destroy breakers
- **Age/general failure** — any component, lower probability, background risk

The event sets the faulted state on the component. The player's diagnosis confirms it.

### Fault discovery flow
1. Player observes symptom — rooms without power on the live map
2. Player consults circuit diagram to trace the affected section back up the tree
3. Player reasons about likely fault location — single room dark vs entire branch dark
4. Player travels to the room containing the suspected component
5. Player runs `diagnose electrical` — timed action, requires HV test kit
6. Diagnosis confirms faulted components in that room
7. Player follows lockout/tagout procedure, then repairs

### The HV Test Kit
A specialist tool required for all electrical system diagnosis and repair. Replaces the scan tool for electrical work — the scan tool is for control/logic systems, the HV kit is for power distribution. 800V DC requires specialist equipment and PPE.

**Contents (single inventory item):**
- HV rated PPE (insulating gloves, arc flash protection)
- HV multimeter — voltage, current, resistance measurement
- Megohmmeter — proves isolation before work begins

**Item fields:**
- Manufacturer/model TBD — serious industrial instrument
- Cannot be substituted with the scan tool for electrical work
- Required for both diagnosis and repair of all electrical components

### Lockout / Tagout procedure
800V DC is lethal. The player must isolate and prove dead before working on any electrical component. Attempting to work on a live system results in instant death — no warning, no recovery.

**Procedure:**
1. Identify the correct upstream breaker to isolate the section
2. `lock out <breaker_id>` — player must be in the room where the breaker physically lives
3. Prove dead — part of the diagnosis timed action (megohmmeter check embedded)
4. Carry out diagnosis and repair
5. `remove lockout <breaker_id>` — restore the section when work is complete

**Breaker locked_out attribute** — new attribute to add to `Breaker` class:
- `locked_out = False` — normal state
- `locked_out = True` — deliberately isolated, cannot be re-energised until lockout removed
- Power tracing treats `locked_out = True` identically to `tripped = True`
- Player must be physically present at the breaker's room to lock out or remove lockout

### Breaker states
Breakers already have `tripped` and `operational` as separate attributes:

| tripped | operational | locked_out | Meaning |
|---------|-------------|------------|---------|
| False | True | False | Normal — passing power |
| True | True | False | Tripped — needs reset |
| True | False | False | Failed — needs replacement unit |
| Any | Any | True | Locked out by player — isolated for work |

**Reset vs replace:**
- Tripped breaker — `reset breaker <id>`, short timed action, no parts required
- Failed breaker — full diagnose/repair flow, replacement breaker unit required (new consumable item)

### Reactor integral main isolator
The direct feed cable `PWC-ENG-01` from `reactor_core` to `PNL-ENG-MAIN` has no upstream breaker. Every real reactor installation has an integral main isolator built in. This is modelled as a breaker with `"integral": true` in the JSON, located at the reactor in Engineering. Locking it out takes the entire ship's main distribution offline. Significant consequence, correct procedure.

### Electrical components by room
Every component has a `location` field in `electrical.json`:
- **Engineering** — reactor, integral isolator, `PNL-ENG-MAIN`, all `FUS-ENG-*`, all `PWC-ENG-*`
- **Main Corridor** — `PNL-MC-SUB-A`, all `FUS-MC-*`, all `PWC-MC-*`
- **Sub Corridor** — `PNL-SC-SUB-B`, all `FUS-SC-*`, all `PWC-SC-*`
- **Recreation Room** — `PNL-REC-SUB-C`, all `FUS-REC-*`, all `PWC-REC-*`
- **Propulsion Bay** — propulsion reactor, `PWC-PROP-01`, `PWC-PROP-02`
- **Life Support** — `BAT-LS-01`
- **Mainframe Room** — `BAT-MF-01`

### diagnose electrical command
New routing in `command_handler.py`. Keywords that resolve to electrical diagnosis:
- `diagnose electrical`
- `diagnose room electrical`
- `diagnose wiring`
- `diagnose power`

### Key design decisions still to make ⚠️
- Exact tablet item manufacturer/model
- HV test kit manufacturer/model
- Replacement breaker unit item definition
- Repair profiles for each electrical component type
- Exact command syntax for lockout/tagout
- Ship's log implementation — stored in memory or written to file

---

## 24. GOING DARK — SHIP DISGUISE AND BARTER

### The problem after the hack
Once the mainframe is hacked and Enso VeilTech's compliance software is removed, the automated compliance process stalls. But Enso VeilTech's security division escalates. The Tempus Fugit's transponder signal — broadcasting its registered identity to every scanner in range — is now a liability. Flying it openly means every port authority, every Enso VeilTech patrol, every affiliated scanner is a potential arrest. The ship needs to disappear.

### Two layers of disguise

**Physical hull camouflage** — bolt-on external modifications that change the Tempus Fugit's visual profile. Panels, sensor blisters, hull plating that alters the silhouette enough to defeat casual visual identification. Requires physical parts sourced through the underground contact. Requires EVA to install — the player must go outside the ship. This naturally unlocks the EVA gameplay phase. Inspired by the disguise configurations used in The Expanse.

**Transponder obfuscator** — a device that spoofs the ship's identification signal, broadcasting a false registration and ship name. Illegal in every jurisdiction. Not available through any legitimate channel. The Ceres Base underground contact is the source. Requires barter — no financial transaction possible.

### Paying for it — the cargo
The Tempus Fugit's cargo bay contains Enso VeilTech goods. From Jack's perspective this is now effectively salvage — he is already a criminal in their system, and the cargo represents his only negotiating currency. The underground contact has interest in certain types of cargo.

The cargo is not uniformly valuable or uniformly safe to liquidate:
- Some items are straightforward trade goods — easily moved, good barter value
- Some items may be dangerous or sensitive — Enso VeilTech may want them back specifically, not just the ship
- Some items may themselves be of questionable origin — Enso VeilTech's supply chain is not clean
- The cargo manifest becomes a narrative device — what Jack is carrying tells a story about the run he was on

The player must assess the manifest, decide what to offer, and negotiate. This is the beginning of the barter economy that replaces the financial system destroyed by the bank hack.

### EVA requirement
Installing physical hull camouflage requires going outside the ship. The EVA suit, helmet, and boots are already in the cargo bay EVA equipment locker. The airlock is already in the game. The EVA phase is the natural next layer of gameplay unlocked by the disguise objective — magnetic boot adhesion on the hull, working in vacuum, time pressure from suit battery/oxygen limits.

### New identity
Once both layers of disguise are in place, the Tempus Fugit has a new name, a new visual profile, and a false transponder signal. Jack Harrow has effectively ceased to exist in the official record. The game enters its second phase — operating entirely outside legitimate society, dependent on the underground network, with Enso VeilTech as a persistent background threat rather than an immediate one.

### Key design decisions still to make ⚠️
- The cargo manifest contents — what is Jack actually carrying, and what secrets does it contain?
- The new ship name and identity
- EVA mechanics detail — suit duration, oxygen limits, hull attachment
- Whether the physical camouflage has gameplay consequences beyond disguise (added mass, changed handling)
- How the transponder obfuscator interacts with port access and NPC interactions in future phases

---

## 25. PROJECT BACKGROUND — HOW THIS CAME TO BE

### In the lead designer's own words

*The following was written by the lead designer during a development session in April 2026, as an honest account of how this project came to be. It is included verbatim as both context for future development sessions and as a genuine artifact of human-AI collaboration.*

---

"I have limited coding knowledge, mainly Python, with a little exposure to javascript, html, css but I am no accomplished programmer. My skills are in logical thought processes, multiple years of real life mechanical repair/diagnosis and an ability to look into what future changes could impact the current codebase which enables a certain amount of 'if we do this, we may need to make allowances for what a future phase may require'.

The development process has been organic, some has been planned for, but certainly not from day one. This is where the design docs are vital.

I am the lead designer, however virtually all coding is done by AI, my coding input has been minimal. The project started from several small projects aka feature experiments eg the electrical system and the typewriter terminal effects. Some experiments didn't work out such as the life support logic so this will need revisiting until I am happy with the result.

This project would never have got to this state without the various AI's (starting with Grok, the SuperGrok, then Sonnet 4.5 and now Sonnet 4.6) and of course it also would not have got to this state without my input, design ideas and constant questions and debates between myself and the AI's such as yourself."

---

### Summary

- Started as a series of feature experiments — electrical system, typewriter terminal, others
- Some experiments succeeded and were integrated, some (e.g. early life support logic) were rejected and await revisiting
- Development has been organic rather than fully planned from day one — the design doc reflects what was learned, not what was originally intended
- The lead designer has limited formal programming background, strong logical thinking, real-world mechanical diagnosis and repair experience, and a particular ability to anticipate how current decisions affect future phases
- Virtually all code is AI-generated, directed and reviewed by the lead designer
- Development has progressed through several AI collaborators: Grok, SuperGrok, Claude Sonnet 4.5, Claude Sonnet 4.6
- The project would not exist in its current form without both the AI implementation and the human design direction — neither alone would have produced this result

---

*Project Orion Game Design Document v18.0*
*April 2026*
