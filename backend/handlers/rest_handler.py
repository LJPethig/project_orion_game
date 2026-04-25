# backend/handlers/rest_handler.py
"""
RestHandler — handles the rest command.

rest — Jack rests for 8 ship hours (REST_SHIP_HOURS) at a designated rest location.
Only available in captain's quarters (bunk) or recreation room (sofa).
Triggers a timed animation, then presents get up / quit choice as clickable buttons.
This is the primary player-initiated save and quit point.
"""

from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager
from config import REST_REAL_SECONDS, REST_SHIP_HOURS

# Rooms where Jack can rest and the flavour message for each
REST_LOCATIONS = {
    'captains_quarters': "You lie down on your bunk.",
    'recreation_room':   "You lie down on the sofa.",
}

# Message when Jack tries to rest somewhere he can't
REST_INVALID_LOCATION = "The floor looks quite uncomfortable here. Resting in your quarters is a better idea."


class RestHandler(BaseHandler):

    def handle_rest(self) -> dict:
        """
        Handle the rest command.
        Returns a timed action response if in a valid rest location,
        or an instant refusal if not.
        """
        room = game_manager.get_current_room()

        if room.id not in REST_LOCATIONS:
            return self._instant(REST_INVALID_LOCATION)

        flavour = REST_LOCATIONS[room.id]

        return {
            'response':      flavour,
            'action_type':   'rest',
            'lock_input':    True,
            'real_seconds':  REST_REAL_SECONDS,
            'game_minutes':  REST_SHIP_HOURS * 60,   # Convert ship hours to minutes for time advance
            'room_changed':  False,
        }


rest_handler = RestHandler()
