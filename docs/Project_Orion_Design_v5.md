# PROJECT ORION
## Space Survival Simulator
### Master Design & Development Document
**Version 5.0 — March 2026**

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
- Dark Star game logic: **examine, full repair, terminals** — pending
- Project Orion electrical system — pending (Phase 15)

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
- `DEBUG_HAS_REPAIR_TOOL` in `config.py` — replaced by real tool check in Phase 16

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
- Inventory, equipment slots (head, body, torso, waist, feet), carry weight (10kg)
- `has_card_for_level(n)` — real inventory check
- Card invalidation: swaps to damaged version

#### Commands
- `take / get / pick up <item>`, `drop <item>`, `debug_inventory`
- Drop blocked if room has no Surface

### Phase 13a — Fixed object data restructure ✅
- `fixed_objects.json` split into `terminals.json`, `storage_units.json`, `surfaces.json`
- `Surface` and `Terminal` classes added to `interactable.py`
- `ship._load_fixed_objects` instantiates correct class per source file
- `ship_rooms.json` updated with `!terminal!` and `#surface#` markup throughout
- All rooms have at least one surface except: head, cockpit, hypersleep chamber, corridors, mainframe, propulsion bay, life support, airlock

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
│   │   ├── room.py
│   │   ├── door.py
│   │   ├── interactable.py
│   │   ├── player.py
│   │   └── chronometer.py
│   │
│   ├── handlers/
│   │   ├── base_handler.py
│   │   ├── command_handler.py
│   │   ├── movement_handler.py
│   │   ├── door_handler.py
│   │   ├── repair_handler.py
│   │   └── item_handler.py
│   │
│   ├── loaders/
│   │   └── item_loader.py
│   │
│   └── api/
│       ├── game.py
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
| `open`, `close`, `lock`, `unlock` | DoorHandler |
| `repair panel`, `repair` | RepairHandler |
| `take`, `get`, `pick up` | ItemHandler |
| `drop` | ItemHandler |
| `debug_inventory` | ItemHandler |

---

## 8. MAIN GAME SCREEN LAYOUT

```
┌─────────────────────────────────────────────────────────────┐
│                    ROOM IMAGE (45%)          │ DESCRIPTION   │
│                                              │ (scrollable)  │
│                                              ├───────────────┤
│                                              │ RESPONSE AREA │
│                                              │ (scrollable)  │
│                                              ├───────────────┤
│                                              │ COMMAND INPUT │
├──────────────────────────────────────────────┴───────────────┤
│ EVENT STRIP         [events]             [ship name + time]  │
└─────────────────────────────────────────────────────────────┘
```

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
| `#surface#` | Surface | Grey bold (empty) / Purple bold (has items) | "Empty" / item count | Examine or expand Layer 3 |

### Description layers
1. **Static prose** — authored JSON, never changes
2. **Layer 2** — open container contents (cyan container name, purple items)
3. **Layer 3** — surface contents when expanded (purple surface name, purple items)

### Drop behaviour
- Items dropped in a room land on a randomly selected Surface
- Drop blocked if room has no Surface: *"There is nowhere to put that here."*

---

## 10. SHIP ROOMS

17 rooms. Rooms with no surfaces (drop blocked): head, cockpit, hypersleep chamber, main corridor, sub corridor, mainframe room, propulsion bay, life support, airlock.

---

## 11. BUILD PLAN — NEXT PHASES

### Phase 13b — Markup parser + hover tooltips ← NEXT
- Update `parseMarkup` in `game.js` to handle all four markup types
- Each type gets distinct CSS class and `data-` attribute
- Backend room data includes object states (container open/closed, surface has_items)
- Hover tooltips for containers, terminals and surfaces
- Surface span colour driven by `has_items` state from backend

### Phase 13c — Click handlers + Layer 2/3 rendering
- Container click → `open`/`close` command (backend)
- Terminal click → `use <terminal>`
- Surface click → expand/collapse Layer 3
- Layer 2: open container contents rendered below prose
- Layer 3: surface contents rendered when expanded
- `open`/`close` container commands wired up end to end

### Phase 14 — Terminals
- `use terminal` / `use <terminal name>`
- Terminal commands: ship status, door map
- Diagnostic map accessible via terminal

### Phase 15 — Electrical integration
- Connect electrical system from `project_orion` prototype
- Room power affects door panels, terminals, life support

### Phase 16 — Full repair system
- Replace `DEBUG_HAS_REPAIR_TOOL` with real tool checks
- Diagnosis, repair, verification flow
- See Section 14 for complete design

### Phase 17+ — Events, life support, navigation...

---

## 12. KNOWN ISSUES / DEFERRED

- **Multiple damaged panels in same room** — repair panel clarification logic exists but has never been tested with multiple broken panels simultaneously. Verify when this scenario is possible.
- **Storage room wiring bug** — `electrical.json` in `project_orion` maps `storage_room` to wrong panel ID. Fix when integrating.
- **Random item placement** — explicit placement only for now. Procedural scatter deferred.
- **Battery drain** — SVG map icons ready, game loop implementation deferred.
- **Clickable exits** — `data-exit` on all exit spans. Click behaviour deferred (exits are hover-only by design).
- **Look command** — deferred.
- **Bypass mechanic** — force open frozen door without repair. Deferred.
- **PAM** — clips to utility belt, shows O₂/temp. Dormant until life support implemented.
- **Inventory screen** — full UI deferred until after examine is working.
- **Equip/unequip commands** — deferred.
- **`put <item> on <surface>`** — explicit surface placement command. Deferred to Phase 13c.

---

## 13. RULES FOR DEVELOPMENT

1. **Upload current codebase at start of every session**
2. **Read the code before changing it**
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

Phase 11 implements magic repair. Full system from Phase 16:

**Step 1 — Diagnose** using Scan Tool + basic access tools + workshop manuals (optional)
**Step 2 — Repair/Replace** correct parts and tools at component location
**Step 3 — Verify** using Scan Tool again
**Step 4 — Operational** or return to Step 2

Without correct manual: diagnosis less precise, chance of incorrect repair.
Bypass mechanic: force open frozen door with crowbar, damages door further.

---

*Project Orion Design Document v5.0*
*March 2026*
