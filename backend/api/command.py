# backend/api/command.py
"""
Command API — single endpoint for all player commands.
POST /api/command        { "command": "enter engineering" }
POST /api/command/swipe  { "door_id": "..." }  — called after card swipe wait
POST /api/command/pin    { "door_id": "...", "pin": "1234" }
"""

from flask import Blueprint, jsonify, request
from backend.handlers.command_handler import command_handler
from backend.models.game_manager import game_manager
from backend.models.door import SecurityLevel
from backend.models.interactable import PortableItem, StorageUnit
from config import REPAIR_PANEL_GAME_MINUTES

command_bp = Blueprint('command', __name__)


def _build_room_data(room) -> dict:
    """Helper — build room dict for frontend including door states and portable items."""
    exits = {}
    for exit_key, exit_data in room.exits.items():
        door = exit_data.get('door')
        exits[exit_key] = {
            'label':      exit_data.get('label', exit_key),
            'door_state': door.get_state() if door else 'none',
        }

    # Portable items on the room floor (not inside containers)
    portable_objects = [
        {'id': obj.id, 'name': obj.name}
        for obj in room.objects
        if isinstance(obj, PortableItem)
        and not isinstance(obj, StorageUnit)
        and obj.takeable
    ]

    return {
        'id':               room.id,
        'name':             room.name,
        'description':      room.description,
        'background_image': room.background_image,
        'exits':            exits,
        'portable_objects': portable_objects,
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
    Called by frontend after the card swipe wait completes.
    door_action: 'open'   — unlock and open door, player stays
    door_action: 'unlock' — unlock and open door, player stays
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
            'response':      f"Credentials verified. The {target_name} door is now locked.",
            'action_type':   'instant',
            'lock_input':    False,
            'room_changed':  False,
            'swipe_complete': True,
            'swipe_action':  'lock',
            'ship_time':     game_manager.get_ship_time(),
        })

    # open or unlock — unlock and open door, player stays
    door.unlock()
    door.open()
    return jsonify({
        'response':      f"Credentials verified. The {target_name} door is now open.",
        'action_type':   'instant',
        'lock_input':    False,
        'room_changed':  False,
        'swipe_complete': True,
        'swipe_action':  'open',
        'ship_time':     game_manager.get_ship_time(),
    })


@command_bp.route('/repair_complete', methods=['POST'])
def complete_repair():
    """
    Called by frontend after the repair wait completes.
    Marks the panel as repaired, advances ship time.
    """
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data     = request.get_json()
    panel_id = data.get('panel_id')
    door_id  = data.get('door_id')

    door = game_manager.ship.get_door_by_id(door_id)
    if not door:
        return jsonify({'error': 'Door not found'}), 400

    # Find the panel by ID across both sides
    panel = next(
        (p for p in door.panels.values() if p.panel_id == panel_id),
        None
    )
    if not panel:
        return jsonify({'error': 'Panel not found'}), 400

    panel.is_broken      = False
    panel.repair_progress = 1.0
    game_manager.advance_time(REPAIR_PANEL_GAME_MINUTES)

    exit_label = data.get('exit_label', 'the door')
    return jsonify({
        'response':        f"You repair the door access panel to {exit_label}. It is now operational.",
        'action_type':     'repair_complete',
        'lock_input':      False,
        'room_changed':    False,
        'security_level': door.security_level,
        'door_id':         door_id,
        'ship_time':       game_manager.get_ship_time(),
    })


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

    # Correct PIN — complete the action
    if pin_input == door.pin:
        door.pin_attempts = 0
        return _complete_door_action(door, door_action)

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
            'card_invalidated': True,
            'ship_time':    game_manager.get_ship_time(),
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
