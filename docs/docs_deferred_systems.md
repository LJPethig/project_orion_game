# PROJECT ORION — DEFERRED SYSTEMS
## Fully Designed, Not Yet Built
**May 2026**

> These systems are fully designed and ready to implement when their phase arrives.
> None of these should be built until the build plan in `Project_Orion_Future_v6.md` reaches them.

---

## 1. JURY-RIGGING SYSTEM

### Overview
A portable power pack provides emergency low-voltage (24V DC) power to compatible fixed objects when ship power is unavailable. Cannot connect to the ship grid or run HV equipment.

### Narrative context
The automated storage facility requires ship power — Enso VeilTech mandates this to log all additions and retrievals. When `PNL-REC-SUB-C` is broken, the storage room loses power and the facility becomes inaccessible — exactly when Jack needs the repair parts inside it. The portable power pack is the jury-rigged solution.

### Portable power pack
- Located in the cargo bay — emergency equipment
- `max_watts` field — output limit e.g. 150W
- `voltage` — 24V DC output
- Cannot power HV systems, ship grid, or door panels

### Compatible fixed objects
Fixed objects that accept jury-rigged power carry:
- `power_watts` — consumption rating e.g. 80W
- `power_voltage` — acceptable input voltage e.g. 24V DC

### Connection mechanic
Player connects the power pack to a compatible fixed object. Handler checks:
1. Voltage matches
2. Watts do not exceed pack limit
3. If compatible → sets `jury_rigged_power: true` on the fixed object
4. Fixed object operates normally despite room power being out

### Implementation notes
- `PortablePowerPack` item class or fields on `PortableItem`
- `jury_rigged_power` flag on `FixedObject` — must be saved when implemented
- `connect` command verb — routes to jury-rig handler
- Terminal/storage handler checks `jury_rigged_power` alongside room power

---

## 2. SACK BARROW AND PORTABLE CONTAINER SYSTEM

### Overview
The sack barrow allows Jack to transport a portable container between rooms, extending his carry capacity for repair operations. Essential for heavy repair jobs where parts exceed Jack's personal carry limit.

### Mechanics
- `use sack barrow` — Jack loads a portable container onto the barrow. Container contents become part of Jack's effective inventory for repair part checks.
- `leave sack barrow` — Jack leaves the barrow and container in the current room.
- Only one container can be loaded at a time.
- The barrow itself is a portable item Jack must be carrying or have in the room.

### Repair system integration
`_check_all_parts()` must be extended to include contents of any container loaded on the sack barrow, alongside Jack's personal inventory.

### Implementation notes
- `SackBarrow` item class or fields on `PortableItem`
- `loaded_container` reference on `SackBarrow` — must be saved when implemented
- `use` command verb — routes to sack barrow handler
- `PLAYER_MAX_CARRY_MASS` in `config.py` currently 40kg for testing — remains until this is implemented

---

## 3. MONOLOGUE AND DIALOGUE SYSTEM

### Current state
One hardcoded monologue trigger: terminal power cut. `appendMonologue(text)` renders text in a styled box.

### Planned: JSON-driven monologue system
`data/narrative/monologue.json` — keyed responses for Jack's internal voice.

- **One-shot triggers** — each key fires once only. Repeat triggers break immersion.
- **Tone variations by game state** — Jack early game (weary but functional) vs late game (desperate, post-compliance-order)
- **Trigger keys** — `terminal_power_failure`, `reactor_offline`, `hull_breach`, `reactor_ejected`, `power_restored` etc.
- **Survival guidance** — monologue serves as the mechanism for guiding Jack through genuinely hopeless situations. Jack's survival instinct fires as internal voice, giving the player a direction. Replaces any need for a mechanical lucky break system.
- **Save/load** — fired monologue keys must be saved to prevent repeat triggers

### Planned: NPC dialogue trees
Full dialogue tree system for the mainframe AI, the friend, and Ceres Base contact. Each character gets a distinct voice box colour:
- Jack — muted blue-grey `#7a8a9a`
- Mainframe AI — cold clinical green
- The friend — warmer tone TBD
- Enso VeilTech (automated) — corporate amber

---

## 4. MAINFRAME HACK

### Objective
Unlock the mainframe, disable the navigation lock, access alternative routing to Ceres Base.

### The mainframe AI
Present from start as an Enso VeilTech system. Post-hack it becomes something else — personality and relationship with Jack is a key narrative element. Details TBD.

### Gameplay
Terminal-based hack mechanic. Details TBD — depends on what the mainframe terminal stub becomes.

---

## 5. GOING DARK — SHIP DISGUISE AND BARTER

### Two layers of disguise
**Physical hull camouflage** — bolt-on external modifications. Requires EVA to install.

**Transponder obfuscator** — spoofs ship identification signal. Illegal. Underground source only. Requires barter.

### Paying for it
The cargo represents Jack's only negotiating currency.

### Key design decisions still to make ⚠️
- The cargo manifest contents and any secrets it contains
- The new ship name and identity
- EVA mechanics: suit duration, oxygen limits, hull attachment

---

## 6. CARGO MOVEMENT

### Deferred mechanics
- Sack barrow mechanic for moving small containers between rooms
- `cargo_handler_operational` flag on GameManager — must exist before this phase
- Stacking accessibility: stacked on pallet → accessible; stacked on container → cargo handler required
- Cargo handler item definition and repair profile

---

*Project Orion Game — Deferred Systems — May 2026*
