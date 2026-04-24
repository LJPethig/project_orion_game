# backend/api/command.py
"""
Command API — single endpoint for all player commands.
POST /api/command        { "command": "enter engineering" }
POST /api/command/swipe  { "door_id": "..." }  — called after card swipe wait
POST /api/command/pin    { "door_id": "...", "pin": "1234" }
"""

from flask import Blueprint, jsonify, request
from backend.handlers.command_handler import command_handler
from backend.handlers.repair_handler import repair_handler
from backend.models.game_manager import game_manager
from backend.models.door import SecurityLevel
from backend.api.game import _build_room_data

command_bp = Blueprint('command', __name__)


@command_bp.route('', methods=['POST'])
def process_command():
    """Process a player command and return the result."""
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({'error': 'No command provided'}), 400

    result = command_handler.process(data['command'])

    if result.get('room_changed'):
        result['room'] = _build_room_data(game_manager.get_current_room())

    result['ship_time'] = game_manager.get_ship_time()
    return jsonify(result)


@command_bp.route('/swipe', methods=['POST'])
def complete_swipe():
    """
    Called by frontend after the card swipe wait completes.
    door_action: 'open'   — unlock and open door, player stays
    door_action: 'unlock' — unlock door only, player stays
    door_action: 'lock'   — lock door, player stays
    Level 3 doors prompt for PIN before completing the action.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data        = request.get_json()
    door_id     = data.get('door_id')
    door_action = data.get('door_action', 'unlock')
    door        = game_manager.ship.get_door_by_id(door_id)

    if not door:
        return jsonify({'error': 'Door not found'}), 400

    # Level 3 — prompt for PIN before acting
    if door.security_level == SecurityLevel.KEYCARD_HIGH_PIN.value:
        return jsonify({
            'response':     'Credentials verified. Enter PIN:',
            'action_type':  'pin_required',
            'lock_input':   False,
            'room_changed': False,
            'door_id':      door_id,
            'door_action':  door_action,
            'pending_move': data.get('pending_move'),
            'ship_time':    game_manager.get_ship_time(),
        })

    return _complete_door_action(door, door_action)


def _complete_door_action(door, door_action: str):
    """Complete an open, unlock, or lock action after credentials are verified."""
    current_room  = game_manager.get_current_room()
    other_room_id = door.get_other_room_id(current_room.id)
    other_room    = game_manager.ship.get_room(other_room_id)
    target_name   = other_room.name if other_room else "the door"

    if door_action == 'lock':
        door.lock()
        return jsonify({
            'response':       f"Credentials verified. The {target_name} door is now locked.",
            'action_type':    'instant',
            'lock_input':     False,
            'room_changed':   False,
            'swipe_complete': True,
            'swipe_action':   'lock',
            'ship_time':      game_manager.get_ship_time(),
        })

    if door_action == 'unlock':
        door.unlock()
        return jsonify({
            'response': f"Credentials verified. The {target_name} door is now unlocked.",
            'action_type': 'instant',
            'lock_input': False,
            'room_changed': False,
            'swipe_complete': True,
            'swipe_action': 'unlock',
            'ship_time': game_manager.get_ship_time(),
        })

    # 'open' — unlock and open
    door.unlock()
    door.open()
    return jsonify({
        'response': f"Credentials verified. The {target_name} door is now open.",
        'action_type': 'instant',
        'lock_input': False,
        'room_changed': False,
        'swipe_complete': True,
        'swipe_action': 'open',
        'ship_time': game_manager.get_ship_time(),
    })


@command_bp.route('/diagnose_complete', methods=['POST'])
def diagnose_complete():
    """
    Called by frontend after the diagnosis timed action completes.
    Populates panel.broken_components and returns diagnosis report.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data = request.get_json()
    panel_id = data.get('panel_id')
    door_id = data.get('door_id')
    game_minutes = data.get('game_minutes', 0)
    exit_label = data.get('exit_label', 'unknown')

    result = repair_handler.complete_diagnosis(panel_id, door_id, game_minutes, exit_label)
    result['ship_time'] = game_manager.get_ship_time()
    return jsonify(result)


@command_bp.route('/no_power_diagnose_complete', methods=['POST'])
def no_power_diagnose_complete():
    """
    Called by frontend after the no-power door panel diagnosis timed action completes.
    Advances ship time and returns a message — no diagnosis state is set.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data        = request.get_json()
    panel_model = data.get('panel_model')
    game_minutes = data.get('game_minutes', 5)

    result = repair_handler.complete_no_power_diagnosis(panel_model, game_minutes)
    result['ship_time'] = game_manager.get_ship_time()
    return jsonify(result)

@command_bp.route('/repair_complete', methods=['POST'])
def repair_complete():
    """
    Called by frontend after a single component repair timed action completes.
    Consumes parts, marks component repaired, returns next action or completion.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data         = request.get_json()
    panel_id     = data.get('panel_id')
    door_id      = data.get('door_id')
    component_id = data.get('component_id')
    exit_label   = data.get('exit_label', 'the door')

    result = repair_handler.complete_component_repair(panel_id, door_id, component_id, exit_label)
    result['ship_time'] = game_manager.get_ship_time()
    return jsonify(result)

