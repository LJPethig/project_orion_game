# PROJECT ORION — REPAIR SYSTEM
## Technical Reference
**May 2026**

---

## 1. OVERVIEW

Profile-driven multi-step repair used by both door panels and electrical junctions. Architecture is generic — same pattern will apply to future fixed object repair.

Routing dispatcher in `repair_handler.py` — 5-step routing in order:
1. Unambiguous electrical keywords (`junction`, `electrical panel`, `PNL-` prefix) → electrical handler
2. Fixed object keywords (stub — no repairable fixed objects yet) → fixed object handler
3. Unambiguous door targets (exit labels, door noise words) → door panel handler
4. Ambiguous/empty args → check room contents (clarification if both present)
5. Unrecognised args → "You can't diagnose that."

---

## 2. DOOR PANEL REPAIR

### Diagnosis architecture
Broken component selection happens **at break time** — when an event fires and damages a panel, the event system immediately selects random broken components from `repair_profiles.json` and stores them on `panel.broken_components`. Diagnosis reveals what is already stored — no random selection happens at diagnosis time.

If `broken_components` is empty when diagnosis runs, this is a data error — crash loudly.

### is_diagnosed flag
`SecurityPanel.is_diagnosed` — set to `True` when `complete_diagnosis` runs. Resets to `False` on repair completion. Persisted in save/load.

- `broken_components` populated + `is_diagnosed = False` → panel broken, not yet diagnosed. Must diagnose before repair.
- `broken_components` populated + `is_diagnosed = True` → diagnosed, repair can proceed.
- Emergency release sets `is_diagnosed = True` immediately if `actuator_reset` is the only fault — Jack can see the lever state without formal diagnosis.

### Door panel state machine
```
is_broken = False
  → operational

is_broken = True, is_diagnosed = False
  → must diagnose first
  → room no power: 5 min timed action, informative message, no state set
  → room powered: full diagnosis with scan tool → is_diagnosed = True

is_broken = True, is_diagnosed = True
  → room no power: repair blocked
  → room powered: repair per-component

repaired_components == broken_components
  → panel restored, is_broken = False, is_diagnosed = False, lists cleared
```

### repair_tools_override
Individual components in `repair_profiles.json` can carry `repair_tools_override` — a list of tool IDs that replaces profile-level `repair_tools_required` for that component only.

- Only remaining component has override → use override tools exclusively
- Other components also remain → union of profile tools + override tools
- No override → profile-level tools apply

Currently used by `actuator_reset` on `vesper_ulock` panels.

### repair_profiles.json format
```json
{
  "vesper_ulock": {
    "diag_tools_required": ["scan_tool", "power_screwdriver_set"],
    "repair_tools_required": ["scan_tool", "power_screwdriver_set", "electrical_service_kit"],
    "components": [
      {"item_id": "relay_switch_array", "qty": 1, "diag_time_mins": 12, "repair_time_mins": 15},
      {"item_id": "cable_low_voltage", "length_m": 0.5, "diag_time_mins": 5, "repair_time_mins": 10},
      {"type": "actuator_reset", "diag_time_mins": 0, "repair_time_mins": 70,
       "repair_tools_override": ["scan_tool", "power_screwdriver_set", "wrench_set"]}
    ]
  }
}
```

### Component entry fields
| Field | Required | Description |
|-------|----------|-------------|
| `item_id` | Yes (except actuator_reset) | Part consumed on repair |
| `qty` | For non-cable parts | Quantity required |
| `length_m` | For cables | Length required |
| `diag_time_mins` | Yes | Diagnosis time contribution |
| `repair_time_mins` | Yes | Repair time |
| `type` | For special tasks | `"actuator_reset"` — time only, no parts |
| `repair_tools_override` | Optional | Overrides profile repair tools for this component |

### Diagnosis timing
`total_diag_mins = (sum of component diag_time_mins) × (1 + DIAG_ACCESS_OVERHEAD) × jitter`

Where `DIAG_ACCESS_OVERHEAD = 0.25` and jitter is ±`DIAG_TIME_JITTER = 0.10`.

### actuator_reset special handling
- Not selected by random component pool — only added by emergency release
- `diag_time_mins: 0` — contributes nothing to diagnosis timing
- When `is_diagnosed` is True and only fault is `actuator_reset` → diagnose returns instant message, no timed action
- Repair time: 70 game minutes
- On repair completion: `door.emergency_released` cleared before panel state wiped

---

## 3. ELECTRICAL JUNCTION REPAIR

### Overview
Full diagnose/repair via PowerJunction fixed object. Player must be in the junction's room. Diagnosis reads live electrical state — no random selection.

