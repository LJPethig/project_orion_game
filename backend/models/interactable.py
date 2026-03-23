# backend/models/interactable.py
"""
Interactable object hierarchy.
Ported from Project Dark Star — Arcade dependencies removed.

    Interactable
    ├── PortableItem      — takeable, carriable, equippable
    │   └── UtilityBelt   — wearable belt, accepts clipped attachments (PAM etc.)
    └── FixedObject       — permanently attached to a room, cannot be taken
        ├── StorageUnit   — fixed container with open/close state, holds PortableItems
        ├── Surface       — always-open surface (shelf, bench, table), holds PortableItems
        └── Terminal      — computer terminal (future: login, commands, access levels)
"""

from typing import List, Optional, Any


class Interactable:
    """Base class for all objects the player can interact with."""

    def __init__(
        self,
        id:           str,
        name:         str,
        description:  str,
        keywords:     Optional[List[str]] = None,
        **kwargs,     # Absorb any extra JSON fields gracefully
    ):
        self.id          = id
        self.name        = name
        self.description = description
        self.keywords    = keywords or [name.lower()]

        # Store any extra fields from JSON (mass, equip_slot, capacity_mass etc.)
        for key, value in kwargs.items():
            setattr(self, key, value)

    def matches(self, input_str: str) -> bool:
        """
        Return True if input_str matches any keyword (case-insensitive).
        Longest keywords checked first to favour specific matches over generic ones
        e.g. 'scan tool' matches before 'tool'.
        """
        input_lower = input_str.strip().lower()
        for kw in sorted(self.keywords, key=len, reverse=True):
            if input_lower == kw.lower():
                return True
        return False

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} '{self.id}'>"


class PortableItem(Interactable):
    """
    An item that can be picked up, carried, and optionally equipped.
    mass and equip_slot come from JSON via kwargs.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.takeable:   bool          = True
        self.mass:       float         = getattr(self, 'mass', 0.0)
        self.equip_slot: Optional[str] = getattr(self, 'equip_slot', None)


class UtilityBelt(PortableItem):
    """
    Wearable belt that accepts clipped attachments (PAM, small tools).
    Attachment mechanic dormant until PAM/EVA phases are implemented.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.attached_pam: bool = False
        # Future: list of clipped items


class FixedObject(Interactable):
    """
    An object permanently attached to a room — terminals, machinery, panels.
    Cannot be taken by the player.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.takeable: bool = False


class StorageUnit(FixedObject):
    """
    A fixed container (locker, cabinet, rack) that holds PortableItems.
    capacity_mass comes from JSON via kwargs.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contents:       List[PortableItem] = []
        self.is_open:        bool               = False
        self.capacity_mass:  float              = getattr(self, 'capacity_mass', 100.0)
        self.current_mass:   float              = 0.0

    def can_add(self, item: PortableItem) -> bool:
        return (self.current_mass + item.mass) <= self.capacity_mass

    def add_item(self, item: PortableItem) -> bool:
        if not self.can_add(item):
            return False
        self.contents.append(item)
        self.current_mass += item.mass
        return True

    def remove_item(self, item: PortableItem) -> bool:
        if item in self.contents:
            self.contents.remove(item)
            self.current_mass -= item.mass
            return True
        return False

    def contents_str(self) -> str:
        """Formatted contents list for examine/look responses."""
        if not self.contents:
            return "It is empty."
        names = [item.name for item in self.contents]
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]} and {names[1]}"
        return ", ".join(names[:-1]) + f", and {names[-1]}"


class Surface(FixedObject):
    """
    An always-open fixed surface — shelf, bench, table, rack.
    No open/close state. Items dropped in the room land here.
    Empty: grey bold. Has items: purple bold.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.contents:     List[PortableItem] = []
        self.current_mass: float              = 0.0

    @property
    def has_items(self) -> bool:
        return len(self.contents) > 0

    def add_item(self, item: PortableItem) -> bool:
        self.contents.append(item)
        self.current_mass += item.mass
        return True

    def remove_item(self, item: PortableItem) -> bool:
        if item in self.contents:
            self.contents.remove(item)
            self.current_mass -= item.mass
            return True
        return False

    def contents_str(self) -> str:
        if not self.contents:
            return "It is empty."
        names = [item.name for item in self.contents]
        if len(names) == 1:
            return names[0]
        if len(names) == 2:
            return f"{names[0]} and {names[1]}"
        return ", ".join(names[:-1]) + f", and {names[-1]}"


class Terminal(FixedObject):
    """
    A fixed computer terminal.
    Future: login state, commands, access levels, power state.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.powered: bool = True   # Future: tied to electrical system
