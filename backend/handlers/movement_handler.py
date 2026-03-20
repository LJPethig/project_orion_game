# backend/handlers/movement_handler.py
"""
MovementHandler — processes movement commands (enter, go, move).
Phase 9: no door checks, no locks. If the exit exists, move there.
Door logic added in a later phase.
"""

from backend.models.game_manager import game_manager


class MovementHandler:

    def handle(self, args: str) -> dict:
        """
        Attempt to move the player to a new room.
        args: the destination string (e.g. "engineering", "rec room", "CH-1")
        Returns a standard command response dict.
        """
        if not args:
            return self._response("Where do you want to go?")

        target = args.strip().lower()
        current_room = game_manager.get_current_room()

        # Find a matching exit
        matched_exit = self._find_exit(current_room, target)

        if not matched_exit:
            return self._response("You can't go that way.")

        # Move the player
        room_id = current_room.exits[matched_exit]['target']
        game_manager.set_current_room(room_id)
        new_room = game_manager.get_current_room()

        return self._response(
            f"You enter {new_room.name}.",
            room_changed=True
        )

    def _find_exit(self, room, target: str) -> str | None:
        """
        Find a matching exit key in the room by:
        1. Exact exit key match (e.g. 'engineering')
        2. Label match (e.g. 'Engineering')
        3. Shortcut match (e.g. 'eng')
        Returns the exit key if found, None otherwise.
        """
        for exit_key, exit_data in room.exits.items():
            # Match on exit key
            if target == exit_key.lower():
                return exit_key

            # Match on label
            if target == exit_data.get('label', '').lower():
                return exit_key

            # Match on shortcuts
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
