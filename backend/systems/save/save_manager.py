# backend/systems/save/save_manager.py
"""
SaveManager — serialises and restores all game state to/from JSON save files.

Two save files are written simultaneously on every save:
  saves/save.json        — primary save file
  saves/save_backup.json — identical backup

On load, save.json is tried first. If it cannot be read or fails validation,
save_backup.json is loaded automatically.

Build order — each stage is tested before the next is added:
  Stage 1: Player (inventory + equipped slots)          ← current
  Stage 2: Ship time
  Stage 3: Rooms (floor items, container states)
  Stage 4: Doors (state, panel repair state)
  Stage 5: Electrical system
  Stage 6: Events (fired + resolved flags)
  Stage 7: Ship log + tablet notes
  Stage 8: Storage + cargo manifests
"""

import json
import os

SAVE_DIR         = 'saves'
SAVE_PATH        = os.path.join(SAVE_DIR, 'save.json')
SAVE_BACKUP_PATH = os.path.join(SAVE_DIR, 'save_backup.json')


# ── Item serialisation helpers ────────────────────────────────

# Fields that can change at runtime and must be saved alongside id and instance_id.
# Everything else (name, description, keywords, mass, manufacturer etc.) is static
# and reloaded from the item registry on restore.
_ITEM_MUTABLE_FIELDS = {'length_m', 'installed_manuals'}


def _serialise_item(item) -> dict:
    """
    Serialise a PortableItem to a minimal dict.
    Only saves id, instance_id, and known mutable runtime fields.
    All static fields are reloaded from the item registry on restore.
    """
    data = {
        'id':          item.id,
        'instance_id': item.instance_id,
    }
    for field in _ITEM_MUTABLE_FIELDS:
        if hasattr(item, field):
            data[field] = getattr(item, field)
    return data


def _restore_item(item_data: dict):
    """
    Restore a PortableItem from a serialised dict.
    Uses instantiate_item() to create a fresh instance from the registry,
    then overlays all saved attributes to restore mutable runtime state.
    """
    from backend.loaders.item_loader import load_item_registry, instantiate_item

    registry  = load_item_registry()
    item_id   = item_data.get('id')
    base_data = registry.get(item_id)

    if not base_data:
        raise ValueError(
            f"[SaveManager] Cannot restore item '{item_id}' — "
            f"not found in item registry. Was items JSON changed since this save was made?"
        )

    # Create a fresh instance from registry definition
    item = instantiate_item(dict(base_data))

    # Overlay all saved attributes to restore runtime state
    # (instance_id, length_m, installed_manuals etc.)
    for key, value in item_data.items():
        setattr(item, key, value)

    return item

# ── Ship time serialisation ───────────────────────────────────

def _serialise_ship_time(chronometer) -> dict:
    """Serialise ship time — total minutes is all that is needed."""
    return {'total_minutes': chronometer.total_minutes}


def _restore_ship_time(chronometer, time_data: dict) -> None:
    """Restore ship time from save data."""
    chronometer.total_minutes = time_data['total_minutes']

# ── Room serialisation ────────────────────────────────────────

def _serialise_rooms(game_manager) -> dict:
    """
    Serialise runtime room state — floor items, container states, surface contents.
    Only rooms with non-default state are included to keep the save file lean.
    Static room data (description, exits, dimensions etc.) is always reloaded from JSON.
    """
    from backend.models.interactable import StorageUnit, Surface

    rooms_data = {}
    current_room_id = game_manager.current_room.id

    for room_id, room in game_manager.ship.rooms.items():

        # Floor items
        floor = [_serialise_item(i) for i in room.floor]

        # Container states
        containers = {}
        for obj in room.objects:
            if isinstance(obj, StorageUnit):
                containers[obj.id] = {
                    'is_open':  obj.is_open,
                    'contents': [_serialise_item(i) for i in obj.contents],
                }

        # Surface contents
        surfaces = {}
        for obj in room.objects:
            if isinstance(obj, Surface):
                surfaces[obj.id] = {
                    'contents': [_serialise_item(i) for i in obj.contents],
                }

        # Only save rooms that have non-default state
        if floor or any(c['is_open'] or c['contents'] for c in containers.values()) or \
           any(s['contents'] for s in surfaces.values()):
            rooms_data[room_id] = {
                'floor':      floor,
                'containers': containers,
                'surfaces':   surfaces,
            }

    return {
        'current_room_id': current_room_id,
        'rooms':           rooms_data,
    }


