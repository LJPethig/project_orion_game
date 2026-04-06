# backend/handlers/equip_handler.py
"""
EquipHandler — wear/equip and remove/unequip commands.

wear <item>    — equip an item from inventory into its designated slot
equip <item>   — alias for wear
remove <item>  — unequip an item, returns to inventory or drops if too heavy
take off <item> — alias for remove
unequip <item> — alias for remove
"""

from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager
from backend.models.interactable import Surface


class EquipHandler(BaseHandler):

    def handle_wear(self, args: str) -> dict:
        if not args:
            return self._instant("Wear what?")

        target = args.strip().lower()
        item = next(
            (i for i in game_manager.player.get_inventory() if
             i.instance_id == target or i.id == target or i.matches(target)),
            None
        )

        if not item:
            return self._instant(f"You are not carrying a '{args.strip()}'.")

        success, msg = game_manager.player.equip(item)
        return self._instant(msg)

    def handle_remove(self, args: str) -> dict:
        if not args:
            return self._instant("Remove what?")

        target       = args.strip().lower()
        player       = game_manager.player
        current_room = game_manager.get_current_room()

        # Find matching equipped item
        matched_slot = None
        for slot in player.EQUIP_SLOTS:
            item = getattr(player, f"{slot}_slot")
            if item and (item.instance_id == target or item.id == target or item.matches(target)):
                matched_slot = slot
                break

        if not matched_slot:
            return self._instant(f"You are not wearing a '{args.strip()}'.")

        item = getattr(player, f"{matched_slot}_slot")

        # Try to add to inventory first
        success, msg = player.add_to_inventory(item)
        if success:
            setattr(player, f"{matched_slot}_slot", None)
            return self._instant(f"You remove the {item.name}.")

        # Too heavy for inventory — try surface, then floor
        setattr(player, f"{matched_slot}_slot", None)
        surfaces = [o for o in current_room.objects if isinstance(o, Surface)]
        if surfaces:
            import random
            surface = random.choice(surfaces)
            surface.add_item(item)
            result = self._instant(
                f"You remove the {item.name}, but you are carrying too much — "
                f"you leave it on the {surface.name}."
            )
        else:
            current_room.floor.append(item)
            result = self._instant(
                f"You remove the {item.name}, but you are carrying too much — "
                f"you drop it on the floor."
            )

        result['room_contents_changed'] = True
        return result
