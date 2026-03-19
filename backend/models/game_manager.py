# backend/models/game_manager.py
"""
GameManager — central coordinator for all game state.
Thin for now: holds the chronometer and game initialisation.
Grows as systems are added (ship, player, events, etc.)
"""

from backend.models.chronometer import Chronometer
from config import SHIP_NAME


class GameManager:
    """
    Single source of truth for game state.
    One instance lives for the lifetime of the Flask app.
    """

    def __init__(self):
        self.initialised  = False
        self.ship_name    = SHIP_NAME
        self.chronometer  = None

    def new_game(self) -> None:
        """Initialise a new game. Resets all state."""
        self.chronometer = Chronometer()
        self.initialised = True

    def get_ship_time(self) -> str:
        """Return formatted ship time, or dashes if not initialised."""
        if not self.initialised or self.chronometer is None:
            return "--  --:--"
        return self.chronometer.get_formatted()

    def advance_time(self, minutes: int) -> None:
        """Advance ship time. Called by timed actions (repairs, waits, etc.)"""
        if self.initialised and self.chronometer:
            self.chronometer.advance(minutes)


# Single shared instance — imported by API routes
game_manager = GameManager()
