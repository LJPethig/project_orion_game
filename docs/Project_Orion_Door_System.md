# PROJECT ORION — DOOR SYSTEM
## Technical Reference
**May 2026**

---

## 1. SECURITY HIERARCHY

| Level | Panel type | Behaviour |
|-------|-----------|-----------|
| 0 | `vesper_ulock` | No card required, instant lock/unlock, emergency release available |
| 2 | `smc_ts1500` | High security card required |
| 3 | `smc_q_emerald` | High security card + PIN required |

---

## 2. PER-SIDE PANEL ASSIGNMENTS

`panel_type` is defined per panel entry in `door_status.json`, not at door level. Interior-facing side of secured rooms always has `vesper_ulock`. The corridor/outside-facing side carries the security level appropriate to the room being protected.

| Door | Outside panel | Inside panel |
|------|--------------|--------------|
| captains_quarters ↔ main_corridor | `smc_ts1500` (main_corridor) | `vesper_ulock` (captains_quarters) |
| crew_cabin ↔ main_corridor | `vesper_ulock` both sides | `vesper_ulock` both sides |
| recreation_room ↔ cockpit | `smc_ts1500` (recreation_room) | `vesper_ulock` (cockpit) |
| main_corridor ↔ engineering | `smc_ts1500` (main_corridor) | `vesper_ulock` (engineering) |
| main_corridor ↔ mainframe_room | `smc_q_emerald` (main_corridor) | `vesper_ulock` (mainframe_room) |
| All other doors | `vesper_ulock` both sides | `vesper_ulock` both sides |

Rationale: once Jack is inside a secured room he is already past the security barrier — the interior panel only needs to let him out.

---

## 3. DOOR STATE MACHINE

Three states: **open**, **closed**, **locked**.

| Command | Behaviour |
|---------|-----------|
| `open` | Unlock and open the door |
| `close` | Close the door (no card required) |
| `unlock` | Unlock only, door stays closed |
| `lock` | Lock the door |

`vesper_ulock` (level 0) — all commands instant, no card.
`smc_ts1500` (level 2) — lock/unlock require card swipe (8s).
`smc_q_emerald` (level 3) — lock/unlock require card swipe then PIN entry.

---

## 4. AUTO-CLOSE SAFETY

When Jack passes through a closed unlocked door, the door auto-closes behind him. Before closing, the destination-side panel is checked:

- **Destination panel powered and not broken** → door closes, normal message
- **Destination panel unpowered or broken** → door stays open, message: *"The door does not autoclose — the access panel on this side is unresponsive."*

This prevents Jack being trapped in a room with a non-functional panel.

---

## 5. DOOR TOOLTIP STATES

Hover tooltip on door markup in the description panel:

| Condition | Tooltip |
|-----------|---------|
| Door open, panel operational | `Door is open` |
| Door closed, panel operational | `Door is closed` |
| Door locked, panel operational | `Door is locked` |
| Room unpowered | `Door is [state] — Offline` |
| Panel broken | `Door is [state] — Offline` |
| Door emergency released | `Door is open — Offline` (both sides) |

Offline states use `--col-alert` (orange).

---

## 6. PIN BEHAVIOUR

Level 3 doors (`smc_q_emerald`) require card swipe + PIN.

- **Correct PIN** — door action completes, pin_attempts reset
- **Wrong PIN** — attempts incremented, remaining count shown
- **3 wrong PINs** — card invalidated, pin_attempts reset. **Door state unchanged** — the door stays in whatever state it was before the attempts.

---

## 7. EMERGENCY RELEASE MECHANIC

### Overview
When a `vesper_ulock` panel is offline or broken, Jack can activate the mechanical emergency release lever below the panel. This is a last resort — the door cannot be closed again until the actuator is repaired.

### Triggers
Emergency release prompt shown when Jack types `open`, `unlock`, `go`, or `enter` on a closed door where his side has a `vesper_ulock` panel that is offline or broken.

`close` and `lock` commands on an offline/broken `vesper_ulock` panel return a standard offline message — no emergency release prompt.

