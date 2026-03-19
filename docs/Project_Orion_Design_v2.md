# PROJECT ORION
## Space Survival Simulator
### Master Design & Development Document
**Version 2.0 — March 2026**

---

## 1. PROJECT OVERVIEW

### Concept
Project Orion is a space survival simulator set in 2275. The player operates a solo trader/explorer spacecraft. Core gameplay revolves around maintaining ship systems, repairing failures, and surviving deep space. This is a serious "slow burner" simulator — not an arcade game. Systems fail, cascade, and the player must diagnose and fix them before things get fatal.

### History
- **Project Dark Star** — previous iteration in Python/Arcade. Got a long way (player, inventory, rooms, doors, security panels, basic repair, life support scaffolding, chronometer). Abandoned due to Arcade's text rendering limitations and UI inflexibility.
- **Project Orion** — Flask backend + HTML/CSS/JS frontend. Carries forward all Dark Star game logic, leaves behind all Arcade UI code.

### Core Philosophy
*"If the ship dies, you die."* Generous time windows. Thoughtful problem solving over frantic action. The player physically moves through the ship, gathers the right tools and parts, and repairs systems.

---

## 2. TECHNOLOGY STACK

| Component | Technology |
|-----------|-----------|
| Game Logic | Python 3.x |
| Web Server | Flask |
| UI | HTML / CSS / Vanilla JS |
| Ship Diagrams | SVG (interactive, live state) |
| Data | JSON files |
| Version Control | Git |

**No JS frameworks. No ORM. Keep it simple and maintainable.**

---

## 3. WHAT EXISTS AND WORKS (DO NOT BREAK)

### From Phase 1–5 of Orion:
- Full electrical system (`electrical_system.py`) — 17 rooms, 28 cables, 17 breakers, 4 panels, 4 power sources
- Break API (`POST /api/systems/electrical/break/<id>`) — cables, breakers, panels, reactors, batteries
- Battery auto-activation when mains power is lost
- Power path tracing with battery fallback
- Interactive SVG diagnostic map (`ship_layout.svg`) — draggable floating window, live room colours, reactor/battery icons, tooltips
- All of the above is tested and committed

### From Project Dark Star (logic only, no Arcade code):
- `Player` — inventory, equipment slots (head/body/torso/waist/feet), mass-based carry limit, worn items free
- `Interactable` / `PortableItem` / `FixedObject` / `StorageUnit` / `UtilityBelt` — complete object hierarchy
- `Room` / `Ship` — room loading, exit patching, door/panel attachment
- `Door` / `SecurityPanel` — security levels, keycard + PIN logic, damaged state, repair progress
- `CommandProcessor` — verb registry with longest-match, all core commands working
- `Chronometer` — pure Python, no Arcade dependencies, ports directly
- `RepairHandler` / `DoorHandler` — separation of concerns already established
- All JSON data — rooms, doors, items, tools, wearables, consumables, starting items

---

## 4. FOLDER STRUCTURE

