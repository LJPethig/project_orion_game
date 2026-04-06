# PROJECT ORION GAME
## Space Survival Simulator
### Master Design & Development Document
**Version 14.0 — April 2026**

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
- Player, inventory, items ✅
- Fixed object data structure: terminals, storage units, surfaces ✅
- Description panel: markup parser, hover tooltips, click handlers, Layer 2/3 ✅
- Container commands: open, close, look in, take from, put in, put on ✅
- Equip/unequip commands: wear, equip, remove, take off, unequip ✅
- Floor fallback: items drop to floor when no surface available ✅
- Player inventory screen: slide-out panel, equipped slots, carried items, actions ✅
- Smart command parser: ID resolver, verb conflict resolution, clarification system ✅
- Item registry: unique instances per placement, unique runtime instance_id per item ✅
- Terminal system: CRT styling, typewriter, keypress nav, sub-menus, terminal mode lockout ✅
- Electrical system: reactor, panels, breakers, cables, batteries, power tracing ✅
- Electrical integrated into gameplay: door panels and terminals check room power ✅
- Engineering terminal: Technical Data, Electrical sub-menu (Power Status map, Circuit Diagram placeholder) ✅
- Debug console: Ctrl+D, break/fix commands, live map refresh ✅
- Full repair system: diagnose + repair commands, scan tool manual validation, per-component repair, wire consumption by length, auto-chain, event hook ✅
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

# Timed actions — real seconds stubs
# REPAIR_REAL_SECONDS and DIAGNOSE_REAL_SECONDS are temporary stubs.
# When proper time scaling is implemented in repair_handler.py, delete these.
REPAIR_REAL_SECONDS    = 8
DIAGNOSE_REAL_SECONDS  = 5
CARD_SWIPE_REAL_SECONDS = 5
CARD_SWIPE_GAME_MINUTES = 0

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
- **Description refresh** — `refreshExits()` updates both `currentExits` and `currentObjects` immediately after break/fix.

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
- Note: ship inventory is NOT a global item manifest. Terminal-managed cataloguing specific to cargo bay and storage room only. Items placed in a tray are automatically stored and catalogued. Items not placed via the terminal are not catalogued.

### Phase 20 — Life support
- Binary operational states driven by electrical system
- Temperature modelling — open/closed doors, room volume, HVAC
- Dynamic room descriptions based on power state

### Phase 21 — Events system
- See Section 18 for full event system design
- Banking hack opening event
- Random and scheduled event architecture
- Player survival mechanics

### Phase 22+ — Navigation, trading...

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
- **`refreshExits()` rename** — function now updates both `currentExits` and `currentObjects`. Should be renamed `refreshDescription()` but touches many call sites — defer to a quiet refactor session.
- **Terminal shutdown on power loss** — if power is lost to a room while the terminal is active (via game events), the terminal should close immediately. Implement when event system is built.
- **Dynamic room descriptions** — static prose needs electrical atmosphere removed. A power-state description layer (dark/silent when unpowered, atmospheric when powered) is planned for Phase 20.
- **Circuit diagram SVG** — being built manually in Inkscape. When complete, integrate into `[C] Circuit Diagram` in engineering terminal.
- **Repair post-repair failure roll** — hook exists, always succeeds. Future: probability-based failure chance, higher for complex repairs or missing manuals.
- **Repair time scaling** — `calc_repair_real_seconds()` and `calc_diagnose_real_seconds()` in `repair_handler.py` currently return fixed stubs. Implement proper scaling with cap. Delete `REPAIR_REAL_SECONDS` and `DIAGNOSE_REAL_SECONDS` from `config.py` when done.
- **Scan tool software updates** — future exotic systems require purchased scan tool updates. Not yet implemented.

### Recently completed deferred items
- ✅ **Wire length display** — `display_name()` method on `PortableItem` appends `(Xm)` for wire items. Used in inventory, containers, surfaces, floor items, clarification options, repair/diagnosis responses, and all take/put/drop/look in response messages.
- ✅ **Unique instance identifiers** — each placed item now receives a unique runtime `instance_id` (e.g. `wire_low_voltage_001`) at load time. Clarification options use `instance_id` in commands. Resolution checks `instance_id` first, bypassing ambiguity entirely. All handlers, serialisation, and frontend clicks updated. Clarification display for wire spools now shows correct lengths and selects the correct instance.
- ✅ **`pick up <item> from <container>`** — preposition handling now correctly routes `pick up` alongside `take` for `from` commands.
- ✅ **Scan tool manual check** — no longer blocks diagnosis. Missing manual shows a corporate warning in orange with Yes/No confirmation. Diagnosis proceeds regardless. Future: missing manual increases post-repair failure probability.
- ✅ **`display_name()` in all response messages** — wire length now shown correctly in all take/put/drop/look in response messages across `item_handler.py` and `container_handler.py`.
- ✅ **resolver_debug.log** — logger removed from `main.py` and `command_handler.py`, log file deleted.
- ✅ **Inventory screen auto-close** — `closeInventoryIfOpen()` added to `setPanelImage()`, `setDamagedPanelImage()`, and `setDoorImage()` in `ui.js`.

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
Fires shortly after game start. The player is woken early from hypersleep by an impact event (ship damage — serious but not immediately critical). Upon accessing the ship's message system, they discover an email sent 3 months prior while they were in stasis.

The bank's quantum encryption system was hacked. The email is written in pure corporate indifference — no apology, no explanation, no recourse. Key details:
- Account balance set to zero by the hack
- Bank treats zero balance as a breach of contract
- Account terminated forthwith
- Player's quantum ID blacklisted across all financial institutions (effectively permanent)
- Compounded interest has been accruing on the account closure fee for the 90 days since termination
- The blacklist was already ancient history in the bank's system by the time the player reads the email

This event permanently removes the player's financial safety net early in the game. Purchasing parts or supplies through normal channels is no longer possible. Scavenging, salvage, and barter become the only options.

The email itself is to be written carefully — it should be a masterpiece of corporate indifference and will set the tone for the entire game world.

### Technical implementation (deferred)
- `check_for_event()` in `game_manager.py` — stub currently returns `None`
- Random events: probability checked in game loop tick
- Scheduled events: game-time threshold comparison against `chronometer` state
- Event response format: standard response dict, handled by frontend `handleResult()`
- Pending events cleared after delivery to prevent repeat firing


---

## 19. PROJECT BACKGROUND — HOW THIS CAME TO BE

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

*Project Orion Game Design Document v14.0*
*April 2026*
