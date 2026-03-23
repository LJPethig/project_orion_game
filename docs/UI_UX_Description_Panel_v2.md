# PROJECT ORION
## UI/UX Design — Room Description Panel
### Version 2.0 — March 2026

---

## 1. OVERVIEW

The description panel is the primary interface between the player and the game world. It has three responsibilities:

1. **Atmosphere** — authored prose that sets the scene for each room
2. **Interaction** — highlighted, clickable spans that tell the player what they can interact with
3. **State** — dynamic sections below the prose that reflect current room state (open containers, surface items)

Everything the player can interact with is visible in the description panel. There is no separate "YOU SEE" list. The description IS the room.

The text input is the primary interaction method. Click behaviour on spans is a convenience enhancement — it must never replace or shortcut the typed command flow.

---

## 2. DESCRIPTION STRUCTURE

The panel has three layers, rendered top to bottom:

```
┌─────────────────────────────────────────────┐
│  LAYER 1 — Static prose                     │
│  Authored in ship_rooms.json. Never changes.│
│  Contains all markup spans.                 │
├─────────────────────────────────────────────┤
│  LAYER 2 — Open container contents          │
│  Only shown if one or more containers are   │
│  open. One line per open container.         │
│  Generated dynamically by backend.          │
├─────────────────────────────────────────────┤
│  LAYER 3 — Surface contents                 │
│  Only shown if a surface has been clicked   │
│  and has items on it.                       │
│  Generated dynamically by backend.          │
└─────────────────────────────────────────────┘
```

Layers 2 and 3 are conditional — they appear and disappear as game state changes. Layer 1 is always present.

---

## 3. MARKUP TYPES

Four markup types are used in description prose. Each has distinct delimiters, colour, hover behaviour, and click behaviour.

### 3.1 `*exit*` — Door / Exit

**Example:** `"A hatch leads back to the *recreation room*."`

Exits are hover-only. Doors have three states (open, closed, locked) and security procedures — reducing them to a click would be ambiguous and would undermine the text adventure nature of the game.

| Property | Value |
|----------|-------|
| Colour | Cyan (`--col-title`) |
| Bold | No |
| Hover | Door state tooltip: "Open", "Closed", or "Locked" (colour coded green/grey/orange) |
| Click | None — hover only |
| Always interactive | Hover yes, click no |

### 3.2 `%object%` — Container

**Example:** `"A %personal locker% with twin sliding doors is built into the far wall."`

Containers are fixed storage units with an open/closed state (lockers, cabinets, crates). The player can open and close them.

| Property | Value |
|----------|-------|
| Colour | Always cyan (`--col-title`) regardless of open/closed state or contents |
| Bold | No |
| Hover | "Open" or "Closed" |
| Click | Toggles state — `open <container>` if closed, `close <container>` if open |
| Always interactive | Yes |

When a container is open, its contents appear in **Layer 2** below the prose.

### 3.3 `!terminal!` — Terminal

**Example:** `"An access !personal terminal! glows softly on the desk."`

Terminals are fixed interactive computer terminals. Same visual appearance as containers but different click behaviour.

| Property | Value |
|----------|-------|
| Colour | Always cyan (`--col-title`) |
| Bold | No |
| Hover | "Terminal" (future: "Offline" when power is implemented) |
| Click | `use <terminal>` |
| Always interactive | Yes |

### 3.4 `#surface#` — Surface

**Example:** `"A #metal shelf# runs along the side wall."`

Surfaces are fixed open storage locations — shelves, benches, tables, racks. Unlike containers they have no open/closed state. Items dropped in the room land on one of the room's designated surfaces.

| Property | Empty state | Has items state |
|----------|-------------|-----------------|
| Colour | Grey (`--col-text`) | Purple (`--col-portable`) |
| Bold | Yes | Yes |
| Hover | "Empty" | Item count, e.g. "3 items" |
| Click | Examine text in response panel | Examine text in response panel and expands contents in Layer 3 |

Bold in both states — signals interactivity consistently. Colour change alone communicates whether items are present.

---

## 4. LAYER 2 — OPEN CONTAINER CONTENTS

Appears below the static prose when one or more containers in the room are open.

**Format:**
```
Personal Locker (open)    Flight Coveralls, Pilot's Jacket, Mag Boots
```