@command_bp.route('/elec_diagnose_complete', methods=['POST'])
def elec_diagnose_complete():
    """
    Called by frontend after the electrical diagnosis timed action completes.
    Advances ship time, writes log, returns diagnosis report.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data         = request.get_json()
    panel_id     = data.get('panel_id')
    game_minutes = data.get('game_minutes', 0)

    from backend.handlers.electrical_repair import electrical_repair_handler
    result = electrical_repair_handler.complete_diagnosis(panel_id, game_minutes)
    result['ship_time'] = game_manager.get_ship_time()
    return jsonify(result)

@command_bp.route('/repair_next', methods=['POST'])
def repair_next():
    """
    Called by frontend to automatically proceed to the next component repair.
    Event checking is handled by the frontend poll — not here.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data = request.get_json()
    panel_id = data.get('panel_id')
    door_id = data.get('door_id')
    exit_label = data.get('exit_label', 'the door')

    door = game_manager.ship.get_door_by_id(door_id)
    if not door:
        return jsonify({'error': 'Door not found'}), 400

    panel = next((p for p in door.panels.values() if p.panel_id == panel_id), None)
    if not panel:
        return jsonify({'error': 'Panel not found'}), 400

    result = repair_handler.begin_next_repair(panel, door, exit_label)
    result['ship_time'] = game_manager.get_ship_time()
    return jsonify(result)


@command_bp.route('/elec_repair_complete', methods=['POST'])
def elec_repair_complete():
    """
    Called by frontend after an electrical component repair timed action completes.
    Consumes parts, marks component repaired, returns next action or completion.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data          = request.get_json()
    panel_id      = data.get('panel_id')
    component_key = data.get('component_key')

    from backend.handlers.electrical_repair import electrical_repair_handler
    result = electrical_repair_handler.complete_component_repair(panel_id, component_key)
    result['ship_time'] = game_manager.get_ship_time()
    return jsonify(result)


@command_bp.route('/elec_repair_next', methods=['POST'])
def elec_repair_next():
    """
    Called by frontend to proceed to the next electrical component repair.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data     = request.get_json()
    panel_id = data.get('panel_id')

    from backend.models.interactable import PowerJunction
    from backend.handlers.electrical_repair import electrical_repair_handler
    room     = game_manager.get_current_room()
    junction = next(
        (o for o in room.objects if isinstance(o, PowerJunction) and o.panel_id == panel_id),
        None
    )
    if not junction:
        return jsonify({'error': f"Junction '{panel_id}' not found"}), 400

    profile = electrical_repair_handler.get_profile(panel_id)
    if not profile:
        return jsonify({'error': f"No repair profile for '{panel_id}'"}), 400

    result = electrical_repair_handler.begin_next_repair(junction, profile)
    result['ship_time'] = game_manager.get_ship_time()
    return jsonify(result)


@command_bp.route('/pin', methods=['POST'])
def submit_pin():
    """
    Called when player submits a PIN for a level 3 door.
    3 failed attempts invalidates the card.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data        = request.get_json()
    door_id     = data.get('door_id')
    pin_input   = data.get('pin', '').strip()
    door_action = data.get('door_action', 'unlock')

    door = game_manager.ship.get_door_by_id(door_id)
    if not door:
        return jsonify({'error': 'Door not found'}), 400

    if pin_input == door.pin:
        door.pin_attempts = 0
        return _complete_door_action(door, door_action)

    door.pin_attempts += 1
    remaining = door.PIN_MAX_ATTEMPTS - door.pin_attempts

    if remaining <= 0:
        door.lock()
        door.pin_attempts = 0
        game_manager.invalidate_card(door.security_level)
        return jsonify({
            'response':         "Incorrect PIN. Card invalidated. Access denied.",
            'action_type':      'instant',
            'lock_input':       False,
            'room_changed':     False,
            'card_invalidated': True,
            'ship_time':        game_manager.get_ship_time(),
        })

    return jsonify({
        'response':     f"Incorrect PIN. {remaining} attempt{'s' if remaining > 1 else ''} remaining.",
        'action_type':  'pin_required',
        'lock_input':   False,
        'room_changed': False,
        'door_id':      door_id,
        'door_action':  door_action,
        'pending_move': None,
        'ship_time':    game_manager.get_ship_time(),
    })
