# PROJECT ORION GAME — NEW CHAT HANDOFF
**March 2026**

---

## CRITICAL RULES — READ FIRST

1. **Never output complete `game.html` or `game.js`** — targeted inline changes only
2. **Always ask to see files before editing** — never work from memory or stale copies
3. **Read uploaded files before making changes** — no assumptions
4. **Minimal targeted changes** — no "while I'm in here" improvements without asking
5. **Backend owns all game state** — JS is display only
6. **Small changes = inline instructions. Large changes = complete file output**
7. **Never add "type X to fix it" hints** — immersive messages only

---

## PROJECT SUMMARY

Flask/HTML/CSS/JS space survival simulator. Player is **Jack Harrow** aboard **Tempus Fugit** (2276). Active codebase: `project_orion_game`.

Two read-only reference projects exist:
- `project_dark_star` — Python/Arcade predecessor. **Deprecated** — Orion Game has surpassed it.
- Electrical system reference project — standalone project with reactor, panels, breakers, cables and SVG diagnostic map. Will merge into Orion Game in Phase 17.

**Design doc:** `project_orion_game/docs/Project_Orion_Design_v7.md`
**Phase 15 addendum:** `project_orion_game/docs/Phase_15_Smart_Parser.md`

---

## CURRENT STATE

### What is complete
- Phases 6-14 complete (rooms, doors, movement, repair, items, containers, surfaces, equip, inventory screen)
- Phase 15 smart command parser — nearly complete, one task remaining (see below)
- Item registry refactored — unique instances per placement

### Phase 15 remaining task — DO THIS FIRST
Strip keyword fallback from handlers. The resolver in command_handler.py now resolves all keywords to IDs before handlers are called. Handlers still have item.id == target or item.matches(target) as fallback — this needs to become item.id == target only.

Handlers to update:
- item_handler.py — handle_drop, _find_portable_in_room
- equip_handler.py — handle_wear, handle_remove
- container_handler.py — handle_take_from, handle_put_in, handle_put_on, _find_storage_unit, _find_surface

Process:
1. Run a full stress test first (see test procedure below)
2. Only strip keyword fallback if no unexpected [RESOLVER FAIL] entries
3. After stripping, run stress test again to confirm nothing broke

### Next phases
- Phase 16 — Terminals (use terminal, TERM tab in tab strip, ship status, SVG map)
- Phase 17 — Electrical system integration (merge reference project)
- Phase 18 — Full repair system

---

## ARCHITECTURE

### Backend
```
backend/
├── models/
│   ├── game_manager.py     — central coordinator, single shared instance
│   ├── ship.py             — rooms, doors, fixed objects, item placement
│   ├── room.py             — Room class, floor list
│   ├── door.py             — Door, SecurityPanel
│   ├── interactable.py     — PortableItem, StorageUnit, Surface, Terminal
│   ├── player.py           — inventory, equip slots
│   └── chronometer.py      — ship time
├── handlers/
│   ├── base_handler.py     — _find_exit (with noise word stripping), _check_card
│   ├── command_handler.py  — resolver, clarification system, verb registry
│   ├── movement_handler.py
│   ├── door_handler.py
│   ├── repair_handler.py
│   ├── item_handler.py
│   ├── container_handler.py
│   └── equip_handler.py
├── loaders/
│   └── item_loader.py      — registry stores raw dicts, instantiate_item() for fresh instances
└── api/
    ├── game.py             — /api/game/room, /api/game/inventory
    └── command.py          — /api/command, /api/command/swipe, /api/command/pin, /api/command/repair_complete
```

### Frontend JS load order (critical)
```
constants.js → api.js → loop.js → ui.js → commands.js → description.js → inventory.js → game.js
```

### Data files
```
data/
├── items/
│   ├── tools.json
│   ├── wearables.json
│   ├── misc_items.json
│   ├── consumables.json
│   ├── terminals.json
│   ├── storage_units.json
│   └── surfaces.json
└── ship/structure/
    ├── ship_rooms.json
    ├── door_status.json
    ├── initial_ship_state.json
    ├── initial_ship_items.json    ← room_floor, containers, surfaces sections
    └── player_items.json
```

---

## KEY ARCHITECTURAL DECISIONS

### Command resolver
All commands go through command_handler.process():
1. Preposition commands intercepted (take from, put in, put on)
2. Ambiguity check — _check_ambiguity() — returns clarification_required if multiple distinct matches
3. Resolver — _resolve_for_verb() converts keywords to IDs
4. Handler receives ID

Resolver scopes: inventory, equipped, room_portable, room_fixed
Resolver debug log: resolver_debug.log in project root

### Clarification system
clarification_required action type — frontend renders clickable options in response panel separated by |. Clicking fires unambiguous command. No command echo shown.

### Object ID convention
roomid_markuptext — ensures endsWith matching is unambiguous within a room.

### Item instances
item_loader.py stores raw dicts. instantiate_item(dict(data)) creates fresh instance each call. Every placed item is unique Python object.

### Floor
room.floor list — fallback when no surface available. Shown as Floor: item1, item2 in description. Automatic only — not a player-accessible drop target.

### Slide-out panels
Tab strip on left edge of image panel. INV tab opens inventory. Panels close on room change. Framework ready for TERM tab (Phase 16).

---

## STRESS TEST PROCEDURE

Run before stripping keyword fallback from handlers. Check resolver_debug.log for unexpected [RESOLVER FAIL] entries.

1. take <item> — surface, open container, floor
2. drop <item> — single surface, multiple surfaces (clarification), no surface (floor)
3. wear <item>, remove <item> — each wearable
4. open/close <container> — by keyword
5. put <item> in <container>, put <item> on <surface> — by keyword
6. take <item> from <container>, take <item> from <surface>
7. Ambiguous cases — take wire (multiple wires), wear boots (multiple boots), open cabinet (multiple cabinets)
8. UI clicks — inventory buttons, Layer 2/3 items, floor items, clarification options
9. Movement, door commands, repair panel — should pass through resolver unchanged
10. Nonexistent item — should get clean not found message

---

## KNOWN ISSUES

- Keyword fallback still in handlers — remove after stress test
- put <item> in <surface> gives wrong error message — improve in Phase 15 cleanup
- Consumable length_m attribute — add to consumables.json when repair system built
- Clarification for same-name items with different state — fix when length_m exists
- Examine/look at command — deferred, to be discussed
- PAM — dormant until life support phase
- DEBUG_HAS_REPAIR_TOOL = True in config.py — replace with real tool check in Phase 17

---

## SESSION RULES

- Upload the codebase zip at start of session
- Upload specific files before editing them
- Commit working states before attempting new features
- Use DEPRECATED folder rather than deleting files
- Push back on careless mistakes — the rule is read before you edit
