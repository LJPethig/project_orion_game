# backend/api/systems.py
"""
Systems API routes - ship systems status and control.
State-change logic lives in electrical_service.py — these routes
are thin HTTP wrappers that call the service and return JSON responses.
"""

from flask import Blueprint, jsonify
from backend.models.game_manager import game_manager
from backend.systems.electrical.electrical_service import break_component, fix_component

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
