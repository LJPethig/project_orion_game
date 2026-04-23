# PROJECT ORION GAME
## Space Survival Simulator
### Future Design & Planning Document
**Version 1.0 — April 2026**

> This document covers future phases, system designs not yet built, narrative decisions, and open design questions.
> For current state, architecture, and technical reference see `Project_Orion_Design_v23.md`.
> For room description authoring rules see `Project_Orion_Room_Description_Style_v1.md`.

---

## 1. BUILD PLAN — SUGGESTED NEXT ORDER

> ⚠️ Sequence changes frequently. Treat as a guide only.

1. **Room descriptions and images** — complete all 15 remaining rooms following the style guide. Generate unpowered (and where applicable reactor-off) images in Reve alongside authoring. Recreation room and engineering complete — use as reference.
2. **Power junction placement** — add junctions to main corridor, sub corridor, propulsion bay descriptions and fixed_objects.
3. **Electrical repair system** ✅ — diagnose/repair for cables, breakers, panels via power junction. `electrical_repair.py` handler, `electrical_repair_profiles.json`.
4. **Fixed object repair** — engines and reactors using same profile-driven pattern.
5. **Event system expansion** — randomisation flags, more event types, `event_effects` implementation.
6. **Jury-rigging system** — portable power pack mechanic. See Section 16.
7. **Codebase review** — clean baseline before save/load.
8. **Save/load system** — autosave only, JSON format.

---

## 2. ROOM DESCRIPTIONS — AUTHORING BACKLOG

All rooms must follow `Project_Orion_Room_Description_Style_v1.md`.

### Completed
- **Recreation Room** ✅ — reference example, all state variants
- **Engineering Bay** ✅ — all state variants including reactor states

### In Progress / Pending
Each room needs:
- `~italic~` neutral atmospheric prose
- `^power_state^` token with `description_powered` and `description_unpowered`
- Navigation (all exits, ISS convention)
- All interactables in prose
- Powered and unpowered room images generated in Reve

Special rooms needing additional tokens:
- **Propulsion Bay** — `&engine_state&` token when implemented. Two engine fixed objects. Propulsion reactor state.
- **Life Support** — `^power_state^` plus battery backup state consideration
- **Mainframe Room** — `^power_state^` plus battery backup state consideration

### Room image naming convention
- `roomname.png` — powered, all systems normal
- `roomname_unpowered.png` — unpowered, emergency lighting only
- `roomname_reactor_off.png` — powered room, reactor offline/ejected (engineering only)
- `roomname_unpowered_reactor_off.png` — unpowered, reactor offline/ejected (engineering only)

---

## 3. DUAL REACTOR SYSTEM — DESIGN

### Normal operation
- Main reactor (25kW) → ship systems (lighting, terminals, door panels)
- Propulsion reactor (120kW) → engines (sub-light + FTL)

### Main reactor ejected
Jack must manually connect the bypass cable `PWC-ENG-00` (currently starts broken — this is an intentional design element). Once connected, the propulsion reactor takes over ship systems AND engines.

**Consequences of running on propulsion reactor only:**
- Sub-light engines — full capability
- FTL — severely limited range (propulsion reactor cannot sustain jump drive load on top of ship systems)
- Brownouts — random electrical junction failures caused by overloaded reactor
- These brownouts are delivered via `reactor_overload_event` — random junction/breaker failures
- Jack must keep repairing while limping to port

**Main reactor ejection is irreversible in deep space.** The shell remains — hull integrity is maintained since the shell is rated to contain fission. Through the crystalline alumina casing, space is visible where the core used to be.

### Propulsion reactor ejected
Main reactor takes over propulsion via reverse bypass. Severely limited sub-light, no FTL.

### Both ejected
Battery backup covers life support and mainframe only. Ship is dead. Unrecoverable without external assistance. Death scenario.

### Repair scope
Jack can repair: cables, breakers, circuit panels, door access panels.
Jack cannot repair without landing at port: reactor cores, engine internals, major structural damage.

