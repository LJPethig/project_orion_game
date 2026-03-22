# PROJECT ORION
## Space Survival Simulator
### Master Design & Development Document
**Version 3.0 — March 2026**

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
- Dark Star game logic: **player, inventory, items, repair** — pending (Phases 12-16)
- Project Orion electrical system — pending (Phase 15)
There are two codebases:

- **`project_orion`** — the electrical testing prototype. Built Phases 1-5: electrical system, break/repair mechanics, SVG diagnostic map. This is a standalone prototype, not the game. **Do not confuse with `project_orion_game`.**
- **`project_orion_game`** — the actual game. This document describes it. Phases 6+ are built here. The electrical system from `project_orion` will be integrated here in a future phase.

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
- Portable items section renders below description when room has items (Phase 10+)

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
- `door_status.json` — 16 connections, all room IDs use underscores
- Fields: `door_open`, `door_locked`, `security_level`, `pin` (level 3 only)
- `repair_progress` removed — runtime state only, not in JSON
- `damaged` field remains for testing — future: move to `starting_damage.json`

#### Door commands
- `go/enter <room>` — open door: silent entry. Closed door: opens, enter, closes behind. Locked door: shows closed hatch image + "The X door is locked." Image stays (no revert — player is still facing a locked door)
- `open <room>` — instant if unlocked, card swipe if locked. Player stays.
- `close <room>` — instant, no card needed. Player stays.
- `lock <room>` — card swipe + PIN if level 3. Player stays.
- `unlock <room>` — card swipe + PIN if level 3. Player stays.

#### Card swipe flow
- 5 second real-world wait (`CARD_SWIPE_REAL_SECONDS` in `config.py`)
- Input locked during wait
- "SCANNING ACCESS CARD" animation with 5 pulsing cyan dots in response panel
- Panel image shown in left panel during scan (level 1/2/3 variants)
- On success: open or closed hatch image for `DOOR_IMAGE_DISPLAY_MS` (in `constants.js`) then room image restores
- Level 3 doors prompt for PIN after successful card swipe
- 3 failed PINs invalidates card, restores room image immediately

#### Card access rules
- High security card works on all levels (1, 2, 3)
- Low security card works on level 1 only
- Debug flags: `DEBUG_HAS_LOW_SEC_CARD`, `DEBUG_HAS_HIGH_SEC_CARD` in `config.py`
- Card state lives on `game_manager` instance — `invalidate_card()` sets flags false at runtime
- When inventory is implemented: swap debug flags for real item checks

#### Door images
- Stored in `frontend/static/images/doors/`
- `panel_level1_swipe.png`, `panel_level2_swipe.png`, `panel_level3_swipe_pin.png`
- `open_hatch.png`, `closed_hatch.png`
- `panel_levelX_swipe_damaged.png` — present but not yet used (needed for Phase 11)

#### Exit hover tooltips
- Hover over cyan `*exit*` links in description → tooltip shows door state
- Green = open, grey = closed, orange = locked
- Tooltip flips left/up if near screen edge

#### Consistency note
All door commands (open, close, lock, unlock) change door state only — player never moves automatically. `go/enter` is the only movement command. This is intentional and consistent.

---

## 4. FOLDER STRUCTURE (CURRENT)

