# Project Orion — New Session Handoff
**March 2026**

---

## Important Note on Project Names

**Project Orion Game is the convergence of two previous codebases:**

- **Project Dark Star** (Python/Arcade) — game logic reference only. Read-only.
- **Project Orion** (Flask prototype) — electrical system reference only. Read-only.

The zip you will receive is:
- **`project_orion_game.zip`** — the actual game. This is what we develop.

Read `docs/Project_Orion_Design_v5.md` inside the zip before doing anything.
Also read `docs/UI_UX_Description_Panel_v2.md` — it covers the description panel design in detail and is essential context for Phase 13.

---

## Current State

Phases 6–13a are complete and tested:

- Splash screen, game shell, room loading and display
- Player movement between rooms
- Full door system — three states, card swipe, PIN, card invalidation (swaps to damaged card)
- Door commands: open, close, lock, unlock
- Exit hover tooltips showing door state
- Real-time ship clock
- Damaged door panels + basic repair with animations
- Initial ship state overlay (door states, panel damage, PINs from `initial_ship_state.json`)
- Player + inventory — take, drop, debug_inventory
- Item loading — tools, wearables, misc, consumables placed in containers and on player
- Fixed object data restructure — terminals, storage units, surfaces as separate files and classes
- `ship_rooms.json` updated with `!terminal!` and `#surface#` markup throughout

---

## What We Are Doing Next — Phase 13b

**Markup parser + hover tooltips**

The description panel currently only handles `*exit*` and `%object%` markup. We need to extend it to handle all four types, add correct CSS classes, pass object state from backend to frontend, and wire up hover tooltips.

### Four markup types:
| Markup | Type | Colour | Hover |
|--------|------|--------|-------|
| `*exit*` | Exit | Cyan | Door state (already working) |
| `%object%` | Container | Cyan | "Open" or "Closed" |
| `!terminal!` | Terminal | Cyan | "Terminal" |
| `#surface#` | Surface | Grey bold (empty) / Purple bold (has items) | "Empty" or item count |

### Backend changes needed:
- `_build_room_data` in `command.py` and `/api/game/room` in `game.py` need to include object states:
  - Which containers are open
  - Which surfaces have items
- This lets the frontend colour surface spans correctly on render

### Frontend changes needed:
- `parseMarkup` in `game.js` — extend regex to handle `!` and `#` delimiters
- Each markup type gets a distinct CSS class and `data-` attribute
- Hover tooltips for containers, terminals, surfaces (same positioning logic as exit tooltips)
- Surface span colour: grey bold when empty, purple bold when has items — driven by backend state

### CSS changes needed:
- New classes for `markup-container`, `markup-terminal`, `markup-surface`
- Surface empty state: `--col-text`, bold
- Surface has-items state: `--col-portable`, bold

---

## What Comes After Phase 13b

**Phase 13c — Click handlers + Layer 2/3 rendering:**
- Container click → `open`/`close` command
- Terminal click → `use <terminal>`
- Surface click → expand/collapse Layer 3
- Layer 2: open container contents below prose
- Layer 3: surface contents when expanded
- `open`/`close` container commands wired up end to end

---

## Important Conventions

- **Always ask to see files before editing** — do not work from memory
- **Give complete files for large changes, inline instructions for small ones**
- **Read `Project_Orion_Design_v5.md` before writing any code**
- **Backend owns all game state** — JS is display only
- **All colours in `game.css` CSS variables**
- **All JS timeouts in `constants.js`**
- **All Python durations in `config.py`**
- **Debate bad ideas** — push back if something seems wrong
- **Never add "type X to fix it" hints** — immersive messages only
- **Python 3.14** — `X | None` type hints valid

---

*Good luck. The ship won't fix itself.*
