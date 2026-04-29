# backend/handlers/movement_handler.py
"""
MovementHandler — enter, go, move commands.
  - No door / open door: move freely
  - Closed door: open, move through, close behind — seamless
  - Locked door: show closed hatch image + locked message, no auto-swipe
                 Player must type 'unlock <room>' to proceed
"""

from backend.models.game_manager import game_manager
from backend.handlers.base_handler import BaseHandler


class MovementHandler(BaseHandler):

    def handle(self, args: str) -> dict:
        if not args:
            return self._instant("Where do you want to go?")

        target       = args.strip().lower()
        current_room = game_manager.get_current_room()

        matched_exit = self._find_exit(current_room, target)
        if not matched_exit:
            return self._instant("You can't go that way.")

        exit_data = current_room.exits[matched_exit]
        door      = exit_data.get('door')

        # ── No door — move freely ─────────────────────────────
        if not door:
            game_manager.set_current_room(exit_data['target'])
            return self._instant(
                f"You enter the {game_manager.get_current_room().name}.",
                room_changed=True
            )

        # ── Open door — broken panel? Still pass (frozen open) ──
        if door.door_open:
            panel = door.get_panel_for_room(current_room.id)
            if panel and panel.is_broken:
                game_manager.set_current_room(exit_data['target'])
                new_room = game_manager.get_current_room()
                return self._instant(
                    f"You pass through the open door into the {new_room.name}.",
                    room_changed=True
                )
            game_manager.set_current_room(exit_data['target'])
            return self._instant(
                f"You enter the {game_manager.get_current_room().name}.",
                room_changed=True
            )

        # ── Closed/locked door — check power then panel damage ──
        target_room = game_manager.ship.get_room(exit_data['target'])
        target_name = target_room.name if target_room else exit_data['target']
        if not self._check_room_power(current_room.id):
            return self._panel_offline_response(door, target_name)
        panel = door.get_panel_for_room(current_room.id)
        if panel and panel.is_broken:
            return self._panel_damaged_response(door, target_name, panel=panel)

        # ── Locked door — show locked image, tell player ──────
        if door.door_locked:
            target_room = game_manager.ship.get_room(exit_data['target'])
            target_name = target_room.name if target_room else exit_data['target']
            return {
                'response': f"The door to the {target_name} is locked.",
                'action_type': 'door_locked',
                'lock_input': False,
                'room_changed': False,
                'security_level': panel.security_level.value if panel else 0,
            }

        # ── Closed unlocked door — open, move, close if dest panel is functional ──
        door.open()
        game_manager.set_current_room(exit_data['target'])
        new_room = game_manager.get_current_room()
        dest_panel = door.get_panel_for_room(new_room.id)
        dest_powered = self._check_room_power(new_room.id)
        dest_panel_ok = dest_powered and (dest_panel is None or not dest_panel.is_broken)
        if dest_panel_ok:
            door.close()
            return self._instant(
                f"You open the door and enter the {new_room.name}. The door closes behind you.",
                room_changed=True
            )
        return self._instant(
            f"You open the door and enter the {new_room.name}. The door does not autoclose — the access panel on this side is unresponsive.",
            room_changed=True
        )
