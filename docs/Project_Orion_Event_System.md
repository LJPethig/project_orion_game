# PROJECT ORION — EVENT SYSTEM
## Technical Reference
**May 2026**

---

## 1. OVERVIEW

Scheduled events triggered by game-time thresholds. Defined in `data/game/events.json`. Frontend polls `/api/events/check` every 15 seconds.

Unknown event types or component IDs raise `ValueError` immediately — bad data must be fixed, never silently skipped.

---

## 2. EVENT JSON FORMAT

```json
{
  "id": "micrometeorite_impact",
  "type": "impact_event",
  "trigger_minutes": 2,
  "event_message": "⚠ MICROMETEORITE IMPACT DETECTED: DAMAGE REPORT: ELECTRICAL SYSTEM FAULTS.",
  "event_log_name": "Impact Event",
  "event_log_detail": "Micrometeorite impact detected. Electrical faults reported.",
  "event_resolved_message": "MICROMETEORITE IMPACT DAMAGE REPAIRED. UPDATING LOGS.",
  "event_resolved_log_detail": "Impact event faults repaired.",
  "affected_components": [
    { "id": "FUS-REC-02", "mode": "tripped" },
    "PWC-REC-02",
    "recreation_room_main_corridor_panel_rec",
    "recreation_room_cockpit_panel_rec"
  ],
  "random_component_pool": [],
  "random_selection_count": 0,
  "event_effects": [],
  "randomise_damage": false,
  "randomise_time": false
}
```

---

## 3. affected_components ENTRY FORMATS

| Format | Behaviour |
|--------|-----------|
| `"panel_id"` (plain string, door panel) | Panel broken; broken_components selected from repair profile immediately |
| `"cable_id"` (plain string, cable) | Cable broken |
| `{"id": "FUS-X", "mode": "damaged"}` | Breaker physically damaged — requires replacement part |
| `{"id": "FUS-X", "mode": "tripped"}` | Breaker tripped — reset only, no part needed |
| `{"id": "PNL-X", "component": "hv_logic_board"}` | Specific internal CircuitPanel component broken |

---

## 4. RANDOMISATION

### randomise_damage
When `true`, the event picks 1 to `random_selection_count` items from `random_component_pool` using `random.sample()` (no replacement) and breaks each one via the same `_break_component_by_id()` logic. Fires after `affected_components` are processed.

`random_component_pool` entries support all the same formats as `affected_components`.

### random_selection_count
Upper bound of selection range. `random_selection_count: 2` means pick 1 or 2 items. Always pick at least 1.

### Example
```json
"affected_components": ["FUS-REC-02"],
"random_component_pool": [
    "recreation_room_main_corridor_panel_rec",
    "PWC-REC-01",
    "FUS-REC-03"
],
"random_selection_count": 2,
"randomise_damage": true
```
Always breaks `FUS-REC-02`. Also randomly breaks 1 or 2 items from the pool.

---

## 5. DOOR PANEL COMPONENT SELECTION AT BREAK TIME

When a door panel is broken by an event, the event system immediately calls `_select_panel_broken_components()`:

1. Loads the panel's `repair_profiles.json` entry (loaded at `EventSystem.__init__`)
2. Excludes `actuator_reset` from the eligible pool — that is only added by emergency release
3. Randomly selects 1–3 components with 60/30/10 weighting
4. Stores result on `panel.broken_components` immediately

Diagnosis then reads what is already stored — no selection at diagnosis time.

---

## 6. SUPPORTED EVENT TYPES

| Type | Status | Behaviour |
|------|--------|-----------|
| `impact_event` | ✅ Implemented | Breaks `affected_components`, optionally random from pool |
| `message_event` | Stub | Delivers message to datapad |
| `solar_flare_event` | Planned | Electrical surge, trips/destroys breakers |
| `reactor_overload_event` | Planned | Random junction failures from overloaded propulsion reactor |

---

## 7. CURRENT EVENTS

### micrometeorite_impact
- **Trigger:** 2 ship minutes after game start
- **Always breaks:** `FUS-REC-02` (tripped), `PWC-REC-02`, `recreation_room_main_corridor_panel_rec`, `recreation_room_cockpit_panel_rec`
- **Random pool:** empty (randomise_damage: false)
- **Resolution:** all broken components repaired

---

## 8. RESOLUTION CHECK

`check_event_resolution()` called after any successful repair. Iterates all fired-but-unresolved events and checks each `affected_components` entry:

- Junction internal component → checks CircuitPanel flag
- Breaker → checks `operational`
- Cable → checks `intact`
- Door panel → checks `panel.is_broken`

If all pass → event resolved, resolved message fired, log entry written.

Note: `random_component_pool` items broken by randomisation are not checked for resolution — only `affected_components` drives resolution. This is intentional — random damage is bonus difficulty, not required for resolution.

---

## 9. DEFERRED

- **randomise_time** — fire anywhere within a time window. Not yet implemented.
- **event_effects** — side effects beyond component damage (room state changes, atmosphere breach). Reserved but not implemented.
- **`^room_state^` token** — permanent room description changes triggered by events. Deferred.

---

## 10. KEY FILES

| File | Role |
|------|------|
| `backend/events/event_system.py` | EventSystem class — loads, schedules, fires, resolves |
| `data/game/events.json` | All event definitions |
| `backend/api/events.py` | `/api/events/check`, `/api/events/active` |

### Import note
`event_system.py` uses lazy imports for `electrical_service` functions inside `check()` to avoid circular imports (`game_manager` imports `EventSystem`, `electrical_service` imports `game_manager`). These lazy imports have explanatory comments — do not move them to top level.

---

## 11. API ENDPOINTS

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/events/check` | GET | Check for due events at current ship time |
| `/api/events/active` | GET | All fired but unresolved events (for strip restoration on load) |

---

*Project Orion Game — Event System Reference — May 2026*