- Container name is cyan, clickable — clicking closes it
- Item names are purple, clickable — clicking takes the item (`take <item>`)
- One line per open container
- If multiple containers are open, multiple lines appear in the order they were opened
- Disappears entirely when all containers are closed

---

## 5. LAYER 3 — SURFACE CONTENTS

Appears below Layer 2 (or below prose if Layer 2 is empty) when the player clicks a surface that has items on it.

**Format:**
```
Metal Shelf    Wrench, Socket Set, Laser Solderer
```

- Surface name is purple, clickable — clicking collapses Layer 3
- Item names are purple, clickable — clicking takes the item (`take <item>`)
- Only one surface can be expanded at a time
- Collapses automatically when all items are taken from the surface

---

## 6. SURFACE — DROP BEHAVIOUR

Every room has at least one designated surface. When the player drops an item it goes onto a randomly selected available surface in the room. The player can also explicitly place an item on a specific surface with `put <item> on <surface>`.

Surfaces are defined in `ship_rooms.json`:

```json
"drop_surfaces": ["storage_room_metal_shelf", "storage_room_small_cabinet"]
```

The surface's colour updates immediately to purple when the first item lands on it, and returns to grey when the last item is taken.

---

## 7. COLOUR SUMMARY

| Element | Colour | Variable |
|---------|--------|----------|
| Exit span | Cyan | `--col-title` |
| Container span | Cyan | `--col-title` |
| Terminal span | Cyan | `--col-title` |
| Surface span — empty | Grey bold | `--col-text` |
| Surface span — has items | Purple bold | `--col-portable` |
| Container name in Layer 2 | Cyan | `--col-title` |
| Item name in Layer 2 | Purple | `--col-portable` |
| Surface name in Layer 3 | Purple | `--col-portable` |
| Item name in Layer 3 | Purple | `--col-portable` |

All interactive spans gain a hover effect (existing CSS behaviour).

---

## 8. MARKUP SUMMARY TABLE

| Markup | Type | Empty colour | Has items colour | Hover | Click |
|--------|------|-------------|-----------------|-------|-------|
| `*exit*` | Exit | Cyan | Cyan | Door state | None |
| `%object%` | Container | Cyan | Cyan | Open/Closed | Toggle open/close |
| `!terminal!` | Terminal | Cyan | Cyan | "Terminal" | `use <terminal>` |
| `#surface#` | Surface | Grey bold | Purple bold | "Empty" / item count | Examine or expand |

---

## 9. EXAMPLE — STORAGE ROOM

**ship_rooms.json description:**
```json
"description": [
    "The ship's designated small storage room. A %large storage unit% is attached to the wall, and a %small cabinet% is mounted next to it.",
    "A #metal shelf# runs along the side wall. The lighting here is harsh and functional.",
    "An automated storage facility is built into the rear wall with an attached !storage terminal!. A hatch leads back to the *recreation room*."
],
"drop_surfaces": ["storage_room_metal_shelf"]
```

**Rendered with large storage unit open and wrench on shelf:**

```
The ship's designated small storage room. A large storage unit is attached
to the wall, and a small cabinet is mounted next to it.
A metal shelf runs along the side wall. The lighting here is harsh
and functional.
An automated storage facility is built into the rear wall with an attached
storage terminal. A hatch leads back to the recreation room.

Large Storage Unit (open)    Socket Set, Electrical Service Kit

Metal Shelf    Adjustable Wrench
```

---

## 10. RESOLVED QUESTIONS

- **Multiple surfaces** — yes, a room can have more than one surface. Dropped items land on a randomly selected available surface. Player can specify with `put <item> on <surface>`.
- **Examine on empty surface** — examine text comes from the object's `description` field in `fixed_objects.json`.
- **Offline terminals** — when electrical system is implemented (Phase 15), terminals without power show "Offline" on hover and do not respond to click. Colour change TBD.
- **Explicit surface placement** — `put <item> on <surface>` command confirmed. Deferred to Phase 13 implementation.
- **Exit click** — exits are hover-only. Three door states and security procedures make click behaviour ambiguous and would undermine the text adventure interaction model.

---

*Project Orion — UI/UX Design Document v2.0*
*March 2026*
