# backend/api/systems.py
"""
Systems API routes - ship systems status and control
"""

from flask import Blueprint, jsonify, request

systems_bp = Blueprint('systems', __name__)

# Import game_manager at module level (will be set by main.py)
game_manager = None


def init_systems(gm):
    """Initialize systems with game_manager reference"""
    global game_manager
    game_manager = gm


@systems_bp.route('/electrical/status', methods=['GET'])
def get_electrical_status():
    """Get complete electrical system status"""
    if not game_manager or not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500
    
    status = game_manager.electrical_system.get_system_status()
    return jsonify(status)


@systems_bp.route('/electrical/room/<room_id>', methods=['GET'])
def get_room_power(room_id):
    """Check if a specific room has power"""
    if not game_manager or not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500
    
    has_power = game_manager.electrical_system.check_room_power(room_id)
    
    return jsonify({
        'room_id': room_id,
        'has_power': has_power
    })


@systems_bp.route('/electrical/break/<component_id>', methods=['POST'])
def break_component(component_id):
    """
    Break any electrical component by ID (case-insensitive).
    Handles: cables, breakers, panels, power sources (reactors/batteries).
    Returns updated room_power map so frontend can refresh SVG immediately.
    """
    if not game_manager or not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    sys = game_manager.electrical_system

    # Normalise to lowercase for lookup, then find the real key
    cid_lower = component_id.lower()

    def find_key(d):
        for k in d:
            if k.lower() == cid_lower:
                return k
        return None

    # --- Cables ---
    key = find_key(sys.cables)
    if key:
        sys.cables[key].intact = False
        return _break_response(sys, 'cable', key, 'severed')

    # --- Breakers ---
    key = find_key(sys.breakers)
    if key:
        breaker = sys.breakers[key]
        breaker.tripped = True
        breaker.operational = False
        return _break_response(sys, 'breaker', key, 'tripped+destroyed')

    # --- Panels (junction boxes) ---
    key = find_key(sys.panels)
    if key:
        sys.panels[key].operational = False
        return _break_response(sys, 'panel', key, 'destroyed')

    # --- Power sources (reactors + batteries) ---
    key = find_key(sys.power_sources)
    if key:
        source = sys.power_sources[key]
        from backend.systems.electrical.electrical_system import FissionReactor, BackupBattery
        if isinstance(source, FissionReactor):
            source.operational = False
            action = 'reactor_shutdown'
        elif isinstance(source, BackupBattery):
            source.active = False
            source.charge_percent = 0
            action = 'battery_destroyed'
        else:
            action = 'disabled'
        return _break_response(sys, 'power_source', key, action)

    # Nothing matched
    return jsonify({
        'success': False,
        'error': f"Component '{component_id}' not found. Check the ID against electrical.json."
    }), 404


def _room_power(sys):
    """Return current room power map (helper)"""
    return {
        room_id: sys.check_room_power(room_id)
        for room_id in sys.room_power_sources.keys()
    }


def _break_response(sys, component_type, component_id, action):
    """Update battery states then build the standard break response"""
    sys.update_battery_states()
    return jsonify({
        'success': True,
        'component_type': component_type,
        'component_id': component_id,
        'action': action,
        'room_power': _room_power(sys),
        'batteries': sys.get_battery_states(),
        'reactors': {
            rid: {
                'name': r.name,
                'operational': r.operational,
                'temperature': r.temperature,
                'output_kw': r.output_kw,
            }
            for rid, r in sys.power_sources.items()
            if hasattr(r, 'operational') and not hasattr(r, 'charge_percent')
        },
    })

@systems_bp.route('/electrical/fix/<component_id>', methods=['POST'])
def fix_component(component_id):
    """
    Fix any electrical component by ID (case-insensitive).
    Reverses the break state for cables, breakers, panels, power sources.
    Returns updated room_power map so frontend can refresh SVG immediately.
    """
    if not game_manager or not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    sys = game_manager.electrical_system

    cid_lower = component_id.lower()

    def find_key(d):
        for k in d:
            if k.lower() == cid_lower:
                return k
        return None

    # --- Cables ---
    key = find_key(sys.cables)
    if key:
        sys.cables[key].intact = True
        return _fix_response(sys, 'cable', key, 'repaired')

    # --- Breakers ---
    key = find_key(sys.breakers)
    if key:
        breaker = sys.breakers[key]
        breaker.tripped = False
        breaker.operational = True
        return _fix_response(sys, 'breaker', key, 'reset')

    # --- Panels ---
    key = find_key(sys.panels)
    if key:
        sys.panels[key].operational = True
        return _fix_response(sys, 'panel', key, 'restored')

    # --- Power sources ---
    key = find_key(sys.power_sources)
    if key:
        source = sys.power_sources[key]
        from backend.systems.electrical.electrical_system import FissionReactor, BackupBattery
        if isinstance(source, FissionReactor):
            source.operational = True
            action = 'reactor_restarted'
        elif isinstance(source, BackupBattery):
            source.charge_percent = 100
            action = 'battery_restored'
        else:
            action = 'restored'
        return _fix_response(sys, 'power_source', key, action)

    return jsonify({
        'success': False,
        'error': f"Component '{component_id}' not found. Check the ID against electrical.json."
    }), 404


def _fix_response(sys, component_type, component_id, action):
    """Update battery states then build the standard fix response"""
    sys.update_battery_states()
    return jsonify({
        'success': True,
        'component_type': component_type,
        'component_id': component_id,
        'action': action,
        'room_power': _room_power(sys),
        'batteries': sys.get_battery_states(),
        'reactors': {
            rid: {
                'name': r.name,
                'operational': r.operational,
                'temperature': r.temperature,
                'output_kw': r.output_kw,
            }
            for rid, r in sys.power_sources.items()
            if hasattr(r, 'operational') and not hasattr(r, 'charge_percent')
        },
    })
