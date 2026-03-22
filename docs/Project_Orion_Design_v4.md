# PROJECT ORION
## Space Survival Simulator
### Master Design & Development Document
**Version 4.0 — March 2026**

---

## 1. PROJECT OVERVIEW

### Concept
Project Orion is a space survival simulator set in 2276. The player operates a solo trader/explorer spacecraft named the **Tempus Fugit**, captained by **Jack Harrow**. Core gameplay revolves around maintaining ship systems, repairing failures, and surviving deep space. This is a serious "slow burner" simulator — not an arcade game. Systems fail, cascade, and the player must diagnose and fix them before things get fatal.

### History
- **Project Dark Star** — previous iteration in Python/Arcade. Got a long way (player, inventory, rooms, doors, security panels, basic repair, life support scaffolding, chronometer). Abandoned due to Arcade's text rendering limitations and UI inflexibility.
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

### Project Lineage

**Project Orion Game is the convergence of two previous codebases:**

- **Project Dark Star** (Python/Arcade) — contributed the game logic: rooms, doors, security panels, player, inventory, items, command system, repair logic, chronometer. Abandoned due to Arcade's text rendering limitations and UI inflexibility.

- **Project Orion** (Flask prototype) — contributed the ship systems: electrical power distribution, break/repair mechanics, power path tracing, SVG diagnostic map. Built as a proof of concept before the game UI existed.

**Project Orion Game absorbs both.** Once the electrical system from Project Orion and the remaining game logic from Project Dark Star are fully integrated, both old codebases are archived and forgotten. Project Orion Game stands alone as the complete product.

Progress toward that goal:
- Dark Star game logic: **rooms, doors, security panels, command system, chronometer** — ported ✅
- Dark Star game logic: **player, inventory, items, basic repair** — ported ✅
- Dark Star game logic: **examine, terminals, full repair** — pending (Phases 13-16)
- Project Orion electrical system — pending (Phase 15)

There are two legacy codebases for reference only:

- **`project_orion`** — the electrical testing prototype. Built Phases 1-5: electrical system, break/repair mechanics, SVG diagnostic map. This is a standalone prototype, not the game. **Do not confuse with `project_orion_game`.**
- **`project_orion_game`** — the actual game. This document describes it. Phases 6+ are built here.

### Phases 1-5 — Electrical System Prototype ✅ (in `project_orion`)

This is fully built and tested in the separate `project_orion` codebase. It will be integrated into `project_orion_game` in Phase 15.

**What was built:**
- Complete electrical system (`electrical_system.py`) — 17 rooms, 28 cables, 16 breakers, 4 panels, 3 power sources
- Hierarchical power distribution: reactor → main panel → sub-panels → rooms
- Power path tracing — any break in the chain cuts power to all downstream rooms
- Battery auto-activation — BAT-LS-01 and BAT-MF-01 auto-activate when mains power lost
- Break API (`POST /api/systems/electrical/break/<id>`) — can break any cable, breaker, panel, reactor, or battery
- Interactive SVG diagnostic map (`ship_layout.svg`) — live room colours (green=powered, red=unpowered), draggable floating window, reactor/battery icons, pan/zoom/tooltips
- All 17 rooms correctly powered and traced

**Electrical architecture:**

