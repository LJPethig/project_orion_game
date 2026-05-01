# PROJECT ORION GAME
## Space Survival Simulator
### Future Design & Planning Document
**Version 6.0 — May 2026**

> This document covers future phases and upcoming system designs.
> For current state see `Project_Orion_Design_v28.md`.
> For fully designed but deferred systems see `docs/deferred_systems.md`.
> For narrative canon see `docs/narrative_notes.md`.

---

## 1. BUILD PLAN — SUGGESTED NEXT ORDER

> ⚠️ Sequence changes frequently. Treat as a guide only.

1. **Room descriptions and images** — complete all 15 remaining rooms following the style guide. Generate unpowered (and where applicable reactor-off) images in Reve alongside authoring. Recreation room and engineering complete — use as reference.
2. **Power junction placement** — add junctions to main corridor, sub corridor, propulsion bay descriptions and fixed_objects.
3. **Fixed object repair** — engines and reactors using same profile-driven pattern as door panels and electrical. See Section 3.
4. **Event system expansion** — more event types, `event_effects` implementation. See Section 4.
5. **diagnosed_components list** — replace `is_diagnosed` boolean with list to support misdiagnosis mechanic. See Section 5.
6. **Sack barrow and portable container system** — See `docs/deferred_systems.md`.
7. **Jury-rigging system** — portable power pack mechanic. See `docs/deferred_systems.md`.

---

## 2. ROOM DESCRIPTIONS — AUTHORING BACKLOG

All rooms must follow `Project_Orion_Room_Description_Style_v1.md`.

### Completed
- **Recreation Room** ✅
- **Engineering Bay** ✅

### Pending
Each room needs: `~italic~` neutral prose, `^power_state^` token, navigation exits, all interactables, powered and unpowered room images.

Special rooms needing additional tokens:
- **Propulsion Bay** — `&engine_state&` token (when implemented), two engine fixed objects, propulsion reactor state
- **Life Support** — battery backup state consideration
- **Mainframe Room** — battery backup state consideration

---

## 3. FIXED OBJECT REPAIR — DESIGN

Engines and reactors repairable using same profile-driven pattern as door panels and electrical.

- `fixed_object_repair.py` handler, routed from `repair_handler.py`
- `Engine` class extended with repair state — minor faults (sensors, relays) potentially in-field
- Reactor minor faults potentially in-field; core replacement always requires port
- Save/load note: when internal component flags implemented, `FissionReactor.operational` and `Engine.online` become derived properties — save flags not direct value

---

## 4. EVENT SYSTEM EXPANSION

### Planned event types
| Type | Behaviour |
|------|-----------|
| `solar_flare_event` | Electrical surge, trips/destroys breakers |
| `reactor_overload_event` | Random junction failures from overloaded propulsion reactor |
| `message_event` | Delivers message to datapad (stub only currently) |

### randomise_time (deferred)
Fire event anywhere within a time window rather than at a fixed trigger. Field reserved in JSON, logic not yet implemented.

### event_effects (deferred)
Side effects beyond component damage:
```json
"event_effects": [
    {"type": "room_state", "room_id": "recreation_room", "state": "hull_breach_minor"},
    {"type": "atmosphere_breach", "room_id": "recreation_room", "severity": "minor"}
]
```

---

## 5. DIAGNOSED_COMPONENTS LIST

### Current state
`SecurityPanel.is_diagnosed` — boolean flag. Set when diagnosis completes, reset on repair completion. Prevents "already diagnosed" message on newly broken panels.

### Future improvement
Replace `is_diagnosed` with `diagnosed_components: list`. This enables the **misdiagnosis mechanic**.

**How it works:**
- `broken_components` — ground truth, set at break time. Never shown to player.
- `diagnosed_components` — what Jack found during diagnosis. May differ from `broken_components` if scan tool manual is missing.
- Repair proceeds from `diagnosed_components`
- Event resolution check reads `broken_components` (ground truth)
- If `diagnosed_components` ⊂ `broken_components` — panel appears repaired but some faults remain

**Implementation notes:**
- `diagnosed_components` persisted in save/load alongside `broken_components`
- `is_diagnosed` becomes redundant — replaced by `len(diagnosed_components) > 0`
- Scan tool manual validation already exists — needs to feed into component selection at diagnosis time

---

## 6. PLAYER SURVIVAL MECHANICS (PHASE 21)

Biological needs impose time pressure alongside ship systems. Jack must eat, drink, sleep, breathe.

- **Hunger, thirst, fatigue** — penalties not interruptions. Jack pushes through and suffers.
- **Long repair auto-chain threshold** — repairs over N game minutes pause and offer "continue or break?" choice.
- **Rest as necessity** — when survival is implemented, rest becomes mandatory not just a meta save action.

---

## 7. LIFE SUPPORT SYSTEM

Binary operational states driven by electrical system. Room atmosphere depends on life support being powered and operational.

- Room temperatures drift toward ambient when life support fails
- Each room has `target_temperature` (JSON) and `current_temperature` (runtime)
- `^room_state^` token handles atmosphere state changes in descriptions
- Do not build on this until life support phase begins — structure may change

---

## 8. DUAL REACTOR CONSEQUENCES

### Main reactor ejected
Jack must manually connect bypass cable `PWC-ENG-00` (starts broken — intentional). Propulsion reactor takes over ship systems AND engines.

Consequences:
- Sub-light engines — full capability
- FTL — severely limited (propulsion reactor cannot sustain jump drive + ship systems)
- Brownouts — random electrical junction failures via `reactor_overload_event`

Main reactor ejection is irreversible in deep space. Shell remains, hull intact.

### Propulsion reactor ejected
Main reactor takes over propulsion via reverse bypass. Severely limited sub-light, no FTL.

### Both ejected
Battery backup covers life support and mainframe only. Ship is dead. Death scenario.

---

## 9. FUTURE PHASES (NOT IN ORDER)

- **Terminal font** — CRT panels need distinct retro/phosphor font
- **`command_handler.py` cleanup** — preposition blocks duplicate `_resolve_for_verb()` logic
- **Scan tool software updates** — future exotic systems require purchased manuals
- **Post-repair failure roll** — probability-based failure chance
- **Examine command** — `examine <item>` → name, manufacturer, model, description
- **EVA phase** — suit mechanics, hull attachment, external modifications
- **Trading phase** — cargo barter, underground contacts, transponder obfuscator
- **Hypersleep pod** — long-distance travel rest and save point
- **Death screen UI** — dead flag in place, UI not built
- **Reactor image bug** — debug reactor break incorrectly appends `_reactor_off` to all rooms
- **Monologue system** — JSON-driven keyed responses, one-shot triggers, save/load fired keys

---

*Project Orion Game — Future Design & Planning v6.0 — May 2026*