### Electrical junction state machine
```
broken_components empty
  → diagnose (reads live electrical state, populates broken_components)

broken_components populated, unrepaired remain
  → repair per-component
  → tripped breakers: reset only, no part consumed
  → damaged breakers/cables: consume parts, fix_component()
  → internal parts: consume parts, set CircuitPanel flag directly

repaired_components == broken_components
  → junction restored, lists cleared
```

### Tools required
- Diagnosis: `hv_service_kit` + `power_screwdriver_set`
- Repair: `hv_service_kit` + `power_screwdriver_set`

### Component types and parts
| Type | Parts required |
|------|---------------|
| `hv_logic_board` | 1x `hv_logic_board` |
| `hv_bus_bar` | 1x `hv_bus_bar` |
| `hv_surge_protector` | 1x `hv_surge_protector` |
| `hv_smoothing_capacitor` | 1x `hv_smoothing_capacitor` |
| `hv_isolation_switch` | 1x `hv_isolation_switch` |
| Breaker (damaged) | 1x matching amp-rated circuit breaker |
| Breaker (tripped) | No part — reset only |
| Cable (standard) | `cable_hv_standard` by total length + 2x `hv_connect_standard` per run |
| Cable (heavy duty) | `cable_hv_heavy_duty` by total length + 2x `hv_connect_heavy` per run |

### Circuit breaker sizes
| Item ID | Rating |
|---------|--------|
| `10a_breaker` | 10A |
| `32a_breaker` | 32A |
| `63a_breaker` | 63A |
| `250a_breaker` | 250A |
| `600a_breaker` | 600A |
| `1200a_breaker` | 1200A |

### Heavy duty cables
`PWC-ENG-01`, `PWC-ENG-00`, `PWC-PRO-01`, `PWC-PRO-02`, `PWC-PRO-03`, `PWC-PRO-04`

### Panel ownership — cable assignment rule
Each junction owns: its incoming cable(s), all outgoing cables to endpoints or to the next junction's incoming cable (exclusive). Emergency bypass cables excluded from normal diagnosis.

### Junction images
| Image | When shown |
|-------|-----------|
| `PNL-XXX-XXX.png` | During diagnosis timed action |
| `junction_burnt.png` | After diagnosis with faults; during repair |
| `junction_intact.png` | After diagnosis with no faults; after repair complete |

### Save/load
Junction `broken_components` and `repaired_components` persisted per room. Diagnosis state survives game restart.

---

## 4. REAL-TIME SCALING

All repair and diagnosis times scale from game minutes to real seconds using config constants:

```python
REPAIR_TIME_BASE_SECONDS  = 8
REPAIR_TIME_SCALE_SECONDS = 8
REPAIR_TIME_PIVOT_MINUTES = 30
REPAIR_TIME_CAP_SECONDS   = 20
```

Short repairs feel fast, long repairs are capped to avoid the player sitting idle.

---

## 5. KEY FILES

| File | Role |
|------|------|
| `repair_handler.py` | 5-step routing dispatcher |
| `door_panel_repair.py` | Door panel diagnosis and repair logic |
| `electrical_repair.py` | Electrical junction diagnosis and repair logic |
| `repair_utils.py` | Shared utilities, cached item registry |
| `data/repair/repair_profiles.json` | Door panel component profiles |
| `data/repair/electrical_repair_profiles.json` | Electrical junction component profiles |

---

## 6. API ENDPOINTS

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/command/diagnose_complete` | POST | Door panel diagnosis completion |
| `/api/command/repair_complete` | POST | Door panel component repair completion |
| `/api/command/repair_next` | POST | Door panel next component |
| `/api/command/no_power_diagnose_complete` | POST | Door panel no-power diagnosis completion |
| `/api/command/elec_diagnose_complete` | POST | Junction diagnosis completion |
| `/api/command/elec_repair_complete` | POST | Junction component repair completion |
| `/api/command/elec_repair_next` | POST | Junction next component |
| `/api/command/emergency_release_complete` | POST | Emergency release lever completion |

---

## 7. FUTURE

- **diagnosed_components list** — replace `is_diagnosed` boolean with a list to support misdiagnosis mechanic. `broken_components` remains ground truth. `diagnosed_components` is what Jack found — may differ if scan tool manual is missing. Repair proceeds from `diagnosed_components`. See `Project_Orion_Future_v6.md`.
- **Post-repair failure roll** — always succeeds currently. Future: probability-based.
- **Fixed object repair** — engines and reactors, same profile-driven pattern. `fixed_object_repair.py` handler, routed from `repair_handler.py`.

---

*Project Orion Game — Repair System Reference — May 2026*
