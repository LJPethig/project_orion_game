# backend/api/command.py
"""
Command API — single endpoint for all player commands.
POST /api/command        { "command": "enter engineering" }
POST /api/command/swipe  { "door_id": "..." }  — called after 8s card swipe wait
POST /api/command/pin    { "door_id": "...", "pin": "1234" }
"""

from flask import Blueprint, jsonify, request
from backend.handlers.command_handler import command_handler
from backend.models.game_manager import game_manager
from backend.models.door import SecurityLevel

command_bp = Blueprint('command', __name__)


def _build_room_data(room) -> dict:
    """Helper — build room dict for frontend including door states."""
    exits = {}
    for exit_key, exit_data in room.exits.items():
        door = exit_data.get('door')
        exits[exit_key] = {
            'label':      exit_data.get('label', exit_key),
            'door_state': door.get_state() if door else 'none',
        }
    return {
        'id':               room.id,
        'name':             room.name,
        'description':      room.description,
        'background_image': room.background_image,
        'exits':            exits,
        'portable_objects': [],
    }


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
    Called by frontend after the 8s card swipe wait completes.
    door_action: 'unlock' — unlock door, move player through
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

    # Level 1/2 — complete the action immediately
    return _complete_door_action(door, door_action, data.get('pending_move'))


def _complete_door_action(door, door_action: str, pending_move: str):
    """Complete an unlock or lock action after credentials are verified."""
    if door_action == 'lock':
        door.lock()
        return jsonify({
            'response':     'Credentials verified. The door is now locked.',
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': False,
            'swipe_complete': True,
            'ship_time':    game_manager.get_ship_time(),
        })

    # unlock — open door and move player through
    door.unlock()
    door.open()
    game_manager.set_current_room(pending_move)
    new_room = game_manager.get_current_room()
    return jsonify({
        'response':       f"Credentials verified. Access granted. You enter {new_room.name}.",
        'action_type':    'instant',
        'lock_input':     False,
        'room_changed':   True,
        'swipe_complete': True,
        'room':           _build_room_data(new_room),
        'ship_time':      game_manager.get_ship_time(),
    })


@command_bp.route('/pin', methods=['POST'])
def submit_pin():
    """
    Called when player submits a PIN for a level 3 door.
    3 failed attempts invalidates the card.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data         = request.get_json()
    door_id      = data.get('door_id')
    pin_input    = data.get('pin', '').strip()
    pending_move = data.get('pending_move')
    door_action  = data.get('door_action', 'unlock')

    door = game_manager.ship.get_door_by_id(door_id)
    if not door:
        return jsonify({'error': 'Door not found'}), 400

    # Correct PIN — complete the action
    if pin_input == door.pin:
        door.pin_attempts = 0
        return _complete_door_action(door, door_action, pending_move)

    # Wrong PIN
    door.pin_attempts += 1
    remaining = door.PIN_MAX_ATTEMPTS - door.pin_attempts

    if remaining <= 0:
        door.lock()
        door.pin_attempts = 0
        game_manager.invalidate_card(door.security_level)
        return jsonify({
            'response':     "Incorrect PIN. Card invalidated. Access denied.",
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': False,
            'ship_time':    game_manager.get_ship_time(),
        })

    return jsonify({
        'response':     f"Incorrect PIN. {remaining} attempt{'s' if remaining > 1 else ''} remaining.",
        'action_type':  'pin_required',
        'lock_input':   False,
        'room_changed': False,
        'door_id':      door_id,
        'door_action':  door_action,
        'pending_move': pending_move,
        'ship_time':    game_manager.get_ship_time(),
    })
