# PROJECT ORION GAME — SESSION HANDOFF
## Phase 17 Complete
**April 2026**

---

## WHAT WAS DONE THIS SESSION

### Phase 16 — Terminal system (completed)
- CSS split: `game.css` → `game.css`, `description.css`, `inventory.css`, `response.css`, `terminal.css`
- Tab strip moved from left edge to top of image panel (horizontal tabs)
- Terminal panel with CRT styling: dark green phosphor, scanlines, text glow
- Typewriter effect with character jitter, blinking block cursor
- Keypress navigation — single key, no Enter required
- Terminal mode lockout: command input disabled, `>` prompt hidden, description clicks blocked
- Only `[X]` exits the terminal — single exit point
- `[T] Technical Data` and `[E] Electrical` on engineering terminal main menu

### Phase 17 — Electrical system integration (completed except circuit diagram SVG)
- Electrical system merged from reference project: `electrical_system.py`, `electrical.json`, `ship_layout.svg`
- `ElectricalSystem` loaded in `game_manager.new_game()`
- `systems.py` registered as blueprint at `/api/systems`
- All 17 rooms powered at game start, confirmed via API
- x/y placeholder coordinates removed from `electrical.json` and all Python classes
- Storage room wiring logic bug fixed in `electrical.json`
- `fix` endpoint added to `systems.py` (mirrors `break`)
- Engineering terminal electrical sub-menu: `[P] Power Status`, `[C] Circuit Diagram`
- Power Status loads `ship_layout.svg` with live room colours from electrical API
- Circuit Diagram shows placeholder text — SVG being built manually in Inkscape
- Debug console: `Ctrl+D` toggle, `break <id>` / `fix <id>` commands
- Map and tooltips refresh immediately after break/fix
- Door panels check room power — offline message, no image
- Terminal access checks room power — offline message
- Exit hover tooltips show "Open — Offline" / "Closed — Offline" in orange
- Terminal tooltips show "Online" / "Offline"
- `refreshExits()` updated to also refresh `currentObjects` so tooltips stay in sync
- All static room descriptions purged of electrical atmosphere references

---

## WHAT IS NOT DONE / PENDING

### Circuit diagram SVG
The player is building this manually in Inkscape using the skeleton SVG (`skeleton.svg`) as a starting point. The skeleton defines these CSS classes: `.reactor`, `.panel`, `.fuse`, `.fuse-bar`, `.cable`, `.cable-dash`, `.endpoint`, `.battery`. When complete, it integrates into the `[C] Circuit Diagram` terminal option in `terminal.js` — same fetch/display pattern as the power status map. No live power colouring on the circuit diagram — it is a static reference tool.

### Terminal shutdown on power loss
If a game event kills power to a room while the player is actively using the terminal, the terminal stays open (no crash, just wrong gameplay). Needs a power-state check triggered by events. Deferred to when the event system is built.

### `refreshExits()` rename
Function now updates both exits and object states but still called `refreshExits`. Should be renamed `refreshDescription()`. Many call sites — defer to a quiet refactor session.

### Dynamic room descriptions
Static room prose has had electrical atmosphere removed. A power-state description layer (atmospheric when powered, dark and silent when not) is planned for Phase 20 alongside life support.

---

## NEXT SESSION PRIORITIES

The most likely next focus is **Phase 18 — Full repair system**. The electrical system is now testable via the debug console, so the repair loop can be designed and built:

1. Scan tool diagnosis — identify failed component
2. Navigate to component location
3. Gather correct tools and parts
4. Perform repair (timed action)
5. Verify restoration

Alternatively, the circuit diagram SVG may be ready to integrate — that is a contained task requiring changes only to `terminal.js` and `engineering.json`.

---

## KEY ARCHITECTURE REMINDERS

- `game_manager.electrical_system` — single `ElectricalSystem` instance, lives for game lifetime
- `_check_room_power(room_id)` in `base_handler.py` — used by door and terminal handlers
- `update_battery_states()` must be called after any electrical component state change
- `refreshExits()` in `commands.js` updates both `currentExits` and `currentObjects`
- Terminal mode suppresses all input except debug console input (checked via `document.activeElement`)
- All door operations pass through `_check_panel()` in `door_handler.py` — power check is there
- `_build_room_data()` in `game.py` includes `panel_powered` on exits and `powered` on terminal object states

---

## FILE LOCATIONS

| File | Path |
|------|------|
| Design doc | `docs/Project_Orion_Design_v10.md` |
| Electrical system | `backend/systems/electrical/electrical_system.py` |
| Electrical data | `data/ship/systems/electrical.json` |
| Systems API | `backend/api/systems.py` |
| Terminal handler | `backend/handlers/terminal_handler.py` |
| Base handler | `backend/handlers/base_handler.py` |
| Door handler | `backend/handlers/door_handler.py` |
| Terminal JS | `frontend/static/js/screens/terminal.js` |
| Commands JS | `frontend/static/js/screens/commands.js` |
| Ship layout SVG | `frontend/static/images/ship_layout.svg` |
| Engineering terminal content | `data/terminals/engineering.json` |
| Terminal definitions | `data/items/terminals.json` |

---

## DEVELOPMENT RULES (SUMMARY)

1. Upload current files at start of every session — never work from memory
2. Read the code before changing it
3. Complete files for large changes, inline instructions for small ones
4. Minimal targeted changes — no unrequested improvements
5. One change at a time — verify before proceeding
6. Backend owns all game state — JS is display only
7. Never output complete game.html or game.js — targeted changes only
8. Debate bad ideas — push back if something seems wrong
9. Never add "type X to fix it" hints — immersive messages only

---

*Project Orion Game — Phase 17 Handoff*
*April 2026*
