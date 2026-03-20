# backend/api/command.py
"""
Command API — single endpoint for all player commands.
POST /api/command  { "command": "enter engineering" }
Returns a standard response the frontend uses to update the UI.
"""

from flask import Blueprint, jsonify, request
from backend.handlers.command_handler import command_handler
from backend.models.game_manager import game_manager

command_bp = Blueprint('command', __name__)


@command_bp.route('', methods=['POST'])
def process_command():
    """Process a player command and return the result."""
    if not game_manager.initialised:
        return jsonify({'error': 'Game not initialised'}), 400

    data = request.get_json()
    if not data or 'command' not in data:
        return jsonify({'error': 'No command provided'}), 400

    raw = data['command']
    result = command_handler.process(raw)

    # If room changed, include updated room data in the response
    if result.get('room_changed'):
        room = game_manager.get_current_room()
        result['room'] = {
            'id':               room.id,
            'name':             room.name,
            'description':      room.description,
            'background_image': room.background_image,
            'exits':            list(room.exits.keys()),
            'portable_objects': [],
        }

    # Always include current ship time
    result['ship_time'] = game_manager.get_ship_time()

    return jsonify(result)
