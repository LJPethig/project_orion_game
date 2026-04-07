# PROJECT ORION GAME — SESSION HANDOFF
## Phase 19 Preparation
**April 2026**

---

## WHERE WE ARE

The deferred fix session is complete. The game is stable and running. The design doc has been updated to v14.

---

## WHAT WAS COMPLETED THIS SESSION

### Unique Instance Identifiers (major refactor)
The core ambiguity bug has been fixed. Every placed portable item now receives a unique runtime `instance_id` (e.g. `wire_low_voltage_001`) at load time. Clarification options use `instance_id` in commands. Resolution checks `instance_id` first, bypassing ambiguity entirely.

Files changed:
- `backend/models/interactable.py` — `instance_id` attribute on `PortableItem`
- `backend/loaders/item_loader.py` — `_instance_counters`, `_assign_instance_id()`, `reset_instance_counters()`
- `backend/models/game_manager.py` — `reset_instance_counters()` called at `new_game()`
- `backend/handlers/command_handler.py` — `_resolve_all` returns `instance_id`; instance_id direct-match bypass; clarified preposition commands routed directly bypassing verb registry; `pick up <item> from <container>` fixed
- `backend/api/game.py` — `instance_id` in all five serialisation locations
- `backend/handlers/item_handler.py` — instance_id matching; `display_name()` in response messages
- `backend/handlers/equip_handler.py` — instance_id matching
- `backend/handlers/container_handler.py` — instance_id matching; `display_name()` in all response messages including `look in`
- `frontend/static/js/screens/inventory.js` — action buttons use `instance_id`
- `frontend/static/js/screens/description.js` — item clicks use `instance_id`

### Scan Tool Manual Check Fix
A previous session incorrectly added a hard block on diagnosis when the scan tool manual was missing. This has been corrected:
- Missing manual no longer blocks diagnosis
- Instead shows a corporate warning message in orange (`--col-alert`) with Yes/No confirmation
- New action type `diagnose_panel_warning` added to `commands.js`
- Player may proceed regardless — future: missing manual will increase post-repair failure probability
- `_check_scan_tool_manual()` in `repair_handler.py` now returns a string sentinel rather than a response dict

### Other fixes
- `display_name()` now used in all take/put/drop/look in response messages
- `put in` clarification deduplicates by `display_name()` (matches `drop`/`put on` behaviour)
- `pick up <item> from <container>` now correctly handled

---

## SAVE/LOAD — IMPORTANT NOTE

Save/load has not been implemented yet. Before Phase 21 (events), a save/load system must be built. Key points established this session:

- `instance_id` must be persisted in save data and restored on load — not regenerated
- On load, after restoring all items, scan them and set each type's counter to `max(existing suffix) + 1` to avoid collisions
- Every major entity already has a stable ID: doors, panels, electrical components, fixed objects, rooms
- The only entity that previously lacked stable unique identifiers was portable items — now fixed
- Recommended: implement save/load after Phase 19 and 20, before Phase 21

---

## FIRST TASKS FOR NEW SESSION

### 1. Upload current files before any changes
Always upload the files you intend to change. Never work from memory or files from a previous session — they may be stale.

### 2. Deferred fixes before Phase 19
The lead designer wants to work through the deferred list to tidy up before any new phases. Candidates from Section 16 of the design doc:

- **Examine command** — `examine <item>` prints name, manufacturer, model, description to response panel. New verb in `command_handler.py`, simple handler.
- **Inventory screen manufacturer/model** — show in item detail panel. Frontend change in `inventory.js` and `game.py` inventory serialisation. Coordinate with examine command.
- **`refreshDescription()` rename** — mechanical rename to `refreshDescription()`. Many call sites — careful search and replace session.
- **`take <item> from floor`** — floor not recognised as valid source in `take from` commands.
- **Circuit diagram SVG** — being built manually in Inkscape. When complete, integrate into `[C] Circuit Diagram` in engineering terminal.

The lead designer will decide which to tackle first in the new chat.

---

## KNOWN ISSUES / DEFERRED (from design doc v14)

- `take <item> from floor` — floor not recognised as valid source name in `take from` commands
- PAM — clips to utility belt. Dormant until life support phase.
- Belt attachment mechanic — deferred until EVA phase.
- Examine / look at command — deferred.
- Inventory screen manufacturer/model — deferred.
- `refreshDescription()` rename — deferred refactor session.
- Terminal shutdown on power loss — implement when event system is built.
- Dynamic room descriptions — planned for Phase 20.
- Circuit diagram SVG — being built manually in Inkscape.
- Repair post-repair failure roll — hook exists, always succeeds. Future: probability-based, higher without correct manual.
- Repair time scaling — fixed stubs. Implement proper scaling with cap, then delete config stubs.
- Scan tool software updates — future exotic systems require purchased updates.

---

## KEY ARCHITECTURE NOTES

### Instance ID system
- `item.instance_id` — unique per placed item, e.g. `wire_low_voltage_001`
- Generated in `item_loader.instantiate_item()` via `_assign_instance_id()`
- Counter reset in `game_manager.new_game()` via `reset_instance_counters()`
- `_resolve_all()` in `command_handler.py` checks `instance_id` first — exact match returns immediately
- Clarified preposition commands (`put in`, `put on`, `take from`) now routed directly in the `clarified:` bypass block, bypassing verb registry
- All handlers check: `item.instance_id == target or item.id == target or item.matches(target)`

### Scan tool manual warning
- `_check_scan_tool_manual()` returns `None` (OK), `'NO_SCAN_TOOL'` (hard block), or `panel_model` string (warning)
- `_begin_diagnosis()` handles all three cases
- Frontend: `diagnose_panel_warning` action type — shows warning in orange, Yes/No confirm, Yes proceeds as normal `diagnose_panel`

### Repair system
- Unchanged from Phase 18 — see design doc Section 15 for full detail

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
13. When a file is uploaded, read it completely and identify ALL instances of any problem pattern before writing any instructions — never fix piecemeal

---

*Project Orion Game — Phase 19 Handoff*
*April 2026*
