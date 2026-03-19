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