```
reactor_core (25kW, Engineering)
  └── PWC-ENG-01 → PNL-ENG-MAIN (main panel, Engineering)
        ├── FUS-ENG-01 → PWC-ENG-02 → life_support
        │     + BAT-LS-01 (auto-backup)
        ├── FUS-ENG-02 → PWC-ENG-03/PWC-MC-06 → PNL-MC-SUB-A (Main Corridor)
        │     ├── PWC-MC-04 → main_corridor
        │     ├── FUS-MC-01 → PWC-MC-01 → crew_cabin
        │     ├── FUS-MC-02 → PWC-MC-02 → captains_quarters
        │     └── FUS-MC-03 → PWC-MC-03 → mainframe_room
        │           + BAT-MF-01 (auto-backup)
        ├── FUS-ENG-03 → PWC-ENG-04/PWC-MC-07/PWC-SC-05 → PNL-SC-SUB-B (Sub Corridor)
        │     ├── PWC-SC-06 → sub_corridor
        │     ├── FUS-SC-01 → PWC-SC-01 → head
        │     ├── FUS-SC-02 → PWC-SC-02 → cargo_bay
        │     ├── FUS-SC-03 → PWC-SC-03 → storage_room
        │     └── FUS-SC-04 → PWC-SC-04 → airlock
        ├── FUS-ENG-04 → PWC-ENG-05/PWC-MC-08/PWC-REC-05 → PNL-REC-SUB-C (Recreation Room)
        │     ├── PWC-REC-06 → recreation_room
        │     ├── FUS-REC-01 → PWC-REC-01 → med_bay
        │     ├── FUS-REC-02 → PWC-REC-02 → hypersleep_chamber
        │     ├── FUS-REC-03 → PWC-REC-03 → galley
        │     └── FUS-REC-04 → PWC-REC-04 → cockpit
        └── FUS-ENG-05 → PWC-ENG-06 → engineering
```

**Known issue:** `storage_room` is mapped to `PNL-SC-SUB-B` (correct per above) but `electrical.json` has a wiring bug mapping it to the wrong panel ID. Fix when integrating.

**When integrated into `project_orion_game` (Phase 15):**
- Every electrical component in the ship requires power or it does not work
- **Door panels receive power from the room they are in** — no room power = panel dead = door frozen in current state, regardless of whether the panel is damaged or not
- This adds a critical new failure mode: cutting power to a room disables all door panels in that room
- The SVG diagnostic map will be accessible via ship terminals (not auto-opening)
- Room power state will affect descriptions, terminal availability, and system functionality

### Phase 6 — Splash screen + game shell ✅
- Splash screen with Dark Star background image, ship name, click/Enter to start
- Fade transition to main game screen
- Calls `/api/game/new` then redirects to `/game`
- Browser auto-opens on `main.py` launch

### Phase 7 — Ship + room loading ✅
- `Ship` loads all 17 rooms from `ship_rooms.json`
- `Room` instances with id, name, description, exits, background_image, temperature
- Player placed in `STARTING_ROOM` (set in `config.py`)
- Room image displayed in left panel with `image_missing.png` fallback
- Room name shown as title in description panel

### Phase 8 — Room description rendering ✅
- Description panel renders automatically on room load — no `look` command needed
- Markup parser handles `*exit*` → cyan span and `%object%` → cyan span
- `data-exit` and `data-object` attributes on spans — hooks for future hover/click
- `white-space: nowrap` on highlights prevents mid-phrase line breaks
- Paragraph-per-string layout with margin spacing

### Phase 9 — Movement ✅
- `go`, `enter`, `move` commands
- Exit matching by key, label, or shortcut
- `POST /api/command` — single endpoint for all player commands
- `CommandHandler` — longest-match verb registry
- `MovementHandler` — handles all movement

### Phase 10 — Door system ✅

#### Door model
- Three states: **open**, **closed**, **locked**
- `Door` class with `door_open`, `door_locked`, `security_level`, `pin`, `pin_attempts`
- `SecurityPanel` class — per-side panel, `is_broken`, `repair_progress` (runtime only)
- `SecurityLevel` enum: NONE(0), KEYCARD_LOW(1), KEYCARD_HIGH(2), KEYCARD_HIGH_PIN(3)

#### Door data
- `door_status.json` — 16 connections, structural only (room IDs, security levels, panel IDs)
- No damage, no PINs, no door states in this file — all pristine
- `initial_ship_state.json` — overrides applied at game init (door states, panel damage, PINs)

