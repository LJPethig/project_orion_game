# backend/models/ship.py
"""
Ship — owns all rooms and provides query helpers.
Phase 7: loads rooms from ship_rooms.json only.
Doors, items, and cargo added in later phases.
"""

import json
from typing import Dict
from backend.models.room import Room
from config import ROOM_TEMP_PRESETS


class Ship:
    """
    Represents the entire ship structure.
    Single source of truth for all rooms.
    """

    def __init__(self, name: str):
        self.name  = name
        self.rooms: Dict[str, Room] = {}

    @classmethod
    def load_from_json(cls, name: str, rooms_path: str) -> 'Ship':
        """
        Load ship rooms from ship_rooms.json.
        Returns a fully initialised Ship instance.
        """
        ship = cls(name)

        with open(rooms_path, 'r', encoding='utf-8') as f:
            rooms_data = json.load(f)

        for room_data in rooms_data:
            room_id = room_data['id']

            # Resolve temperature preset string → float
            temp_label = room_data.get('target_temperature', 'normal').lower()
            target_temp = ROOM_TEMP_PRESETS.get(temp_label, 21.5)

            room = Room(
                room_id=room_id,
                name=room_data['name'],
                description=room_data['description'],
                background_image=room_data.get('background_image', ''),
                exits=room_data.get('exits', {}),
                dimensions_m=room_data['dimensions_m'],
                target_temperature=target_temp,
            )
            ship.rooms[room_id] = room

        return ship

    # ── Query helpers ────────────────────────────────────────

    def get_room(self, room_id: str) -> Room | None:
        return self.rooms.get(room_id)

    def __repr__(self) -> str:
        return f"<Ship '{self.name}' rooms={len(self.rooms)}>"
