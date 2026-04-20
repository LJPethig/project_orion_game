# backend/loaders/item_loader.py
"""
ItemLoader — reads all item JSON files and returns a master registry.

The registry maps item_id → raw data dict (not an instance).
ship.py calls _make_item() which creates a fresh instance each time,
ensuring every placed item is a unique Python object with independent state.

Fixed objects are handled separately by ship.py since they live in rooms.

Subclass selection rules:
  - id == 'utility_belt'  → UtilityBelt
  - everything else       → PortableItem

Duplicate IDs across files are flagged as warnings — last one wins.
"""

import json
from backend.models.interactable import PortableItem, UtilityBelt
from config import ITEM_FILES


# ── Instance counters — reset each new game ───────────────────
_instance_counters: dict = {}


def reset_instance_counters() -> None:
    """Reset all instance counters. Call at new_game() time."""
    global _instance_counters
    _instance_counters = {}

def _assign_instance_id(item) -> None:
    """Assign a unique instance_id to a PortableItem at load time."""
    type_id = item.id
    count = _instance_counters.get(type_id, 0) + 1
    _instance_counters[type_id] = count
    item.instance_id = f"{type_id}_{count:03d}"

def load_item_registry() -> dict:
    """
    Load all portable item definitions from ITEM_FILES.
    Returns dict of item_id → raw data dict.
    Instantiation happens in ship._make_item() to ensure unique instances.
    """
    registry = {}

    for path in ITEM_FILES:
        with open(path, 'r', encoding='utf-8') as f:
            items = json.load(f)

            for data in items:
                item_id = data.get('id')
                if not item_id:
                    raise ValueError(f"Item in '{path}' has no id field — malformed data.")
                if item_id in registry:
                    raise ValueError(f"Duplicate item id '{item_id}' found in '{path}' — fix the data.")

                registry[item_id] = dict(data) # store raw data, not instance

    return registry


def instantiate_item(data: dict) -> PortableItem:
    """
    Instantiate the correct PortableItem subclass from a data dict.

    cable items use mass_per_metre + length_m instead of a fixed mass.
    mass is computed at instantiation time: length_m * mass_per_metre.
    length_m may be supplied as an instance override from placement data.
    """
    kwargs = {k: v for k, v in data.items()}

    # ── cable mass computation ─────────────────────────────────
    if 'mass_per_metre' in kwargs:
        length_m = kwargs.get('length_m', kwargs.get('max_length_m', 0.0))
        kwargs['length_m'] = length_m
        kwargs['mass'] = round(length_m * kwargs['mass_per_metre'], 4)

    if kwargs.get('id') == 'utility_belt':
        item = UtilityBelt(**kwargs)
        _assign_instance_id(item)
        return item

    item = PortableItem(**kwargs)
    _assign_instance_id(item)
    return item