```
project_orion/
│
├── main.py                          ← Flask entry point, registers blueprints
├── config.py                        ← All constants (STARTING_ROOM, SHIP_NAME, etc.)
├── requirements.txt
│
├── backend/
│   ├── models/
│   │   ├── game_manager.py          ← Central coordinator
│   │   ├── player.py                ← Player state, inventory, equipment
│   │   ├── ship.py                  ← Ship, rooms, doors loader
│   │   ├── room.py                  ← Room class
│   │   ├── chronometer.py           ← Game clock
│   │   └── interactables.py         ← All item classes:
│   │                                   Interactable, PortableItem, FixedObject,
│   │                                   StorageUnit, UtilityBelt
│   │
│   ├── systems/
│   │   ├── electrical/
│   │   │   └── electrical_system.py ← Complete ✅
│   │   ├── life_support/            ← Placeholder (future)
│   │   ├── navigation/              ← Placeholder (future)
│   │   └── events/
│   │       └── event_manager.py     ← Game loop event checking
│   │
│   ├── handlers/
│   │   ├── command_handler.py       ← Verb registry, routes to sub-handlers
│   │   ├── movement_handler.py      ← go, enter, move
│   │   ├── interaction_handler.py   ← take, drop, examine, open, close, put in/from
│   │   ├── inventory_handler.py     ← wear, remove, inventory display
│   │   ├── door_handler.py          ← lock, unlock, keycard, PIN
│   │   └── repair_handler.py        ← repair commands
│   │
│   └── api/
│       ├── game.py                  ← /api/game/* — state, new game, time
│       ├── command.py               ← /api/command — single POST for all commands
│       ├── systems.py               ← /api/systems/* — electrical etc ✅
│       └── player.py                ← /api/player/* — inventory, status
│
├── frontend/
│   ├── templates/
│   │   ├── splash.html              ← Splash screen
│   │   └── game.html                ← Main game screen
│   │
│   └── static/
│       ├── css/
│       │   ├── splash.css
│       │   ├── game.css             ← Main game screen layout
│       │   └── terminal.css         ← Terminal/diagnostic screen (current main.css)
│       │
│       ├── js/
│       │   ├── core/
│       │   │   ├── api.js           ← All fetch calls, one function per endpoint
│       │   │   ├── state.js         ← Client-side game state cache
│       │   │   └── loop.js          ← Frontend polling loop (time, events)
│       │   ├── screens/
│       │   │   ├── splash.js        ← Splash screen logic
│       │   │   ├── game.js          ← Main game screen orchestrator (thin)
│       │   │   └── terminal.js      ← Terminal/diagnostic screen
│       │   └── components/
│       │       ├── map.js           ← SVG map (extracted from current game.js)
│       │       ├── event_strip.js   ← Bottom event strip
│       │       └── room_view.js     ← Room image + description rendering
│       │
│       └── images/
│           ├── ship_layout.svg      ← Complete ✅
│           └── rooms/               ← Room background images (from Dark Star)
│
└── data/
    ├── ship/
    │   ├── structure/
    │   │   ├── ship_rooms.json      ← Dark Star version (complete, with descriptions/exits)
    │   │   └── door_status.json     ← From Dark Star
    │   └── systems/
    │       └── electrical.json      ← Complete ✅
    ├── items/
    │   ├── tools.json
    │   ├── wearables.json
    │   ├── consumables.json
    │   ├── misc_items.json
    │   └── storage_units.json
    └── game/
        └── starting_items.json
```

---

## 5. THE GAME LOOP — CRITICAL ARCHITECTURE

This is the most important design decision. Get it right from day one.

### Two types of player actions:

**Instant actions** — `look`, `take wrench`, `examine locker`
- No game time passes
- Backend responds immediately
- Frontend stays unlocked

**Timed actions** — repairs, waiting, sleeping, card swipes
- Backend returns a duration
- Frontend locks input, shows feedback ("Repairing panel...")
- Frontend waits the real-world seconds (e.g. 8 seconds)
- Frontend calls back to complete the action
- Backend advances ship time by game-world minutes (e.g. 30 minutes)
- Backend checks for events triggered by time passing
- Frontend unlocks

### Standard API response shape:

Every command response returns this structure:

```json
{
  "response": "You begin repairing the panel...",
  "action_type": "instant",
  "lock_input": false,
  "ship_time": "01-01-2276  00:00",
  "events": []
}
```

For timed actions:
```json
{
  "response": "Repairing door access panel...",
  "action_type": "timed",
  "real_seconds": 8,
  "game_minutes": 30,
  "lock_input": true,
  "ship_time": "01-01-2276  00:00",
  "events": []
}
```

### Why this matters:
- The blocking logic is written **once**, in `loop.js`
- Every timed action in the entire game just sets `real_seconds` and `game_minutes`
- The frontend never needs to know what any command means — it just sends strings and renders responses
- All game logic stays in Python where it belongs

### Ship time:
- Backend owns the truth — `Chronometer` in Python
- Frontend polls every 10 seconds via `loop.js` for passive state updates
- Ship time always visible in the event strip (bottom right)
- Time only advances when something causes it to advance — not in real time

---

## 6. THE COMMAND SYSTEM

Single endpoint: `POST /api/command`

Request:
```json
{ "command": "take wrench" }
```

The frontend sends a string. The backend's `CommandHandler` processes it using the verb registry (longest-match pattern from Dark Star). The frontend renders the response. The frontend never interprets commands — it stays dumb.

This keeps all game logic in Python and means the JS never needs to change when new commands are added.

---

## 7. MAIN GAME SCREEN LAYOUT

