# backend/handlers/container_handler.py
"""
ContainerHandler — open, close, look in, take from, put in/on commands.

open <container>              — open a closed storage unit
close <container>             — close an open storage unit
look in <container>           — list contents of an open storage unit
take <item> from <container>  — take an item from an open storage unit
put <item> in <container>     — put an inventory item into an open storage unit
place <item> in <container>   — alias for put in
put <item> on <surface>       — put an inventory item onto a surface
place <item> on <surface>     — alias for put on
take <item> from <surface>    — take an item from a surface (by ID or keyword)
"""

from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager
from backend.models.interactable import StorageUnit, Surface, PortableItem


class ContainerHandler(BaseHandler):

    def handle_open(self, args: str) -> dict:
        if not args:
            return self._instant("Open what?")

        unit = self._find_storage_unit(args.strip().lower())
        if not unit:
            return None  # Signal to caller: no container found, try door

        if unit.is_open:
            return self._instant(f"The {unit.name} is already open.")

        unit.is_open = True
        response = f"You open the {unit.name}."
        if unit.open_description:
            response += f" {unit.open_description}"

        result = self._instant(response)
        result['room_contents_changed'] = True
        return result

    def handle_close(self, args: str) -> dict:
        if not args:
            return self._instant("Close what?")

        unit = self._find_storage_unit(args.strip().lower())
        if not unit:
            return None  # Signal to caller: no container found, try door

        if not unit.is_open:
            return self._instant(f"The {unit.name} is already closed.")

        unit.is_open = False
        result = self._instant(f"You close the {unit.name}.")
        result['room_contents_changed'] = True
        return result

    def handle_look_in(self, args: str) -> dict:
        if not args:
            return self._instant("Look in what?")

        unit = self._find_storage_unit(args.strip().lower())
        if not unit:
            return self._instant(f"There is no '{args.strip()}' here.")

        if not unit.is_open:
            return self._instant(f"The {unit.name} is closed.")

        if not unit.contents:
            return self._instant(f"The {unit.name} is empty.")

        names = [item.display_name() for item in unit.contents]
        return self._instant(f"Inside the {unit.name} you see: {', '.join(names)}.")

    def handle_take_from(self, args: str) -> dict:
        """Syntax: take <item> from <container or surface>"""
        if not args or ' from ' not in args.lower():
            return self._instant("Take what from where? Try 'take <item> from <container>'.")

        parts     = args.lower().split(' from ', 1)
        item_name = parts[0].strip()
        cont_name = parts[1].strip()

        # Try container first
        unit = self._find_storage_unit(cont_name)
        if unit:
            if not unit.is_open:
                return self._instant(f"The {unit.name} is closed.")
            item = next(
                (i for i in unit.contents if i.instance_id == item_name or i.id == item_name or i.matches(item_name)),
                None
            )
            if not item:
                return self._instant(f"There is no '{item_name}' in the {unit.name}.")
            success, msg = game_manager.player.add_to_inventory(item)
            if not success:
                return self._instant(msg)
            unit.remove_item(item)
            result = self._instant(f"You take the {item.display_name()} from the {unit.name}.")
            result['room_contents_changed'] = True
            return result

        # Try surface
        surface = self._find_surface(cont_name)
        if surface:
            item = next(
                (i for i in surface.contents if
                 i.instance_id == item_name or i.id == item_name or i.matches(item_name)),
                None
            )
            if not item:
                return self._instant(f"There is no '{item_name}' on the {surface.name}.")
            success, msg = game_manager.player.add_to_inventory(item)
            if not success:
                return self._instant(msg)
            surface.remove_item(item)
            result = self._instant(f"You take the {item.display_name()} from the {surface.name}.")
            result['room_contents_changed'] = True
            return result

        # Try floor
        if cont_name in ('floor', 'the floor', 'ground'):
            room = game_manager.get_current_room()
            item = next(
                (i for i in room.floor if
                 i.instance_id == item_name or i.id == item_name or i.matches(item_name)),
                None
            )
            if not item:
                return self._instant(f"There is no '{item_name}' on the floor.")
            success, msg = game_manager.player.add_to_inventory(item)
            if not success:
                return self._instant(msg)
            room.floor.remove(item)
            result = self._instant(f"You take the {item.display_name()} from the floor.")
            result['room_contents_changed'] = True
            return result

        return self._instant(f"There is no '{cont_name}' here.")

    def handle_put_in(self, args: str) -> dict:
        """Syntax: put/place <item> in <container>"""
        if not args or ' in ' not in args.lower():
            return self._instant("Put what in where? Try 'put <item> in <container>'.")

        parts     = args.lower().split(' in ', 1)
        item_name = parts[0].strip()
        cont_name = parts[1].strip()

        unit = self._find_storage_unit(cont_name)
        if not unit:
            return self._instant(f"There is no '{cont_name}' here.")

        if not unit.is_open:
            return self._instant(f"The {unit.name} is closed.")

        item = next(
            (i for i in game_manager.player.get_inventory() if
             i.instance_id == item_name or i.id == item_name or i.matches(item_name)),
            None
        )

        if not item:
            return self._instant(f"You are not carrying a '{item_name}'.")

        if not unit.add_item(item):
            return self._instant(f"The {unit.name} is too full to hold the {item.name}.")

        game_manager.player.remove_from_inventory(item)
        result = self._instant(f"You put the {item.display_name()} in the {unit.name}.")
        result['room_contents_changed'] = True
        return result

    def handle_put_on(self, args: str) -> dict:
        """Syntax: put/place <item> on <surface>"""
        if not args or ' on ' not in args.lower():
            return self._instant("Put what on where? Try 'put <item> on <surface>'.")

        parts      = args.lower().split(' on ', 1)
        item_name  = parts[0].strip()
        surf_name  = parts[1].strip()

        surface = self._find_surface(surf_name)
        if not surface:
            return self._instant(f"There is no '{surf_name}' here.")

        item = next(
            (i for i in game_manager.player.get_inventory() if
             i.instance_id == item_name or i.id == item_name or i.matches(item_name)),
            None
        )

        if not item:
            return self._instant(f"You are not carrying a '{item_name}'.")

        game_manager.player.remove_from_inventory(item)
        surface.add_item(item)
        result = self._instant(f"You put the {item.display_name()} on the {surface.name}.")
        result['room_contents_changed'] = True
        return result

    # ── Helpers ──────────────────────────────────────────────

    @staticmethod
    def _find_storage_unit(target: str) -> StorageUnit | None:
        """Find a StorageUnit in the current room by ID or keyword match."""
        room = game_manager.get_current_room()
        for obj in room.objects:
            if isinstance(obj, StorageUnit):
                if obj.id == target or obj.matches(target):
                    return obj
        return None

    @staticmethod
    def _find_surface(target: str) -> Surface | None:
        """Find a Surface in the current room by ID or keyword match."""
        room = game_manager.get_current_room()
        for obj in room.objects:
            if isinstance(obj, Surface):
                if obj.id == target or obj.matches(target):
                    return obj
        return None
