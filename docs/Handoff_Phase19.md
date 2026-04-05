# PROJECT ORION GAME — SESSION HANDOFF
## Phase 19 Preparation
**April 2026**

---

## WHERE WE ARE

Phase 18 is complete. A series of smaller deferred fixes were also completed in the same session. The game is stable and running. The design doc has been updated to v13.

---

## WHAT WAS COMPLETED THIS SESSION

### Phase 18 — Full Repair System
- Data-driven repair system via `repair_profiles.json`
- `diagnose` and `repair` as separate commands
- Scan tool manual validation against `door_access_panel_types.json`
- Per-component repair with parts and wire consumption by length
- Full upfront missing tools and parts reporting
- Auto-chain through multiple components with `check_for_event()` hook
- Structured, styled response messages via `appendRepairMessage()` in `ui.js`
- Door panel type system — `panel_type` field, `door_access_panel_types.json`
- Security level 0 panels — no card required, instant lock/unlock

### Deferred fixes completed
- **resolver_debug.log** — removed from `main.py` and `command_handler.py`, log deleted
- **Inventory auto-close** — `closeInventoryIfOpen()` in `setPanelImage()`, `setDamagedPanelImage()`, `setDoorImage()` in `ui.js`
- **Wire length display** — `display_name()` on `PortableItem` appends `(Xm)` for wire. Used everywhere items are displayed.
- **Clarification dedup for wire** — partially fixed. Two spools of different lengths now show as distinct options. Known limitation: `clarified:` prefix takes first matching instance by order — may pick wrong spool when two identical-length spools exist. See design doc Section 16 for full detail and correct fix.

---

## FIRST TASKS FOR NEW SESSION

### 1. Upload current files before any changes
Always upload the files you intend to change. Never work from memory or files from this session — they may be stale.

### 2. Remaining small deferred fixes (pick from Section 16 of design doc)
Good candidates for targeted work:
- **Examine command** — `examine <item>` verb, prints name, manufacturer, model, description to response panel. New verb in `command_handler.py`, simple handler.
- **Inventory screen manufacturer/model** — show in item detail panel. Frontend change in `inventory.js` and `game.py` inventory serialisation.
- **`refreshExits()` rename** — mechanical rename to `refreshDescription()`. Many call sites — careful search and replace session.

### 3. Unique instance identifiers (if wire clarification is a priority)
See design doc Section 16 for full spec. Touches `item_loader.py`, `command_handler.py`, `game.py`. Not trivial — plan carefully before starting.

---

## KEY ARCHITECTURE NOTES

### Repair system
- `repair_handler.py` — `handle_diagnose()` and `handle_repair()` are separate entry points
- `_begin_diagnosis()` checks diag tools and scan tool manuals, returns `diagnose_panel` action
- `_begin_next_repair()` checks ALL missing tools and parts upfront before starting any component
- `complete_diagnosis()` called by `/api/command/diagnose_complete` — randomly selects broken components
- `complete_component_repair()` called by `/api/command/repair_complete` — consumes parts, marks repaired
- `/api/command/repair_next` — calls `check_for_event()` then `_begin_next_repair()` for auto-chain
- `check_for_event()` in `game_manager.py` — stub returning `None`, event hook for future

### Door panel type system
- `door_status.json` — `panel_type` field per connection (e.g. `vesper_ulock`, `smc_ts1500`, `smc_q_emerald`)
- `door_access_panel_types.json` — type registry, `security_level` resolved here at load time
- `SecurityPanel` — carries `panel_type`, `security_level`, `broken_components`, `diagnosed_components`, `repaired_components`

### Wire display
- `PortableItem.display_name()` — returns `"{name} ({length_m}m)"` if wire, else `name`
- All serialisation in `game.py` uses `display_name()`
- `repair_handler._component_display_name(component)` — same for profile component dicts

### Clarification bypass
- Clarification clicks send `clarified:{command}` to backend
- `command_handler.process()` strips prefix and skips ambiguity check
- Known issue: takes first matching instance by order, not guaranteed correct for identical items

---

## PENDING FROM PHASE 17
- **Circuit diagram SVG** — being built manually in Inkscape. When complete, integrate into `[C] Circuit Diagram` in engineering terminal. Changes: `terminal.js` (fetch and display SVG) and `engineering.json` (replace placeholder with `view: circuit_diagram`).

---

## DEVELOPMENT RULES (SUMMARY)

1. Upload current files before any changes — never work from memory
2. Read the code before changing it — ask to see files before editing
3. Complete files for large changes, inline instructions for small ones
4. New functions — give as instructions to append, not complete files
5. Minimal targeted changes — no unrequested improvements
6. One change at a time — verify before proceeding
7. No silent fallbacks — missing data must crash loudly
8. Backend owns all game state — JS is display only
9. Never add "type X to fix it" hints — immersive messages only
10. Debate bad ideas — push back if something seems wrong
11. Give explicit instructions — exact strings to find and replace, exact insertion points
12. Always verify counts before stating them (grep first)

---

*Project Orion Game — Phase 19 Handoff*
*April 2026*
