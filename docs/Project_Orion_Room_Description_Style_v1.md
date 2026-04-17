# Project Orion — Room Description Style Guide
## Version 1.1 — April 2026

---

## PURPOSE

This document defines the writing rules for all room descriptions in Project Orion.
Every room description must follow these rules without exception. Consistency is
essential — the player builds a mental model of the game world through the prose,
and inconsistency breaks immersion.

---

## STRUCTURE

Every room description has the following structure, in this order:

### 1. Neutral Prose — Atmosphere and Character
Describes the physical space. Makes the room feel inhabited and real. No reference
to power state whatsoever. No takeable items. Pure set dressing and character.

### 2. Power State Addendum (italic)
Injected by the renderer at the position of the state token in the description
array. Rendered in italic, same default grey colour as prose. Two standard variants:

- **description_powered** — atmosphere when room has power
- **description_unpowered** — atmosphere when room has no power

See Special Cases below for rooms that require additional power state variants.

### 3. Navigation
All exits, every one. Uses ISS directional convention. No exceptions.

### 4. Interactables
All interactive fixed objects — storage units, surfaces, terminals, power junctions,
engines, cargo handler etc. No portable items. No contents of containers or surfaces.

---

## TOKEN INJECTION SYSTEM

### Overview
The `description` array in `ship_rooms.json` is a mixed array of prose strings
and state tokens. The renderer processes each element in order:

- **Prose string** — rendered as normal description text
- **State token** — resolved to the appropriate state-specific array and rendered
  in italic

This allows the author to control exactly where state addendums appear in the
description flow without hardcoding any logic in the renderer.

### Token Reference

| Token | Resolves to | JSON fields |
|-------|-------------|-------------|
| `^power_state^` | Room power state addendum | `description_powered`, `description_unpowered` |
| `@reactor_state@` | Main reactor state addendum | `description_reactor_online`, `description_reactor_offline`, `description_reactor_ejected` |
| `&engine_state&` | Engine state addendum | `description_engines_online`, `description_engines_offline` |

Additional tokens can be added as new game systems require them. The renderer
gains one new condition per token type. All other rooms are unaffected.

### Renderer Logic
1. Iterate through the `description` array
2. If element is a prose string — render normally
3. If element matches a token pattern — resolve to the correct state-specific
   array and render those lines in italic
4. If a token has no matching state field — render nothing (silent skip)

### Fallback Behaviour
If a special case state field is absent, the renderer skips the token silently.
This means rooms only carry the fields they need. No empty fields, no null checks
for irrelevant states.

### Example — ship_rooms.json
```json
"description": [
    "The curved hull walls close in around an amber leather sofa...",
    "^power_state^",
    "The *cockpit* is through the forward door..."
],
"description_powered": [
    "The strip lighting hums overhead. The forward screen loops..."
],
"description_unpowered": [
    "The strip lighting is dead. Photoluminescent deck strips..."
]
```

### Design Principles
- **Order is preserved** — the author controls placement of addendums exactly
- **Tokens are explicit** — readable in JSON without knowing the renderer
- **Extensible** — new state types require only a new token and new JSON fields
- **Backend agnostic** — the backend serves state data as it already does.
  All token resolution logic lives in the frontend renderer
- **Rooms only carry what they need** — engineering has `@reactor_state@`,
  the rec room does not

---

## WRITING RULES

### Voice
Jack Harrow is a working spacer — experienced, weary, dry. The prose reflects his
perspective. Understated, observational, occasionally sardonic. Never corporate,
never generic, never tourist-brochure.

### Neutral Prose Rules
- **No power state references** — no hums, lighting, screens active, beeping,
  flickering. Anything that requires electricity belongs in the addendum only.
- **No takeable items** — contents of surfaces and containers are rendered
  dynamically by Layer 2 and Layer 3. Never mention them in prose.
- **One detail that earns its place** — every description should have one specific,
  unexpected detail that makes the room feel real and lived in.
- **General detritus is acceptable** — non-interactive clutter (food wrappers,
  old magazines, general mess) can be referenced as set dressing. It must be
  mundane enough that no player would attempt to interact with it.
- **Open with sensation or character** — never label the room. Make the player
  feel they are standing in it.
- **Objects earn their mention** — only reference what the player can interact
  with, or what tells us something true about Jack's life.
- **Contents stay out of prose** — never describe what is on a surface or inside
  a container. The markup and layer system handles that.

### Power State Addendum Rules
- **Short** — two to four sentences maximum.
- **Italic rendering** — the renderer applies italic style automatically.
- **Mirror structure** — powered and unpowered addendums should reference the
  same elements in opposite states where possible. This creates a deliberate
  parallel that feels intentional.
- **Photoluminescent deck strips** — all rooms have these as emergency lighting.
  They are independent of the electrical system. Always present, always dim green.
  Reference them in unpowered addendums where appropriate.
- **No life support references** — air recycler, oxygen levels, temperature etc.
  are independent systems that can fail separately. Never reference them in a
  power state addendum.

### Navigation Rules
- **ISS directional convention** — forward, aft, port, starboard, overhead, deck.
  No compass directions. No relative terms (behind you, to your left, in front).
- **Forward = toward cockpit** — this is the ship's forward direction throughout.
- **All exits must appear** — every exit in the room's JSON must be referenced
  in the prose. No exceptions.
- **Exits at the end of neutral prose** — navigation comes after atmosphere,
  before interactables.
