# backend/api/game.py
"""
Game API routes.
/api/game/state  — current game state (ship time, etc.)
/api/game/new    — start a new game
"""

from flask import Blueprint, jsonify, request
from backend.models.game_manager import game_manager
from backend.models.interactable import PortableItem, StorageUnit, Surface, Terminal
from config import SHIP_NAME

import os

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



@game_bp.route("/inventory", methods=["GET"])
def get_inventory():
    """Return player inventory and equipped slots for the inventory panel."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

    player = game_manager.player

    # Equipped slots — all five, occupied or empty
    equipped = {}
    for slot in player.EQUIP_SLOTS:
        item = getattr(player, f"{slot}_slot")
        equipped[slot] = {
            'id':          item.id                            if item else None,
            'name':        item.name                          if item else None,
            'description': item.description                   if item else None,
            'mass':        item.mass                          if item else None,
            'image':       f"images/items/{item.id}.png"      if item else None,
            'equip_slot':  getattr(item, 'equip_slot', None)  if item else None,
        }

    # Loose carried items
    carried = [
        {
            'id':          item.id,
            'name':        item.name,
            'description': item.description,
            'mass':        item.mass,
            'image':       f"images/items/{item.id}.png",
            'equip_slot':  getattr(item, 'equip_slot', None),
        }
        for item in player.get_inventory()
    ]

    return jsonify({
        'player_name':   player.name,
        'carry_current': round(player.current_carry_mass, 2),
        'carry_max':     player.max_carry_mass,
        'equipped':      equipped,
        'carried':       carried,
    })

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

    # Object states — containers (open/closed + contents), surfaces (has_items + contents), terminals
    object_states = {}
    for obj in room.objects:
        if isinstance(obj, StorageUnit):
            object_states[obj.id] = {
                'type': 'container',
                'name': obj.name,
                'is_open': obj.is_open,
                'has_items': len(obj.contents) > 0,
                'contents': [{'id': i.id, 'name': i.name} for i in obj.contents] if obj.is_open else [],
            }
        elif isinstance(obj, Surface):
            object_states[obj.id] = {
                'type': 'surface',
                'name': obj.name,
                'has_items': obj.has_items,
                'contents': [{'id': i.id, 'name': i.name} for i in obj.contents],
            }
        elif isinstance(obj, Terminal):
            object_states[obj.id] = {
                'type': 'terminal',
                'name': obj.name,
            }

    # Floor items — only populated when items are present
    floor_items = [{'id': i.id, 'name': i.name} for i in room.floor]

    return {
        'id':               room.id,
        'name':             room.name,
        'description':      room.description,
        'background_image': room.background_image,
        'exits':            exits,
        'portable_objects': portable_objects,
        'object_states':    object_states,
        'floor_items':      floor_items,
    }

@game_bp.route("/terminal/content", methods=["POST"])
def get_terminal_content():
    """Return content for a terminal sub-menu action."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

    from config import TERMINAL_CONTENT_PATH
    import json

    data      = request.get_json()
    term_type = data.get('terminal_type')
    action    = data.get('action')

    if not term_type or not action:
        return jsonify({"error": "Missing terminal_type or action"}), 400

    content_path = os.path.join(TERMINAL_CONTENT_PATH, f"{term_type}.json")
    try:
        with open(content_path, 'r', encoding='utf-8') as f:
            content_data = json.load(f)
    except FileNotFoundError:
        return jsonify({"error": f"No content file for terminal type '{term_type}'"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    action_content = content_data.get('content', {}).get(action)
    if not action_content:
        return jsonify({"error": f"No content for action '{action}'"}), 404

    return jsonify({
        "title": action_content.get("title", ""),
        "text":  action_content.get("text", []),
    })