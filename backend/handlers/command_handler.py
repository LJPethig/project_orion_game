# backend/handlers/command_handler.py
"""
CommandHandler — central verb registry.
Routes player commands to the appropriate sub-handler.
Uses longest-match on verbs (same pattern as Dark Star).
"""

from backend.handlers.movement_handler import MovementHandler
from backend.handlers.door_handler import DoorHandler
from backend.handlers.repair_handler import RepairHandler
from backend.handlers.item_handler import ItemHandler


class CommandHandler:

    def __init__(self):
        self._movement = MovementHandler()
        self._door     = DoorHandler()
        self._repair   = RepairHandler()
        self._item     = ItemHandler()

        self.commands = {
            # Movement
            'enter':             self._movement.handle,
            'go':                self._movement.handle,
            'move':              self._movement.handle,
            # Door control
            'open':              self._door.handle_open,
            'unlock':            self._door.handle_unlock,
            'lock':              self._door.handle_lock,
            'close':             self._door.handle_close,
            # Repair
            'repair panel':      self._repair.handle,
            'repair':            self._repair.handle,
            # Items
            'take':              self._item.handle_take,
            'get':               self._item.handle_take,
            'pick up':           self._item.handle_take,
            'drop':              self._item.handle_drop,
            'debug_inventory':   self._item.handle_debug_inventory,
        }

    def process(self, raw: str) -> dict:
        cmd = raw.strip().lower()
        if not cmd:
            return self._unknown('')

        words = cmd.split()

        for i in range(len(words), 0, -1):
            verb = ' '.join(words[:i])
            if verb in self.commands:
                args = ' '.join(words[i:])
                return self.commands[verb](args)

        return self._unknown(cmd)

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