#### Door commands
- `go/enter <room>` — open door: silent entry. Closed door: opens, enter, closes behind. Locked door: shows closed hatch image + locked message.
- `open <room>` — instant if unlocked, card swipe if locked. Player stays.
- `close <room>` — instant, no card needed. Player stays.
- `lock <room>` — card swipe + PIN if level 3. Player stays.
- `unlock <room>` — card swipe + PIN if level 3. Player stays.

#### Card swipe flow
- 5 second real-world wait (`CARD_SWIPE_REAL_SECONDS` in `config.py`)
- Input locked during wait
- "SCANNING ACCESS CARD" animation with 5 pulsing cyan dots in response panel
- Panel image shown in left panel during scan (level 1/2/3 variants)
- On success: open or closed hatch image for `DOOR_IMAGE_DISPLAY_MS` then room image restores
- Level 3 doors prompt for PIN after successful card swipe
- 3 failed PINs: card is not removed — it is swapped for a damaged version (`id_card_high_sec_damaged`) that no longer grants access. The player keeps the physical card.

#### Card access rules
- High security card works on all levels (1, 2, 3)
- Low security card works on level 1 only
- Card checks use real player inventory (no debug flags)

#### Door images
- Stored in `frontend/static/images/doors/`
- `panel_level1_swipe.png`, `panel_level2_swipe.png`, `panel_level3_swipe_pin.png`
- `open_hatch.png`, `closed_hatch.png`
- `panel_levelX_swipe_damaged.png` — shown during repair and on blocked interaction

#### Exit hover tooltips
- Hover over cyan `*exit*` links in description → tooltip shows door state
- Green = open, grey = closed, orange = locked
- Tooltip flips left/up if near screen edge

### Phase 11 — Damaged door panels + basic repair ✅

- Broken panel freezes door in current state
- `go/enter` on broken panel + closed/locked → blocked, damaged panel image shown persistently
- `go/enter` on broken panel + open → pass freely, no message about panel
- `open`, `close`, `lock`, `unlock` on broken panel → all blocked, damaged panel image shown
- `repair panel [target]` — 8s real wait, 30 game minutes advance
- During repair: damaged panel image shown with "REPAIRING ACCESS PANEL" animation
- On completion: repaired panel image shown briefly, then room image restores
- `DEBUG_HAS_REPAIR_TOOL` flag in `config.py` — replaced by real tool check in Phase 16

### Phase 12 — Ship state, player, inventory ✅

#### Ship state architecture
- `door_status.json` — pristine structural data only. No damage, no PINs, no door states.
- `initial_ship_state.json` — scenario overlay applied at game init. Sets door open/locked states, panel damage, and level 3 PINs. Only entries that differ from pristine.
- Ship loads pristine, overlay applied on top. Missing overlay file is silently skipped.

#### Item data files
```
data/
  items/
    tools.json          — portable tool definitions
    wearables.json      — equippable item definitions
    misc_items.json     — ID cards and misc items
    consumables.json    — wire and consumable definitions
    fixed_objects.json  — fixed object definitions (terminals, lockers, cabinets)
  ship/
    structure/
      ship_items.json   — explicit item placement (room floors and container contents)
      player_items.json — player starting inventory and equipped slots
```

#### Item hierarchy
```
Interactable
├── PortableItem      — takeable, carriable, equippable
│   └── UtilityBelt   — wearable belt, accepts clipped attachments (PAM etc.)
└── FixedObject       — permanently attached to a room, cannot be taken
    └── StorageUnit   — fixed container that holds PortableItems
```

#### Player
- Inventory list (loose carried items), equipment slots (head, body, torso, waist, feet)
- Carry weight limit (10kg default)
- `has_card_for_level(n)` — real inventory check replacing debug flags
- Card invalidation: swaps `id_card_high_sec` → `id_card_high_sec_damaged` in inventory