```
project_orion_game/
│
├── main.py                          ← Flask entry point, registers blueprints
├── config.py                        ← All constants
├── requirements.txt
│
├── backend/
│   ├── models/
│   │   ├── game_manager.py          ← Central coordinator, card state
│   │   ├── ship.py                  ← Ship loader, door attachment
│   │   ├── room.py                  ← Room class
│   │   ├── door.py                  ← Door + SecurityPanel classes
│   │   └── chronometer.py           ← Game clock (30-day months, 360-day year)
│   │
│   ├── handlers/
│   │   ├── base_handler.py          ← Shared: card check, exit finding, swipe response
│   │   ├── command_handler.py       ← Verb registry (longest-match)
│   │   ├── movement_handler.py      ← go, enter, move
│   │   └── door_handler.py          ← open, close, lock, unlock
│   │
│   └── api/
│       ├── game.py                  ← /api/game/* — state, new game, room, tick
│       └── command.py               ← /api/command — all player commands
│                                       /api/command/swipe — post card swipe
│                                       /api/command/pin — PIN entry
│
├── frontend/
│   ├── templates/
│   │   ├── splash.html
│   │   └── game.html
│   │
│   └── static/
│       ├── css/
│       │   ├── splash.css
│       │   └── game.css             ← All colours as CSS variables matching Dark Star
│       │
│       ├── js/
│       │   ├── core/
│       │   │   ├── constants.js     ← Frontend constants (DOOR_IMAGE_DISPLAY_MS etc.)
│       │   │   ├── api.js           ← All fetch calls
│       │   │   └── loop.js          ← Polling (10s) + real-time clock tick (60s)
│       │   └── screens/
│       │       ├── splash.js
│       │       └── game.js          ← Main orchestrator
│       │
│       └── images/
│           ├── image_missing.png    ← Universal fallback
│           ├── start_screen.png
│           ├── rooms/               ← 15 room images
│           └── doors/               ← Panel and hatch images
│
└── data/
    └── ship/
        └── structure/
            ├── ship_rooms.json      ← 17 rooms, prose descriptions, markup
            └── door_status.json     ← 16 door connections
```

---

## 5. CONFIG.PY — KEY CONSTANTS

```python
SHIP_NAME                = "Tempus Fugit"
PLAYER_NAME              = "Jack Harrow"
STARTING_ROOM            = "captains_quarters"
START_DATE_TIME          = (2276, 1, 1, 0, 0)

REPAIR_PANEL_REAL_SECONDS  = 8
REPAIR_PANEL_GAME_MINUTES  = 30
CARD_SWIPE_REAL_SECONDS    = 5

DEBUG_HAS_LOW_SEC_CARD   = True
DEBUG_HAS_HIGH_SEC_CARD  = True

ROOMS_JSON_PATH          = 'data/ship/structure/ship_rooms.json'
DOORS_JSON_PATH          = 'data/ship/structure/door_status.json'
```

---

## 6. THE GAME LOOP — ARCHITECTURE

### Two types of player actions:

**Instant actions** — `open galley`, `close cockpit`, `examine locker`
- No game time passes
- Backend responds immediately
- Frontend stays unlocked

**Timed actions** — repairs, card swipes, waiting
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
- Advances 1 game minute per real minute via `POST /api/game/tick` (called by `loop.js` every 60s)
- Also advances on timed actions (repairs etc.)
- Displayed in event strip bottom right

---

## 7. THE COMMAND SYSTEM

Single endpoint: `POST /api/command`

The frontend sends a raw string. `CommandHandler` uses longest-match verb registry to route to the correct handler. The frontend never interprets commands — it sends strings and renders responses. All game logic stays in Python.

### Current verb registry:
| Verb | Handler |
|------|---------|
| `go`, `enter`, `move` | MovementHandler |
| `open` | DoorHandler |
| `close` | DoorHandler |
| `lock` | DoorHandler |
| `unlock` | DoorHandler |

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

### Colour palette (from Dark Star constants.py):
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

17 rooms loaded from `ship_rooms.json`:

| Room | ID |
|------|----|
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
- Both are hooks for future hover context menus

---

## 10. DOOR CONNECTIONS

16 doors in `door_status.json`:

