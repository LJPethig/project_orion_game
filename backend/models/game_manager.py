# backend/models/game_manager.py
"""
GameManager — central coordinator for all game state.
Single source of truth. One instance lives for the lifetime of the Flask app.
"""

import json
from backend.models.chronometer import Chronometer
from backend.models.ship import Ship
from backend.models.player import Player
from backend.systems.electrical.electrical_system import ElectricalSystem
from config import SHIP_NAME, PLAYER_NAME, STARTING_ROOM, ROOMS_JSON_PATH, \
                   PLAYER_ITEMS_JSON_PATH, ELECTRICAL_JSON_PATH, SHIP_ITEMS_JSON_PATH, \
                   CARGO_JSON_PATH, CARGO_CONTAINERS_JSON_PATH, PALLET_PLATFORMS_JSON_PATH


class GameManager:

    def __init__(self):
        self.initialised  = False
        self.ship_name    = SHIP_NAME
        self.chronometer  = None
        self.ship         = None
        self.player       = None
        self.current_room = None
        self.electrical_system = None
        self.ship_log = []  # list of timestamped log entry strings
        self.tablet_notes = {}  # dict keyed by panel_id → note dict
        self.datapad_suppressed = False
        self.storage_manifest = {}  # instance_id → PortableItem
        self.cargo_manifest = {'containers': [], 'pallets': []}  # loaded from initial_cargo.json

    def new_game(self) -> None:
        """Initialise a new game. Resets all state."""
        from backend.loaders.item_loader import reset_instance_counters
        reset_instance_counters()
        self.chronometer = Chronometer()
        self.ship         = Ship.load_from_json(SHIP_NAME, ROOMS_JSON_PATH)
        self.player       = Player(PLAYER_NAME)
        self.current_room = self.ship.get_room(STARTING_ROOM)
        self._load_player_items()
        self._load_storage_facility()
        self._load_cargo()
        self.electrical_system = ElectricalSystem.load_from_json(ELECTRICAL_JSON_PATH)
        self.update_electrical_states()
        self.initialised  = True
        self.ship_log = []
        self.tablet_notes = {}
        self.datapad_suppressed = False

    def _load_player_items(self) -> None:
        """
        Load player starting inventory and equipped slots from player_items.json.
        Uses the same item registry as the ship loader.
        """
        from backend.loaders.item_loader import load_item_registry, instantiate_item

        with open(PLAYER_ITEMS_JSON_PATH, 'r', encoding='utf-8') as f:
            player_data = json.load(f)

        registry = load_item_registry()

        for item_id in player_data.get('inventory', []):
            item_data = registry.get(item_id)
            item = instantiate_item(dict(item_data)) if item_data else None
            if not item:
                print(f"Warning: player_items.json references unknown item '{item_id}'")
                continue
            success, msg = self.player.add_to_inventory(item)
            if not success:
                print(f"Warning: Could not add '{item_id}' to player inventory: {msg}")

        for slot, item_id in player_data.get('equipped', {}).items():
            item_data = registry.get(item_id)
            item = instantiate_item(dict(item_data)) if item_data else None
            if not item:
                print(f"Warning: player_items.json references unknown item '{item_id}'")
                continue
            slot_attr = f"{slot}_slot"
            if hasattr(self.player, slot_attr):
                setattr(self.player, slot_attr, item)
            else:
                print(f"Warning: player_items.json references unknown slot '{slot}'")

    def _load_storage_facility(self) -> None:
        """
        Load initial storage facility contents from ship_items.json.
        Instantiates items and populates storage_manifest directly.
        """
        from backend.loaders.item_loader import load_item_registry, instantiate_item

        with open(SHIP_ITEMS_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        registry = load_item_registry()

        for entry in data.get('storage_facility', []):
            if isinstance(entry, str):
                item_id, quantity = entry, 1
            else:
                item_id = entry.get('id')
                quantity = entry.get('quantity', 1)
            item_data = registry.get(item_id)
            if not item_data:
                print(f"Warning: storage_facility references unknown item '{item_id}'")
                continue
            for _ in range(quantity):
                item = instantiate_item(dict(item_data))
                self.storage_manifest[item.instance_id] = item

    def _load_cargo(self) -> None:
        """Load initial cargo manifest from initial_cargo.json.
        Merges type definitions from cargo_containers.json and pallet_platforms.json
        so all type fields are available on each instance.
        """
        with open(CARGO_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Build type registry from both type definition files
        type_registry = {}
        for path in (CARGO_CONTAINERS_JSON_PATH, PALLET_PLATFORMS_JSON_PATH):
            with open(path, 'r', encoding='utf-8') as f:
                for entry in json.load(f):
                    type_registry[entry['id']] = entry

        def _merge(instances):
            merged = []
            for instance in instances:
                type_id = instance.get('type_id')
                type_def = type_registry.get(type_id, {})
                merged.append({**type_def, **instance})
            return merged

        self.cargo_manifest = {
            'containers': _merge(data.get('containers', [])),
            'pallets': _merge(data.get('pallets', [])),
        }

    # ── Card access (real inventory checks) ──────────────────

    @property
    def has_low_sec_card(self) -> bool:
        return self.player.has_card_for_level(1) if self.player else False

    @property
    def has_high_sec_card(self) -> bool:
        return self.player.has_card_for_level(2) if self.player else False

    def invalidate_card(self, security_level: int) -> None:
        """
        Invalidate a card after 3 failed PIN attempts.
        The card is not removed — it is swapped for a damaged version.
        The player keeps the physical card but it no longer grants access.
        """
        from backend.models.door import SecurityLevel as SL
        from backend.loaders.item_loader import load_item_registry, instantiate_item

        if not self.player:
            return

        if security_level == SL.KEYCARD_HIGH_PIN.value:
            card = self.player.find_in_inventory('id_card_high_sec')
            if card:
                registry = load_item_registry()
                data = registry.get('id_card_high_sec_damaged')
                if data:
                    damaged = instantiate_item(dict(data))
                    self.player.remove_from_inventory(card)
                    self.player.add_to_inventory(damaged)

    # ── Time ─────────────────────────────────────────────────

    def get_ship_time(self) -> str:
        if not self.initialised or not self.chronometer:
            return "--  --:--"
        return self.chronometer.get_formatted()

    def advance_time(self, minutes: int) -> None:
        if self.initialised and self.chronometer:
            self.chronometer.advance(minutes)

    # ── Events ───────────────────────────────────────────────

    def check_for_event(self) -> dict | None:
        """
        Check for any pending game events.
        Called between component repairs to allow event interruption.

        TODO: implement event system — two event types:
          - Random events: probability-based, checked periodically (micrometeorites, failures)
          - Scheduled events: game-time threshold triggers (hunger, fatigue, thirst)
        Scheduled events must interrupt long repairs (e.g. 48hr job interrupted every 8hrs).
        Returns an event response dict if an event fires, None otherwise.
        """
        return None

    # ── Room ─────────────────────────────────────────────────

    def get_current_room(self):
        return self.current_room

    def set_current_room(self, room_id: str) -> bool:
        room = self.ship.get_room(room_id)
        if not room:
            return False
        self.current_room = room
        return True

    # ── Ship log and tablet notes ─────────────────────────────

    def add_log_entry(self, entry: dict) -> None:
        """Append a structured entry to the ship log."""
        self.ship_log.append(entry)

    def set_tablet_note(self, panel_id: str, note: dict) -> None:
        """Create or replace a tablet note for a panel."""
        self.tablet_notes[panel_id] = note

    def delete_tablet_note(self, panel_id: str) -> None:
        """Remove a tablet note when repair is complete."""
        self.tablet_notes.pop(panel_id, None)

    # ── Electrical helpers ────────────────────────────────────

    def get_all_engines(self) -> list:
        """Return all Engine instances from all rooms in the ship."""
        from backend.models.interactable import Engine
        engines = []
        for room in self.ship.rooms.values():
            for obj in room.objects:
                if isinstance(obj, Engine):
                    engines.append(obj)
        return engines

    def update_electrical_states(self) -> None:
        """Update battery and engine powered states after any electrical change.
        Call this wherever update_battery_states() was previously called.
        """
        self.electrical_system.update_battery_states()
        self.electrical_system.update_engine_states(self.get_all_engines())

    # ── Storage facility ──────────────────────────────────────

    def store_item(self, item) -> None:
        """Remove item from player inventory and add to storage manifest."""
        self.player.remove_from_inventory(item)
        self.storage_manifest[item.instance_id] = item

    def retrieve_item(self, instance_id: str):
        """
        Remove a single item from the storage manifest by instance_id.
        Returns the PortableItem, or None if not found.
        """
        return self.storage_manifest.pop(instance_id, None)

    def get_storage_manifest(self) -> list:
        """
        Return storage manifest grouped by display_name for terminal display.
        Each entry: {'display_name': str, 'quantity': int, 'instance_id': str}
        instance_id is one representative from the group — used by retrieve button.
        Items sorted alphabetically by display_name.
        """
        groups = {}
        for item in self.storage_manifest.values():
            name = item.display_name()
            if name not in groups:
                groups[name] = {'display_name': name, 'quantity': 0, 'instance_id': item.instance_id}
            groups[name]['quantity'] += 1

        return sorted(groups.values(), key=lambda x: x['display_name'])

# Single shared instance — imported by all API routes and handlers
game_manager = GameManager()