#### Commands
- `take / get / pick up <item>` — take portable item from room floor
- `drop <item>` — drop inventory item onto room floor
- `debug_inventory` — dump player inventory and equipped slots to response panel
- Room description updates immediately on take/drop

#### Item loading
- `backend/loaders/item_loader.py` — master registry: reads all item JSON files, returns `item_id → instance`
- Ship loads fixed objects from `fixed_objects.json` into rooms
- Ship places portables into rooms/containers from `ship_items.json`
- GameManager loads player items from `player_items.json`

---

## 4. FOLDER STRUCTURE (CURRENT)

```
project_orion_game/
│
├── main.py
├── config.py                        ← All constants and file paths
├── requirements.txt
│
├── backend/
│   ├── models/
│   │   ├── game_manager.py          ← Central coordinator, player, card state
│   │   ├── ship.py                  ← Ship loader, door/object attachment, state overlay
│   │   ├── room.py                  ← Room class
│   │   ├── door.py                  ← Door + SecurityPanel classes
│   │   ├── interactable.py          ← Interactable hierarchy
│   │   ├── player.py                ← Player inventory and equipment
│   │   └── chronometer.py           ← Game clock
│   │
│   ├── handlers/
│   │   ├── base_handler.py          ← Shared utilities
│   │   ├── command_handler.py       ← Verb registry (longest-match)
│   │   ├── movement_handler.py      ← go, enter, move
│   │   ├── door_handler.py          ← open, close, lock, unlock
│   │   ├── repair_handler.py        ← repair panel
│   │   └── item_handler.py          ← take, drop, debug_inventory
│   │
│   ├── loaders/
│   │   └── item_loader.py           ← Portable item registry from JSON files
│   │
│   └── api/
│       ├── game.py                  ← /api/game/* — state, new game, room, tick
│       └── command.py               ← /api/command and sub-routes
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
│       │
│       ├── js/
│       │   ├── core/
│       │   │   ├── constants.js
│       │   │   ├── api.js
│       │   │   └── loop.js
│       │   └── screens/
│       │       ├── splash.js
│       │       └── game.js
│       │
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
    │   └── fixed_objects.json
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
CARD_SWIPE_GAME_MINUTES    = 0

DEBUG_HAS_REPAIR_TOOL      = True   # Replace with real tool check in Phase 16

ROOMS_JSON_PATH         = 'data/ship/structure/ship_rooms.json'
DOORS_JSON_PATH         = 'data/ship/structure/door_status.json'
INITIAL_STATE_JSON_PATH = 'data/ship/structure/initial_ship_state.json'
SHIP_ITEMS_JSON_PATH    = 'data/ship/structure/ship_items.json'
PLAYER_ITEMS_JSON_PATH  = 'data/ship/structure/player_items.json'
FIXED_OBJECTS_JSON_PATH = 'data/items/fixed_objects.json'
ITEM_FILES = [
    'data/items/tools.json',
    'data/items/wearables.json',
    'data/items/misc_items.json',
    'data/items/consumables.json',
]
```

---

## 6. THE GAME LOOP — ARCHITECTURE

### Two types of player actions:

**Instant actions** — `open galley`, `take wrench`, `drop card`
- No game time passes
- Backend responds immediately
- Frontend stays unlocked

**Timed actions** — repairs, card swipes
- Backend returns `real_seconds` and `game_minutes`
- Frontend locks input, shows feedback
- Frontend waits real-world seconds
- Frontend calls back to complete action
- Backend advances ship time
- Frontend unlocks

### Standard API response shape:
```json
{
  "response": "You open the door to Galley.",
  "action_type": "instant",
  "lock_input": false,
  "ship_time": "01-01-2276  00:15"
}
```

### Ship time:
- `Chronometer` in Python owns the truth
- Advances 1 game minute per real minute via `POST /api/game/tick`
- Also advances on timed actions

---

## 7. THE COMMAND SYSTEM

Single endpoint: `POST /api/command`

