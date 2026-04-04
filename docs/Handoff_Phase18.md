# PROJECT ORION GAME — SESSION HANDOFF
## Phase 18 — Full Repair System
**April 2026**

---

## WHERE WE ARE

Phase 17 is complete (except the circuit diagram SVG which is being built manually in Inkscape). Phase 18 is fully designed and ready to build. The design is documented in full in `docs/Project_Orion_Design_v11.md` Section 15.

---

## WHAT PHASE 18 BUILDS

A realistic multi-step repair system, scoped to door panels first but designed generically so it applies to any future repairable object. The single `repair <panel>` command is stateful — it diagnoses first, then repairs on the next invocation. No sub-commands.

The full design is in the design doc. Key points:

**Repair state on each panel:**
```python
panel.broken_components = ["logic_circuit", "wiring_optical"]   # ground truth, set at break time
panel.diagnosed_components = []                                   # what player discovered, set by scan
```

**Command state machine:**
- `is_broken = False` → already operational
- `is_broken = True`, `diagnosed_components` empty → run diagnosis
- `is_broken = True`, `diagnosed_components` populated → run repair

**Data-driven via `data/repair/repair_profiles.json`** — one profile per repairable object type, keyed by security level for door panels (`door_panel_l1`, `door_panel_l2`, `door_panel_l3`). The repair handler reads this generically.

---

## FIRST TASKS FOR NEW SESSION

### 1. Audit existing item JSON files
Upload `tools.json`, `wearables.json`, `consumables.json` and read them carefully before making any changes. Check:
- Does `scan_tool` exist? What attributes does it currently have?
- Does `power_screwdriver_set` exist?
- Does `electrical_service_kit` exist?
- Do door panel component parts exist in `consumables.json`? (logic circuit board, interface module, panel screen, light duty wire, optical wire)

Add anything missing. Item IDs must match exactly what will be referenced in `repair_profiles.json`.

### 2. Add new fields to all items — manufacturer, model, fluff text
Every item in the game must have `manufacturer` and `model` fields added. Descriptions must be rewritten with character — no generic text anywhere. Every item should feel like it exists in the world of 2276.

Examples of the right tone:

**Scan tool:** "Veridian Systems VS-900 Portable Diagnostic Unit. The casing is scuffed from years of use and someone has scratched 'MINE' into the back in capital letters. The screen still reads crisp."

**Door panel manual (L1):** "Axiom Systems AX-3 Access Panel — Field Service Manual. Covers single-factor proximity reader units fitted to standard internal compartment doors. Rev 4.2."

**Component parts:** manufacturer names, part numbers, condition notes if second-hand.

This applies to all items — do a full pass across all JSON files.

### 3. Update scan tool — installed_manuals attribute
Add `installed_manuals` to the scan tool entry:
```json
"installed_manuals": ["door_panel_l1", "door_panel_l2", "door_panel_l3"]
```
The repair handler checks this list to confirm the scan tool has the required manual before allowing diagnosis.

### 4. Update wire consumables — new fields
Wire items need `max_length_m` and `mass_per_metre` instead of `mass`. Mass is computed at runtime from `length_m * mass_per_metre`. See design doc Section 11 for full spec.

### 5. Update initial_ship_items.json — mixed placement format
The loader needs to support both simple string and dict formats:
```json
{"id": "wire_light_duty", "length_m": 12.5}
```
Update `item_loader.py` to handle both formats and set instance attributes (including computed mass for wire).

### 6. Write repair_profiles.json
Create `data/repair/repair_profiles.json` with three door panel profiles (`door_panel_l1`, `door_panel_l2`, `door_panel_l3`). Item IDs must match `consumables.json`. Full structure in design doc Section 15.

### 7. Add REPAIR_PROFILES_PATH to config.py
```python
REPAIR_PROFILES_PATH = 'data/repair/repair_profiles.json'
```

### 8. Update door panel model
`door.py` — `DoorPanel` class needs two new fields:
```python
self.broken_components = []      # list of component IDs broken at break time
self.diagnosed_components = []   # list of component IDs discovered by scan
```

### 9. Build repair handler
`repair_handler.py` — rewrite to use repair profiles. Magic repair replaced entirely. See design doc Section 15 for full flow.

### 10. Breaking a panel for testing
The debug console currently handles electrical components only. Need a mechanism to break door panels for testing. Discuss approach at start of session — options include a debug command extension or a temporary `break_panel <panel_id>` API endpoint.

---

## KEY ARCHITECTURE NOTES

- `base_handler._check_room_power(room_id)` — power check used by door and terminal handlers
- `update_battery_states()` must be called after any electrical component state change
- `refreshExits()` in `commands.js` updates both `currentExits` and `currentObjects`
- All timed actions: backend returns `real_seconds`, frontend locks input, calls back to complete
- `DEBUG_HAS_REPAIR_TOOL = True` in config.py — currently bypasses tool checks. Phase 18 replaces this with real checks. Remove flag when repair system is complete.
- Wire instance `mass` is computed: `length_m * mass_per_metre` — not stored in JSON

---

## FILE LOCATIONS

| File | Path |
|------|------|
| Design doc | `docs/Project_Orion_Design_v11.md` |
| Tools | `data/items/tools.json` |
| Wearables | `data/items/wearables.json` |
| Consumables | `data/items/consumables.json` |
| Ship items placement | `data/ship/structure/initial_ship_items.json` |
| Repair profiles | `data/repair/repair_profiles.json` (to be created) |
| Door model | `backend/models/door.py` |
| Repair handler | `backend/handlers/repair_handler.py` |
| Base handler | `backend/handlers/base_handler.py` |
| Item loader | `backend/loaders/item_loader.py` |
| Config | `config.py` |

---

## PENDING FROM PHASE 17

- **Circuit diagram SVG** — being built manually in Inkscape. When complete, integrate into `[C] Circuit Diagram` in engineering terminal. Changes needed: `terminal.js` (fetch and display SVG, same pattern as power status map) and `engineering.json` (replace placeholder text with `view: circuit_diagram`).
- **`refreshExits()` rename** — should become `refreshDescription()`. Many call sites — quiet refactor session.
- **resolver_debug.log** — remove logger setup from `main.py` and delete log file. Tidy-up task.

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

*Project Orion Game — Phase 18 Handoff*
*April 2026*