---

## 4. ELECTRICAL REPAIR SYSTEM — DESIGN ✅ IMPLEMENTED

### Overview
Diagnose/repair gameplay via PowerJunction fixed object. Player must be in the junction's room.
- Tool: `hv_service_kit` + `power_screwdriver_set`
- Components: internal panel parts, cables, breakers
- Tripped breakers reset only — no replacement part consumed
- Post-repair: calls `electrical_service.fix_component()` or sets internal flag directly

### What was built
- `electrical_repair_profiles.json` — keyed by panel ID, all 5 panels
- `electrical_repair.py` — full diagnose/repair handler
- `repair_handler.py` — 5-step routing dispatcher, handles all diagnose/repair verbs
- Internal panel components: `hv_logic_board`, `hv_bus_bar`, `hv_surge_protector`, `hv_smoothing_capacitor`, `hv_isolation_switch`
- `CircuitPanel.operational` is derived from internal component flags
- Event system breaks specific internal components via `{"id": "PNL-X", "component": "hv_logic_board"}`
- `random_component_pool` field in events.json — deferred, structure ready

### Deferred
- Junction panel images: `junction_closed.png`, `junction_open.png`
- Post-repair failure roll
- Event system randomisation (`randomise_damage: true`)

---

## 5. FIXED OBJECT REPAIR — DESIGN

### Overview
Engines and reactors repairable using same profile-driven pattern as door panels and electrical.

### Engine repair
- `Engine` class extended with repair state
- Diagnosis determines which internal components failed
- Repair requires specialist parts not carried as spares — requires port for major work
- Minor faults (sensors, relays) potentially repairable in-field

### Reactor repair
- Power sources treated as fixed objects for repair purposes
- Core replacement always requires port — out of scope for in-game repair
- Minor faults (coolant sensors, monitoring systems) potentially in-field

### Implementation
- `fixed_object_repair.py` handler
- Routed from `repair_handler.py`
- Same profile-driven pattern

---

## 6. EVENT SYSTEM EXPANSION

### Planned event types
| Type | Behaviour |
|------|-----------|
| `impact_event` | Breaks components — implemented ✅ |
| `message_event` | Delivers message to datapad — stub only |
| `solar_flare_event` | Electrical surge, trips/destroys breakers |
| `reactor_overload_event` | Random junction failures from overloaded propulsion reactor |

### Randomisation flags (deferred)
- `randomise_damage: true` — pick N random components from `random_component_pool` list
- `randomise_time: true` — fire anywhere within a time window
- `randomise_count` — how many components to pick from the pool

### Two-list damage system
- `affected_components` — always broken, exact components specified
- `random_component_pool` — pool to pick from when `randomise_damage: true`
- Both lists support: plain string (door panels), `{"id", "mode"}` (breakers/cables), `{"id", "component"}` (panel internals)

### `event_effects` array (deferred)
Future side effects beyond component damage:
```json
"event_effects": [
    {
        "type": "room_state",
        "room_id": "recreation_room",
        "state": "hull_breach_minor"
    },
    {
        "type": "atmosphere_breach",
        "room_id": "recreation_room",
        "severity": "minor"
    }
]
```

### `^room_state^` token (deferred)
For permanent room description changes triggered by events. Room carries `room_states` dict keyed by state name. `event_effects` sets active states. Multiple states stack — renderer iterates all active states.

---

## 7. SAVE / LOAD SYSTEM — DESIGN ⚠️ NEEDS FURTHER DISCUSSION

### Philosophy
No scum saving. No reloading. When you die, you are dead.

### Splash screen
- **New Game** — greyed out if save file exists
- **Continue** — greyed out if no save file exists

### Save triggers — autosave only
- Room change
- After any timed action completes
- On clean quit

### Death state
Save file written with `dead: true`. Continue shows death screen. Only New Game available.

### Self-termination ⚠️ NEEDS FURTHER DISCUSSION
Multi-step auto-destruct sequence across multiple rooms. Airlock spacing as alternative. Both write dead save state identically.

