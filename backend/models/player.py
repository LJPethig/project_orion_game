# backend/models/player.py
"""
Player — inventory, equipped slots, carry capacity.
Ported from Project Dark Star — Arcade dependencies removed.
"""

from typing import Optional, List, Tuple
from config import PLAYER_MAX_CARRY_MASS
from backend.models.interactable import PortableItem


class Player:

    EQUIP_SLOTS = ('head', 'body', 'torso', 'waist', 'feet')

    def __init__(self, name: str):
        self.name            = name
        self._inventory:     List[PortableItem]           = []
        self.max_carry_mass: float                        = PLAYER_MAX_CARRY_MASS

        # Fixed equipment slots
        self.head_slot:  Optional[PortableItem] = None
        self.body_slot:  Optional[PortableItem] = None
        self.torso_slot: Optional[PortableItem] = None
        self.waist_slot: Optional[PortableItem] = None
        self.feet_slot:  Optional[PortableItem] = None

    # ── Carry mass ───────────────────────────────────────────

    @property
    def current_carry_mass(self) -> float:
        """Mass of loose (unequipped) inventory items only."""
        return sum(item.mass for item in self._inventory)

    @property
    def equipped_items(self) -> List[PortableItem]:
        return [
            getattr(self, f"{slot}_slot")
            for slot in self.EQUIP_SLOTS
            if getattr(self, f"{slot}_slot") is not None
        ]

    # ── Inventory ────────────────────────────────────────────

    def get_inventory(self) -> List[PortableItem]:
        return self._inventory.copy()

    def has_item(self, item_id: str) -> bool:
        """Check loose inventory and equipped slots."""
        if any(i.id == item_id for i in self._inventory):
            return True
        return any(i.id == item_id for i in self.equipped_items)

    def add_to_inventory(self, item: PortableItem) -> Tuple[bool, str]:
        """Add item to loose inventory. Fails if over carry limit."""
        if self.current_carry_mass + item.mass > self.max_carry_mass:
            remaining = self.max_carry_mass - self.current_carry_mass
            return False, f"Too heavy. You can carry {remaining:.1f} kg more."
        self._inventory.append(item)
        return True, f"You take the {item.name}."

    def remove_from_inventory(self, item: PortableItem) -> bool:
        if item in self._inventory:
            self._inventory.remove(item)
            return True
        return False

    def clear_inventory(self) -> None:
        """Clear all loose inventory items. Used by save/load restore only."""
        self._inventory.clear()

    def restore_inventory_item(self, item: PortableItem) -> None:
        """Append item directly without carry mass check. Used by save/load restore only."""
        self._inventory.append(item)

    def find_in_inventory(self, item_id: str) -> Optional[PortableItem]:
        """Return the inventory item with the given id, or None."""
        for item in self._inventory:
            if item.id == item_id:
                return item
        return None

    # ── Equipment ────────────────────────────────────────────

    def equip(self, item: PortableItem) -> Tuple[bool, str]:
        """
        Equip an item into its designated slot.
        Blocked if the slot is already occupied — player must remove first.
        """
        slot = getattr(item, 'equip_slot', None)
        if not slot or slot not in self.EQUIP_SLOTS:
            return False, f"The {item.name} cannot be equipped."

        slot_attr = f"{slot}_slot"
        old_item  = getattr(self, slot_attr)

        if old_item:
            return False, f"You are already wearing the {old_item.name}. Remove it first."

        setattr(self, slot_attr, item)
        self.remove_from_inventory(item)
        return True, f"You put on the {item.name}."

    def unequip(self, slot_name: str) -> Tuple[bool, str]:
        """
        Unequip item from slot into loose inventory.
        Returns (False, msg) if too heavy — caller handles drop logic.
        """
        slot_attr = f"{slot_name.lower()}_slot"
        if not hasattr(self, slot_attr):
            return False, f"No such slot: {slot_name}."

        item = getattr(self, slot_attr)
        if item is None:
            return False, f"Nothing equipped in {slot_name} slot."

        success, msg = self.add_to_inventory(item)
        if success:
            setattr(self, slot_attr, None)
            return True, f"You remove the {item.name}."

        return False, msg

    # ── Card checks (replaces debug flags) ───────────────────

    def has_card_for_level(self, security_level: int) -> bool:
        """Return True if the player carries a valid card for the given security level."""
        from backend.models.door import SecurityLevel as SL
        if security_level == SL.KEYCARD_LOW.value:
            return self.has_item('id_card_high_sec') or self.has_item('id_card_low_sec')
        if security_level in (SL.KEYCARD_HIGH.value, SL.KEYCARD_HIGH_PIN.value):
            return self.has_item('id_card_high_sec')
        return False

    # ── Debug ─────────────────────────────────────────────────

    def debug_str(self) -> str:
        lines = [
            f"--- {self.name} ({self.current_carry_mass:.1f}/{self.max_carry_mass:.1f} kg) ---"
        ]
        if self._inventory:
            for item in self._inventory:
                lines.append(f"  {item.name} ({item.mass:.1f} kg)")
        else:
            lines.append("  (empty)")

        lines.append("--- Equipped ---")
        any_equipped = False
        for slot in self.EQUIP_SLOTS:
            item = getattr(self, f"{slot}_slot")
            if item:
                lines.append(f"  [{slot}] {item.name}")
                any_equipped = True
        if not any_equipped:
            lines.append("  (none)")

        return "\n".join(lines)
