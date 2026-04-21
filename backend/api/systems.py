# backend/api/systems.py
"""
Systems API routes - ship systems status and control.
State-change logic lives in electrical_service.py — these routes
are thin HTTP wrappers that call the service and return JSON responses.
"""

from flask import Blueprint, jsonify
from backend.models.game_manager import game_manager
from backend.systems.electrical.electrical_service import break_component, fix_component, eject_reactor, install_reactor, trip_component

systems_bp = Blueprint('systems', __name__)


@systems_bp.route('/electrical/status', methods=['GET'])
def get_electrical_status():
    """Get complete electrical system status"""
    if not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    status = game_manager.electrical_system.get_system_status()
    engines = {}
    for engine in game_manager.get_all_engines():
        engines[engine.id] = {
            'name': engine.name,
            'powered': engine.powered,
            'online': engine.online,
        }
    status['engines'] = engines
    return jsonify(status)


@systems_bp.route('/electrical/room/<room_id>', methods=['GET'])
def get_room_power(room_id):
    """Check if a specific room has power"""
    if not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    has_power = game_manager.electrical_system.check_room_power(room_id)
    return jsonify({
        'room_id':  room_id,
        'has_power': has_power,
    })


@systems_bp.route('/electrical/break/<component_id>', methods=['POST'])
def break_component_route(component_id):
    """
    Break any electrical component by ID (case-insensitive).
    Delegates to electrical_service.break_component().
    """
    if not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    result = break_component(component_id)
    if not result['success']:
        return jsonify(result), 404
    return jsonify(result)


@systems_bp.route('/electrical/fix/<component_id>', methods=['POST'])
def fix_component_route(component_id):
    """
    Fix any electrical component by ID (case-insensitive).
    Delegates to electrical_service.fix_component().
    """
    if not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    result = fix_component(component_id)
    if not result['success']:
        return jsonify(result), 404
    return jsonify(result)

@systems_bp.route('/electrical/check/<component_id>', methods=['GET'])
def check_component_route(component_id):
    """
    Return the current state of any electrical component by ID — debug console only.
    """
    if not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    sys = game_manager.electrical_system

    from backend.systems.electrical.electrical_service import _find_key

    key = _find_key(sys.breakers, component_id)
    if key:
        b = sys.breakers[key]
        return jsonify({
            'success': True,
            'component_type': 'breaker',
            'component_id': key,
            'damaged': b.damaged,
            'tripped': b.tripped,
            'operational': b.operational,
        })

    key = _find_key(sys.cables, component_id)
    if key:
        c = sys.cables[key]
        return jsonify({
            'success': True,
            'component_type': 'cable',
            'component_id': key,
            'connected': c.connected,
            'intact': c.intact,
        })

    key = _find_key(sys.panels, component_id)
    if key:
        p = sys.panels[key]
        return jsonify({
            'success': True,
            'component_type': 'panel',
            'component_id': key,
            'operational': p.operational,
        })

    return jsonify({'success': False, 'error': f"Component '{component_id}' not found."}), 404

@systems_bp.route('/electrical/trip/<component_id>', methods=['POST'])
def trip_component_route(component_id):
    """
    Trip a circuit breaker by ID — debug console only.
    Delegates to electrical_service.trip_component().
    """
    if not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    result = trip_component(component_id)
    if not result['success']:
        return jsonify(result), 404
    return jsonify(result)

@systems_bp.route('/electrical/reactor/eject/<reactor_id>', methods=['POST'])
def eject_reactor_route(reactor_id):
    """
    Eject a reactor core by ID — debug console only.
    Delegates to electrical_service.eject_reactor().
    """
    if not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    result = eject_reactor(reactor_id)
    if not result['success']:
        return jsonify(result), 404
    return jsonify(result)


@systems_bp.route('/electrical/reactor/install/<reactor_id>', methods=['POST'])
def install_reactor_route(reactor_id):
    """
    Install a reactor core by ID — debug console only.
    Delegates to electrical_service.install_reactor().
    """
    if not game_manager.electrical_system:
        return jsonify({'error': 'Electrical system not initialized'}), 500

    result = install_reactor(reactor_id)
    if not result['success']:
        return jsonify(result), 404
    return jsonify(result)
