# backend/systems/electrical/electrical_service.py
"""
Electrical service — shared logic for breaking and fixing electrical components.

Called by:
  - backend/api/systems.py        — debug console API endpoints
  - backend/events/event_system.py — event-driven damage
  - backend/handlers/electrical_repair.py — repair completion (future)

Returns a result dict, not an HTTP response. Callers build their own responses.

Result dict on success:
  {
      'success':        True,
      'component_type': str,   # 'cable' | 'breaker' | 'panel' | 'power_source'
      'component_id':   str,   # normalised key as stored in electrical system
      'action':         str,   # e.g. 'severed', 'tripped+destroyed', 'repaired'
      'power_changed':  True,
      'room_power':     dict,  # room_id -> bool
      'batteries':      dict,
      'reactors':       dict,
  }

Result dict on failure:
  {
      'success': False,
      'error':   str,
  }
"""

from backend.models.game_manager import game_manager
from backend.systems.electrical.electrical_system import FissionReactor, BackupBattery


def _find_key(d: dict, component_id: str) -> str | None:
    """Case-insensitive key lookup."""
    cid_lower = component_id.lower()
    for k in d:
        if k.lower() == cid_lower:
            return k
    return None


def _room_power(sys) -> dict:
    """Return current room power map."""
    return {
        room_id: sys.check_room_power(room_id)
        for room_id in sys.room_power_sources.keys()
    }


def _build_result(sys, component_type: str, component_id: str, action: str) -> dict:
    """Update electrical states and build the standard result dict."""
    game_manager.update_electrical_states()
    return {
        'success':        True,
        'component_type': component_type,
        'component_id':   component_id,
        'action':         action,
        'power_changed':  True,
        'room_power':     _room_power(sys),
        'batteries':      sys.get_battery_states(),
        'reactors': {
            rid: {
                'name':        r.name,
                'operational': r.operational,
                'temperature': r.temperature,
                'output_kw':   r.output_kw,
                'ejected':     r.ejected,
            }
            for rid, r in sys.power_sources.items()
            if isinstance(r, FissionReactor)
        },
    }


def break_component(component_id: str) -> dict:
    """
    Break any electrical component by ID (case-insensitive).
    Handles: cables, breakers, panels, power sources (reactors/batteries).
    Returns a result dict — caller builds the HTTP response or handles directly.
    """
    sys = game_manager.electrical_system
    if not sys:
        return {'success': False, 'error': 'Electrical system not initialized'}

    # --- Cables ---
    key = _find_key(sys.cables, component_id)
    if key:
        sys.cables[key].intact = False
        return _build_result(sys, 'cable', key, 'severed')

    # --- Breakers ---
    key = _find_key(sys.breakers, component_id)
    if key:
        sys.breakers[key].tripped = True
        sys.breakers[key].operational = False
        return _build_result(sys, 'breaker', key, 'tripped+destroyed')

    # --- Panels ---
    key = _find_key(sys.panels, component_id)
    if key:
        sys.panels[key].operational = False
        return _build_result(sys, 'panel', key, 'destroyed')

    # --- Power sources ---
    key = _find_key(sys.power_sources, component_id)
    if key:
        source = sys.power_sources[key]
        if isinstance(source, FissionReactor):
            source.operational = False
            action = 'reactor_shutdown'
        elif isinstance(source, BackupBattery):
            source.active = False
            source.charge_percent = 0
            action = 'battery_destroyed'
        else:
            action = 'disabled'
        return _build_result(sys, 'power_source', key, action)

    return {
        'success': False,
        'error': f"Component '{component_id}' not found. Check the ID against electrical.json.",
    }


def fix_component(component_id: str) -> dict:
    """
    Fix any electrical component by ID (case-insensitive).
    Reverses the break state for cables, breakers, panels, power sources.
    Returns a result dict — caller builds the HTTP response or handles directly.
    """
    sys = game_manager.electrical_system
    if not sys:
        return {'success': False, 'error': 'Electrical system not initialized'}

    # --- Cables ---
    key = _find_key(sys.cables, component_id)
    if key:
        sys.cables[key].intact = True
        return _build_result(sys, 'cable', key, 'repaired')

    # --- Breakers ---
    key = _find_key(sys.breakers, component_id)
    if key:
        sys.breakers[key].tripped = False
        sys.breakers[key].operational = True
        return _build_result(sys, 'breaker', key, 'reset')

    # --- Panels ---
    key = _find_key(sys.panels, component_id)
    if key:
        sys.panels[key].operational = True
        return _build_result(sys, 'panel', key, 'restored')

    # --- Power sources ---
    key = _find_key(sys.power_sources, component_id)
    if key:
        source = sys.power_sources[key]
        if isinstance(source, FissionReactor):
            source.operational = True
            action = 'reactor_restarted'
        elif isinstance(source, BackupBattery):
            source.charge_percent = 100
            action = 'battery_restored'
        else:
            action = 'restored'
        return _build_result(sys, 'power_source', key, action)

    return {
        'success': False,
        'error': f"Component '{component_id}' not found. Check the ID against electrical.json.",
    }
