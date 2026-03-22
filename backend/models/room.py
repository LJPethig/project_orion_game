# backend/models/room.py
"""
Room — represents a single compartment on the ship.
Ported from Project Dark Star with Arcade dependencies removed.
Objects and doors are added later (Phase 8+).
"""

from typing import Dict, List, Any


class Room:
    """
    A single ship compartment. Loaded from ship_rooms.json.
    Grows as systems are added — objects, doors, temperature, pressure.
    """

    def __init__(
        self,
        room_id:            str,
        name:               str,
        description:        List[str],
        background_image:   str,
        exits:              Dict[str, Dict[str, Any]],
        dimensions_m:       dict,
        target_temperature: float = 21.5,
    ):
        self.id                 = room_id
        self.name               = name
        self.description        = description
        self.background_image   = background_image
        self.exits              = exits
        self.dimensions_m, self.volume_m3 = self._validate_and_compute_volume(
            dimensions_m, room_id
        )

        # Objects and panels added later
        self.fixed_object_ids: List[str]  = []   # IDs from JSON — resolved in ship._load_fixed_objects
        self.objects:          List[Any]  = []
        self.panels:           Dict[str, Any] = {}

        # Temperature — target set from JSON preset, current starts at target
        self.target_temperature  = target_temperature
        self.current_temperature = target_temperature

    # ── Volume validation ────────────────────────────────────

    @staticmethod
    def _validate_and_compute_volume(dimensions_m: dict, room_id: str) -> tuple[dict, float]:
        if not isinstance(dimensions_m, dict):
            raise ValueError(f"Room '{room_id}': dimensions_m must be a dict")

        expected = {"length", "width", "height"}
        if set(dimensions_m) != expected:
            missing = expected - set(dimensions_m)
            extra   = set(dimensions_m) - expected
            raise ValueError(
                f"Room '{room_id}': dimensions_m wrong keys. "
                f"Missing: {missing}, Extra: {extra}"
            )

        try:
            length = float(dimensions_m["length"])
            width  = float(dimensions_m["width"])
            height = float(dimensions_m["height"])
        except (TypeError, ValueError):
            raise ValueError(f"Room '{room_id}': dimensions_m values must be numbers")

        if length <= 0 or width <= 0 or height <= 0:
            raise ValueError(f"Room '{room_id}': all dimensions must be positive")

        return dimensions_m, length * width * height

    # ── Object management (used from Phase 8+) ───────────────

    def add_object(self, obj: Any) -> None:
        self.objects.append(obj)

    def remove_object(self, obj_id: str) -> bool:
        for i, obj in enumerate(self.objects):
            if obj.id == obj_id:
                self.objects.pop(i)
                return True
        return False

    def __repr__(self) -> str:
        return f"<Room '{self.id}' vol={self.volume_m3:.2f} m³>"
