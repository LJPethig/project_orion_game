# backend/systems/save/save_manager.py
"""
SaveManager — serialises and restores all game state to/from JSON save files.

Two save files are written simultaneously on every save:
  saves/save.json        — primary save file
  saves/save_backup.json — identical backup

On load, save.json is tried first. If it cannot be read or fails validation,
save_backup.json is loaded automatically.
"""

import json
import os

from backend.loaders.item_loader import (
    load_item_registry,
    instantiate_item,
    get_instance_counters,
    restore_instance_counters,
)
from backend.models.interactable import StorageUnit, Surface
from backend.systems.electrical.electrical_system import FissionReactor, BackupBattery


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
        Static room data (description, exits, dimensions etc.) is always reloaded from JSON.
    """

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

        rooms_data[room_id] = {
            'floor': floor,
            'containers': containers,
            'surfaces': surfaces,
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

# ── Door serialisation ────────────────────────────────────────

def _serialise_doors(game_manager) -> dict:
    """
    Serialise runtime door state — open/locked flags and panel repair state.
    Static door data (panel_type, security_level, pins) is reloaded from JSON by new_game().
    """
    doors_data = {}
    for door in game_manager.ship.doors:
        door_id = door.id
        panels = {}
        for panel in door.panels.values():
            panels[panel.panel_id] = {
                'is_broken':           panel.is_broken,
                'broken_components':   panel.broken_components,
                'repaired_components': panel.repaired_components,
            }
        doors_data[door_id] = {
            'door_open':   door.door_open,
            'door_locked': door.door_locked,
            'panels':      panels,
        }
    return doors_data

def _restore_doors(game_manager, doors_data: dict) -> None:
    """
    Restore runtime door state from save data.
    new_game() has already loaded static door data from JSON — we only overlay runtime state.
    """
    for door_id, door_state in doors_data.items():
        door = game_manager.ship.get_door_by_id(door_id)
        if not door:
            raise ValueError(
                f"[SaveManager] Door '{door_id}' in save file not found in ship. "
                f"Was door_status.json changed since this save was made?"
            )
        door.door_open   = door_state['door_open']
        door.door_locked = door_state['door_locked']

        for panel_id, panel_state in door_state.get('panels', {}).items():
            # Find the panel by panel_id across all sides of this door
            panel = next(
                (p for p in door.panels.values() if p.panel_id == panel_id),
                None
            )
            if not panel:
                raise ValueError(
                    f"[SaveManager] Panel '{panel_id}' in save file not found on door '{door_id}'. "
                    f"Was door_status.json changed since this save was made?"
                )
            panel.is_broken           = panel_state['is_broken']
            panel.broken_components   = panel_state['broken_components']
            panel.repaired_components = panel_state['repaired_components']

# ── Electrical system serialisation ───────────────────────────

def _serialise_electrical(es) -> dict:
    """
    Serialise runtime electrical state — reactor, battery, panel, breaker and cable flags.
    Static data (names, locations, ratings, wiring) is reloaded from electrical.json by new_game().

    NOTE: FissionReactor.operational is currently a direct flag — saved as-is.
    When reactor internal components are implemented, operational will become a derived
    property and this code must be updated to save the internal flags instead.
    """

    reactors = {}
    batteries = {}
    for source_id, source in es.power_sources.items():
        if isinstance(source, FissionReactor):
            reactors[source_id] = {
                'operational': source.operational,
                'temperature': source.temperature,
                'ejected':     source.ejected,
            }
        elif isinstance(source, BackupBattery):
            batteries[source_id] = {
                'active':         source.active,
                'charge_percent': source.charge_percent,
            }

    panels = {}
    for panel_id, panel in es.panels.items():
        panels[panel_id] = {
            'logic_board_intact':        panel.logic_board_intact,
            'bus_bar_intact':            panel.bus_bar_intact,
            'surge_protector_intact':    panel.surge_protector_intact,
            'smoothing_capacitor_intact': panel.smoothing_capacitor_intact,
            'isolation_switch_intact':   panel.isolation_switch_intact,
        }

    breakers = {}
    for breaker_id, breaker in es.breakers.items():
        breakers[breaker_id] = {
            'damaged': breaker.damaged,
            'tripped': breaker.tripped,
        }

    cables = {}
    for cable_id, cable in es.cables.items():
        cables[cable_id] = {
            'intact':    cable.intact,
            'connected': cable.connected,
        }

    return {
        'reactors': reactors,
        'batteries': batteries,
        'panels':    panels,
        'breakers':  breakers,
        'cables':    cables,
    }


def _restore_electrical(es, elec_data: dict, game_manager) -> None:
    """
    Restore runtime electrical state from save data.
    new_game() has already loaded static electrical data from JSON — we only overlay runtime state.
    After restoring, update_electrical_states() is called to recalculate derived states.
    """

    for source_id, state in elec_data.get('reactors', {}).items():
        source = es.power_sources.get(source_id)
        if not source:
            raise ValueError(
                f"[SaveManager] Reactor '{source_id}' in save file not found in electrical system. "
                f"Was electrical.json changed since this save was made?"
            )
        source.operational = state['operational']
        source.temperature = state['temperature']
        source.ejected     = state['ejected']

    for source_id, state in elec_data.get('batteries', {}).items():
        source = es.power_sources.get(source_id)
        if not source:
            raise ValueError(
                f"[SaveManager] Battery '{source_id}' in save file not found in electrical system. "
                f"Was electrical.json changed since this save was made?"
            )
        source.active         = state['active']
        source.charge_percent = state['charge_percent']

    for panel_id, state in elec_data.get('panels', {}).items():
        panel = es.panels.get(panel_id)
        if not panel:
            raise ValueError(
                f"[SaveManager] Panel '{panel_id}' in save file not found in electrical system. "
                f"Was electrical.json changed since this save was made?"
            )
        panel.logic_board_intact         = state['logic_board_intact']
        panel.bus_bar_intact             = state['bus_bar_intact']
        panel.surge_protector_intact     = state['surge_protector_intact']
        panel.smoothing_capacitor_intact = state['smoothing_capacitor_intact']
        panel.isolation_switch_intact    = state['isolation_switch_intact']

    for breaker_id, state in elec_data.get('breakers', {}).items():
        breaker = es.breakers.get(breaker_id)
        if not breaker:
            raise ValueError(
                f"[SaveManager] Breaker '{breaker_id}' in save file not found in electrical system. "
                f"Was electrical.json changed since this save was made?"
            )
        breaker.damaged = state['damaged']
        breaker.tripped = state['tripped']

    for cable_id, state in elec_data.get('cables', {}).items():
        cable = es.cables.get(cable_id)
        if not cable:
            raise ValueError(
                f"[SaveManager] Cable '{cable_id}' in save file not found in electrical system. "
                f"Was electrical.json changed since this save was made?"
            )
        cable.intact    = state['intact']
        cable.connected = state['connected']

    # Recalculate all derived states after restoring
    game_manager.update_electrical_states()

# ── Event serialisation ───────────────────────────────────────

def _serialise_events(game_manager) -> dict:
    """Serialise event fired and resolved flags."""
    return game_manager.event_system.get_fired_state()


def _restore_events(game_manager, events_data: dict) -> None:
    """Restore event fired and resolved flags from save data."""
    game_manager.event_system.restore_fired_state(events_data)

# ── Ship log and tablet notes serialisation ───────────────────

def _serialise_log_and_notes(game_manager) -> dict:
    """Serialise ship log and tablet notes — both are plain JSON-serialisable structures."""
    return {
        'ship_log':     game_manager.ship_log,
        'tablet_notes': game_manager.tablet_notes,
    }


def _restore_log_and_notes(game_manager, data: dict) -> None:
    """Restore ship log and tablet notes from save data."""
    game_manager.ship_log     = data['ship_log']
    game_manager.tablet_notes = data['tablet_notes']

# ── Storage and cargo manifest serialisation ──────────────────

def _serialise_manifests(game_manager) -> dict:
    """
    Serialise storage facility manifest and cargo manifest.
    Storage manifest contains PortableItem instances — serialised minimally.
    Cargo manifest is plain dicts — serialised as-is.
    Both are new-game-only on load — initial_ship_items.json and initial_cargo.json
    are never reloaded on a save restore.
    """
    storage = {
        instance_id: _serialise_item(item)
        for instance_id, item in game_manager.storage_manifest.items()
    }
    return {
        'storage_manifest': storage,
        'cargo_manifest':   game_manager.cargo_manifest,
    }


def _restore_manifests(game_manager, data: dict) -> None:
    """
    Restore storage and cargo manifests from save data.
    Clears new_game() populated state before restoring.
    """
    # Clear storage manifest loaded by new_game()
    game_manager.storage_manifest.clear()
    for instance_id, item_data in data.get('storage_manifest', {}).items():
        item = _restore_item(item_data)
        game_manager.storage_manifest[item.instance_id] = item

    # Cargo manifest is plain dicts — overwrite directly
    game_manager.cargo_manifest = data['cargo_manifest']

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
    player.clear_inventory()
    for slot in player.EQUIP_SLOTS:
        setattr(player, f"{slot}_slot", None)

    # Restore inventory
    for item_data in player_data.get('inventory', []):
        item = _restore_item(item_data)
        player.restore_inventory_item(item)

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
        'meta': {
            'dead':              False,
            'instance_counters': get_instance_counters(),
        },
        'player': _serialise_player(game_manager.player),
        'ship_time': _serialise_ship_time(game_manager.chronometer),
        'rooms': _serialise_rooms(game_manager),
        'doors':       _serialise_doors(game_manager),
        'electrical': _serialise_electrical(game_manager.electrical_system),
        'events': _serialise_events(game_manager),
        'log_notes': _serialise_log_and_notes(game_manager),
        'manifests': _serialise_manifests(game_manager),
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
    Raises RuntimeError if the save has dead=True — caller must handle this
    and show the death screen instead of proceeding to the game.
    """
    save_data = _read_save_file()

    meta = save_data.get('meta', {})

    if meta.get('dead', False):
        raise RuntimeError('dead')

    # Restore instance counters immediately — before any item is created.
    # new_game() has already reset them to zero; restoring here ensures
    # new items created after load continue from the saved sequence and
    # never collide with an existing instance_id.
    restore_instance_counters(meta.get('instance_counters', {}))

    _restore_player(game_manager.player, save_data['player'])
    _restore_ship_time(game_manager.chronometer, save_data['ship_time'])
    _restore_rooms(game_manager, save_data['rooms'])
    _restore_doors(game_manager, save_data['doors'])
    _restore_electrical(game_manager.electrical_system, save_data['electrical'], game_manager)
    _restore_events(game_manager, save_data['events'])
    _restore_log_and_notes(game_manager, save_data['log_notes'])
    _restore_manifests(game_manager, save_data['manifests'])


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


def is_save_dead() -> bool:
    """
    Return True if the existing save has dead=True.
    Returns False if no save exists or if the file cannot be read.
    """
    try:
        save_data = _read_save_file()
        return save_data.get('meta', {}).get('dead', False)
    except RuntimeError:
        return False


def mark_dead() -> None:
    """
    Write dead=True to both save files simultaneously.
    Called when Jack dies. After this, neither save file can be used to continue.
    Both files are read, the dead flag is set, and both are rewritten.
    If a file cannot be read it is written fresh with only the dead flag so the
    splash screen still detects the death state on next launch.
    """
    for path in (SAVE_PATH, SAVE_BACKUP_PATH):
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data.setdefault('meta', {})['dead'] = True

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)