| Verb | Handler |
|------|---------|
| `go`, `enter`, `move` | MovementHandler |
| `open` | DoorHandler |
| `close` | DoorHandler |
| `lock` | DoorHandler |
| `unlock` | DoorHandler |
| `repair panel`, `repair` | RepairHandler |
| `take`, `get`, `pick up` | ItemHandler |
| `drop` | ItemHandler |
| `debug_inventory` | ItemHandler |

---

## 8. MAIN GAME SCREEN LAYOUT

```
┌─────────────────────────────────────────────────────────────┐
│                    ROOM IMAGE (45%)          │ DESCRIPTION   │
│                                              │ (flex:3,      │
│                                              │  scrollable)  │
│                                              ├───────────────┤
│                                              │ RESPONSE AREA │
│                                              │ (flex:2,      │
│                                              │  scrollable)  │
│                                              ├───────────────┤
│                                              │ COMMAND INPUT │
│                                              │ (fixed 48px)  │
├──────────────────────────────────────────────┴───────────────┤
│ EVENT STRIP (70px)  [events left]        [ship name + time]  │
└─────────────────────────────────────────────────────────────┘
```

### Colour palette:
| Variable | Hex | Use |
|----------|-----|-----|
| `--col-text` | `#bababa` | Default text |
| `--col-title` | `#27e6ec` | Cyan — titles, exits, fixed objects |
| `--col-portable` | `#bea5cd` | Purple — portable items |
| `--col-alert` | `#ff8c00` | Orange — alerts, locked doors |
| `--col-prompt` | `#00ff00` | Green — command prompt, open doors |
| `--col-response` | `#7e97ae` | Muted blue — player input echo |

---

## 9. SHIP ROOMS

17 rooms loaded from `ship_rooms.json`. Fixed objects are referenced by ID in the `fixed_objects` array of each room — definitions live in `data/items/fixed_objects.json`.

| Room | ID |
|------|-----|
| Captain's Quarters | `captains_quarters` |
| Crew Cabin | `crew_cabin` |
| Bathroom/Head | `head` |
| Galley | `galley` |
| Recreation Room | `recreation_room` |
| Cockpit | `cockpit` |
| Storage Room | `storage_room` |
| Hyper-sleep Chamber | `hypersleep_chamber` |
| Med-Bay | `med_bay` |
| Main Corridor CH-1 | `main_corridor` |
| Mainframe Room | `mainframe_room` |
| Sub Corridor CH-2 | `sub_corridor` |
| Engineering | `engineering` |
| Propulsion Bay | `propulsion_bay` |
| Life Support | `life_support` |
| Airlock | `airlock` |
| Cargo Bay | `cargo_bay` |

### Description markup:
- `*exit name*` → cyan bold span, `data-exit` attribute
- `%object name%` → cyan bold span, `data-object` attribute
- Exit spans have working hover tooltips showing door state
- Object spans have `data-object` hook — behaviour TBD (see Section 15)

---

## 10. DOOR CONNECTIONS

16 doors in `door_status.json`. Initial states set in `initial_ship_state.json`.

| Connection | Level |
|-----------|-------|
| captains_quarters ↔ main_corridor | 2 |
| crew_cabin ↔ main_corridor | 1 |
| recreation_room ↔ galley | 1 |
| recreation_room ↔ cockpit | 2 |
| recreation_room ↔ main_corridor | 1 |
| recreation_room ↔ med_bay | 1 |
| recreation_room ↔ storage_room | 1 |
| med_bay ↔ hypersleep_chamber | 1 |
| main_corridor ↔ sub_corridor | 1 |
| main_corridor ↔ engineering | 2 |
| main_corridor ↔ mainframe_room | 3 |
| sub_corridor ↔ cargo_bay | 1 |
| sub_corridor ↔ head | 1 |
| engineering ↔ life_support | 3 |
| engineering ↔ propulsion_bay | 3 |
| cargo_bay ↔ airlock | 3 |

