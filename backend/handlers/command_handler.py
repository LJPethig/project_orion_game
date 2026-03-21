# backend/handlers/command_handler.py
"""
CommandHandler — central verb registry.
Routes player commands to the appropriate sub-handler.
Uses longest-match on verbs (same pattern as Dark Star).
"""

from backend.handlers.movement_handler import MovementHandler
from backend.handlers.door_handler import DoorHandler


class CommandHandler:

    def __init__(self):
        self._movement = MovementHandler()
        self._door     = DoorHandler()

        self.commands = {
            # Movement
            'enter':  self._movement.handle,
            'go':     self._movement.handle,
            'move':   self._movement.handle,
            # Door control
            'unlock': self._door.handle_unlock,
            'lock':   self._door.handle_lock,
            'close':  self._door.handle_close,
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