- **Group related exits** — exits on the same bulkhead or serving similar
  destinations can share a sentence naturally.
- **Exits as destinations, not directions** — "the galley is through the
  starboard hatch" not "a hatch on the right leads somewhere".

### Interactable Rules
- **All interactables must appear** — every fixed interactive object must be
  referenced. Surfaces, storage units, terminals, power junctions, engines,
  cargo handler.
- **No contents** — never describe what is on a surface or inside a container.
- **Anchor objects to each other or the space** — objects in relationship to
  each other read as scene, not list.
- **Power junctions use ?name? markup** — e.g. ?power junction?, ?main power junction?

---

## MARKUP REFERENCE

| Object type | Markup | Rendering |
|-------------|--------|-----------|
| Exit/door | `*label*` | Title case, bold, exits colour |
| Storage unit | `%name%` | Title case, bold, containers colour |
| Surface | `#name#` | Title case, bold, containers colour |
| Terminal | `!name!` | Title case, bold, terminals colour |
| Power junction | `?name?` | Title case, bold, junctions colour |

All markup renders title case and bold. The colour distinguishes the object type.

---

## SPECIAL CASES — ADDITIONAL POWER STATES

Certain rooms require additional addendum variants beyond the standard
powered/unpowered pair. These are added as optional fields in ship_rooms.json
and the renderer falls back to the standard addendum if the special case field
is absent.

### Engineering
The main reactor may be operational while the room itself has no power (cable
or breaker fault between reactor and distribution panel). The reactor may also
be ejected. These are meaningfully different atmospheric states.

Planned additional variants:
- `description_reactor_offline` — room powered but reactor not operational
- `description_reactor_ejected` — reactor has been ejected

### Propulsion Bay
The propulsion reactor and engines have an independent electrical tree. Engine
state is separate from room lighting state.

Planned additional variants:
- `description_engines_offline` — room powered but engines not running
- `description_propulsion_reactor_offline` — propulsion reactor not operational

### Life Support
May be running on battery backup while mains power is lost. Battery backup state
has its own distinct atmosphere — something is running, but something is also wrong.

Planned additional variants:
- `description_battery_backup` — running on battery, mains lost

### Mainframe Room
Same battery backup consideration as life support.

Planned additional variants:
- `description_battery_backup` — running on battery, mains lost

### Implementation Note
Special case variants are deferred. The standard powered/unpowered addendum
covers all rooms including these for the initial implementation. Special case
fields are added per room when the relevant game systems are built out.

---

## LENGTH CONSTRAINT

Room descriptions must not require scrolling in the description panel before
any containers are opened. Once containers open and Layer 2 content renders,
scrolling is acceptable and unavoidable.

This constraint applies to the neutral prose plus one addendum combined.
Keep prose tight. Every sentence must earn its place.

---

## REFERENCE EXAMPLE — Recreation Room

**ship_rooms.json:**
```json
"description": [
    "The curved hull walls close in around an amber leather sofa — too large, too expensive, entirely wrong for a cargo hauler. A stained rug covers part of the deck, the rest scattered with food wrappers, old magazines and the general detritus of a man living alone in deep space.",
    "^power_state^",
    "The *cockpit* is through the forward door, the *main corridor* through the aft hatch. The *galley* is through the starboard hatch. Port side doors lead to the *med-bay* and *storage room*. A #shelving unit# runs along the starboard bulkhead, a ?power junction? mounted beside the aft hatch on the port side."
],
"description_powered": [
    "The strip lighting hums overhead. The forward screen loops between an Enso VeilTech corporate wellness programme nobody asked for and product infomercials nobody watches — ways to spend what's left of your meagre salary after corporate deductions."
],
"description_unpowered": [
    "The strip lighting is dead. Photoluminescent deck strips cast just enough green light to navigate carefully. The forward screen is dark and silent — a small mercy. Something somewhere has gone wrong."
]
```

**Rendered — powered (addendum in italic):**

The curved hull walls close in around an amber leather sofa — too large, too
expensive, entirely wrong for a cargo hauler. A stained rug covers part of the
deck, the rest scattered with food wrappers, old magazines and the general
detritus of a man living alone in deep space.

*The strip lighting hums overhead. The forward screen loops between an Enso
VeilTech corporate wellness programme nobody asked for and product infomercials
nobody watches — ways to spend what's left of your meagre salary after corporate
deductions.*

The *cockpit* is through the forward door, the *main corridor* through the aft
hatch. The *galley* is through the starboard hatch. Port side doors lead to the
*med-bay* and *storage room*. A #shelving unit# runs along the starboard
bulkhead, a ?power junction? mounted beside the aft hatch on the port side.

**Rendered — unpowered (addendum in italic):**

The curved hull walls close in around an amber leather sofa — too large, too
expensive, entirely wrong for a cargo hauler. A stained rug covers part of the
deck, the rest scattered with food wrappers, old magazines and the general
detritus of a man living alone in deep space.

*The strip lighting is dead. Photoluminescent deck strips cast just enough green
light to navigate carefully. The forward screen is dark and silent — a small
mercy. Something somewhere has gone wrong.*

The *cockpit* is through the forward door, the *main corridor* through the aft
hatch. The *galley* is through the starboard hatch. Port side doors lead to the
*med-bay* and *storage room*. A #shelving unit# runs along the starboard
bulkhead, a ?power junction? mounted beside the aft hatch on the port side.

---

*Project Orion Game — Room Description Style Guide v1.1 — April 2026*