---

## 11. BUILD PLAN — NEXT PHASES

### Phase 13 — Examine + fixed objects ← NEXT
- `examine <item>` — works on room floor items, inventory items, and open container contents
- `examine <object>` — works on fixed objects in the room
- `open <container>` / `close <container>` — open/close storage units
- Container contents shown in `YOU SEE` when open (see Section 15 for display design)
- Fixed objects shown in `YOU SEE` (see Section 15 for display design)

### Phase 14 — Terminals
- `use terminal` / `use <terminal name>`
- Screen splits: terminal left, output right
- Terminal commands: ship status, door map, electrical status
- Diagnostic map accessible via terminal (not auto-opening)

### Phase 15 — Electrical integration
- Connect electrical system to game loop
- Room power affects lighting descriptions
- Life support room losing power → scrubber efficiency drops
- Battery drain over time

### Phase 16 — Full repair system
See Section 14 for complete design. Replaces `DEBUG_HAS_REPAIR_TOOL` with real tool checks.

### Phase 17+ — Events, life support, navigation...

---

## 12. KNOWN ISSUES / DEFERRED

- **Storage room wiring bug** — `electrical.json` in `project_orion` maps `storage_room` to wrong panel ID. Fix when integrating electrical system.
- **Electrical integration** — full electrical system from `project_orion` needs porting. Room power affects door panels, terminals, life support, all systems. Phase 15.
- **Random item placement** — `ship_items.json` currently uses explicit placement only. A procedural scatter function for certain item categories is planned but deferred. When implemented it should be a deliberate design decision, not a default.
- **Battery drain** — battery bar icons in SVG map are ready. Needs game loop implementation.
- **Clickable exits** — `data-exit` attributes on all exit spans. Wire up click → `go <room>` when ready.
- **Look command** — deferred. Description auto-renders on room load. `look` may be added later as "look harder" to find hidden items.
- **Bypass mechanic** — force open a frozen door without repairing the panel. Deferred to full repair system phase.
- **PAM (Personal Atmospheric Monitor)** — clips to utility belt, shows O₂/temp in event strip. Dormant until life support is implemented.
- **Inventory screen** — full UI screen for inventory management. Deferred to after examine is working.
- **Equip/unequip commands** — deferred. Player starts with items equipped via `player_items.json`.

---

## 13. RULES FOR DEVELOPMENT

1. **Upload the current zip at the start of every session** — never work from memory
2. **Read the code before changing it** — ask to see files before editing
3. **Give complete files for large changes, inline instructions for small ones** — zip files for anything more than a few lines; show exact find/replace instructions for 1-3 line changes
4. **Minimal targeted changes** — no rewrites, no "while I'm in here" improvements. Flag improvements separately and ask before making them.
5. **Only create what we need right now** — port Dark Star files only when actually needed
6. **No god files** — grouped logically by domain
7. **Backend owns all game state** — JS is display only. Sends strings, renders responses.
8. **All colours in CSS variables** — never hardcode colours in JS or HTML
9. **All JS timeouts in `constants.js`** — `DOOR_IMAGE_DISPLAY_MS` etc.
10. **All Python durations in `config.py`** — `CARD_SWIPE_REAL_SECONDS` etc.
11. **Debate bad ideas** — push back if something seems wrong or inconsistent
12. **Never add "type X to fix it" hints** — messages must be immersive. The player discovers commands.
13. **Small changes — show inline instructions, not files.** If only a few lines change, show exactly where to find them and what to replace.

---

## 14. FULL REPAIR SYSTEM — TARGET DESIGN

This is the intended end-state repair system. Phase 11 implements a simplified "magic repair" placeholder. The full system is built out incrementally from Phase 16 onwards once inventory, tools, and parts are in place.

### Design Philosophy
Repair is the core gameplay loop. It should feel like real diagnostic work — methodical, rewarding, occasionally frustrating. The right tools and knowledge make it possible. The wrong approach wastes time and can make things worse.