```
┌─────────────────────────────────────────────────────────────┐
│                    ROOM IMAGE (45%)          │ DESCRIPTION   │
│                                              │ (scrollable)  │
│                                              │               │
│                                              ├───────────────┤
│                                              │ RESPONSE AREA │
│                                              │               │
│                                              ├───────────────┤
│                                              │ COMMAND INPUT │
├──────────────────────────────────────────────┴───────────────┤
│ EVENT STRIP  [events/alerts LH side]    [ship time / vitals] │
└─────────────────────────────────────────────────────────────┘
```

- **Room image** — 45% width, full height minus event strip
- **Description** — top 50% of right panel, scrollable, shows room contents/exits/objects
- **Response area** — middle of right panel, last command result
- **Command input** — bottom of right panel, always focused
- **Event strip** — full width, fixed height at bottom
  - Left side: events and alerts (hull breach, low O₂, etc.)
  - Right side: ship time + vitals (O₂, temp — when PAM is worn and implemented)

### Aesthetic:
- Same green-on-black as current Orion terminal screen
- Monospace font throughout
- Colour coding (from Dark Star): cyan for fixed objects, purple for portables, different colour for exits

### Separate screens (open in new view, not floating panels):
- **Inventory screen** — replaces main screen, back button returns
- **Terminal screen** — the current Orion interface becomes this. Green-on-black, command input, scrolling output.

### Diagnostic map:
- When the player uses a computer terminal that has map access, the screen splits: terminal on left, map on right
- The map does NOT auto-open on game start — it's a tool accessed via terminals

---

## 8. BUILD PLAN — ONE STEP AT A TIME

### ✅ Phase 1–5: Electrical system, SVG map, break mechanics — COMPLETE

### Phase 6: Splash screen + main game screen shell
- Splash screen (black, ship name, click to start)
- Main game screen — five zones, correct proportions, styled
- Ship time visible in event strip, updating every real minute
- Chronometer running in backend from game start
- Nothing else — no commands, no room data, just the shell with a live clock

### Phase 7: Ship instance + player placement
- Load Dark Star's `ship_rooms.json` into Ship/Room models
- Load `door_status.json`
- Place player in `STARTING_ROOM` (from config.py)
- Show that room's background image on the left panel
- Show room name in description area

### Phase 8: `look` command
- First command wired up
- Returns room description, visible objects, exits
- Displayed in description area

### Phase 9: Movement
- `go to [room]` / clickable exits (TBD — text, click, or both)
- Room image updates on move

### Phase 10: Inventory + items
- Port Player, Interactable hierarchy from Dark Star
- `take`, `drop`, `examine`
- Inventory screen

### Phase 11+: Doors, repair, terminals, electrical integration, events...

---

## 9. KNOWN ISSUES / DEFERRED

- **Storage room wiring bug** — `room_power_sources` maps `storage_room` to `PNL-SC-SUB-B` (wrong panel). Should be `PNL-REC-SUB-C`. Fix in `electrical.json` when addressing electrical/room integration.
- **Life support** — Dark Star had a simulation scaffold but it wasn't working well. Leave for later. Will connect to electrical system (life support room loses power → scrubber efficiency drops to zero).
- **Battery drain over time** — battery bar icons ready for this. Needs game loop implementation.
- **Repair mechanics** — basic structure from Dark Star exists. Port when needed.
- **Clickable vs text movement** — undecided. Build text first, add clicks later if it feels right.

---

## 10. RULES FOR DEVELOPMENT

Carried forward from Dark Star's hard-won lessons:

1. **Read the code before changing it** — never assume, never work from memory
2. **Minimal targeted changes** — no rewrites, no "while I'm in here" improvements
3. **Only create what we need right now** — port Dark Star files only when they're actually needed
4. **No god files** — everything grouped logically by domain. Handlers split by verb group. Models one class per concern (except interactables which are all closely related).
5. **No multiple tiny files either** — use judgement. Five item classes in one file is fine. One function per file is not.
6. **Backend owns all game state** — JS is display only. It sends strings, renders responses.
7. **Ship time in from day one** — the game loop is the foundation. Events, repairs, waiting all depend on it being correct from the start.
8. **Zip only changed files** — not the whole project

---

*Project Orion Design Document v2.0*
*March 2026*
