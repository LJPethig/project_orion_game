# backend/api/game.py
"""
Game API routes.
/api/game/state        — current game state (ship time, etc.)
/api/game/new          — start a new game
/api/game/save_status  — check whether a save file exists and whether it is dead
/api/game/load         — load saved game (calls new_game() then load_game())
"""
import os
import json

from flask import Blueprint, jsonify, request
from backend.models.game_manager import game_manager
from backend.models.interactable import StorageUnit, Surface, Terminal, PowerJunction
from backend.handlers.storage_handler import storage_handler
from backend.handlers.repair_utils import item_name
from backend.systems.electrical.electrical_system import FissionReactor
from backend.systems.save.save_manager import save_exists, is_save_dead, load_game
from config import TERMINAL_CONTENT_PATH


game_bp = Blueprint("game", __name__)


@game_bp.route("/state", methods=["GET"])
def get_state():
    """Return current game state for frontend polling."""
    has_datapad = False
    if game_manager.initialised and game_manager.player:
        has_datapad = (
                any(i.id == 'ships_datapad' for i in game_manager.player.get_inventory())
                and not game_manager.datapad_suppressed
        )
    return jsonify({
        "initialised": game_manager.initialised,
        "ship_name":   game_manager.ship_name,
        "ship_time":   game_manager.get_ship_time(),
        "has_datapad": has_datapad,
    })


@game_bp.route("/new", methods=["POST"])
def new_game():
    """Start a new game — initialises all state."""
    game_manager.new_game()
    return jsonify({
        "success": True,
        "ship_name": game_manager.ship_name,
        "ship_type": game_manager.ship_type,
        "ship_time": game_manager.get_ship_time(),
        "ship_location": game_manager.ship_location,
        "ship_mission": game_manager.ship_mission,
    })


@game_bp.route("/save_status", methods=["GET"])
def save_status():
    """
    Return whether a save file exists and whether it carries the dead flag.
    Called by the splash screen on load to decide which buttons to show.
    """
    exists = save_exists()
    dead   = is_save_dead() if exists else False
    return jsonify({
        "exists": exists,
        "dead":   dead,
    })


@game_bp.route("/load", methods=["POST"])
def load_game_route():
    """
    Load a saved game.
    Sequence: new_game() to build clean state, then load_game() to overlay save data.
    Returns active events so the frontend can restore the event strip immediately.

    On dead save: returns {'dead': True} — the splash screen must intercept this
    and show the death screen instead of redirecting to the game.

    TODO — Death screen behaviour (implement when death screen UI is built):
      - Splash screen receives {'dead': True} from this endpoint.
      - It must NOT redirect to /game.
      - It must show a full-screen death state: black background, red-tinted title,
        message explaining Jack is dead and the save cannot be continued.
      - Only a 'New Game' button is shown — no Continue button.
      - New Game from a dead save must delete both save files before calling /api/game/new,
        so save_status() returns exists=False on the next launch.
    """
    game_manager.new_game()

    try:
        load_game(game_manager)
    except RuntimeError as e:
        if str(e) == 'dead':
            return jsonify({'dead': True})
        raise

    active_events = game_manager.event_system.get_active_events()

    return jsonify({
        "success": True,
        "ship_name": game_manager.ship_name,
        "ship_type": game_manager.ship_type,
        "ship_time": game_manager.get_ship_time(),
        "ship_location": game_manager.ship_location,
        "ship_mission": game_manager.ship_mission,
        "active_events": active_events,
    })


