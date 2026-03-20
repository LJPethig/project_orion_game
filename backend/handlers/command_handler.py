# backend/handlers/command_handler.py
"""
CommandHandler — central verb registry.
Routes player commands to the appropriate sub-handler.
Uses longest-match on verbs (same pattern as Dark Star).
Grows as new commands are added — each new handler registers its verbs here.
"""

from backend.handlers.movement_handler import MovementHandler


class CommandHandler:

    def __init__(self):
        # Verb registry — longest match wins
        # Format: 'verb' → (handler_instance, method_name)
        self._movement = MovementHandler()

        self.commands = {
            'enter': self._movement.handle,
            'go':    self._movement.handle,
            'move':  self._movement.handle,
        }

    def process(self, raw: str) -> dict:
        """
        Process a raw command string from the player.
        Returns a standard response dict.
        """
        cmd = raw.strip().lower()
        if not cmd:
            return self._unknown('')

        words = cmd.split()

        # Longest-match: try from full string down to first word
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
