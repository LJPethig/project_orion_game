# backend/handlers/storage_handler.py
"""
StorageHandler — handles store and retrieve commands.
Both commands are only valid in the storage room.
Interacts with game_manager.storage_manifest directly.
"""

import random

from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager

STORAGE_ROOM_ID = 'storage_room'

_STORE_RESPONSES = [
    "You place the {name} onto the intake bin. A robotic arm yanks it inside with a grinding noise. Hopefully it gets logged undamaged.",
    "You put the {name} onto the intake bin. A robotic arm drags it in. Another day, another chance corporate screws you on the logs.",
    "You drop the {name} onto the intake bin. Nothing happens. You give it a frustrated kick. The arm finally whirs to life and yanks the item inside with a grinding screech.",
]

_RETRIEVE_RESPONSES = [
    "After a few disconcerting grinding sounds, the {name} drops into the output bin, thankfully undamaged. You snatch it up before the company changes its mind.",
    "The {name} is unceremoniously dumped into the output bin. You grab it quickly.",
    "The {name} drops into the output bin coated in dirty lubricant. You sigh and pick it up. Another cleaning bill you'll never see reimbursed.",
]


class StorageHandler(BaseHandler):

    def handle_store(self, instance_id: str) -> dict:
        """Store a carried item in the automated storage facility."""
        if game_manager.current_room.id != STORAGE_ROOM_ID:
            return self._instant("There is no automated storage facility in this room.")

        if not instance_id:
            return self._instant("Store what?")

        item = next(
            (i for i in game_manager.player.get_inventory() if i.instance_id == instance_id),
            None
        )
        if not item:
            return self._instant("You're not carrying that.")

        name = item.display_name()
        game_manager.store_item(item)
        msg = random.choice(_STORE_RESPONSES).format(name=name)
        return self._instant(msg)

    def handle_retrieve(self, instance_id: str) -> dict:
        """Retrieve a single item from the automated storage facility."""
        if game_manager.current_room.id != STORAGE_ROOM_ID:
            return self._instant("There is no automated storage facility in this room.")

        if not instance_id:
            return self._instant("Retrieve what?")

        item = game_manager.retrieve_item(instance_id)
        if not item:
            return self._instant("That item is not in the storage facility.")

        success, msg = game_manager.player.add_to_inventory(item)
        if not success:
            # Inventory full — put it back
            game_manager.storage_manifest[item.instance_id] = item
            return self._instant(f"You can't carry any more. {msg}")

        name = item.display_name()
        msg = random.choice(_RETRIEVE_RESPONSES).format(name=name)
        return self._instant(msg)

storage_handler = StorageHandler()
