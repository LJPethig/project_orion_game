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
      'action':         str,   # e.g. 'severed', 'damaged', 'tripped', 'repaired', 'hv_logic_board_damaged'
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
    To trip a breaker instead, use trip_component().
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
        sys.breakers[key].damaged = True
        return _build_result(sys, 'breaker', key, 'damaged')

    # --- Panels ---
    # Panels are not broken directly — use break_panel_component() instead.
    if _find_key(sys.panels, component_id):
        return {
            'success': False,
            'error': f"Panels cannot be broken directly. Use break_panel_component() to break a specific internal component.",
        }

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


def break_panel_component(panel_id: str, component: str) -> dict:
    """
    Break a specific internal component of a circuit panel by panel ID and component name.
    Valid component names: 'hv_logic_board', 'hv_bus_bar', 'hv_surge_protector',
                           'hv_smoothing_capacitor', 'hv_isolation_switch'
    Returns a result dict — caller builds the HTTP response or handles directly.
    """
    sys = game_manager.electrical_system
    if not sys:
        return {'success': False, 'error': 'Electrical system not initialized'}

    key = _find_key(sys.panels, panel_id)
    if not key:
        return {'success': False, 'error': f"Panel '{panel_id}' not found."}

    panel = sys.panels[key]

    component_map = {
        'hv_logic_board':         'logic_board_intact',
        'hv_bus_bar':             'bus_bar_intact',
        'hv_surge_protector':     'surge_protector_intact',
        'hv_smoothing_capacitor': 'smoothing_capacitor_intact',
        'hv_isolation_switch':    'isolation_switch_intact',
    }

    flag = component_map.get(component)
    if not flag:
        return {
            'success': False,
            'error': f"Unknown panel component '{component}'. "
                     f"Valid: {', '.join(component_map.keys())}",
        }

    setattr(panel, flag, False)
    return _build_result(sys, 'panel', key, f"{component}_damaged")


def trip_component(component_id: str) -> dict:
    """
    Trip a circuit breaker by ID (case-insensitive).
    A tripped breaker requires resetting only — no replacement part needed.
    Only valid for breakers — returns an error for any other component type.
    """
    sys = game_manager.electrical_system
    if not sys:
        return {'success': False, 'error': 'Electrical system not initialized'}

    key = _find_key(sys.breakers, component_id)
    if key:
        sys.breakers[key].tripped = True
        return _build_result(sys, 'breaker', key, 'tripped')

    return {
        'success': False,
        'error': f"Breaker '{component_id}' not found. Only breakers can be tripped.",
    }

def connect_cable(cable_id: str) -> dict:
    """
    Connect a cable by ID (case-insensitive).
    Sets connected: True and intact: True — cable is physically installed and undamaged.
    Only valid for cables with emergency_bypass: True.
    """
    sys = game_manager.electrical_system
    if not sys:
        return {'success': False, 'error': 'Electrical system not initialized'}

    key = _find_key(sys.cables, cable_id)
    if key:
        cable = sys.cables[key]
        if not cable.emergency_bypass:
            return {'success': False, 'error': f"Cable '{cable_id}' is not a bypass cable."}
        cable.connected = True
        cable.intact    = True
        return _build_result(sys, 'cable', key, 'connected')

    return {'success': False, 'error': f"Cable '{cable_id}' not found."}


def disconnect_cable(cable_id: str) -> dict:
    """
    Disconnect a cable by ID (case-insensitive).
    Sets connected: False — cable is physically removed from the circuit.
    Only valid for cables with emergency_bypass: True.
    """
    sys = game_manager.electrical_system
    if not sys:
        return {'success': False, 'error': 'Electrical system not initialized'}

    key = _find_key(sys.cables, cable_id)
    if key:
        cable = sys.cables[key]
        if not cable.emergency_bypass:
            return {'success': False, 'error': f"Cable '{cable_id}' is not a bypass cable."}
        cable.connected = False
        return _build_result(sys, 'cable', key, 'disconnected')

    return {'success': False, 'error': f"Cable '{cable_id}' not found."}

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
        cable = sys.cables[key]
        if not cable.connected:
            return {
                'success': False,
                'error': f"Cable '{key}' is not connected. Use connect_cable() to install it first.",
            }
        cable.intact = True
        return _build_result(sys, 'cable', key, 'repaired')

    # --- Breakers ---
    key = _find_key(sys.breakers, component_id)
    if key:
        sys.breakers[key].damaged = False
        sys.breakers[key].tripped = False
        return _build_result(sys, 'breaker', key, 'reset')

    # --- Panels ---
    key = _find_key(sys.panels, component_id)
    if key:
        panel = sys.panels[key]
        panel.logic_board_intact = True
        panel.bus_bar_intact = True
        panel.surge_protector_intact = True
        panel.smoothing_capacitor_intact = True
        panel.isolation_switch_intact = True
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

def eject_reactor(reactor_id: str) -> dict:
    """
    Eject a reactor core by ID (case-insensitive).
    Sets ejected = True and operational = False on the reactor.
    Debug console only — in-game ejection will be a separate command.
    """
    sys = game_manager.electrical_system
    if not sys:
        return {'success': False, 'error': 'Electrical system not initialized'}

    key = _find_key(sys.power_sources, reactor_id)
    if not key:
        return {'success': False, 'error': f"Reactor '{reactor_id}' not found."}

    source = sys.power_sources[key]
    if not isinstance(source, FissionReactor):
        return {'success': False, 'error': f"'{reactor_id}' is not a reactor."}

    source.ejected     = True
    source.operational = False
    return _build_result(sys, 'reactor', key, 'ejected')


def install_reactor(reactor_id: str) -> dict:
    """
    Reinstall a reactor core by ID (case-insensitive).
    Reverses ejection — debug console only, not physically realistic.
    """
    sys = game_manager.electrical_system
    if not sys:
        return {'success': False, 'error': 'Electrical system not initialized'}

    key = _find_key(sys.power_sources, reactor_id)
    if not key:
        return {'success': False, 'error': f"Reactor '{reactor_id}' not found."}

    source = sys.power_sources[key]
    if not isinstance(source, FissionReactor):
        return {'success': False, 'error': f"'{reactor_id}' is not a reactor."}

    source.ejected     = False
    source.operational = True
    return _build_result(sys, 'reactor', key, 'installed')

