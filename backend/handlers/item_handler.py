# backend/handlers/item_handler.py
"""
ItemHandler — take, drop, debug_inventory commands.

take <item>         — take a portable item from room surfaces
drop <item>         — drop an inventory item onto a room surface
debug_inventory     — dump player inventory to response panel
"""

import random
from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager
from backend.models.interactable import PortableItem, StorageUnit, Surface


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

        self._remove_item_from_room(room, item)
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

        room    = game_manager.get_current_room()
        surface = self._find_drop_surface(room)
        if not surface:
            return self._instant("There is nowhere to put that here.")

        game_manager.player.remove_from_inventory(item)
        surface.add_item(item)
        result = self._instant(f"You put the {item.name} on the {surface.name}.")
        result['room_contents_changed'] = True
        return result

    def handle_debug_inventory(self, args: str) -> dict:
        return self._instant(game_manager.player.debug_str())

    # ── Helpers ──────────────────────────────────────────────

    @staticmethod
    def _find_portable_in_room(room, target: str) -> PortableItem | None:
        """Find a takeable item on room surfaces."""
        for obj in room.objects:
            if isinstance(obj, Surface):
                for item in obj.contents:
                    if item.id == target or item.matches(target):
                        return item
        return None

    @staticmethod
    def _remove_item_from_room(room, item: PortableItem) -> None:
        """Remove item from a surface. Warns if found loose on floor — should not happen."""
        for obj in room.objects:
            if isinstance(obj, Surface) and item in obj.contents:
                obj.remove_item(item)
                return
        print(f"Warning: item '{item.id}' found loose in room '{room.id}' — removing from floor")
        room.remove_object(item.id)

    @staticmethod
    def _find_drop_surface(room) -> Surface | None:
        """Return a randomly selected surface in the room, or None."""
        surfaces = [o for o in room.objects if isinstance(o, Surface)]
        return random.choice(surfaces) if surfaces else None
