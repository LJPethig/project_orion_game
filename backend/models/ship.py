# backend/models/ship.py
"""
Ship — owns all rooms and doors, provides query helpers.
Loads rooms from ship_rooms.json and doors from door_status.json.
"""

import json

from typing import Dict, Optional, List
from backend.models.room import Room
from backend.models.door import Door, SecurityPanel
from backend.models.interactable import PortableItem, FixedObject, StorageUnit, Surface, Terminal, Engine, PalletContainer, Pallet, PowerJunction
from backend.loaders.item_loader import instantiate_item
from config import ROOM_TEMP_PRESETS, DOORS_JSON_PATH, DOOR_PANEL_TYPES_PATH, \
                   INITIAL_STATE_JSON_PATH, TERMINALS_JSON_PATH, STORAGE_UNITS_JSON_PATH, \
                   SURFACES_JSON_PATH, ENGINES_JSON_PATH, POWER_JUNCTIONS_JSON_PATH, \
                   SHIP_ITEMS_JSON_PATH, CARGO_CONTAINERS_JSON_PATH, PALLET_PLATFORMS_JSON_PATH


class Ship:
    """
    Represents the entire ship structure.
    Single source of truth for all rooms and doors.
    """

    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.doors: List[Door]      = []

    @classmethod
    def load_from_json(cls, rooms_path: str) -> 'Ship':
        """
        Load ship rooms, doors, fixed objects and placed items from JSON files.
        Apply initial state overlay last.
        Returns a fully initialised Ship instance.
        """
        ship = cls()
        ship._load_rooms(rooms_path)
        ship._load_doors()
        ship._load_fixed_objects()
        ship._load_ship_items()
        ship._apply_initial_state()
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
                images=room_data.get('images', {}),
                exits=room_data.get('exits', {}),
                dimensions_m=room_data['dimensions_m'],
                target_temperature=target_temp,
            )
            room.fixed_object_ids = room_data.get('fixed_objects', [])
            room.description_powered = room_data.get('description_powered', [])
            room.description_unpowered = room_data.get('description_unpowered', [])
            room.description_reactor_online = room_data.get('description_reactor_online', [])
            room.description_reactor_offline = room_data.get('description_reactor_offline', [])
            room.description_reactor_ejected = room_data.get('description_reactor_ejected', [])
            self.rooms[room_id] = room

    def _load_doors(self) -> None:
        """Load all doors from door_status.json and attach to rooms.
        Panel type and security level are resolved from door_access_panel_types.json.
        """
        # ── Load panel type registry ──────────────────────────
        try:
            with open(DOOR_PANEL_TYPES_PATH, 'r', encoding='utf-8') as f:
                panel_types = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load door_access_panel_types.json: {e}")
            panel_types = {}

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
            )

            # Create panels and attach to door and room
            for panel_data in conn.get('panel_ids', []):
                panel_type = panel_data['panel_type']  # KeyError if missing — intentional
                type_data = panel_types[panel_type]  # KeyError if unknown type — intentional
                security_level = type_data['security_level']  # KeyError if missing — intentional

                panel = SecurityPanel(
                    panel_id=panel_data['id'],
                    door_id=door.id,
                    side=panel_data['side'],
                    panel_type=panel_type,
                    security_level=security_level,
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

    def _load_fixed_objects(self) -> None:
        """
        Load fixed objects from terminals.json, storage_units.json and surfaces.json.
        Instantiate the correct class based on which file the definition comes from.
        Place objects into rooms that reference their IDs in fixed_objects arrays.
        """
        definitions = {}   # id → (data_dict, class)

        file_class_map = [
            (TERMINALS_JSON_PATH, Terminal),
            (STORAGE_UNITS_JSON_PATH, StorageUnit),
            (SURFACES_JSON_PATH, Surface),
            (ENGINES_JSON_PATH, Engine),
            (POWER_JUNCTIONS_JSON_PATH, PowerJunction),
            (CARGO_CONTAINERS_JSON_PATH, PalletContainer),
            (PALLET_PLATFORMS_JSON_PATH, Pallet),
        ]

        for path, cls in file_class_map:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for obj in data:
                obj_id = obj.get('id')
                if obj_id:
                    definitions[obj_id] = (obj, cls)

        for room in self.rooms.values():
            for obj_id in room.fixed_object_ids:
                if obj_id not in definitions:
                    print(f"Warning: No definition for fixed object '{obj_id}' in room '{room.id}'")
                    continue
                data, cls = definitions[obj_id]
                kwargs = {k: v for k, v in data.items()}
                room.add_object(cls(**kwargs))

    def _load_ship_items(self) -> None:
        """
        Place portable items into the world from ship_items.json.
        Items land on room floors or inside storage containers.
        Requires item registry from ItemLoader — loaded fresh here to avoid
        circular imports with GameManager.
        """
        from backend.loaders.item_loader import load_item_registry

        with open(SHIP_ITEMS_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        registry = load_item_registry()

        # ── Loose items on room floors ────────────────────────
        for entry in data.get('room_floor', []):
            room = self.rooms.get(entry['room_id'])
            if not room:
                print(f"Warning: ship_items.json references unknown room '{entry['room_id']}'")
                continue
            for item_entry in entry.get('items', []):
                for item_id, overrides in self._parse_item_entries(item_entry):
                    item = self._make_item(item_id, registry, overrides)
                    if item:
                        room.floor.append(item)

            # ── Items inside containers ───────────────────────────
        container_index = self._build_container_index()
        for entry in data.get('containers', []):
            container = container_index.get(entry['container_id'])
            if not container:
                print(f"Warning: ship_items.json references unknown container '{entry['container_id']}'")
                continue
            for item_entry in entry.get('items', []):
                for item_id, overrides in self._parse_item_entries(item_entry):
                    item = self._make_item(item_id, registry, overrides)
                    if item:
                        if not container.add_item(item):
                            print(f"Warning: '{item_id}' could not fit in '{entry['container_id']}' — over capacity")

        # ── Items on surfaces ─────────────────────────────────
        surface_index = self._build_surface_index()
        for entry in data.get('surfaces', []):
            surface = surface_index.get(entry['surface_id'])
            if not surface:
                print(f"Warning: ship_items.json references unknown surface '{entry['surface_id']}'")
                continue
            for item_entry in entry.get('items', []):
                for item_id, overrides in self._parse_item_entries(item_entry):
                    item = self._make_item(item_id, registry, overrides)
                    if item:
                        surface.add_item(item)

    def _parse_item_entries(self, entry) -> list[tuple[str, dict | None]]:
        """
        Parse a placement entry from initial_ship_items.json.
        Supports three formats:
          "cable_low_voltage"
          {"id": "cable_low_voltage", "length_m": 12.5}
          {"id": "cable_low_voltage", "quantity": 3}
        Returns a list of (item_id, overrides_or_None) tuples — one per instance to place.
        quantity is consumed here and never passed as an override to the item factory.
        """
        if isinstance(entry, str):
            return [(entry, None)]
        item_id = entry.get('id')
        quantity = int(entry.get('quantity', 1))
        overrides = {k: v for k, v in entry.items() if k not in ('id', 'quantity')}
        return [(item_id, overrides or None)] * quantity

    def _make_item(self, item_id: str, registry: dict, overrides: dict = None) -> PortableItem | None:
        """Create a fresh item instance from registry data. Each call returns a unique object.
        overrides — optional dict of instance attributes to apply after base data (e.g. length_m for wire).
        """
        data = registry.get(item_id)
        if not data:
            print(f"Warning: initial_ship_items.json references unknown item '{item_id}'")
            return None
        merged = dict(data)
        if overrides:
            merged.update(overrides)
        return instantiate_item(merged)

    def _build_container_index(self) -> dict:
        """Return a flat dict of container_id → StorageUnit across all rooms."""
        index = {}
        for room in self.rooms.values():
            for obj in room.objects:
                if isinstance(obj, StorageUnit):
                    index[obj.id] = obj
        return index

    def _build_surface_index(self) -> dict:
        """Return a flat dict of surface_id → Surface across all rooms."""
        index = {}
        for room in self.rooms.values():
            for obj in room.objects:
                if isinstance(obj, Surface):
                    index[obj.id] = obj
        return index

    def _apply_initial_state(self) -> None:
        """
        Apply initial_ship_state.json on top of the pristine ship.
        Overrides door states, panel damage, and PINs.
        Missing file is silently skipped — pristine ship is valid on its own.
        """
        try:
            with open(INITIAL_STATE_JSON_PATH, 'r', encoding='utf-8') as f:
                state = json.load(f)
        except FileNotFoundError:
            return
        except Exception as e:
            print(f"Warning: Could not load initial_ship_state.json: {e}")
            return

        # ── Door states ───────────────────────────────────────
        for entry in state.get('doors', []):
            door = self.get_door_by_id(entry['id'])
            if not door:
                print(f"Warning: initial_ship_state references unknown door '{entry['id']}'")
                continue
            if 'door_open' in entry:
                door.door_open = entry['door_open']
            if 'door_locked' in entry:
                door.door_locked = entry['door_locked']

        # ── Panel damage ──────────────────────────────────────
        panel_index = self.build_panel_index()
        for entry in state.get('panels', []):
            panel = panel_index.get(entry['id'])
            if not panel:
                print(f"Warning: initial_ship_state references unknown panel '{entry['id']}'")
                continue
            if 'damaged' in entry:
                panel.is_broken = entry['damaged']

        # ── PINs ──────────────────────────────────────────────
        for entry in state.get('pins', []):
            door = self.get_door_by_id(entry['door_id'])
            if not door:
                print(f"Warning: initial_ship_state references unknown door '{entry['door_id']}' for PIN")
                continue
            door.pin = entry['pin']
            for panel in door.panels.values():
                panel.pin = entry['pin']

    def build_panel_index(self) -> dict:
        """Return a flat dict of panel_id → SecurityPanel across all doors."""
        index = {}
        for door in self.doors:
            for panel in door.panels.values():
                index[panel.panel_id] = panel
        return index

    # ── Query helpers ────────────────────────────────────────

    def get_room(self, room_id: str) -> Optional[Room]:
        return self.rooms.get(room_id)

    def get_door_between(self, room_a_id: str, room_b_id: str) -> Optional[Door]:
        """Return the door connecting two rooms, if any."""
        for door in self.doors:
            if set(door.room_ids) == {room_a_id, room_b_id}:
                return door
        return None

    def get_door_by_id(self, door_id: str) -> Optional[Door]:
        """Return a door by its ID."""
        for door in self.doors:
            if door.id == door_id:
                return door
        return None


    def get_broken_panels_in_room(self, room_id: str) -> list:
        """
        Return all broken panels reachable from room_id.
        Each entry is (panel, door, exit_label) — enough for RepairHandler
        to act without further lookups.
        """
        room = self.rooms.get(room_id)
        if not room:
            return []

        results = []
        for exit_data in room.exits.values():
            door = exit_data.get('door')
            if not door:
                continue
            panel = door.get_panel_for_room(room_id)
            if panel and panel.is_broken:
                other_id = door.get_other_room_id(room_id)
                other_room = self.rooms.get(other_id)
                exit_label = exit_data.get('label') or (other_room.name if other_room else other_id)
                results.append((panel, door, exit_label))
        return results

    def __repr__(self) -> str:
        return f"<Ship rooms={len(self.rooms)} doors={len(self.doors)}>"
