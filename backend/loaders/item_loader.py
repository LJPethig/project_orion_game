# backend/loaders/item_loader.py
"""
ItemLoader — reads all item JSON files and returns a master registry.

The registry maps item_id → item instance (PortableItem / UtilityBelt subclass).
Fixed objects are handled separately by ship.py since they live in rooms.

Subclass selection rules:
  - id == 'utility_belt'  → UtilityBelt
  - everything else       → PortableItem

Duplicate IDs across files are flagged as warnings — last one wins.
"""

import json
from backend.models.interactable import PortableItem, UtilityBelt
from config import ITEM_FILES


def load_item_registry() -> dict:
    """
    Load all portable item definitions from ITEM_FILES.
    Returns dict of item_id → PortableItem (or subclass) instance.
    """
    registry = {}

    for path in ITEM_FILES:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                items = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load item file '{path}': {e}")
            continue

        for data in items:
            item_id = data.get('id')
            if not item_id:
                print(f"Warning: Item in '{path}' has no id — skipped.")
                continue
            if item_id in registry:
                print(f"Warning: Duplicate item id '{item_id}' in '{path}' — overwriting.")

            registry[item_id] = _instantiate(data)

    return registry


def _instantiate(data: dict) -> PortableItem:
    """Instantiate the correct PortableItem subclass from a data dict."""
    kwargs = {k: v for k, v in data.items()}

    if kwargs.get('id') == 'utility_belt':
        return UtilityBelt(**kwargs)

    return PortableItem(**kwargs)
