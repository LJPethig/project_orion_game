# PROJECT ORION
## Space Survival Simulator
### Master Design & Development Document
**Version 6.0 — March 2026**

---

## 1. PROJECT OVERVIEW

### Concept
Project Orion is a space survival simulator set in 2276. The player operates a solo trader/explorer spacecraft named the **Tempus Fugit**, captained by **Jack Harrow**. Core gameplay revolves around maintaining ship systems, repairing failures, and surviving deep space. This is a serious "slow burner" simulator — not an arcade game. Systems fail, cascade, and the player must diagnose and fix them before things get fatal.

### History
- **Project Dark Star** — previous iteration in Python/Arcade. Abandoned due to Arcade's text rendering limitations and UI inflexibility.
- **Project Orion** — Flask backend + HTML/CSS/JS frontend. Carries forward all Dark Star game logic, leaves behind all Arcade UI code.

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
- Dark Star game logic: **rooms, doors, security panels, command system, chronometer** ✅
- Dark Star game logic: **player, inventory, items, basic repair** ✅
- Fixed object data structure: **terminals, storage units, surfaces** ✅
- Description panel: **markup parser, hover tooltips, click handlers, Layer 2/3** ✅
- Container commands: **open, close, look in, take from, put in, put on** ✅
- Equip/unequip commands: **wear, equip, remove, take off, unequip** ✅
- Floor fallback: **items drop to floor when no surface available** ✅
- Dark Star game logic: **examine** — pending (Phase 15+)
- Dark Star feature parity: nearly complete — inventory screen (Phase 14) closes the gap. Full repair and terminals are Orion-original features, not ported from Dark Star.
- Project Orion electrical system — pending (Phase 17)

### Phase 6 — Splash screen + game shell ✅
### Phase 7 — Ship + room loading ✅
### Phase 8 — Room description rendering ✅
### Phase 9 — Movement ✅
### Phase 10 — Door system ✅

#### Door model
- Three states: open, closed, locked
- `SecurityPanel` — per-side, `is_broken`, `repair_progress`
- `SecurityLevel` enum: NONE(0), KEYCARD_LOW(1), KEYCARD_HIGH(2), KEYCARD_HIGH_PIN(3)

#### Door data
- `door_status.json` — pristine structural data (room IDs, security levels, panel IDs)
- `initial_ship_state.json` — scenario overlay: door states, panel damage, level 3 PINs

#### Card swipe flow
- 5s real-world wait, input locked, scanning animation
- 3 failed PINs: `id_card_high_sec` swapped for `id_card_high_sec_damaged` in inventory
- Card checks use real player inventory

### Phase 11 — Damaged door panels + basic repair ✅
- Broken panel freezes door, shows damaged panel image persistently
- `repair panel [target]` — 8s wait, 30 game minutes, shows repair animation
- On completion: repaired panel image shown briefly, then room restores
- `DEBUG_HAS_REPAIR_TOOL` in `config.py` — replaced by real tool check in Phase 18

### Phase 12 — Ship state, player, inventory ✅

#### Ship state architecture
- `door_status.json` — pristine, no damage/PINs/states
- `initial_ship_state.json` — overlay applied at game init

#### Item data files
```
data/
  items/
    tools.json
    wearables.json
    misc_items.json
    consumables.json
    terminals.json        ← fixed terminals
    storage_units.json    ← fixed containers with capacity/open_description
    surfaces.json         ← fixed surfaces (shelf, bench, table)
  ship/
    structure/
      ship_items.json     ← item placement (room floors and containers)
      player_items.json   ← player starting inventory and equipped slots
```

#### Item hierarchy
```
Interactable
├── PortableItem      — takeable, carriable, equippable
│   └── UtilityBelt   — wearable belt, accepts clipped attachments
└── FixedObject       — permanently attached to a room
    ├── StorageUnit   — open/close container, holds PortableItems
    ├── Surface       — always-open surface, holds PortableItems
    └── Terminal      — computer terminal (future: login, commands, power)
```

#### Player
- Inventory, equipment slots (head, body, torso, waist, feet), carry weight
- `has_card_for_level(n)` — real inventory check
- Card invalidation: swaps to damaged version
- Equipping blocked if slot already occupied — player must remove first

#### Commands
- `take / get / pick up <item>`, `drop <item>`, `debug_inventory`
- `open / close <container>`, `look in <container>`
- `take <item> from <container/surface>`, `put <item> in <container>`
- `put / place <item> on <surface>`
- `wear / equip <item>`, `remove / take off / unequip <item>`

