# backend/handlers/movement_handler.py
"""
MovementHandler — processes movement commands (enter, go, move).
Checks door state before allowing movement:
  - No door: move freely
  - Open door: move freely, no message about door
  - Closed door: open it, move through, close it behind — one seamless action
  - Locked door: blocked, explain why
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

        target       = args.strip().lower()
        current_room = game_manager.get_current_room()

        # Find a matching exit
        matched_exit = self._find_exit(current_room, target)
        if not matched_exit:
            return self._response("You can't go that way.")

        exit_data = current_room.exits[matched_exit]
        door      = exit_data.get('door')

        # ── Door state checks ────────────────────────────────
        if door:
            if door.door_locked:
                return self._response(
                    f"The door is locked. You need a keycard to proceed."
                )

            if not door.door_open:
                # Closed but unlocked — open it, move through, close behind
                door.open()
                game_manager.set_current_room(exit_data['target'])
                new_room = game_manager.get_current_room()
                door.close()
                return self._response(
                    f"You open the door and enter {new_room.name}. The door closes behind you.",
                    room_changed=True
                )

        # ── Open door or no door — move freely ───────────────
        game_manager.set_current_room(exit_data['target'])
        new_room = game_manager.get_current_room()
        return self._response(
            f"You enter {new_room.name}.",
            room_changed=True
        )

    def _find_exit(self, room, target: str):
        """
        Find a matching exit key in the room by:
        1. Exact exit key match (e.g. 'engineering')
        2. Label match (e.g. 'Engineering')
        3. Shortcut match (e.g. 'eng')
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

    @staticmethod
    def _response(message: str, room_changed: bool = False) -> dict:
        return {
            'response':     message,
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': room_changed,
        }