### Save file scope
Player state, portable item positions, door states, panel states, electrical system state, ship time, instance ID counters, cargo manifest state, storage manifest state, event fired/resolved flags, dead flag.

### Event system save/load ⚠️
`GameEvent.fired` and `GameEvent.resolved` are in-memory only. Must be serialised and restored after `load_from_json()` — otherwise events re-fire after loading.

---

## 8. MONOLOGUE AND DIALOGUE SYSTEM — DESIGN

### Current state
One hardcoded monologue trigger: terminal power cut.

### Planned: JSON-driven monologue system
`data/narrative/monologue.json` — keyed responses for Jack's internal voice.

Key design considerations:
- **One-shot vs repeatable** — some lines fire once only. Hearing the same monologue twice breaks immersion.
- **Tone variations by game state** — Jack early game (weary but functional) vs late game (desperate, post-compliance-order).
- **Trigger keys** — `terminal_power_failure`, `reactor_offline`, `hull_breach`, `reactor_ejected`, `power_restored` etc.

### Planned: NPC dialogue trees
Full dialogue tree system for:
- **The mainframe AI** — post-hack personality, adversarial then reluctant ally
- **The friend** — encrypted messages, backstory delivery
- **Ceres Base contact** — first external human contact

Each character gets a distinct voice box colour in the response panel.

### Voice box rendering
`appendMonologue(text, character)` — character parameter selects box colour:
- Jack — muted blue-grey `#7a8a9a`
- Mainframe AI — cold clinical green
- The friend — warmer tone TBD
- Enso VeilTech (automated) — corporate amber

---

## 9. PLAYER SURVIVAL MECHANICS (PHASE 21)

### Overview
Biological needs impose a time pressure alongside ship systems. Jack must eat, drink, sleep, and breathe.

### Mechanics
- **Hunger** — must eat at regular intervals. Galley provides food.
- **Thirst** — must drink. Water recycler in galley.
- **Fatigue** — must rest/sleep. Bunk in captain's quarters or hypersleep pod.
- **Atmospheric survival** — breathable air, correct temperature, correct pressure.

### Interaction with repairs
Survival events do not interrupt repairs — they impose penalties instead (slower repair, increased failure chance). Jack pushes through and suffers the consequences.

### Long repair auto-chain threshold
Repairs over N game minutes per component pause after completion and require the player to explicitly continue rather than auto-chaining. Prevents player leaving a repair running unattended for hours while survival mechanics tick down.

---

## 10. LIFE SUPPORT SYSTEM — DESIGN

### Overview
Binary operational states driven by electrical system. Room atmosphere depends on life support being powered and operational.

### Temperature modelling
- Room temperatures drift toward ambient (cold space) when life support fails
- Each room has `target_temperature` (JSON) and `current_temperature` (runtime)
- `ROOM_TEMP_PRESETS` in `config.py` defines temperature labels
- Do not build on this until life support phase begins — structure may change

### Dynamic room descriptions
`^room_state^` token handles atmosphere state changes — venting, temperature extremes, pressure loss.

---

## 11. OPENING NARRATIVE SEQUENCE

### Jack Harrow — starting situation
Jack Harrow is an Enso VeilTech employee operating the Tempus Fugit as a solo trader/courier. Currently in deep space, returning from a long haul run, in hypersleep.

### The opening sequence
1. Impact event wakes Jack early. Ship has damage.
2. Three messages waiting:
   - Bank — account terminated, blacklisted
   - Enso VeilTech compliance — return ship, 72 hours
   - The friend — don't comply, hack the mainframe, Ceres Base contact
3. Mainframe processes compliance order, locks navigation course.
4. Player must hack the mainframe. First major non-repair objective.

### Key decisions still to make ⚠️
- The friend's identity, backstory, and name
- The Ceres Base contact's name and personality
- The mainframe AI's name and personality post-hack
- Exact wording of the bank email and Enso VeilTech compliance message
- The 72-hour countdown mechanic in gameplay terms

