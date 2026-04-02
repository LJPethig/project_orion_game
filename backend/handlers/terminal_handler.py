# backend/handlers/terminal_handler.py
"""
TerminalHandler — access terminal command.

access terminal         — open terminal in current room (clarification if multiple)
access <terminal name>  — open specific terminal by keyword
"""

from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager
from backend.models.interactable import Terminal


class TerminalHandler(BaseHandler):

    def handle_terminal_access(self, args: str) -> dict:
        room      = game_manager.get_current_room()
        terminals = [obj for obj in room.objects if isinstance(obj, Terminal)]

        if not terminals:
            return self._instant("There is no terminal here.")

        # Resolve target terminal
        target = args.strip().lower()
        if target:
            matched = next(
                (t for t in terminals if t.id == target or t.matches(target)),
                None
            )
            if not matched:
                return self._instant(f"There is no '{args.strip()}' here.")
        elif len(terminals) == 1:
            matched = terminals[0]
        else:
            # Multiple terminals — clarification
            options = [
                {'label': t.name, 'command': f"access {t.id}"}
                for t in terminals
            ]
            return {
                'response':     'Which terminal do you want to access?',
                'action_type':  'clarification_required',
                'lock_input':   False,
                'room_changed': False,
                'options':      options,
            }

        if not self._check_room_power(room.id):
            return self._instant(f"The {matched.name} is unresponsive — it looks like it's offline.")

        return {
            'response': f"You access the {matched.name}.",
            'action_type': 'terminal_open',
            'lock_input': False,
            'room_changed': False,
            'terminal_id': matched.id,
            'terminal_name': matched.name,
            'terminal_type': matched.terminal_type,
            'menu': matched.menu,
        }