### The Four Steps

**Step 1 — Diagnose**

The player must diagnose the fault before attempting repair. This requires:

- **Diagnostic tool** (Scan Tool) — a handheld device with oscilloscope, scan reader, bi-directional controls, and onboard diagnostic capability
- **Basic access tools** — screwdrivers and other basic tools to remove panels and gain physical access to the component
- **Workshop manuals** (optional but important) — e.g. "Reactor Manual — Model 14". Without the correct manual, diagnosis is less effective and may miss faults or misidentify them.

Diagnosis takes time (TBD) and produces a fault report: what failed, what parts are needed to fix it, what tools are required.

Without the diagnostic tool: the player can still attempt a repair but is guessing — higher chance of failure and possible additional damage.

Without the correct manual: diagnosis succeeds but is less precise — fault description is vaguer, parts list may be incomplete or incorrect.

**Step 2 — Repair / Replace**

Once the fault is diagnosed, the player gathers the required parts and tools and performs the repair. This requires:

- Correct replacement parts (from storage units, cargo bay, or fabricated)
- Correct tools (beyond basic access tools — may require specialised equipment)
- The player must physically be at the component location

**Step 3 — Verification**

After repair, the system must be verified using the diagnostic tool again. Without the correct manual there is a chance of incorrect repair — the wrong part was replaced or the repair was done incorrectly — which may cause additional damage or leave the original fault unresolved.

**Step 4 — System operational**

If verification passes cleanly: component is fully restored. If verification fails: return to Step 2. Time and parts consumed. Stress increases.

### Bypass Mechanic (deferred)
For frozen doors: the player can attempt to physically force the door open without repairing the panel. Requires a crowbar or engineering kit. The door is damaged further — cannot be closed again without full repair. Only possible on unlocked frozen doors.

---

## 15. ROOM INTERACTION DISPLAY — DESIGN DISCUSSION

This section captures an open design question to be resolved in Phase 13.

### The issue
Orion currently has two ways to communicate interactive objects to the player:

1. **Description prose** — `%object%` markup renders fixed objects as cyan highlighted text inline in the room description. E.g. *"A large parts storage unit sits next to a workbench."* Hovering these spans has the `data-object` hook but currently does nothing.

2. **`YOU SEE` section** — currently shows only loose portable items on the room floor (purple text).

### Dark Star's approach (reference)
Dark Star listed all interactive objects under `YOU SEE` — both fixed objects (cyan) and loose portables (purple). When a container was opened, it expanded inline to show its contents: *"Tool Storage Cabinet (open): Scan Tool, Adjustable Wrench..."*. This was clear and functional.

### Orion's advantage
Orion has interactive hover on `*exit*` spans — hovering a door exit shows its state (open/closed/locked) in a tooltip. The `%object%` spans have the same hook available. This didn't exist in Dark Star.

### Options under consideration

**Option A — Dark Star approach**
List all fixed objects and loose portables under `YOU SEE`. Fixed objects show open/closed state and contents when open. No hover behaviour on object spans. Simple and proven.

**Option B — Hover-driven**
No `YOU SEE` section for fixed objects. Object spans in description prose show state and contents on hover. Player discovers everything through prose. Cleaner visually but less discoverable.

**Option C — Hybrid (current leaning)**
`YOU SEE` lists loose portable items only (things you can pick up — purple). Fixed objects stay in prose with hover tooltips showing state and contents when open. The two systems serve different purposes: `YOU SEE` = "you can pick this up", hover = "you can interact with this fixed thing".

### Decision
**Not yet finalised.** To be decided and implemented in Phase 13. Whichever approach is chosen, it should be consistent throughout the game. The `data-object` hook is already in place on all object spans — no structural changes needed to implement any of the above options.

---

*Project Orion Design Document v4.0*
*March 2026*
