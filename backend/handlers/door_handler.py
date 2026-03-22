# backend/handlers/door_handler.py
"""
DoorHandler — open, close, lock, unlock commands.

open <room>   — opens a closed door (instant); card swipe if locked, player stays
close <room>  — closes an open door (instant, no card)
lock <room>   — card swipe (+ PIN if level 3), door locks, player stays
unlock <room> — card swipe (+ PIN if level 3), door unlocks and opens, player stays
"""

from backend.models.game_manager import game_manager
from backend.handlers.base_handler import BaseHandler


class DoorHandler(BaseHandler):

    def handle_open(self, args: str) -> dict:
        """Open a closed door — instant if unlocked, card swipe if locked."""
        if not args:
            return self._instant("Open which door?")

        door, exit_data, error = self._get_door(args.strip().lower())
        if error:
            return self._instant(error)

        if not door:
            return self._instant("There is no door there.")

        target_room = game_manager.ship.get_room(exit_data['target'])
        target_name = target_room.name if target_room else exit_data['target']

        panel_response = self._check_panel(door, target_name)
        if panel_response:
            return panel_response

        if door.door_open:
            return self._instant(f"The {target_name} door is already open.")

        # Locked — requires card swipe
        if door.door_locked:
            has_card, card_msg = self._check_card(door)
            if not has_card:
                return self._instant(card_msg)
            result = self._card_swipe_response(door, action='open', pending_move=None)
            result['response'] = f"You swipe the access panel to {target_name}."
            return result

        # Closed but unlocked — open instantly
        door.open()
        result = self._instant(f"You open the door to {target_name}.")
        result['door_image'] = 'open'
        return result

    def handle_unlock(self, args: str) -> dict:
        """Unlock a locked door — card swipe (+ PIN if level 3), player stays."""
        if not args:
            return self._instant("Unlock which door?")

        door, exit_data, error = self._get_door(args.strip().lower())
        if error:
            return self._instant(error)

        if not door:
            return self._instant("There is no door there.")

        target_room = game_manager.ship.get_room(exit_data['target'])
        target_name = target_room.name if target_room else exit_data['target']

        panel_response = self._check_panel(door, target_name)
        if panel_response:
            return panel_response

        if door.door_open:
            return self._instant(f"The {target_name} door is already open.")

        if not door.door_locked:
            return self._instant(f"The {target_name} door is not locked.")

        has_card, card_msg = self._check_card(door)
        if not has_card:
            return self._instant(card_msg)

        result = self._card_swipe_response(door, action='unlock', pending_move=None)
        result['response'] = f"You swipe the access panel to {target_name}."
        return result

    def handle_lock(self, args: str) -> dict:
        """Lock a closed or open door — card swipe (+ PIN if level 3), player stays."""
        if not args:
            return self._instant("Lock which door?")

        door, exit_data, error = self._get_door(args.strip().lower())
        if error:
            return self._instant(error)

        if not door:
            return self._instant("There is no door there.")

        target_room = game_manager.ship.get_room(exit_data['target'])
        target_name = target_room.name if target_room else exit_data['target']

        panel_response = self._check_panel(door, target_name)
        if panel_response:
            return panel_response

        if door.door_locked:
            return self._instant(f"The {target_name} door is already locked.")

        has_card, card_msg = self._check_card(door)
        if not has_card:
            return self._instant(card_msg)

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

        target_room = game_manager.ship.get_room(exit_data['target'])
        target_name = target_room.name if target_room else exit_data['target']

        panel_response = self._check_panel(door, target_name)
        if panel_response:
            return panel_response

        if door.door_locked:
            return self._instant(f"The {target_name} door is locked — it is already closed.")

        if not door.door_open:
            return self._instant(f"The {target_name} door is already closed.")

        door.close()
        result = self._instant(f"You close the door to {target_name}.")
        result['door_image'] = 'closed'
        return result

    def _check_panel(self, door, target_name: str) -> dict | None:
        """
        Return a panel_damaged response dict if the panel on the player's side
        is broken. Returns None if operational (or absent).
        """
        current_room = game_manager.get_current_room()
        panel = door.get_panel_for_room(current_room.id)
        if panel and panel.is_broken:
            return self._panel_damaged_response(door, target_name)
        return None

    def _get_door(self, target: str):
        """
        Find exit and door matching the target string.
        Returns (door, exit_data, error_message).
        """
        current_room = game_manager.get_current_room()
        matched_exit = self._find_exit(current_room, target)

        if not matched_exit:
            return None, None, "There's no exit that way."

        exit_data = current_room.exits[matched_exit]
        door      = exit_data.get('door')
        return door, exit_data, None
