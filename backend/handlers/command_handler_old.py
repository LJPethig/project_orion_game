# backend/handlers/command_handler.py
"""
CommandHandler — central verb registry.
Routes player commands to the appropriate sub-handler.
Uses longest-match on verbs (same pattern as Dark Star).

open/close routing:
  1. Try container first — if found, use ContainerHandler
  2. Try door second — if found, use DoorHandler
  3. If both match — ambiguity message (Phase 13d)
  4. If neither — "You can't open/close that"
"""

from backend.handlers.movement_handler import MovementHandler
from backend.handlers.door_handler import DoorHandler
from backend.handlers.repair_handler import RepairHandler
from backend.handlers.item_handler import ItemHandler
from backend.handlers.container_handler import ContainerHandler
from backend.handlers.equip_handler import EquipHandler


class CommandHandler:

    def __init__(self):
        self._movement   = MovementHandler()
        self._door       = DoorHandler()
        self._repair     = RepairHandler()
        self._item       = ItemHandler()
        self._container  = ContainerHandler()
        self._equip      = EquipHandler()

        self.commands = {
            # Movement
            'enter':             self._movement.handle,
            'go':                self._movement.handle,
            'move':              self._movement.handle,
            # open/close — routed through disambiguation methods
            'open':              self._route_open,
            'close':             self._route_close,
            # Door only
            'lock':              self._door.handle_lock,
            'unlock':            self._door.handle_unlock,
            # Repair
            'repair panel':      self._repair.handle,
            'repair':            self._repair.handle,
            # Items
            'take':              self._item.handle_take,
            'get':               self._item.handle_take,
            'pick up':           self._item.handle_take,
            'drop':              self._item.handle_drop,
            'debug_inventory':   self._item.handle_debug_inventory,
            # Equip/unequip
            'wear':              self._equip.handle_wear,
            'equip':             self._equip.handle_wear,
            'remove':            self._equip.handle_remove,
            'take off':          self._equip.handle_remove,
            'unequip':           self._equip.handle_remove,
            # Container specific
            'look in':           self._container.handle_look_in,
            'take from':         self._container.handle_take_from,
            'put in':            self._container.handle_put_in,
            'place in':          self._container.handle_put_in,
            'put on':            self._container.handle_put_on,
            'place on':          self._container.handle_put_on,
        }

    def _route_open(self, args: str) -> dict:
        """
        Route 'open' to container or door handler.
        Container takes priority — returns None if no match, then door is tried.
        """
        if not args:
            return self._unknown_action("Open what?")

        container_result = self._container.handle_open(args)
        if container_result is not None:
            return container_result

        return self._door.handle_open(args)

    def _route_close(self, args: str) -> dict:
        """
        Route 'close' to container or door handler.
        Container takes priority — returns None if no match, then door is tried.
        """
        if not args:
            return self._unknown_action("Close what?")

        container_result = self._container.handle_close(args)
        if container_result is not None:
            return container_result

        return self._door.handle_close(args)

    def process(self, raw: str) -> dict:
        cmd = raw.strip().lower()
        if not cmd:
            return self._unknown('')

        # Special handling for preposition commands before verb matching
        if ' from ' in cmd and cmd.startswith('take '):
            parts = cmd.split(' from ', 1)
            return self._container.handle_take_from(
                f"{parts[0][5:].strip()} from {parts[1].strip()}"
            )

        if ' in ' in cmd and (cmd.startswith('put ') or cmd.startswith('place ')):
            prefix_len = 4 if cmd.startswith('put ') else 6
            parts = cmd.split(' in ', 1)
            return self._container.handle_put_in(
                f"{parts[0][prefix_len:].strip()} in {parts[1].strip()}"
            )

        if ' on ' in cmd and (cmd.startswith('put ') or cmd.startswith('place ')):
            prefix_len = 4 if cmd.startswith('put ') else 6
            parts = cmd.split(' on ', 1)
            return self._container.handle_put_on(
                f"{parts[0][prefix_len:].strip()} on {parts[1].strip()}"
            )

        words = cmd.split()

        for i in range(len(words), 0, -1):
            verb = ' '.join(words[:i])
            if verb in self.commands:
                args = ' '.join(words[i:])
                return self.commands[verb](args)

        return self._unknown(cmd)

    @staticmethod
    def _unknown_action(msg: str) -> dict:
        return {
            'response':     msg,
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': False,
        }

    @staticmethod
    def _unknown(cmd: str) -> dict:
        msg = f"Unknown command: '{cmd}'." if cmd else "Enter a command."
        return {
            'response':     msg,
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': False,
        }


# Single shared instance
command_handler = CommandHandler()
