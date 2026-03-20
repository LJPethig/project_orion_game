# backend/models/ship.py
"""
Ship — owns all rooms and doors, provides query helpers.
Loads rooms from ship_rooms.json and doors from door_status.json.
"""

import json
from typing import Dict, Optional, List
from backend.models.room import Room
from backend.models.door import Door, SecurityPanel
from config import ROOM_TEMP_PRESETS, DOORS_JSON_PATH


class Ship:
    """
    Represents the entire ship structure.
    Single source of truth for all rooms and doors.
    """

    def __init__(self, name: str):
        self.name  = name
        self.rooms: Dict[str, Room] = {}
        self.doors: List[Door]      = []

    @classmethod
    def load_from_json(cls, name: str, rooms_path: str) -> 'Ship':
        """
        Load ship rooms and doors from JSON files.
        Returns a fully initialised Ship instance.
        """
        ship = cls(name)
        ship._load_rooms(rooms_path)
        ship._load_doors()
        return ship

    def _load_rooms(self, rooms_path: str) -> None:
        """Load all rooms from ship_rooms.json."""
        with open(rooms_path, 'r', encoding='utf-8') as f:
            rooms_data = json.load(f)

        for room_data in rooms_data:
            room_id     = room_data['id']
            temp_label  = room_data.get('target_temperature', 'normal').lower()
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
            self.rooms[room_id] = room

    def _load_doors(self) -> None:
        """Load all doors from door_status.json and attach to rooms."""
        try:
            with open(DOORS_JSON_PATH, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load door_status.json: {e}")
            return

        for conn in data.get('connections', []):
            room_ids = conn['rooms']
            if len(room_ids) != 2:
                print(f"Warning: Door {conn['id']} does not connect exactly two rooms")
                continue

            room_a_id, room_b_id = room_ids[0], room_ids[1]

            if room_a_id not in self.rooms or room_b_id not in self.rooms:
                print(f"Warning: Door {conn['id']} references unknown room(s): {room_a_id}, {room_b_id}")
                continue

            door = Door(
                door_id=conn['id'],
                room_a_id=room_a_id,
                room_b_id=room_b_id,
                door_open=conn.get('door_open', False),
                door_locked=conn.get('door_locked', False),
                security_level=conn.get('security_level', 1),
                pin=conn.get('pin'),
            )

            # Create panels and attach to door and room
            for panel_data in conn.get('panel_ids', []):
                panel = SecurityPanel(
                    panel_id=panel_data['id'],
                    door_id=door.id,
                    side=panel_data['side'],
                    security_level=conn.get('security_level', 1),
                    pin=conn.get('pin'),
                    damaged=panel_data.get('damaged', False),
                )
                door.panels[panel_data['side']] = panel

                if panel_data['side'] in self.rooms:
                    self.rooms[panel_data['side']].panels[door.id] = panel

            self.doors.append(door)
            self._attach_door_to_exits(door, room_a_id, room_b_id)

    def _attach_door_to_exits(self, door: Door, room_a_id: str, room_b_id: str) -> None:
        """Attach a door instance to the matching exit in each room."""
        room_a = self.rooms[room_a_id]
        room_b = self.rooms[room_b_id]

        for exit_data in room_a.exits.values():
            if exit_data.get('target') == room_b_id:
                exit_data['door'] = door
                break

        for exit_data in room_b.exits.values():
            if exit_data.get('target') == room_a_id:
                exit_data['door'] = door
                break

    # ── Query helpers ────────────────────────────────────────

    def get_room(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    def get_door_between(self, room_a_id: str, room_b_id: str) -> Optional[Door]:
        """Return the door connecting two rooms, if any."""
        for door in self.doors:
            if set(door.room_ids) == {room_a_id, room_b_id}:
                return door
        return None

    def __repr__(self) -> str:
        return f"<Ship '{self.name}' rooms={len(self.rooms)} doors={len(self.doors)}>"
