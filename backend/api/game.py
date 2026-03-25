# backend/api/game.py
"""
Game API routes.
/api/game/state  — current game state (ship time, etc.)
/api/game/new    — start a new game
"""

from flask import Blueprint, jsonify
from backend.models.game_manager import game_manager
from backend.models.interactable import PortableItem, StorageUnit, Surface
from config import SHIP_NAME

game_bp = Blueprint("game", __name__)


@game_bp.route("/state", methods=["GET"])
def get_state():
    """Return current game state for frontend polling."""
    return jsonify({
        "initialised": game_manager.initialised,
        "ship_name":   game_manager.ship_name,
        "ship_time":   game_manager.get_ship_time(),
    })


@game_bp.route("/new", methods=["POST"])
def new_game():
    """Start a new game — initialises all state."""
    game_manager.new_game()
    return jsonify({
        "success":   True,
        "ship_name": SHIP_NAME,
        "ship_time": game_manager.get_ship_time(),
    })


@game_bp.route("/tick", methods=["POST"])
def tick():
    """Advance ship time by 1 minute. Called by frontend every 60 real seconds."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400
    game_manager.advance_time(1)
    return jsonify({"ship_time": game_manager.get_ship_time()})


@game_bp.route("/room", methods=["GET"])
def get_room():
    """Return current room data for the frontend."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

    room = game_manager.get_current_room()
    if not room:
        return jsonify({"error": "No current room"}), 400

    return jsonify(_build_room_data(room))


def _build_room_data(room) -> dict:
    """Build room dict for frontend — exits, portable items, object states."""
    exits = {}
    for exit_key, exit_data in room.exits.items():
        door = exit_data.get('door')
        exits[exit_key] = {
            'label':      exit_data.get('label', exit_key),
            'door_state': door.get_state() if door else 'none',
        }

    # Portable items on the room floor (safety net — surfaces are primary)
    portable_objects = [
        {'id': obj.id, 'name': obj.name}
        for obj in room.objects
        if isinstance(obj, PortableItem)
        and not isinstance(obj, StorageUnit)
        and not isinstance(obj, Surface)
        and obj.takeable
    ]

    # Object states — containers (open/closed + contents) and surfaces (has_items + contents)
    object_states = {}
    for obj in room.objects:
        if isinstance(obj, StorageUnit):
            object_states[obj.id] = {
                'type':      'container',
                'is_open':   obj.is_open,
                'has_items': len(obj.contents) > 0,
                'contents':  [{'id': i.id, 'name': i.name} for i in obj.contents] if obj.is_open else [],
            }
        elif isinstance(obj, Surface):
            object_states[obj.id] = {
                'type':      'surface',
                'has_items': obj.has_items,
                'contents':  [{'id': i.id, 'name': i.name} for i in obj.contents],
            }

    return {
        'id':               room.id,
        'name':             room.name,
        'description':      room.description,
        'background_image': room.background_image,
        'exits':            exits,
        'portable_objects': portable_objects,
        'object_states':    object_states,
    }