### Phase 13 — Description panel, containers, surfaces, equip ✅

#### 13a — Fixed object data restructure
- `fixed_objects.json` split into `terminals.json`, `storage_units.json`, `surfaces.json`
- `Surface` and `Terminal` classes added to `interactable.py`
- `ship._load_fixed_objects` instantiates correct class per source file
- `ship_rooms.json` updated with `!terminal!` and `#surface#` markup throughout

#### 13b — Markup parser + hover tooltips
- `parseMarkup` handles all four markup types with distinct CSS classes
- Hover tooltips for containers (open/closed), terminals, surfaces (empty/has items)
- Backend `object_states` includes name, type, is_open, has_items, contents
- Surface span colour: grey bold when empty, purple bold when has items

#### 13c — Click handlers + Layer 2/3 rendering
- Container click → toggles open/close
- Terminal click → `use <terminal>`
- Surface click → expand/collapse Layer 3
- Layer 2: open container contents (cyan name, purple items, clickable)
- Layer 3: expanded surface contents (purple, clickable)
- Floor line: appears below description when items on floor (italic label, purple items)
- `room.floor` — fallback list for rooms with no surface
- Drop lands on random surface, falls back to floor

#### 13d — Equip/unequip commands
- `wear / equip <item>` — equips from inventory into designated slot
- `remove / take off / unequip <item>` — unequips to inventory, surface, or floor
- Equipping blocked if slot occupied: *"You are already wearing X. Remove it first."*
- `equip_handler.py` — new handler, drop logic owned here not in `player.py`

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
│   │   ├── base_handler.py
│   │   ├── command_handler.py
│   │   ├── movement_handler.py
│   │   ├── door_handler.py
│   │   ├── repair_handler.py
│   │   ├── item_handler.py
│   │   ├── container_handler.py
│   │   └── equip_handler.py
│   │
│   ├── loaders/
│   │   └── item_loader.py
│   │
│   └── api/
│       ├── game.py              ← _build_room_data includes object_states, floor_items
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
            ├── ship_items.json
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
SHIP_ITEMS_JSON_PATH    = 'data/ship/structure/ship_items.json'
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
| `put on`, `place on` | ContainerHandler |
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

### Tab strip (left edge, always visible)
A narrow vertical strip of icon tabs on the far left edge of the screen, slightly overlapping the image panel. Each tab opens a panel that slides out over the image section. Only one panel open at a time — clicking an open tab closes it.

| Tab | Icon | Panel |
|-----|------|-------|
| INV | backpack/person | Player inventory |
| MAP | ship outline | Ship diagnostic map |
| LOG | document | Mission/event log (future) |
| SYS | gear/circuit | Ship systems status (future) |

Icons are approximately 32x32px, dark background, cyan icon, subtle border. Hover lights up the icon, active state keeps it highlighted while panel is open.

### Colour palette:
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

See `docs/UI_UX_Description_Panel_v2.md` for full design. Summary:

### Markup types
| Markup | Type | Colour | Hover | Click |
|--------|------|--------|-------|-------|
| `*exit*` | Exit | Cyan | Door state | None |
| `%object%` | Container | Cyan | Open/Closed | Toggle open/close |
| `!terminal!` | Terminal | Cyan | "Terminal" | `use <terminal>` |
| `#surface#` | Surface | Grey bold (empty) / Purple bold (has items) | "Empty" / "Has items" | Expand Layer 3 |

### Description layers
1. **Static prose** — authored JSON, never changes
2. **Layer 2** — open container contents (cyan name clickable to close, purple items clickable to take)
3. **Layer 3** — expanded surface contents (purple name clickable to collapse, purple items clickable to take)
4. **Floor line** — appears only when items on floor: `Floor: item1, item2` (italic label, purple items)

### Drop behaviour
- Items dropped land on a randomly selected Surface
- If no Surface in room, item goes to `room.floor`
- Floor line appears automatically when floor is occupied

---

## 10. INVENTORY SYSTEM

### Two distinct inventories

**Player inventory** — personal carried and worn items
- Accessed via `INV` tab (slide-out panel over image section) or `inventory` command
- Shows loose carried items (with mass) and equipped slots
- Equip slots: head, body, torso, waist, feet
- Carry weight limit (configurable in `config.py`)

