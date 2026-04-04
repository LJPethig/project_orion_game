# backend/handlers/repair_handler.py
"""
RepairHandler — handles 'repair panel <target>' command.

Ported from Dark Star's repair_handler.py. Arcade dependencies stripped.
Repair is a timed action: 8s real, 30 game minutes.

Phase 11 uses magic repair — no diagnosis, no parts, no tools checked yet.
A debug flag (DEBUG_HAS_REPAIR_TOOL in config.py) gates the repair for now.
Real inventory checks replace this in Phase 12.

Flow:
  1. Player types 'repair panel [target]'
  2. Backend validates: panel exists, is broken, player has tool (debug flag)
  3. Returns action_type='repair_panel' with real_seconds, panel_id, damaged image path
  4. Frontend shows damaged panel image, locks input for 8s
  5. Frontend calls POST /api/command/repair_complete { panel_id }
  6. Backend marks panel not broken, advances time, returns instant result
"""

from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager
from config import REPAIR_REAL_SECONDS, DEBUG_HAS_REPAIR_TOOL


class RepairHandler(BaseHandler):

    def handle(self, args: str) -> dict:
        """
        Entry point for 'repair panel [target]'.
        CommandHandler registers 'repair panel' as the verb, so args is
        everything after that — typically a room name or empty.
        """
        current_room = game_manager.get_current_room()
        broken = game_manager.ship.get_broken_panels_in_room(current_room.id)

        if not broken:
            return self._instant("There are no damaged door access panels in this room.")

        # ── Check tool availability (debug flag for now) ──────
        if not DEBUG_HAS_REPAIR_TOOL:
            return self._instant(
                "You need a repair tool to fix this. "
                "A wrench or engineering kit would do."
            )

        # ── Resolve target ────────────────────────────────────
        target = args.strip().lower()

        # Strip noise words — if nothing remains, treat as no target
        noise = ['door access panel', 'access panel', 'door panel',
                 'access door', 'access', 'panel', 'hatch', 'door', 'doors']
        cleaned = target
        for word in sorted(noise, key=len, reverse=True):
            cleaned = cleaned.replace(word, '').strip()

        if not target or not cleaned:
            # Auto-select if only one broken panel in the room
            if len(broken) == 1:
                panel, door, exit_label = broken[0]
                return self._begin_repair(panel, door, exit_label)

            # Multiple — ask for clarification with clickable options
            options = [
                {'label': label, 'command': f"repair panel {label.lower()}"}
                for _, _, label in broken
            ]
            return {
                'response': f"There are {len(broken)} damaged door access panels in this room. Which do you want to repair?",
                'action_type': 'clarification_required',
                'lock_input': False,
                'room_changed': False,
                'options': options,
            }

        # Explicit target provided — find matching door/panel
        matched_exit = self._find_exit(current_room, target)
        if matched_exit:
            exit_data = current_room.exits[matched_exit]
            door = exit_data.get('door')
            if door:
                panel = door.get_panel_for_room(current_room.id)
                if panel and panel.is_broken:
                    target_room = game_manager.ship.get_room(door.get_other_room_id(current_room.id))
                    exit_label = exit_data.get('label') or (target_room.name if target_room else target)
                    return self._begin_repair(panel, door, exit_label)
                elif panel and not panel.is_broken:
                    target_room = game_manager.ship.get_room(door.get_other_room_id(current_room.id))
                    name = target_room.name if target_room else target
                    return self._instant(f"The {name} door access panel is not damaged.")

        return self._instant(f"No damaged door access panel to '{args.strip()}'.")

    def _begin_repair(self, panel, door, exit_label: str) -> dict:
        """
        Return the timed repair_panel response.
        Frontend handles the wait and calls /api/command/repair_complete.
        """
        return {
            'response':       f"Repairing door access panel to {exit_label}...",
            'action_type':    'repair_panel',
            'lock_input':     True,
            'real_seconds':   REPAIR_REAL_SECONDS,
            'room_changed':   False,
            'panel_id':       panel.panel_id,
            'door_id':        door.id,
            'security_level': door.security_level,
            'exit_label':     exit_label,
        }

