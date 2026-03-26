# Phase 15 — Smart Command Parser
## Design Addendum
**March 2026**

---

## Background

The current command system has two separate resolution paths:

- **Typed commands** — keyword matching in handlers against live game objects. `drop pam` → handler searches inventory for item matching keyword `"pam"`.
- **UI clicks** — ID resolution in frontend against `currentObjects`/`contents`/`floor_items`. Click fires with known ID.

These two paths never meet. The bug exposed in Phase 14b was that inventory action buttons were incorrectly routing UI clicks (which know the ID) through the typed command parser (which expects keywords). The short-term fix was adding `item.id == target` checks to the affected handlers.

---

## Target Architecture

The command handler becomes a single resolution point. Every command — whether typed by the player or fired by a UI click — goes through the same path:

### Resolution flow
1. `command_handler.process` parses verb and raw args as normal
2. Before passing args to the handler, the resolver attempts to find the target object:
   - **ID match first** — search inventory, equipped slots, room surfaces, floor, and fixed objects for an exact ID match
   - **Keyword match second** — if no ID match, search by keyword as currently
   - **Multiple keyword matches** — ambiguity detected, return `clarification_required` response with clickable options (see below)
   - **No match** — pass args through to handler unchanged (handler returns appropriate "not found" message)
3. Pass the resolved ID to the handler
4. Handler does a simple ID lookup — no keyword matching needed

### Result
- Handlers get simpler — ID lookup only, no keyword matching
- Typed commands and UI clicks go through the same path
- No dedicated endpoints needed for UI actions
- Resolution logic lives in one place

---

## Clarification System

When the resolver finds multiple keyword matches, it returns a `clarification_required` response:

```json
{
    "action_type": "clarification_required",
    "response": "Which cabinet do you want to open?",
    "options": [
        { "label": "Small Cabinet", "command": "open storage_room_small_cabinet" },
        { "label": "Large Storage Unit", "command": "open storage_room_large_storage_unit" }
    ]
}
```

The frontend renders options as clickable cyan spans in the response panel. Clicking fires the full unambiguous command with the resolved ID — which then passes straight through the resolver as an ID match.

### Cases covered
- `repair panel` — multiple broken panels in room
- `take card` — multiple cards on surfaces/floor
- `drop card` — multiple surfaces in room (currently random, should ask)
- `open cabinet` — multiple cabinets in room
- `put card on shelf` — multiple surfaces matching "shelf"
- Any future command where the target is not uniquely identifiable

---

## Handler Simplification

Once the resolver is in place, handlers no longer need keyword matching. Example — `item_handler.handle_drop` becomes:

```python
def handle_drop(self, item_id: str) -> dict:
    item = game_manager.player.find_in_inventory(item_id)
    if not item:
        return self._instant(f"You are not carrying that.")
    # ... drop logic
```

All the `item.matches(target)` calls are removed. The resolver handles all of that upstream.

---

## Migration Strategy

1. Build resolver in `command_handler.process`
2. Update handlers one at a time — each becomes simpler
3. Remove `item.id == target or item.matches(target)` patches added in Phase 14
4. Wire up clarification response in frontend

---

*Phase 15 Design Addendum*
*March 2026*