**Ship inventory** — managed manifest of tradeable/consumable stock
- Accessed via storage terminals in cargo bay and storage room only
- Tracks consumables, components, and trading items
- Not a list of everything placed around the ship — only formally logged stock
- Implemented in a future phase (after terminals)

### Player inventory screen (Phase 14)
The INV tab slides a panel out from the left, covering the image section. Description panel remains fully visible — the player can see room contents while managing inventory. Panel dismissed by clicking the tab again or pressing a key.

---

## 11. BUILD PLAN — NEXT PHASES

### Phase 14 — Player inventory screen ← NEXT
- Tab strip framework — narrow icon tabs on left edge, always visible
- Each tab slides a panel out over the image section
- INV tab — player inventory panel showing carried items and equipped slots
- `inventory` command toggles the panel
- Foundation for MAP, LOG, SYS tabs in future phases

### Phase 15 — Smart command parser
- Ambiguous commands prompt for clarification with clickable options in response panel
- Covers: `repair panel` (multiple broken panels), `take card` (multiple cards), `drop` (multiple surfaces), `open cabinet` (multiple cabinets)
- General disambiguation system, not per-command special cases
- Fixes `put on <item>` vs `put <item> on <surface>` conflict

### Phase 16 — Terminals
- `use terminal` / `use <terminal name>`
- Terminal commands: ship status, door map
- MAP tab wired up — ship diagnostic SVG accessible via tab or terminal
- Diagnostic map from `project_orion` prototype integrated here

### Phase 17 — Ship inventory + cargo
- Ship inventory manifest — tracked via storage terminals
- Cargo bay trading items — add/remove from manifest
- `PortableContainer` (moveable crate) — can be taken, moved, dropped
- Essential for freight trading mechanics

### Phase 18 — Electrical integration
- Connect electrical system from `project_orion` prototype
- Room power affects door panels, terminals, life support
- `DEBUG_HAS_REPAIR_TOOL` replaced with real tool checks

### Phase 19 — Full repair system
- See Section 14 for complete design
- Diagnosis, repair, verification flow

### Phase 20+ — Events, life support, navigation...

---

## 12. KNOWN ISSUES / DEFERRED

- **Multiple damaged panels in same room** — clarification logic exists but untested with multiple simultaneous broken panels. Verify when possible.
- **Storage room wiring bug** — `electrical.json` in `project_orion` maps `storage_room` to wrong panel ID. Fix when integrating electrical system.
- **Random item placement** — explicit placement only. Procedural scatter deferred.
- **Battery drain** — SVG map icons ready, game loop implementation deferred.
- **Clickable exits** — hover only by design. No click behaviour planned.
- **Look command** — deferred. May be added as "look harder" to find hidden items.
- **Bypass mechanic** — force open frozen door without repair. Deferred to full repair phase.
- **PAM** — clips to utility belt, shows O₂/temp in event strip. Dark Star's life support implementation was not reliable enough to port directly. Full PAM + life support will be redesigned as an Orion-original system — a separate reference codebase exists with extensive temperature modelling work (open/closed door effects, multi-day game time simulation) that should be consulted when this phase begins.
- **Belt attachment mechanic** — utility belt accepts clipped items (PAM, EVA tools). Deferred until EVA phase.
- **`put on <item>` conflict** — `put on` routes to surface handler, not equip. Workaround: use `wear` or `equip`. Fix in Phase 15 smart parser.
- **`put <item> in <surface>` gives wrong error** — surface exists but is not a container. Improve error message in Phase 15.
- **object_states should derive display name from backend** — `_getObjectName` in `game.js` currently has ID-humanisation fallback. Already fixed for containers/surfaces via `name` field in `object_states`, fallback remains for edge cases.
- **Carry weight on unequip not checked** — unequipping always succeeds; if inventory is full item drops to surface/floor. Intentional for now.

---

## 13. RULES FOR DEVELOPMENT

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
13. **Small changes — show inline instructions, not zipped files**

---

## 14. FULL REPAIR SYSTEM — TARGET DESIGN

Phase 11 implements magic repair. Full system from Phase 19:

**Step 1 — Diagnose** using Scan Tool + basic access tools + workshop manuals (optional)
**Step 2 — Repair/Replace** correct parts and tools at component location
**Step 3 — Verify** using Scan Tool again
**Step 4 — Operational** or return to Step 2

Without correct manual: diagnosis less precise, chance of incorrect repair.
Bypass mechanic: force open frozen door with crowbar, damages door further.

---

*Project Orion Design Document v6.0*
*March 2026*
