# PROJECT ORION GAME
## Space Survival Simulator
### Master Design & Development Document
**Version 19.1 — April 2026**

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
- Fixed object data structure: terminals, storage units, surfaces, pallet containers, pallet platforms ✅
- Description panel: markup parser, hover tooltips, click handlers, Layer 2/3 ✅
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
- Automated storage facility: store/retrieve via UI, manifest on GameManager, CRT terminal display ✅
- Cargo bay manifest: container/pallet instance data, read-only CRT terminal display ✅
- Door action distinction: `open` unlocks and opens, `unlock` unlocks only, `lock` locks ✅
- Input locking during door image display — all paths covered ✅
- Description panel click lockout during timed actions via pointer-events ✅
- Ship log structured entries: timestamp, event, location, detail fields ✅
- Messages system stub — datapad Messages menu functional, shows placeholder ✅

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
│   │   ├── game_manager.py        ← owns all game state, storage_manifest, cargo_manifest
│   │   ├── ship.py
│   │   ├── room.py
│   │   ├── door.py                ← panel_type, security_level resolved at load time
│   │   ├── interactable.py        ← StorageUnit, Surface, Terminal, PalletContainer, Pallet
│   │   ├── player.py
│   │   └── chronometer.py
│   │
│   ├── systems/
│   │   └── electrical/
│   │       └── electrical_system.py
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
│   │   ├── terminal_handler.py
│   │   └── storage_handler.py     ← store/retrieve for automated storage facility
│   │
│   ├── loaders/
│   │   └── item_loader.py
│   │
│   └── api/
│       ├── game.py                ← storage and cargo manifest endpoints added
│       ├── command.py
│       └── systems.py
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
│       │   └── terminal.css       ← storage/cargo manifest styles added
│       ├── js/
│       │   ├── core/
│       │   │   ├── constants.js
│       │   │   ├── api.js         ← storeItem, retrieveItem, getStorageManifest, getCargoManifest
│       │   │   └── loop.js
│       │   └── screens/
│       │       ├── splash.js
│       │       ├── ui.js
│       │       ├── commands.js
│       │       ├── description.js
│       │       ├── inventory.js   ← Store button added
│       │       ├── terminal.js    ← storage_room and cargo_bay terminal types added
│       │       └── game.js
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
    │   ├── surfaces.json
    │   ├── cargo_containers.json  ← PalletContainer type definitions
    │   └── pallet_platforms.json  ← Pallet type definitions
    ├── terminals/
    │   └── engineering.json
    ├── repair/
    │   └── repair_profiles.json
    └── ship/
        ├── structure/
        │   ├── ship_rooms.json
        │   ├── door_status.json
        │   ├── door_access_panel_types.json
        │   ├── initial_ship_state.json
        │   ├── initial_ship_items.json   ← storage_facility section added
        │   ├── initial_cargo.json        ← cargo bay instance data
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

# Repair/diagnosis real-time scaling
REPAIR_TIME_BASE_SECONDS  = 8
REPAIR_TIME_SCALE_SECONDS = 8
REPAIR_TIME_PIVOT_MINUTES = 30
REPAIR_TIME_CAP_SECONDS   = 20
DIAG_ACCESS_OVERHEAD      = 0.25
DIAG_TIME_JITTER          = 0.10

ROOMS_JSON_PATH              = 'data/ship/structure/ship_rooms.json'
DOORS_JSON_PATH              = 'data/ship/structure/door_status.json'
DOOR_PANEL_TYPES_PATH        = 'data/ship/structure/door_access_panel_types.json'
INITIAL_STATE_JSON_PATH      = 'data/ship/structure/initial_ship_state.json'
SHIP_ITEMS_JSON_PATH         = 'data/ship/structure/initial_ship_items.json'
CARGO_JSON_PATH              = 'data/ship/structure/initial_cargo.json'
PLAYER_ITEMS_JSON_PATH       = 'data/ship/structure/player_items.json'
REPAIR_PROFILES_PATH         = 'data/repair/repair_profiles.json'
ITEM_FILES = [
    'data/items/tools.json',
    'data/items/wearables.json',
    'data/items/misc_items.json',
    'data/items/consumables.json',
]
TERMINALS_JSON_PATH          = 'data/items/terminals.json'
STORAGE_UNITS_JSON_PATH      = 'data/items/storage_units.json'
SURFACES_JSON_PATH           = 'data/items/surfaces.json'
CARGO_CONTAINERS_JSON_PATH   = 'data/items/cargo_containers.json'
PALLET_PLATFORMS_JSON_PATH   = 'data/items/pallet_platforms.json'
TERMINAL_CONTENT_PATH        = 'data/terminals'
ELECTRICAL_JSON_PATH         = 'data/ship/systems/electrical.json'
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

---

## 14. BUILD PLAN — NEXT PHASES

### Phase 19 — Ship inventory + cargo (COMPLETE)
See Section 19.

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

### Phase 25 — Cargo movement (sack barrow + cargo handler)
- Sack barrow mechanic — Jack moves small containers between rooms
- Cargo handler operational check — `cargo_handler_operational` flag on GameManager
- Stacking accessibility logic:
  - Container stacked directly on pallet → accessible, sack barrow sufficient
  - Container stacked on another container → cargo handler must be operational to unstack first
