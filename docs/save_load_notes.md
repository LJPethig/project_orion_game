# Project Orion — Save/Load Design Notes
**Status: Active — updated as decisions are made**

This document captures save/load design decisions as they are made during development.
It supplements Section 7 of `Project_Orion_Future_v1-2.md`, which has the core
serialisation list. Read both documents before starting Phase 19.5.

---

## Save triggers

Save occurs at natural break points only — never mid-action:

- Between component repairs (the natural break between each component replaced)
- On room change
- After any timed action completes
- On clean quit

The game will never save while a terminal, datapad, or inventory panel is open.

Complex repairs (reactor, engines etc.) may take several days of ship time. The break
between each component replaced is the intended save and rest point. Future survival
logic will present a "continue or take a break?" choice at each break, making these
save points explicit to the player and creating a natural entry point for hunger,
fatigue, and consumable mechanics.

⚠️ CONTRADICTION WITH FUTURE DOC: The Future doc (Section 7) lists save triggers as
"room change, after any timed action completes, on clean quit" — it does not include
"between component repairs." The between-repairs save trigger was decided during the
April 2026 review session and supersedes the Future doc. The Future doc needs updating.

---

## State that must be serialised

### Repair state

**`PowerJunction.broken_components` and `repaired_components`** — both fields can be
populated at save time. The game saves between component repairs, so a repair may be
partially complete. `broken_components` lists all faults found at diagnosis.
`repaired_components` tracks which have been fixed. On load, repair resumes from the
first component in `broken_components` that is not in `repaired_components`. The
corresponding tablet note must be saved and restored alongside these fields.

**`SecurityPanel.broken_components` and `repaired_components`** — same requirement as
above but for door panels.

### Tablet notes

**`game_manager.tablet_notes`** — the entire dict must be saved and restored. Multiple
notes can exist simultaneously — one per diagnosed but not-yet-repaired panel (both door
panels and electrical junctions). Repair completion reads the note for log labels and
then deletes it. If a note is missing after loading, repair completion will crash.

Notes are written at diagnosis time and deleted on repair completion. This is intentional
design — the note serves as the player's record of what components and tools are needed
while the repair is in progress.

---

## State that does NOT need serialising

**`_item_registry` in `repair_utils`** — read-only template cache of item definitions.
Loaded once at module import. Never changes at runtime. See comment in `repair_utils.py`.

**`datapad_suppressed` in `game_manager`** — always `False` at save time. The game never
saves while a terminal session is active.

**Frontend globals** (`pendingPin`, `currentRoomId`, `currentRoomPowered` etc.) — reset
automatically on page load. No explicit reset needed unless in-game load without a page
reload is ever added.

---

## Open questions for Phase 19.5

- What save file format? JSON is the natural choice given the rest of the codebase.
- Single save slot or multiple? Design doc to decide.
- `instance_id` counters must be restored past the maximum existing instance ID at load
  time — not regenerated. This was established during the instance ID refactor (March 2026).
- Battery `charge_percent` must be saved. Future drain logic will make this significant.

---

---

# Appended from design documents — April 2026
*All save/load relevant content extracted from `Project_Orion_Design_v24.md` and
`Project_Orion_Future_v1-2.md`. Copied verbatim including any contradictions.
Reconciliation and final planning to follow.*

---

## From Future Doc — Section 7: Save/Load System

### Philosophy
No scum saving. No reloading. When you die, you are dead.

### Splash screen
- **New Game** — greyed out if save file exists
- **Continue** — greyed out if no save file exists

### Save triggers — autosave only (from Future doc — may conflict with review decisions above)
- Room change
- After any timed action completes
- On clean quit

### Death state
Save file written with `dead: true`. Continue shows death screen. Only New Game available.

### Self-termination ⚠️ NEEDS FURTHER DISCUSSION
Multi-step auto-destruct sequence across multiple rooms. Airlock spacing as alternative.
Both write dead save state identically.

### Save file scope (from Future doc)
Player state, portable item positions, door states, panel states, electrical system state,
ship time, instance ID counters, cargo manifest state, storage manifest state, event
fired/resolved flags, dead flag.

### Event system save/load ⚠️
`GameEvent.fired` and `GameEvent.resolved` are in-memory only. Must be serialised and
restored after `load_from_json()` — otherwise events re-fire after loading.

---

