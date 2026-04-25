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

def _serialise_item(item) -> dict:
    """
    Serialise a PortableItem to a plain dict.
    Captures all attributes set via __dict__ so mutable runtime fields
    (length_m, installed_manuals etc.) are preserved alongside standard fields.
    Excludes non-serialisable internals (takeable is always True for PortableItems
    and is restored by instantiate_item, so we skip it).
    """
    data = {}
    for key, value in item.__dict__.items():
        # Skip non-serialisable or always-default fields
        if key == 'takeable':
            continue
        data[key] = value
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
        # Stage 3+: rooms, doors, electrical, events, log, manifests
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
    # Stage 3+: restore rooms, doors, electrical, events, log, manifests


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



