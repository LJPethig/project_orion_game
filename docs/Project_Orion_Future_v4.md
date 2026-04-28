# PROJECT ORION GAME
## Space Survival Simulator
### Future Design & Planning Document
**Version 4.0 — April 2026**

> This document covers future phases, system designs not yet built, narrative decisions, and open design questions.
> For current state, architecture, and technical reference see `Project_Orion_Design_v26.md`.
> For room description authoring rules see `Project_Orion_Room_Description_Style_v1.md`.
> For narrative canon see `docs/narrative_notes.md`.

---

## 1. BUILD PLAN — SUGGESTED NEXT ORDER

> ⚠️ Sequence changes frequently. Treat as a guide only.

1. **Room descriptions and images** — complete all 15 remaining rooms following the style guide. Generate unpowered (and where applicable reactor-off) images in Reve alongside authoring. Recreation room and engineering complete — use as reference.
2. **Power junction placement** — add junctions to main corridor, sub corridor, propulsion bay descriptions and fixed_objects.
3. **Fixed object repair** — engines and reactors using same profile-driven pattern as door panels and electrical.
4. **Event system expansion** — randomisation flags, more event types, `event_effects` implementation.
5. **Sack barrow and portable container system** — See Section 17.
6. **Jury-rigging system** — portable power pack mechanic. See Section 16.

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

## 4. ELECTRICAL REPAIR SYSTEM — ✅ IMPLEMENTED

See `Project_Orion_Design_v26.md` Section 19 for full details.

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

### Save/load note
When reactor and engine internal components are implemented:
- `FissionReactor.operational` becomes a derived property — save the internal component flags instead of the direct flag
- `Engine.online` same pattern
- Both are flagged in the existing `save_manager.py` comments

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

## 7. SAVE/LOAD SYSTEM — ✅ COMPLETE AND TESTED

See `Project_Orion_Design_v26.md` Section 20 for full details. Phase 19.5 is complete.

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
- **Survival guidance** — monologue also serves as the mechanism for guiding Jack (and the player) through genuinely hopeless situations. Jack's survival instinct fires as internal voice, giving the player a direction they wouldn't have found alone. This replaces any need for a mechanical lucky break system.
- **Save/load** — fired monologue keys must be saved to prevent repeat triggers. Add to save_manager when implemented.

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
- **Fatigue** — must rest/sleep. Bunk in captain's quarters or rec-room sofa.
- **Atmospheric survival** — breathable air, correct temperature, correct pressure.

### Interaction with repairs
Survival events do not interrupt repairs — they impose penalties instead (slower repair, increased failure chance). Jack pushes through and suffers the consequences.

### Long repair auto-chain threshold
Repairs over N game minutes per component pause after completion and present the player with a "continue or take a break?" choice rather than auto-chaining. This is the natural save point for long repairs. Prevents player leaving a repair running unattended while survival mechanics tick down.

### Rest and save integration
Jack must rest every 16 ship hours to avoid fatigue penalties. Rest is already the only save point. When survival mechanics are implemented, rest becomes a necessity rather than just a meta action — the save system becomes self-enforcing.

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
See `docs/narrative_notes.md` for full narrative canon. Summary:

- Jack is 18 days from destination, in hypersleep
- 3 months earlier, a bank hack destroyed his finances — he is blacklisted
- Enso VeilTech knows, has arranged security and legal to meet him on arrival
- The impact event wakes him early — only he can repair the ship
- A security vessel is now diverted: **48 hours away**

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
- The 48-hour countdown mechanic in gameplay terms

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

**Scan tool software updates** — future exotic systems require purchased scan tool manuals.

**Post-repair failure roll** — probability-based failure chance, higher for complex repairs or missing manuals.

**Examine command** — `examine <item>` prints name, manufacturer, model, description to response panel. New verb in command handler.

**EVA phase** — suit mechanics, hull attachment, external modifications.

**Trading phase** — cargo barter, underground contacts, transponder obfuscator.

**Hypersleep pod** — used for long-distance travel. Also a natural rest and save point (deferred).

**Death screen UI** — dead flag infrastructure in place. start-screen screen death state UI not yet built. See `load_game_route()` docstring in `game.py` for required behaviour.

**Door trap — unpowered panel on destination side** — potential softlock when Jack enters a room with a non-functional panel on the destination side. No decision made on fix. See Session Notes in design doc.

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
- `jury_rigged_power` flag on `FixedObject` — must be saved when implemented
- `connect` command verb — routes to jury-rig handler
- Handler checks compatibility and sets flag
- Terminal/storage handler checks `jury_rigged_power` alongside room power

---

## 17. SACK BARROW AND PORTABLE CONTAINER SYSTEM — DESIGN

### Overview
The sack barrow allows Jack to transport a portable container between rooms, effectively extending his carry capacity for repair operations. Essential for heavy repair jobs where parts exceed Jack's personal carry limit.

### Narrative context
Jack's carry capacity is limited — a full junction repair requiring multiple cables, breakers and connectors can exceed what one person can carry. The sack barrow is the practical solution for moving a parts container from storage to the repair site.

### Mechanics
- `use sack barrow` — Jack loads a portable container onto the barrow. The container and its contents become accessible as part of Jack's effective inventory for repair part checks.
- `leave sack barrow` — Jack leaves the barrow (and container) in the current room. It is no longer part of his effective inventory.
- The sack barrow itself is a portable item Jack must be carrying or have in the room.
- Only one container can be loaded at a time.
- The barrow cannot be taken up ladders or through certain hatches — deferred constraint.

### Repair system integration
The repair handler's part check (`_check_all_parts`) must be extended to include contents of any container currently loaded on Jack's sack barrow, in addition to his personal inventory.

### Implementation — deferred
- `SackBarrow` item class or fields on `PortableItem`
- `loaded_container` reference on `SackBarrow` — must be saved when implemented
- `use` command verb — routes to sack barrow handler
- Repair handler checks `player.sack_barrow.loaded_container.contents` alongside inventory
- `PLAYER_MAX_CARRY_MASS` in `config.py` currently 40kg for testing until this is implemented

---

*Project Orion Game — Future Design & Planning v4.0 — April 2026*
