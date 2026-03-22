# backend/handlers/item_handler.py
"""
ItemHandler — take, drop, debug_inventory commands.

take <item>         — take a portable item from the current room floor
drop <item>         — drop an inventory item onto the current room floor
debug_inventory     — dump player inventory to response panel
"""

from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager
from backend.models.interactable import PortableItem, StorageUnit


class ItemHandler(BaseHandler):

    def handle_take(self, args: str) -> dict:
        if not args:
            return self._instant("Take what?")

        target = args.strip().lower()
        room   = game_manager.get_current_room()

        item = self._find_portable_in_room(room, target)
        if not item:
            return self._instant(f"You don't see a '{args.strip()}' here.")

        success, msg = game_manager.player.add_to_inventory(item)
        if not success:
            return self._instant(msg)

        room.remove_object(item.id)
        result = self._instant(msg)
        result['room_contents_changed'] = True
        return result

    def handle_drop(self, args: str) -> dict:
        if not args:
            return self._instant("Drop what?")

        target = args.strip().lower()
        item = next(
            (i for i in game_manager.player.get_inventory() if i.matches(target)),
            None
        )

        if not item:
            return self._instant(f"You are not carrying a '{args.strip()}'.")

        game_manager.player.remove_from_inventory(item)
        game_manager.get_current_room().add_object(item)
        result = self._instant(f"You drop the {item.name}.")
        result['room_contents_changed'] = True
        return result

    def handle_debug_inventory(self, args: str) -> dict:
        return self._instant(game_manager.player.debug_str())

    # ── Helpers ──────────────────────────────────────────────

    @staticmethod
    def _find_portable_in_room(room, target: str) -> PortableItem | None:
        """
        Find a takeable item on the room floor matching target.
        Ignores fixed objects and storage units.
        """
        for obj in room.objects:
            if isinstance(obj, PortableItem) and not isinstance(obj, StorageUnit):
                if obj.takeable and obj.matches(target):
                    return obj
        return None