def _restore_rooms(game_manager, rooms_data: dict) -> None:
    """
    Restore runtime room state from save data.
    Clears all room floor/container/surface state first, then restores from save.
    Static room data is already loaded from JSON by new_game().
    """
    from backend.models.interactable import StorageUnit, Surface

    # First clear all runtime room state — new_game() has already populated
    # containers and surfaces from initial_ship_items.json, so we must wipe
    # that before restoring save state
    for room in game_manager.ship.rooms.values():
        room.floor.clear()
        for obj in room.objects:
            if isinstance(obj, StorageUnit):
                obj.contents.clear()
                obj.current_mass = 0.0
                obj.is_open = False
            elif isinstance(obj, Surface):
                obj.contents.clear()
                obj.current_mass = 0.0

    # Restore current room
    current_room_id = rooms_data.get('current_room_id')
    if current_room_id:
        game_manager.set_current_room(current_room_id)

    # Restore saved room state
    for room_id, room_state in rooms_data.get('rooms', {}).items():
        room = game_manager.ship.get_room(room_id)
        if not room:
            raise ValueError(
                f"[SaveManager] Room '{room_id}' in save file not found in ship. "
                f"Was ship_rooms.json changed since this save was made?"
            )

        # Floor items
        for item_data in room_state.get('floor', []):
            room.floor.append(_restore_item(item_data))

        # Container states
        for obj in room.objects:
            if isinstance(obj, StorageUnit):
                container_data = room_state.get('containers', {}).get(obj.id)
                if container_data:
                    obj.is_open = container_data['is_open']
                    for item_data in container_data.get('contents', []):
                        item = _restore_item(item_data)
                        obj.contents.append(item)
                        obj.current_mass += item.mass

            elif isinstance(obj, Surface):
                surface_data = room_state.get('surfaces', {}).get(obj.id)
                if surface_data:
                    for item_data in surface_data.get('contents', []):
                        item = _restore_item(item_data)
                        obj.contents.append(item)
                        obj.current_mass += item.mass

# ── Player serialisation ──────────────────────────────────────

def _serialise_player(player) -> dict:
    """Serialise player inventory and equipped slots."""
    inventory = [_serialise_item(item) for item in player.get_inventory()]

    equipped = {}
    for slot in player.EQUIP_SLOTS:
        item = getattr(player, f"{slot}_slot")
        equipped[slot] = _serialise_item(item) if item else None

    return {
        'inventory': inventory,
        'equipped':  equipped,
    }


def _restore_player(player, player_data: dict) -> None:
    """
    Restore player inventory and equipped slots from save data.
    Clears existing state before restoring — never merges with current state.
    """
    # Clear current inventory and equipped slots
    player._inventory.clear()
    for slot in player.EQUIP_SLOTS:
        setattr(player, f"{slot}_slot", None)

    # Restore inventory
    for item_data in player_data.get('inventory', []):
        item = _restore_item(item_data)
        player._inventory.append(item)

    # Restore equipped slots
    for slot, item_data in player_data.get('equipped', {}).items():
        if item_data is not None:
            item = _restore_item(item_data)
            setattr(player, f"{slot}_slot", item)


# ── Save ─────────────────────────────────────────────────────

def save_game(game_manager) -> None:
    """
    Serialise all game state and write to both save files simultaneously.
    Creates the saves/ directory if it does not exist.
    """
    os.makedirs(SAVE_DIR, exist_ok=True)

    save_data = {
        'player': _serialise_player(game_manager.player),
        'ship_time': _serialise_ship_time(game_manager.chronometer),
        'rooms': _serialise_rooms(game_manager),
        # Stage 4+: doors, electrical, events, log, manifests
    }

    serialised = json.dumps(save_data, indent=2, ensure_ascii=False)

    # Write both files — primary then backup
    with open(SAVE_PATH, 'w', encoding='utf-8') as f:
        f.write(serialised)
    with open(SAVE_BACKUP_PATH, 'w', encoding='utf-8') as f:
        f.write(serialised)


# ── Load ─────────────────────────────────────────────────────

def load_game(game_manager) -> None:
    """
    Load save data and restore all game state.
    Tries save.json first — falls back to save_backup.json on failure.
    Raises RuntimeError if neither file can be loaded.
    """
    save_data = _read_save_file()

    _restore_player(game_manager.player, save_data['player'])
    _restore_ship_time(game_manager.chronometer, save_data['ship_time'])
    _restore_rooms(game_manager, save_data['rooms'])
    # Stage 4+: restore doors, electrical, events, log, manifests


def _read_save_file() -> dict:
    """
    Read and parse the save file.
    Tries save.json first, falls back to save_backup.json.
    Raises RuntimeError if neither can be read.
    """
    for path in (SAVE_PATH, SAVE_BACKUP_PATH):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            continue

    raise RuntimeError(
        "[SaveManager] Neither save.json nor save_backup.json could be read. "
        "Save files may be missing or corrupted."
    )


def save_exists() -> bool:
    """Return True if at least one save file exists."""
    return os.path.exists(SAVE_PATH) or os.path.exists(SAVE_BACKUP_PATH)



