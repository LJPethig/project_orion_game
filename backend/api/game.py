# backend/api/game.py
"""
Game API routes.
/api/game/state  — current game state (ship time, etc.)
/api/game/new    — start a new game
"""

from flask import Blueprint, jsonify
from backend.models.game_manager import game_manager
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


@game_bp.route("/room", methods=["GET"])
def get_room():
    """Return current room data for the frontend."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

    room = game_manager.get_current_room()
    if not room:
        return jsonify({"error": "No current room"}), 400

    # Build exit dict with door state for tooltip display
    exits = {}
    for exit_key, exit_data in room.exits.items():
        door = exit_data.get('door')
        exits[exit_key] = {
            'label':      exit_data.get('label', exit_key),
            'door_state': door.get_state() if door else 'none',
        }

    return jsonify({
        "id":               room.id,
        "name":             room.name,
        "description":      room.description,
        "background_image": room.background_image,
        "exits":            exits,
        "portable_objects": [],
    })
