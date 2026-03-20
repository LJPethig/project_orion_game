# backend/models/door.py
"""
Door and SecurityPanel — represent door connections between rooms.
Ported from Project Dark Star with Arcade dependencies removed.
Three door states: open, closed, locked.
Security panel logic (keycard/PIN) kept for future use but not enforced yet.
"""

from typing import Optional
from enum import Enum


class SecurityLevel(Enum):
    NONE             = 0
    KEYCARD_LOW      = 1
    KEYCARD_HIGH     = 2
    KEYCARD_HIGH_PIN = 3


class SecurityPanel:
    """
    A panel on one side of a door.
    Controls locking/unlocking from that side.
    repair_progress is runtime state — initialised here, not loaded from JSON.
    """

    def __init__(
        self,
        panel_id:       str,
        door_id:        str,
        side:           str,
        security_level: int,
        pin:            Optional[str] = None,
        damaged:        bool = False,
    ):
        self.panel_id       = panel_id
        self.door_id        = door_id
        self.side           = side
        self.security_level = SecurityLevel(security_level)
        self.pin            = pin
        self.is_broken      = damaged
        self.repair_progress = 0.0    # Runtime state only — not in JSON

    def get_state_label(self) -> str:
        """Return a short display label for the panel state."""
        if self.is_broken:
            return "damaged"
        return "operational"


class Door:
    """
    A bi-directional door connecting two rooms.
    Tracks open/closed/locked state independently.
    Each side has its own SecurityPanel.
    """

    def __init__(
        self,
        door_id:        str,
        room_a_id:      str,
        room_b_id:      str,
        door_open:      bool,
        door_locked:    bool,
        security_level: int,
        pin:            Optional[str] = None,
    ):
        self.id             = door_id
        self.room_ids       = (room_a_id, room_b_id)
        self.door_open      = door_open
        self.door_locked    = door_locked
        self.security_level = security_level
        self.pin            = pin

        # Per-side panels: room_id → SecurityPanel
        self.panels: dict[str, SecurityPanel] = {}

    def get_other_room_id(self, current_room_id: str) -> Optional[str]:
        """Return the room ID on the other side of this door."""
        if current_room_id == self.room_ids[0]:
            return self.room_ids[1]
        elif current_room_id == self.room_ids[1]:
            return self.room_ids[0]
        return None

    def get_panel_for_room(self, room_id: str) -> Optional[SecurityPanel]:
        """Return the SecurityPanel on the given room's side."""
        return self.panels.get(room_id)

    def get_state(self) -> str:
        """Return the door state as a string for display."""
        if self.door_locked:
            return "locked"
        if self.door_open:
            return "open"
        return "closed"

    def open(self) -> None:
        """Open the door (only if not locked)."""
        if not self.door_locked:
            self.door_open = True

    def close(self) -> None:
        """Close the door."""
        self.door_open = False

    def lock(self) -> None:
        """Lock the door — also closes it."""
        self.door_locked = True
        self.door_open   = False

    def unlock(self) -> None:
        """Unlock the door — does not open it."""
        self.door_locked = False

    def __repr__(self) -> str:
        return f"<Door '{self.id}' {self.get_state()}>"