| Connection | Level | Initially |
|-----------|-------|-----------|
| captains_quarters ↔ main_corridor | 1 | closed |
| crew_cabin ↔ main_corridor | 1 | closed |
| recreation_room ↔ galley | 1 | open |
| recreation_room ↔ cockpit | 2 | closed |
| recreation_room ↔ main_corridor | 1 | open |
| recreation_room ↔ med_bay | 1 | closed |
| recreation_room ↔ storage_room | 1 | open |
| med_bay ↔ hypersleep_chamber | 1 | closed |
| main_corridor ↔ sub_corridor | 1 | open |
| main_corridor ↔ engineering | 2 | closed |
| main_corridor ↔ mainframe_room | 2 | closed |
| sub_corridor ↔ cargo_bay | 1 | closed |
| sub_corridor ↔ head | 1 | open |
| engineering ↔ life_support | 3 | closed |
| engineering ↔ propulsion_bay | 2 | closed |
| cargo_bay ↔ airlock | 3 | closed |

---

## 11. BUILD PLAN — NEXT PHASES

### Phase 11 — Damaged door panels + basic repair ← NEXT
- `damaged: true` in `door_status.json` causes panel to start broken
- Broken panel: door frozen in current state (panel controls both lock AND actuation)
- `go/enter` on a door with broken panel + closed/locked → blocked, message explains panel damaged
- `go/enter` on a door with broken panel + open → pass freely (frozen open)
- `open`, `close`, `lock`, `unlock` on broken panel → all blocked, panel damaged message
- `repair panel <room>` command — `RepairHandler` (port from Dark Star)
- **Phase 11 uses magic repair** — no diagnosis, no parts, just a debug flag for "has tool"
- 8 second real-world wait (`REPAIR_PANEL_REAL_SECONDS`), 30 game minutes
- Damaged panel image shown during repair (`panel_levelX_swipe_damaged.png` — already in `frontend/static/images/doors/`)
- On completion: panel restored, door operational
- The full repair system (see Section 14) is the long-term target — Phase 11 is the scaffolding

### Phase 12 — Player + inventory
- Port `Player` from Dark Star — inventory list, equipment slots, carry weight
- Port `Interactable` hierarchy — `PortableItem`, `FixedObject`, `StorageUnit`
- Load items into rooms from JSON
- `take <item>`, `drop <item>`, `examine <item>`
- Portable items listed in description panel (purple)
- Inventory screen (replaces main screen, back button returns)
- Replace debug card flags with real card item checks

### Phase 13 — Examine + fixed objects
- `examine <object>` — detailed description
- Fixed objects listed in description (cyan)
- Storage units — `open <unit>`, `close <unit>`, list contents

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
See Section 14 for complete design.

### Phase 17+ — Events, life support, navigation...

---

## 12. KNOWN ISSUES / DEFERRED

- **Storage room wiring bug** — `electrical.json` in `project_orion` maps `storage_room` to wrong panel ID. Fix when integrating electrical system into `project_orion_game`.
- **Electrical integration** — the full electrical system from `project_orion` (Phases 1-5) needs to be ported into `project_orion_game`. When done, room power affects everything — door panels, terminals, life support, all systems. This is Phase 15 but the architecture must not preclude it.
- **Starting damage file** — `damaged` field currently in `door_status.json` for testing. Should move to a separate `starting_damage.json` that overrides pristine ship state at game init. Ship loads clean, damage file applied on top.
- **Battery drain** — battery bar icons in SVG map are ready. Needs game loop implementation.
- **Clickable exits** — `data-exit` attributes already on all exit spans. Wire up click → `go <room>` when ready.
- **Look command** — deferred. Description auto-renders on room load. `look` may be added later as "look harder" to find hidden items.
- **Bypass mechanic** — force open a frozen door without repairing the panel. Requires tools, takes time, damages door further. Deferred to full repair system phase.
- **PAM (Personal Atmospheric Monitor)** — wearable device shows O₂/temp in event strip. Deferred.

---

## 13. RULES FOR DEVELOPMENT

Carried forward from Dark Star's hard-won lessons:

