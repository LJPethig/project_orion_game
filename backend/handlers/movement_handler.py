# backend/handlers/movement_handler.py
"""
MovementHandler — processes movement commands (enter, go, move).
Door states:
  - No door / open door: move freely
  - Closed unlocked door: open, move through, close behind
  - Locked door: card swipe required (8s wait), PIN if level 3
  - Broken panel: door frozen in current state
"""

from backend.models.game_manager import game_manager
from backend.models.door import SecurityLevel
from config import CARD_SWIPE_REAL_SECONDS


class MovementHandler:

    def handle(self, args: str) -> dict:
        """
        Attempt to move the player to a new room.
        Returns a standard command response dict.
        """
        if not args:
            return self._response("Where do you want to go?")

        target       = args.strip().lower()
        current_room = game_manager.get_current_room()

        matched_exit = self._find_exit(current_room, target)
        if not matched_exit:
            return self._response("You can't go that way.")

        exit_data = current_room.exits[matched_exit]
        door      = exit_data.get('door')

        # ── No door — move freely ─────────────────────────────
        if not door:
            game_manager.set_current_room(exit_data['target'])
            return self._response(
                f"You enter {game_manager.get_current_room().name}.",
                room_changed=True
            )

        # ── Open door — move freely ───────────────────────────
        if door.door_open:
            game_manager.set_current_room(exit_data['target'])
            return self._response(
                f"You enter {game_manager.get_current_room().name}.",
                room_changed=True
            )

        # ── Locked door — card swipe required ─────────────────
        if door.door_locked:
            panel = door.get_panel_for_room(current_room.id)
            has_card, card_msg = self._check_card(door, panel)
            if not has_card:
                return self._response(card_msg)

            target_room   = game_manager.ship.get_room(exit_data['target'])
            target_name   = target_room.name if target_room else exit_data['target']
            needs_pin     = door.security_level == SecurityLevel.KEYCARD_HIGH_PIN.value

            return {
                'response':       f"The entrance to {target_name} is locked. You swipe the access panel.",
                'action_type':    'card_swipe',
                'lock_input':     True,
                'real_seconds':   CARD_SWIPE_REAL_SECONDS,
                'room_changed':   False,
                'pending_move':   exit_data['target'],
                'needs_pin':      needs_pin,
                'door_id':        door.id,
                'security_level': door.security_level,
            }

        # ── Closed unlocked door — open, move, close ──────────
        door.open()
        game_manager.set_current_room(exit_data['target'])
        new_room = game_manager.get_current_room()
        door.close()
        return self._response(
            f"You open the door and enter {new_room.name}. The door closes behind you.",
            room_changed=True
        )

    def _check_card(self, door, panel) -> tuple[bool, str]:
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

    def _find_exit(self, room, target: str):
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

    @staticmethod
    def _response(message: str, room_changed: bool = False) -> dict:
        return {
            'response':     message,
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': room_changed,
        }