@game_bp.route("/save", methods=["DELETE"])
def delete_save_route():
    """Delete both save files — called when player starts a new game over an existing save."""
    from backend.systems.save.save_manager import delete_save
    delete_save()
    return jsonify({"success": True})


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
            'id': item.id if item else None,
            'instance_id': item.instance_id if item else None,
            'name': item.display_name() if item else None,
            'description': item.description if item else None,
            'mass': item.mass if item else None,
            'manufacturer': getattr(item, 'manufacturer', None) if item else None,
            'model': getattr(item, 'model', None) if item else None,
            'image': f"images/items/{item.id}.png" if item else None,
            'equip_slot': getattr(item, 'equip_slot', None) if item else None,
        }

    # Loose carried items
    carried = [
        {
            'id': item.id,
            'instance_id': item.instance_id,
            'name': item.display_name(),
            'description': item.description,
            'mass': item.mass,
            'manufacturer': getattr(item, 'manufacturer', None),
            'model': getattr(item, 'model', None),
            'image': f"images/items/{item.id}.png",
            'equip_slot': getattr(item, 'equip_slot', None),
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

def _get_reactor_state(es) -> str:
    """Return current main reactor state: 'online', 'offline', or 'ejected'."""
    if not es:
        return 'online'
    for source in es.power_sources.values():
        if isinstance(source, FissionReactor) and source.id == 'reactor_core':
            if source.ejected:
                return 'ejected'
            if not source.operational:
                return 'offline'
            return 'online'
    return 'online'

def _build_room_data(room) -> dict:
    """Build room dict for frontend — exits, portable items, object states."""
    exits = {}
    es = game_manager.electrical_system
    for exit_key, exit_data in room.exits.items():
        door = exit_data.get('door')
        powered = True
        if es and door:
            powered = es.check_room_power(room.id)
        exits[exit_key] = {
            'label': exit_data.get('label', exit_key),
            'door_state': door.get_state() if door else 'none',
            'panel_powered': powered,
        }

    # Object states — containers (open/closed + contents), surfaces (has_items + contents), terminals
    object_states = {}
    for obj in room.objects:
        if isinstance(obj, StorageUnit):
            object_states[obj.id] = {
                'type': 'container',
                'name': obj.name,
                'is_open': obj.is_open,
                'has_items': len(obj.contents) > 0,
                'contents': [{'id': i.id, 'instance_id': i.instance_id, 'name': i.display_name()} for i in
                             obj.contents] if obj.is_open else [],
            }
        elif isinstance(obj, Surface):
            object_states[obj.id] = {
                'type': 'surface',
                'name': obj.name,
                'has_items': obj.has_items,
                'contents': [{'id': i.id, 'instance_id': i.instance_id, 'name': i.display_name()} for i in
                             obj.contents],
            }
        elif isinstance(obj, Terminal):
            object_states[obj.id] = {
                'type': 'terminal',
                'name': obj.name,
                'powered': es.check_room_power(room.id) if es else True,
            }
        elif isinstance(obj, PowerJunction):
            object_states[obj.id] = {
                'type': 'power_junction',
                'name': obj.name,
                'panel_id': obj.panel_id,
            }

    # Floor items — only populated when items are present
    floor_items = [{'id': i.id, 'instance_id': i.instance_id, 'name': i.display_name()} for i in room.floor]

    room_powered = es.check_room_power(room.id) if es else True

    reactor_state = _get_reactor_state(es)

    return {
        'id': room.id,
        'name': room.name,
        'description': room.description,
        'description_powered': room.description_powered,
        'description_unpowered': room.description_unpowered,
        'description_reactor_online': room.description_reactor_online,
        'description_reactor_offline': room.description_reactor_offline,
        'description_reactor_ejected': room.description_reactor_ejected,
        'reactor_state': reactor_state,
        'room_powered': room_powered,
        'background_image': room.background_image,
        'exits': exits,
        'object_states': object_states,
        'floor_items': floor_items,
    }

@game_bp.route("/terminal/content", methods=["POST"])
def get_terminal_content():
    """Return content for a terminal sub-menu action."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

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

    # View — return view type and any additional fields (menu etc.)
    if action_content.get('view'):
        response = {
            "title": action_content.get("title", ""),
            "view": action_content.get("view"),
        }
        if action_content.get('menu'):
            response['menu'] = action_content.get('menu')
        return jsonify(response)

    return jsonify({
        "title": action_content.get("title", ""),
        "text": action_content.get("text", []),
    })

@game_bp.route("/datapad", methods=["GET"])
def get_datapad_data():
    """Return ship log and tablet notes for the datapad."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

    return jsonify({
        'ship_log':     list(reversed(game_manager.ship_log)),   # newest first
        'tablet_notes': list(game_manager.tablet_notes.values()),
    })

@game_bp.route("/terminal/close", methods=["POST"])
def terminal_close():
    """Called when player exits a terminal session."""
    if game_manager.initialised:
        game_manager.datapad_suppressed = False
    return jsonify({"success": True})

@game_bp.route("/storage/store", methods=["POST"])
def storage_store():
    """Store a carried item in the automated storage facility."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

    data = request.get_json()
    instance_id = data.get('instance_id')
    if not instance_id:
        return jsonify({"error": "Missing instance_id"}), 400

    result = storage_handler.handle_store(instance_id)
    return jsonify(result)


@game_bp.route("/storage/retrieve", methods=["POST"])
def storage_retrieve():
    """Retrieve a single item from the automated storage facility."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

    data = request.get_json()
    instance_id = data.get('instance_id')
    if not instance_id:
        return jsonify({"error": "Missing instance_id"}), 400

    result = storage_handler.handle_retrieve(instance_id)
    return jsonify(result)


@game_bp.route("/storage/manifest", methods=["GET"])
def storage_manifest():
    """Return the storage facility manifest for terminal display."""
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

    return jsonify({
        'manifest': game_manager.get_storage_manifest()
    })

@game_bp.route("/cargo/manifest", methods=["GET"])
def cargo_manifest():
    """Return the cargo bay manifest for terminal display.
    Resolves item IDs to display names for container contents and pallet attached_items.
    """
    if not game_manager.initialised:
        return jsonify({"error": "Game not initialised"}), 400

    def resolve_contents(contents):
        return [
            {'name': item_name(entry['item']), 'quantity': entry['quantity']}
            for entry in contents
        ]

    containers = []
    for c in game_manager.cargo_manifest.get('containers', []):
        entry = dict(c)
        entry['contents'] = resolve_contents(c.get('contents', []))
        containers.append(entry)

    pallets = []
    for p in game_manager.cargo_manifest.get('pallets', []):
        entry = dict(p)
        entry['attached_items'] = resolve_contents(p.get('attached_items', []))
        pallets.append(entry)

    return jsonify({'containers': containers, 'pallets': pallets})