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
                   PLAYER_ITEMS_JSON_PATH, ELECTRICAL_JSON_PATH


class GameManager:

    def __init__(self):
        self.initialised  = False
        self.ship_name    = SHIP_NAME
        self.chronometer  = None
        self.ship         = None
        self.player       = None
        self.current_room = None
        self.electrical_system = None

    def new_game(self) -> None:
        """Initialise a new game. Resets all state."""
        self.chronometer  = Chronometer()
        self.ship         = Ship.load_from_json(SHIP_NAME, ROOMS_JSON_PATH)
        self.player       = Player(PLAYER_NAME)
        self.current_room = self.ship.get_room(STARTING_ROOM)
        self._load_player_items()
        self.electrical_system = ElectricalSystem.load_from_json(ELECTRICAL_JSON_PATH)
        self.electrical_system.update_battery_states()
        self.initialised  = True

    def _load_player_items(self) -> None:
        """
        Load player starting inventory and equipped slots from player_items.json.
        Uses the same item registry as the ship loader.
        """
        from backend.loaders.item_loader import load_item_registry, instantiate_item

        try:
            with open(PLAYER_ITEMS_JSON_PATH, 'r', encoding='utf-8') as f:
                player_data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load player_items.json: {e}")
            return

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


# Single shared instance — imported by all API routes and handlers
game_manager = GameManager()
