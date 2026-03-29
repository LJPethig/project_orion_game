# PROJECT ORION GAME
## Space Survival Simulator
### Master Design & Development Document
**Version 8.0 — March 2026**

---

## 1. PROJECT OVERVIEW

### Concept
Project Orion Game is a space survival simulator set in 2276. The player operates a solo trader/explorer spacecraft named the **Tempus Fugit**, captained by **Jack Harrow**. Core gameplay revolves around maintaining ship systems, repairing failures, and surviving deep space. This is a serious "slow burner" simulator — not an arcade game. Systems fail, cascade, and the player must diagnose and fix them before things get fatal.

### History
- **Project Dark Star** — previous iteration in Python/Arcade. Deprecated — Project Orion Game has surpassed it in every area.
- **Project Orion Game** — Flask backend + HTML/CSS/JS frontend. The active codebase. All Dark Star game logic has been ported and significantly improved.
- **Electrical system reference project** — a separate standalone project containing electrical system architecture, reactor, panels, breakers, cables and an interactive SVG diagnostic map. Will be merged into Project Orion Game in Phase 17.

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

### Progress
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
- Dark Star feature parity: **complete** — Project Dark Star is now deprecated

### Phase 6 — Splash screen + game shell ✅
### Phase 7 — Ship + room loading ✅
### Phase 8 — Room description rendering ✅
### Phase 9 — Movement ✅
### Phase 10 — Door system ✅
### Phase 11 — Damaged door panels + basic repair ✅
### Phase 12 — Ship state, player, inventory ✅
### Phase 13 — Description panel, containers, surfaces, equip ✅
### Phase 14 — Player inventory screen ✅
### Phase 15 — Smart command parser ✅

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
│   │   ├── game_manager.py
│   │   ├── ship.py
│   │   ├── room.py              ← includes floor list
│   │   ├── door.py
│   │   ├── interactable.py      ← StorageUnit, Surface, Terminal
│   │   ├── player.py
│   │   └── chronometer.py
│   │
│   ├── handlers/
│   │   ├── base_handler.py      ← _find_exit with noise word stripping
│   │   ├── command_handler.py   ← resolver, clarification system
│   │   ├── movement_handler.py
│   │   ├── door_handler.py
│   │   ├── repair_handler.py
│   │   ├── item_handler.py
│   │   ├── container_handler.py
│   │   └── equip_handler.py
│   │
│   ├── loaders/
│   │   └── item_loader.py       ← registry stores raw dicts, instantiate_item() for fresh instances
│   │
│   └── api/
│       ├── game.py              ← /api/game/inventory endpoint
│       └── command.py
│
├── frontend/
│   ├── templates/
│   │   ├── splash.html
│   │   └── game.html
│   │
│   └── static/
│       ├── css/
│       │   ├── splash.css
│       │   └── game.css
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
│       │       └── game.js
│       └── images/
│           ├── image_missing.png
│           ├── start_screen.png
│           ├── rooms/
│           └── doors/
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
    └── ship/
        └── structure/
            ├── ship_rooms.json
            ├── door_status.json
            ├── initial_ship_state.json
            ├── initial_ship_items.json
            └── player_items.json
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
STORAGE_UNITS_JSON_PATH = 'data/items/storage_units.json'
SURFACES_JSON_PATH      = 'data/items/surfaces.json'
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
Handlers retain both `item.id == target` and `item.matches(target)` checks. This is intentional:

- The resolver upstream converts keywords to IDs before dispatch — so in normal operation handlers receive IDs.
- UI clicks fire with known IDs directly — these pass straight through the resolver and hit the `item.id == target` check.
- The keyword fallback `item.matches(target)` acts as a safety net for any edge cases where resolution fails or a keyword passes through unchanged.

Removing the keyword fallback from handlers was attempted and reverted. The resolver operates on room-scoped snapshots and the preposition early-exit blocks in `process()` have their own resolution paths — keeping keyword matching in handlers avoids fragile chains of state-dependent resolution logic in the preposition paths.

### Fixed object keyword uniqueness
Fixed objects (containers, surfaces) must have unique keywords within a room. This eliminates ambiguity for `open`, `close`, `put in`, `take from` commands without requiring state-filtered resolution. Portable items (e.g. two pairs of boots) may share keywords — the clarification system handles those cases.

### Clarification system
When multiple distinct matches found, returns `clarification_required` with clickable options rendered in response panel. Covers: take, drop, wear, equip, open, close, look in, remove, repair panel, put in, put on.

### Verb registry
| Verb | Handler |
|------|---------|
| `go`, `enter`, `move` | MovementHandler |
| `open`, `close` | _route_open/_route_close (container first, door second) |
| `lock`, `unlock` | DoorHandler |
| `repair panel`, `repair` | RepairHandler |
| `take`, `get`, `pick up` | ItemHandler |
| `drop` | ItemHandler |
| `look in` | ContainerHandler |
| `take from` | ContainerHandler |
| `put in`, `place in` | ContainerHandler |
| `put on`, `place on` | ContainerHandler / EquipHandler (via _route_put_on) |
| `wear`, `equip` | EquipHandler |
| `remove`, `take off`, `unequip` | EquipHandler |
| `debug_inventory` | ItemHandler |

---

## 8. MAIN GAME SCREEN LAYOUT