---

## 12. MAINFRAME HACK — DESIGN

### Objective
Unlock the mainframe, disable the navigation lock, access alternative routing to Ceres Base.

### The mainframe AI
Present from the start as an Enso VeilTech system. Post-hack it becomes something else — its personality and relationship with Jack is a key narrative element. Details TBD.

### Gameplay
Terminal-based hack mechanic. Details TBD — depends on what the mainframe terminal stub becomes.

---

## 13. GOING DARK — SHIP DISGUISE AND BARTER (PHASE 23)

### Two layers of disguise
**Physical hull camouflage** — bolt-on external modifications. Requires EVA to install.

**Transponder obfuscator** — spoofs ship identification signal. Illegal. Underground source only. Requires barter.

### Paying for it — the cargo
The cargo represents Jack's only negotiating currency. Narrative cargo manifest to be authored.

### Key design decisions still to make ⚠️
- The cargo manifest contents — what is Jack actually carrying, and what secrets does it contain?
- The new ship name and identity
- EVA mechanics: suit duration, oxygen limits, hull attachment

---

## 14. CARGO MOVEMENT (PHASE 25)

### Deferred mechanics
- Sack barrow mechanic for moving small containers between rooms
- `cargo_handler_operational` flag on GameManager — must exist before this phase
- Stacking accessibility: stacked on pallet → accessible; stacked on container → cargo handler required
- Cargo handler item definition and repair profile

---

## 15. FUTURE PHASES (NOT IN ORDER)

**Terminal font** — CRT panels need a distinct retro/phosphor font. Applied via `terminal.css`.

**`command_handler.py` cleanup** — preposition command blocks partially duplicate `_resolve_for_verb()` logic. Targeted cleanup pass.

**Python built-in shadowing audit** — `id` and `type` as parameter names throughout. Dedicated cleanup pass.

**Scan tool software updates** — future exotic systems require purchased scan tool manuals.

**Post-repair failure roll** — probability-based failure chance, higher for complex repairs or missing manuals.

**Examine command** — `examine <item>` prints name, manufacturer, model, description to response panel. New verb in command handler.

**EVA phase** — suit mechanics, hull attachment, external modifications.

**Trading phase** — cargo barter, underground contacts, transponder obfuscator.

---

## 16. JURY-RIGGING SYSTEM — DESIGN

### Overview
A portable power pack provides emergency low-voltage (24V DC) power to compatible fixed objects when ship power is unavailable. Cannot connect to the ship grid or run HV equipment.

### Narrative context
The automated storage facility requires ship power to operate — Enso VeilTech mandates this to log all additions and retrievals and to reserve the right to withhold components remotely. When `PNL-REC-SUB-C` is broken, the storage room loses power and the facility becomes inaccessible — exactly when Jack needs the repair parts inside it. The portable power pack is the jury-rigged solution.

### Portable power pack
- Located in the cargo bay — emergency equipment
- `max_watts` field — output limit e.g. 150W
- `voltage` — 24V DC output
- Cannot power HV systems, ship grid, or door panels

### Compatible fixed objects
Fixed objects that can accept jury-rigged power carry:
- `power_watts` — consumption rating e.g. 80W
- `power_voltage` — acceptable input voltage e.g. 24V DC

### Connection mechanic
Player connects the power pack to a compatible fixed object. Handler checks:
1. Voltage matches
2. Watts do not exceed pack limit
3. If compatible — sets `jury_rigged_power: true` on the fixed object
4. Fixed object operates normally despite room power being out

### Implementation — deferred
- `PortablePowerPack` item class or fields on `PortableItem`
- `jury_rigged_power` flag on `FixedObject`
- `connect` command verb — routes to jury-rig handler
- Handler checks compatibility and sets flag
- Terminal/storage handler checks `jury_rigged_power` alongside room power

---

*Project Orion Game — Future Design & Planning v1.0 — April 2026*