## From Design Doc — Section 20: Known Issues / Deferred

**Event system save/load** — `GameEvent.fired` and `GameEvent.resolved` in-memory only.
Must be serialised. (Repeated from Future doc — flagged in both documents.)

---

## From Design Doc — relevant state per system

### Player state (Section 10 — Inventory System)
- Player inventory — carried items with full instance state
- Equipped slots — all five slots (head, torso, hands, feet, accessory)
- Carry capacity: currently 40kg (temporarily increased — sack barrow not implemented)
- `storage_manifest` on `GameManager` — dict keyed by `instance_id` → `PortableItem`
- `cargo_manifest` on `GameManager` — containers and pallets lists

### Item system (Section 11)
- Every placed item is a unique Python object with independent state
- `instance_id` — unique runtime ID per item instance, must be persisted and restored
  (not regenerated — counters must be initialised past the maximum existing ID at load)
- Cable consumables carry mutable `length_m` field — decremented on use, must be saved
- Scan tool carries `installed_manuals` list — must be saved

### Door state (Section 14 — Repair System)
- Door states: open/closed/locked
- `is_broken` flag on each security panel
- `SecurityPanel.broken_components` and `repaired_components`
- `pin_attempts` counter on each door — must be saved (3 failed attempts invalidates card)
- Card invalidation state — which security cards are invalidated

### Electrical system state (Section 13)
Each component carries runtime state that must be saved:

**FissionReactor:**
- `operational`
- `ejected`
- `temperature`

**BackupBattery:**
- `active`
- `charge_percent`

**CircuitPanel:**
- `logic_board_intact`
- `bus_bar_intact`
- `surge_protector_intact`
- `smoothing_capacitor_intact`
- `isolation_switch_intact`

**Breaker:**
- `damaged`
- `tripped`

**PowerCable:**
- `intact`
- `connected` (emergency bypass cables start `False` — state must be preserved)

### Event system state (Section 15)
Per `GameEvent`:
- `fired`
- `resolved`

These are in-memory only and must be serialised. If not restored, events re-fire on load.

### Ship time (Section 6 — Game Loop)
- Chronometer state — current ship time in minutes
- Ship time multiplier: 40 real seconds = 1 ship minute (this is a config constant,
  not runtime state — does not need saving)

### Ship log (Section 17 — Tablet, Ship's Log and Messages)
- `game_manager.ship_log` — list of structured dicts: `timestamp`, `event`, `location`,
  `detail`. Full log must be saved and restored.

### Storage and cargo (Section 16 — Ship Inventory System)
- `game_manager.storage_manifest` — full manifest with all item instance state
- `game_manager.cargo_manifest` — containers and pallets with contents

### Room state
- Current player room — `game_manager.current_room_id` (or equivalent)
- Floor items per room — items that have been dropped on floors
- Open/closed state of all `StorageUnit` containers

### Engine state (Section 13)
- `Engine.online` flag — damaged/undamaged (not the same as `powered`, which is derived
  from electrical trace and does not need saving)
- `Engine.powered` — derived at runtime from electrical trace, does NOT need saving

### Monologue system (Section 18 / Future doc Section 8)
- One-shot monologue triggers must track which have fired — otherwise Jack repeats himself
- Future: `monologue.json` fired-keys list must be saved
- Current state: only one hardcoded trigger (terminal power cut) — no save needed yet

---

## From Future Doc — other systems with save implications

### Survival mechanics (Future doc Section 9)
When implemented:
- Hunger level
- Thirst level
- Fatigue level
- Atmospheric state per room (temperature, pressure, atmosphere composition)

These do not exist yet — flagged for awareness only.

### Sack barrow (Future doc Section 17)
When implemented:
- `SackBarrow.loaded_container` reference must be saved
- The container and its contents would already be serialised as part of portable item
  positions — the link between barrow and container is the additional piece

### Jury-rigging system (Future doc Section 16)
When implemented:
- `jury_rigged_power` flag on any fixed object — must be saved
- `PortablePowerPack` charge state — must be saved

### Room state tokens (Future doc Section 6)
When `^room_state^` token and `event_effects` are implemented:
- `room.room_states` dict (active states per room) must be saved
- These are triggered by events and persist permanently

### Monologue fired keys (Future doc Section 8)
When JSON-driven monologue system is implemented:
- List of fired monologue keys must be saved to prevent repeat triggers