- Cargo handler as a repairable item — breaks down, must be repaired before cargo loading/unloading

### Phase 26+ — Navigation, trading, further narrative...

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

### Repair system architecture — future refactor
When a second repairable type is added, extract common logic to `repair_utils.py`. `repair_handler.py` stays as door panel handler. New handlers import from `repair_utils.py`.

### API endpoints
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/command/diagnose_complete` | POST | Populates broken_components, returns diagnosis report |
| `/api/command/repair_complete` | POST | Consumes parts, marks component repaired |
| `/api/command/repair_next` | POST | Event check then next component repair |

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
- ✅ **Description panel click lockout during timed actions** — implemented via `pointer-events: none` on `description-content` in `Loop.lockInput()` and `Loop.unlockInput()`.
- **Codebase size and structure analysis** — ✅ completed April 2026. Known remaining targets: `repair_handler.py` (→ `repair_utils.py`) before Phase 24, `terminal.js` split before Phase 22.
- **`terminal.js` split** — split into `terminal_core.js`, `terminal_engineering.js`, `terminal_manifest.js` before Phase 22 mainframe work begins.
- **`PalletContainer.pallet` flag** — purpose unclear, appears unused. Resolve before Phase 23.
- **Cargo contents** — initial_cargo.json containers are currently empty. Cargo contents to be authored when narrative cargo manifest is defined (Phase 23).
- **Cargo handler operational flag** — `cargo_handler_operational` stub needed on GameManager before Phase 25.


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

## 18. EVENT SYSTEM — DESIGN (PHASE 21)

### Overview
Two categories of events exist with different triggering mechanisms.

**Random events** — probability-based, checked periodically in the game loop. Examples: micrometeorite impacts causing ship damage, electrical faults, system failures.

**Scheduled events** — triggered by game-time thresholds. Examples: hunger, thirst, fatigue, atmospheric exposure.

### Event delivery
Events are delivered by the frontend poll — `loop.js` calls `/api/events/check` every 15 seconds when no timed action, repair chain, or PIN entry is in progress. The backend `EventSystem` checks elapsed ship time against scheduled event thresholds and returns any due events.

Diagnosis and individual component repairs are atomic — events cannot fire during them. The `repairInProgress` flag in `loop.js` covers the brief inter-component gap where `inputLocked` is momentarily false between components.

### Repairs and survival mechanics
Long repairs (multi-hour component jobs) need a natural break point between components so survival mechanics can fire and the player can choose to rest. This will be addressed by an auto-chain threshold — repairs over N game minutes per component will pause after completion and require the player to explicitly continue rather than auto-chaining. Implement when Phase 21 survival mechanics are built.

Survival events do not interrupt repairs — they impose penalties instead (slower repair, increased failure chance). Jack pushes through and suffers the consequences.

### Player survival mechanics (Phase 21)
- **Hunger** — must eat at regular intervals.
- **Thirst** — must drink at regular intervals.
- **Fatigue** — must rest/sleep.
- **Atmospheric survival** — breathable air, correct temperature, correct pressure.

### Technical implementation
- `EventSystem` in `backend/events/event_system.py` — schedule, check, resolve
- `/api/events/check` — frontend polls this endpoint every 15 seconds
- Events scheduled in `game_manager._init_events()` with `trigger_minutes` threshold
- Random events: probability checked in game loop tick (not yet implemented)
- Scheduled events: ship-time threshold comparison against `chronometer` state

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

## 23. ELECTRICAL SYSTEM REPAIR — DESIGN (PHASE 24)

### Overview
The same diagnose/repair gameplay used for door panels extends to the ship's electrical system. Key differences: HV test kit required, lockout/tagout safety procedure mandatory, electrical components are not visible — player must reason from symptoms.

### Fault causes
Electrical faults are always caused by game events — never random at diagnosis time. Events: micrometeorite impact (severs cables), power surge (trips/destroys breakers), age/general failure.

### The HV Test Kit
Specialist tool for all electrical diagnosis and repair. Cannot be substituted with scan tool. Contains HV rated PPE, HV multimeter, megohmmeter.

### Lockout / Tagout procedure
800V DC is lethal. Player must isolate and prove dead before working. Attempting to work live = instant death.

1. Identify upstream breaker
2. `lock out <breaker_id>` — must be physically present at breaker's room
3. Prove dead (embedded in diagnosis timed action)
4. Diagnose and repair
5. `remove lockout <breaker_id>`

**Breaker `locked_out` attribute:**

| tripped | operational | locked_out | Meaning |
|---------|-------------|------------|---------|
| False | True | False | Normal — passing power |
| True | True | False | Tripped — needs reset |
| True | False | False | Failed — needs replacement |
| Any | Any | True | Locked out by player |

### Reactor integral main isolator
Modelled as a breaker with `"integral": true`. Locking it out takes entire main distribution offline.

### Key design decisions still to make ⚠️
- HV test kit manufacturer/model
- Replacement breaker unit item definition
- Repair profiles for each electrical component type
- Exact command syntax for lockout/tagout

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

*Project Orion Game Design Document v19.1*
*April 2026*
