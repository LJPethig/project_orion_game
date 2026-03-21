# backend/handlers/door_handler.py
"""
DoorHandler — unlock, lock, close commands.

unlock <room> — card swipe (+ PIN if level 3), door opens, player walks through
lock <room>   — card swipe (+ PIN if level 3), door locks, player stays
close <room>  — instant, no card needed, closes an open door
"""

from backend.models.game_manager import game_manager
from backend.handlers.base_handler import BaseHandler


class DoorHandler(BaseHandler):

    def handle_unlock(self, args: str) -> dict:
        """Unlock and walk through a locked door."""
        if not args:
            return self._instant("Unlock which door?")

        door, exit_data, error = self._get_door(args.strip().lower())
        if error:
            return self._instant(error)

        if not door:
            return self._instant("There is no door there.")

        if not door.door_locked:
            if door.door_open:
                return self._instant("The door is already open.")
            return self._instant("The door is not locked.")

        has_card, card_msg = self._check_card(door)
        if not has_card:
            return self._instant(card_msg)

        target_room = game_manager.ship.get_room(exit_data['target'])
        target_name = target_room.name if target_room else exit_data['target']

        result = self._card_swipe_response(door, action='unlock', pending_move=exit_data['target'])
        result['response'] = f"You swipe the access panel to {target_name}."
        return result

    def handle_lock(self, args: str) -> dict:
        """Lock a closed or open door."""
        if not args:
            return self._instant("Lock which door?")

        door, exit_data, error = self._get_door(args.strip().lower())
        if error:
            return self._instant(error)

        if not door:
            return self._instant("There is no door there.")

        if door.door_locked:
            return self._instant("The door is already locked.")

        has_card, card_msg = self._check_card(door)
        if not has_card:
            return self._instant(card_msg)

        target_room = game_manager.ship.get_room(exit_data['target'])
        target_name = target_room.name if target_room else exit_data['target']

        result = self._card_swipe_response(door, action='lock', pending_move=None)
        result['response'] = f"You swipe the access panel to {target_name}."
        return result

    def handle_close(self, args: str) -> dict:
        """Close an open door — no card required."""
        if not args:
            return self._instant("Close which door?")

        door, exit_data, error = self._get_door(args.strip().lower())
        if error:
            return self._instant(error)

        if not door:
            return self._instant("There is no door there.")

        if door.door_locked:
            return self._instant("The door is locked — it is already closed.")

        if not door.door_open:
            return self._instant("The door is already closed.")

        door.close()
        target_room = game_manager.ship.get_room(exit_data['target'])
        target_name = target_room.name if target_room else exit_data['target']
        return self._instant(f"You close the door to {target_name}.")

    def _get_door(self, target: str):
        """
        Find exit and door matching the target string.
        Returns (door, exit_data, error_message).
        error_message is None on success.
        """
        current_room = game_manager.get_current_room()
        matched_exit = self._find_exit(current_room, target)

        if not matched_exit:
            return None, None, "There's no exit that way."

        exit_data = current_room.exits[matched_exit]
        door      = exit_data.get('door')
        return door, exit_data, None
