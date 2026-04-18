# backend/models/interactable.py
"""
Interactable object hierarchy.

    Interactable
    ├── PortableItem        — takeable, carriable, equippable
    │   └── UtilityBelt     — wearable belt, accepts clipped attachments (PAM etc.)
    ├── FixedObject         — permanently attached to a room, cannot be taken
    │   ├── StorageUnit     — fixed container with open/close state, holds PortableItems
    │   │   └── PalletContainer — moveable container, requires equipment to move
    │   ├── Surface         — always-open surface, holds PortableItems
    │   │   └── Pallet      — moveable flat platform, requires equipment to move
    │   ├── Engine          — propulsion engine (sub-light or FTL)
    │   ├── Terminal        — computer terminal
    │   └── PowerJunction   — circuit breaker panel, physical access point for electrical repair

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
        self.instance_id: Optional[str] = getattr(self, 'instance_id', None)

    def display_name(self) -> str:
        """Return name with wire length appended if applicable."""
        length_m = getattr(self, 'length_m', None)
        if length_m is not None:
            return f"{self.name} ({length_m}m)"
        return self.name


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
        self.powered: bool = True  # Future: tied to electrical system
        self.terminal_type: str = getattr(self, 'terminal_type', 'generic')
        self.menu: list = getattr(self, 'menu', [{"label": "Exit", "action": "exit"}])


class Engine(FixedObject):
    """
    A ship propulsion engine — sub-light ion drive or FTL jump drive.
    powered: computed from electrical trace — does the engine have a live feed?
    online:  manual flag — is the engine undamaged and functional?
    An engine is only usable when both powered and online are True.
    Future: repairable with own components and repair profiles (Phase 24).
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.powered: bool = False          # set by electrical system at runtime
        self.online:  bool = getattr(self, 'online', True)   # default True — undamaged


class PowerJunction(FixedObject):
    """
    A fixed circuit breaker panel — the physical access point for electrical
    diagnosis and repair. The player interacts with this object to access the
    electrical system. panel_id links to the corresponding CircuitPanel in the
    electrical system.

    No display or status indicator — the player must diagnose to determine state.
    Future: diagnose and repair commands routed via panel_id to electrical repair handler.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.panel_id: str = getattr(self, 'panel_id', '')


class PalletContainer(StorageUnit):
    """
    A moveable cargo container — subclass of StorageUnit.
    Cannot be carried by hand. Requires equipment to move between rooms.

    Sizes:
      large  — 1200x800x900mm, cargo handler only
      medium — 600x800x900mm,  cargo handler only, sits on pallet platform
      small  — 600x400x900mm,  sack barrow or cargo handler, sits on pallet platform

    movement_equipment: 'cargo_handler' | 'sack_barrow'
    moveable: True — can be relocated between rooms by appropriate equipment
    pallet: True — flagged for auto-logging to cargo_manifest at game init
    declared_value: int — credits, 0 until trading phase assigns real values
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.moveable:            bool  = True
        self.container_size:      str   = getattr(self, 'container_size', 'small')
        self.movement_equipment:  str   = getattr(self, 'movement_equipment', 'sack_barrow')
        self.declared_value:      int   = getattr(self, 'declared_value', 0)
        self.pallet:              bool  = getattr(self, 'pallet', False)


class Pallet(Surface):
    """
    A moveable flat pallet platform — subclass of Surface.
    Cannot be carried by hand. Requires cargo handler to move.
    Items and containers sit on top — no open/close state, inherited from Surface.

    Dimensions: 1200x800x150mm
    movement_equipment: always 'cargo_handler'
    moveable: True — can be relocated by cargo handler
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.moveable:           bool = True
        self.movement_equipment: str  = 'cargo_handler'
