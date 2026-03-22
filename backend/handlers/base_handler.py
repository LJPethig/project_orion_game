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
        Returns the exit key if found, None otherwise.
        """
        for exit_key, exit_data in room.exits.items():
            if target == exit_key.lower():
                return exit_key
            if target == exit_data.get('label', '').lower():
                return exit_key
            shortcuts = exit_data.get('shortcuts', [])
            if isinstance(shortcuts, list):
                if target in [s.lower() for s in shortcuts]:
                    return exit_key
        return None

    def _check_card(self, door) -> tuple[bool, str]:
        """Check if the player has the required card for this door."""
        level         = door.security_level
        has_low_card  = game_manager.has_low_sec_card
        has_high_card = game_manager.has_high_sec_card

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

    def _card_swipe_response(self, door, action: str, pending_move: str = None) -> dict:
        """
        Build the card_swipe response that triggers the 8s wait.
        action: 'unlock' or 'lock' — tells the swipe endpoint what to do after.
        """
        needs_pin = door.security_level == SecurityLevel.KEYCARD_HIGH_PIN.value
        return {
            'action_type':    'card_swipe',
            'lock_input':     True,
            'real_seconds':   CARD_SWIPE_REAL_SECONDS,
            'room_changed':   False,
            'door_id':        door.id,
            'door_action':    action,
            'needs_pin':      needs_pin,
            'security_level': door.security_level,
            'pending_move':   pending_move,
        }

    def _panel_damaged_response(self, door, target_name: str) -> dict:
        """
        Return the panel_damaged response — shows damaged panel image persistently,
        same pattern as door_locked. No hint about how to fix it.
        """
        return {
            'response':       f"The {target_name} door access panel is damaged and will not respond.",
            'action_type':    'panel_damaged',
            'lock_input':     False,
            'room_changed':   False,
            'security_level': door.security_level,
        }

    @staticmethod
    def _instant(message: str, room_changed: bool = False) -> dict:
        return {
            'response':     message,
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': room_changed,
        }