```
┌──┬──────────────────────────────────────────┬──────────────┐
│  │                                          │ DESCRIPTION  │
│T │         ROOM IMAGE (45%)                 │ (scrollable) │
│A │    ← slide-out panels cover this area    ├──────────────┤
│B │                                          │ RESPONSE     │
│S │                                          │ (scrollable) │
│  │                                          ├──────────────┤
│  │                                          │ COMMAND INPUT│
├──┴──────────────────────────────────────────┴──────────────┤
│ EVENT STRIP              [events]      [ship name + time]  │
└────────────────────────────────────────────────────────────┘
```

### Tab strip
Narrow vertical icon tabs on left edge. Each opens a slide-out panel over the image section. Currently: INV only. Future: TERM (terminals phase).

### Colour palette
| Variable | Hex | Use |
|----------|-----|-----|
| `--col-text` | `#bababa` | Default text |
| `--col-title` | `#27e6ec` | Cyan — titles, exits, containers, terminals |
| `--col-portable` | `#bea5cd` | Purple — portable items, surfaces with items |
| `--col-alert` | `#ff8c00` | Orange — alerts, locked doors |
| `--col-prompt` | `#00ff00` | Green — command prompt, open doors |
| `--col-response` | `#7e97ae` | Muted blue — player input echo |

---

## 9. DESCRIPTION PANEL — MARKUP SYSTEM

### Markup types
| Markup | Type | Colour | Hover | Click |
|--------|------|--------|-------|-------|
| `*exit*` | Exit | Cyan | Door state | None |
| `%object%` | Container | Cyan | Open/Closed | Toggle open/close |
| `!terminal!` | Terminal | Cyan | "Terminal" | `use <terminal>` |
| `#surface#` | Surface | Grey bold (empty) / Purple bold (has items) | "Empty" / "Has items" | Expand Layer 3 |

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
- Closes automatically on room change
- Wear/Drop/Remove action buttons

**Ship inventory** — managed manifest of tradeable/consumable stock
- Accessed via storage terminals only (Phase 17)

---

## 11. ITEM SYSTEM

### Item registry
- `item_loader.py` stores raw data dicts — not instances
- `instantiate_item()` creates fresh `PortableItem` instance each call
- Every placed item is a unique Python object with independent state
- Foundation for consumables with mutable attributes (e.g. `length_m` for wire)

### Consumables
Wire and cable items will have `length_m` attribute in `consumables.json`. After use in repair, instance `length_m` is decremented. Two spools of the same wire type are independent — using one doesn't affect the other.

### Object ID naming convention
`roomid_markuptext` — ensures unambiguous ID matching within a room.

---

## 12. BUILD PLAN — NEXT PHASES

### Phase 16 — Terminals
- `use terminal` / `use <terminal name>` — opens terminal for current room
- Clicking a terminal markup link in the description panel also opens it
- Terminal slide-out panel — opens over the room image, same as INV panel
- No TERM tab in the tab strip — terminal is opened via command or description
  click only, not a persistent tab
- Terminal UI styled as an old-school computer menu — navigable with up/down
  arrows and enter key, mouse click also selectable
- Menu items and submenus are specific to the terminal type (nav, storage, etc.)
- Panel closes automatically on room change — same logic as inventory panel

### Phase 17 — Electrical system integration
- Merge electrical system reference project into codebase
- Reactor, panels, breakers, cables
- Room power affects door panels, terminals
- `DEBUG_HAS_REPAIR_TOOL` replaced with real tool checks

### Phase 18 — Full repair system
- Diagnosis, repair, verification flow
- Real tool and parts checks
- See Section 14 for complete design

### Phase 19 — Ship inventory + cargo
- Ship inventory manifest via storage terminals
- Cargo bay trading items
- `PortableContainer` (moveable crate) — floor only, moved via automated handler

### Phase 20 — Life support
- Redesign from scratch as Orion-original system
- Binary operational states driven by electrical system (working or not)
- Temperature modelling — open/closed doors, room volume, HVAC
- Reference project exists with extensive temperature modelling work

### Phase 21+ — Events, navigation, trading...

---

## 13. KNOWN ISSUES / DEFERRED

- **Multiple damaged panels same room** — clarification system handles it, untested with 3+ panels simultaneously
- **Storage room wiring bug** — electrical reference project maps storage_room to wrong panel ID. Fix when merging.
- **Carry weight on unequip** — always succeeds, drops to surface/floor if too heavy. Intentional for now.
- **PAM** — clips to utility belt. Dormant until life support phase.
- **Belt attachment mechanic** — utility belt accepts clipped items. Deferred until EVA phase.
- **Examine / look at command** — deferred. To be discussed.
- **Consumable `length_m`** — wire instances need `length_m` attribute in consumables.json. Add when repair system built.
- **Clarification display for items with same name but different state** — e.g. `Optical Wire (5m)` vs `Optical Wire (10m)`. Fix when `length_m` attribute exists.

---

## 14. RULES FOR DEVELOPMENT

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

---

## 15. FULL REPAIR SYSTEM — TARGET DESIGN

Phase 11 implements magic repair. Full system from Phase 18:

**Step 1 — Diagnose** using Scan Tool + basic access tools + workshop manuals (optional)
**Step 2 — Repair/Replace** correct parts and tools at component location
**Step 3 — Verify** using Scan Tool again
**Step 4 — Operational** or return to Step 2

Without correct manual: diagnosis less precise, chance of incorrect repair.
Bypass mechanic: force open frozen door with crowbar, damages door further.

---

*Project Orion Game Design Document v8.0*
*March 2026*
