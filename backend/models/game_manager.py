# backend/models/game_manager.py
"""
GameManager — central coordinator for all game state.
Phase 7: adds ship loading and current room tracking.
"""

import os
from backend.models.chronometer import Chronometer
from backend.models.ship import Ship
from config import SHIP_NAME, STARTING_ROOM


# Path to ship_rooms.json — relative to project root
ROOMS_JSON_PATH = os.path.join('data', 'ship', 'structure', 'ship_rooms.json')


class GameManager:
    """
    Single source of truth for game state.
    One instance lives for the lifetime of the Flask app.
    """

    def __init__(self):
        self.initialised    = False
        self.ship_name      = SHIP_NAME
        self.chronometer    = None
        self.ship           = None
        self.current_room   = None

    def new_game(self) -> None:
        """Initialise a new game. Resets all state."""
        self.chronometer  = Chronometer()
        self.ship         = Ship.load_from_json(SHIP_NAME, ROOMS_JSON_PATH)
        self.current_room = self.ship.get_room(STARTING_ROOM)
        self.initialised  = True

    # ── Time ─────────────────────────────────────────────────

    def get_ship_time(self) -> str:
        """Return formatted ship time, or dashes if not initialised."""
        if not self.initialised or not self.chronometer:
            return "--  --:--"
        return self.chronometer.get_formatted()

    def advance_time(self, minutes: int) -> None:
        """Advance ship time. Called by timed actions (repairs, waits, etc.)"""
        if self.initialised and self.chronometer:
            self.chronometer.advance(minutes)

    # ── Room ─────────────────────────────────────────────────

    def get_current_room(self):
        """Return the current Room instance."""
        return self.current_room

    def set_current_room(self, room_id: str) -> bool:
        """Move player to a new room by ID. Returns False if room not found."""
        room = self.ship.get_room(room_id)
        if not room:
            return False
        self.current_room = room
        return True


# Single shared instance — imported by all API routes
game_manager = GameManager()