1. **Upload the current zip at the start of every session** — never work from memory
2. **Read the code before changing it** — ask to see files before editing
3. **Give complete files, not diffs** — for anything more than 1-2 lines
4. **Minimal targeted changes** — no rewrites, no "while I'm in here" improvements
5. **Only create what we need right now** — port Dark Star files only when actually needed
6. **No god files** — grouped logically by domain
7. **Backend owns all game state** — JS is display only. Sends strings, renders responses.
8. **All colours in CSS variables** — never hardcode colours in JS or HTML
9. **All JS timeouts in `constants.js`** — `DOOR_IMAGE_DISPLAY_MS` etc.
10. **All Python durations in `config.py`** — `CARD_SWIPE_REAL_SECONDS` etc.
11. **Debate bad ideas** — push back if something seems wrong or inconsistent

---

## 14. FULL REPAIR SYSTEM — TARGET DESIGN

This is the intended end-state repair system. Phase 11 implements a simplified "magic repair" placeholder. The full system is built out incrementally from Phase 16 onwards once inventory, tools, and parts are in place.

### Design Philosophy
Repair is the core gameplay loop. It should feel like real diagnostic work — methodical, rewarding, occasionally frustrating. The right tools and knowledge make it possible. The wrong approach wastes time and can make things worse.

### The Four Steps

**Step 1 — Diagnose**

The player must diagnose the fault before attempting repair. This requires:

- **Diagnostic tool** (e.g. "Ship Systems Analyser") — a handheld device with oscilloscope, scan reader, bi-directional controls, and onboard diagnostic capability
- **Basic access tools** — screwdrivers and other basic tools to remove panels and gain physical access to the component
- **Workshop manuals** (optional but important) — e.g. "Reactor Manual — Model 14". Without the correct manual, diagnosis is less effective and may miss faults or misidentify them. Manuals are updatable (future feature)

Diagnosis takes time (TBD) and produces a fault report: what failed, what parts are needed to fix it, what tools are required.

Without the diagnostic tool: the player can still attempt a repair but is guessing — higher chance of failure and possible additional damage.

Without the correct manual: diagnosis succeeds but is less precise — fault description is vaguer, parts list may be incomplete or incorrect.

**Step 2 — Repair / Replace**

Once the fault is diagnosed, the player gathers the required parts and tools and performs the repair. This requires:

- Correct replacement parts (from storage units, cargo bay, or fabricated)
- Correct tools (beyond basic access tools — may require specialised equipment)
- The player must physically be at the component location

Repair takes time (TBD, varies by component complexity).

**Step 3 — Verification**

After repair, the system must be verified. This requires:

- Running the diagnostic tool again
- The correct manual increases the chance of a clean verification pass

Without the manual: verification may pass incorrectly (fault appears fixed but isn't), or flag false positives. There is a chance of **incorrect repair** — the wrong part was replaced or the repair was done incorrectly — which may cause additional damage or leave the original fault unresolved. In this case more parts and tools are consumed.

**Step 4 — System operational**

If verification passes cleanly: component is fully restored, door/system operational.

If verification fails: return to Step 2 with the new fault information. Time and parts consumed. Stress increases.

### Time Costs
All durations TBD and tunable via `config.py`. Factors affecting time:
- Component type and complexity
- Whether the correct tools are available
- Whether the correct manual is available
- Player's condition (future: fatigue, injury)

### Implications for Game Design
- The player needs to plan ahead — gather tools and parts before the repair
- The diagnostic tool is a critical early-game item
- Manuals become valuable loot/trade items
- A poorly equipped player can still attempt repairs but at greater risk and cost
- Cascading failures become genuinely threatening — fix one thing wrong and you create another problem

### Bypass Mechanic (deferred, same phase)
For frozen doors specifically: the player can attempt to physically force the door open without repairing the panel. This requires:
- Physical tools (crowbar or engineering kit)
- Time and effort
- The door is damaged further — it cannot be closed again without full repair
- Only possible on unlocked frozen doors — a locked frozen door requires panel repair or bypass of the lock separately
9. **All timeouts in constants.js** — never hardcode durations in JS
10. **All durations in config.py** — never hardcode durations in Python
11. **Debate bad ideas** — push back if something is wrong, short-sighted, or inconsistent

---

*Project Orion Design Document v3.0*
*March 2026*