### Prompt
```
The [room] door access panel is unresponsive — it looks like it's offline.
The door is currently [state]. An emergency mechanical release is available — activate?
[Yes] | [No]
```

### Activation sequence
1. Yes clicked — 5 second lever animation ("ACTIVATING EMERGENCY RELEASE") with progress counter
2. After animation, `/api/command/emergency_release_complete` called with `door_id` and `pending_move`
3. Backend sets:
   - `panel.is_broken = True`
   - `panel.broken_components.append('actuator_reset')`
   - If `actuator_reset` is only fault → `panel.is_diagnosed = True` (Jack can see the lever)
   - `door.emergency_open()` → `emergency_released = True`, `door_open = True`, `door_locked = False`
   - Ship time advances 3 minutes
4. If triggered by `go`/`enter` (`pending_move = True`) — Jack moves through the door automatically
5. Response: *"Finally after several turns of the lever, each one harder than the last there is a loud crack, and the door to [room] slams open violently. The actuator is now disconnected — the door is jammed in the open position until the release mechanism can be reset."*

### Post-release state
- Door is open, `emergency_released = True`
- `close` → *"The [room] door actuator is disconnected — the door cannot be operated until the release mechanism is reset."*
- `lock` → same message
- Both sides of door show "Offline" tooltip
- State persisted in save/load

### Actuator reset repair
Jack types `diagnose panel` then `repair panel` in the room with the broken panel.

- If `actuator_reset` is the only fault and `is_diagnosed` is already True → `diagnose panel` returns instant message: *"You can see the [room] door emergency release lever has been activated. The mechanism needs resetting before the door can be operated."*
- Repair tools required (override): `scan_tool`, `power_screwdriver_set`, `wrench_set`
- Repair time: 70 game minutes
- On completion: `emergency_released` cleared, `is_diagnosed` reset, door fully operational

---

## 8. DOOR PANEL — DATA MODEL

### SecurityPanel fields
| Field | Type | Description |
|-------|------|-------------|
| `panel_id` | str | Unique panel ID |
| `door_id` | str | Parent door ID |
| `side` | str | Room ID this panel faces |
| `panel_type` | str | Key into `door_access_panel_types.json` |
| `security_level` | SecurityLevel | Resolved from panel_type at load time |
| `pin` | str\|None | Set on level 3 panels |
| `is_broken` | bool | Set by event system or emergency release |
| `is_diagnosed` | bool | Set when diagnosis completes; persisted in save/load |
| `broken_components` | list | Set at break time by event system; actuator_reset added by emergency release |
| `repaired_components` | list | Populated during repair |

### Door fields
| Field | Type | Description |
|-------|------|-------------|
| `id` | str | Unique door ID |
| `room_ids` | tuple | (room_a_id, room_b_id) |
| `door_open` | bool | |
| `door_locked` | bool | |
| `emergency_released` | bool | Set by emergency_open(); persisted in save/load |
| `panels` | dict | room_id → SecurityPanel |
| `pin` | str\|None | Set on level 3 doors |
| `pin_attempts` | int | Resets on success or card invalidation |

---

## 9. door_status.json FORMAT

```json
{
  "id": "main_corridor_mainframe_room",
  "rooms": ["main_corridor", "mainframe_room"],
  "door_open": true,
  "door_locked": false,
  "panel_ids": [
    {"id": "main_corridor_mainframe_room_panel_main", "side": "main_corridor", "panel_type": "smc_q_emerald"},
    {"id": "main_corridor_mainframe_room_panel_mainframe", "side": "mainframe_room", "panel_type": "vesper_ulock"}
  ]
}
```

Note: `panel_type` is per panel entry, not at door level.

---

## 10. API ENDPOINTS

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/command` | POST | open, close, lock, unlock, go, enter |
| `/api/command/swipe` | POST | Card swipe completion |
| `/api/command/pin` | POST | PIN submission |
| `/api/command/emergency_release_complete` | POST | Lever animation completion |

---

*Project Orion Game — Door System Reference — May 2026*
