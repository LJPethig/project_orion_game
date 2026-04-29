# backend/handlers/base_handler.py
"""
BaseHandler — shared utilities for all command handlers.
Card checking and exit finding used by both MovementHandler and DoorHandler.
"""

from backend.models.game_manager import game_manager
from backend.models.door import SecurityLevel
from config import CARD_SWIPE_REAL_SECONDS


class BaseHandler:

    def _find_exit(self, room, target: str):
        """
        Find a matching exit key in the room by:
        1. Exact exit key match
        2. Label match
        3. Shortcut match
        Strips common door-related noise words before matching.
        Returns the exit key if found, None otherwise.
        """
        noise = ['door access panel', 'access panel', 'door panel',
                 'access door', 'access', 'panel', 'hatch', 'door', 'doors']
        cleaned = target.strip().lower()
        for word in sorted(noise, key=len, reverse=True):
            cleaned = cleaned.replace(word, '').strip()

        for attempt in ([cleaned, target] if cleaned != target else [target]):
            t = attempt.strip().lower()
            if not t:
                continue
            for exit_key, exit_data in room.exits.items():
                if t == exit_key.lower():
                    return exit_key
                if t == exit_data.get('label', '').lower():
                    return exit_key
                shortcuts = exit_data.get('shortcuts', [])
                if isinstance(shortcuts, list):
                    if t in [s.lower() for s in shortcuts]:
                        return exit_key
        return None

    def _check_card(self, door, panel=None) -> tuple[bool, str]:
        """Check if the player has the required card for this door.
        panel — the SecurityPanel on the player's side; if provided, security level
        is read from the panel rather than the door.
        """
        level = panel.security_level.value if panel else 0
        has_low_card = game_manager.has_low_sec_card
        has_high_card = game_manager.has_high_sec_card

        if level == SecurityLevel.NONE.value:
            return True, ""
        if level == SecurityLevel.KEYCARD_LOW.value:
            if has_high_card or has_low_card:
                return True, ""
            return False, "Access denied. A keycard is required."

        elif level in (SecurityLevel.KEYCARD_HIGH.value,
                       SecurityLevel.KEYCARD_HIGH_PIN.value):
            if has_high_card:
                return True, ""
            if has_low_card:
                return False, "Access denied. High-security clearance required."
            return False, "Access denied. A high-security keycard is required."

        return False, "Access denied."

    def _card_swipe_response(self, door, action: str, pending_move: str = None, panel=None) -> dict:
        """
        Build the card_swipe response that triggers the 8s wait.
        action: 'unlock' or 'lock' — tells the swipe endpoint what to do after.
        panel — the SecurityPanel on the player's side; security level read from panel.
        """
        level = panel.security_level.value if panel else 0
        needs_pin = level == SecurityLevel.KEYCARD_HIGH_PIN.value
        return {
            'action_type': 'card_swipe',
            'lock_input': True,
            'real_seconds': CARD_SWIPE_REAL_SECONDS,
            'room_changed': False,
            'door_id': door.id,
            'door_action': action,
            'needs_pin': needs_pin,
            'security_level': level,
            'pending_move': pending_move,
        }

    def _panel_damaged_response(self, door, target_name: str, panel=None) -> dict:
        """
        Return the panel_damaged response — shows damaged panel image persistently,
        same pattern as door_locked. No hint about how to fix it.
        panel — the SecurityPanel on the player's side; security level read from panel.
        """
        level = panel.security_level.value if panel else 0
        return {
            'response': f"The {target_name} door access panel is damaged and will not respond.",
            'action_type': 'panel_damaged',
            'lock_input': False,
            'room_changed': False,
            'security_level': level,
        }

    def _panel_offline_response(self, door, target_name: str) -> dict:
        """
        Return the panel_offline response — no image, just a message.
        Used when the panel's room has no power.
        """
        return {
            'response': f"The {target_name} door access panel is unresponsive — it looks like it's offline.",
            'action_type': 'instant',
            'lock_input': False,
            'room_changed': False,
        }

    def _check_room_power(self, room_id: str) -> bool:
        """Check if a room has power via the electrical system."""
        es = game_manager.electrical_system
        if not es:
            return True  # No electrical system — assume powered
        return es.check_room_power(room_id)

    @staticmethod
    def _instant(message: str, room_changed: bool = False) -> dict:
        return {
            'response':     message,
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': room_changed,
        }
