# backend/handlers/command_handler.py
"""
CommandHandler — central verb registry.
Routes player commands to the appropriate sub-handler.
Uses longest-match on verbs (same pattern as Dark Star).

open/close routing:
  1. Try container first — if found, use ContainerHandler
  2. Try door second — if found, use DoorHandler
  3. If both match — ambiguity message (Phase 13d)
  4. If neither — "You can't open/close that"
"""

from backend.handlers.movement_handler import MovementHandler
from backend.handlers.door_handler import DoorHandler
from backend.handlers.repair_handler import RepairHandler
from backend.handlers.item_handler import ItemHandler
from backend.handlers.container_handler import ContainerHandler
from backend.handlers.equip_handler import EquipHandler
from backend.models.game_manager import game_manager

import logging
resolver_logger = logging.getLogger('resolver')

class CommandHandler:

    def __init__(self):
        self._movement   = MovementHandler()
        self._door       = DoorHandler()
        self._repair     = RepairHandler()
        self._item       = ItemHandler()
        self._container  = ContainerHandler()
        self._equip      = EquipHandler()

        self.commands = {
            # Movement
            'enter':             self._movement.handle,
            'go':                self._movement.handle,
            'move':              self._movement.handle,
            # open/close — routed through disambiguation methods
            'open':              self._route_open,
            'close':             self._route_close,
            # Door only
            'lock':              self._door.handle_lock,
            'unlock':            self._door.handle_unlock,
            # Repair
            'repair panel':      self._repair.handle,
            'repair':            self._repair.handle,
            # Items
            'take':              self._item.handle_take,
            'get':               self._item.handle_take,
            'pick up':           self._item.handle_take,
            'drop':              self._item.handle_drop,
            'debug_inventory':   self._item.handle_debug_inventory,
            # Equip/unequip
            'wear':              self._equip.handle_wear,
            'equip':             self._equip.handle_wear,
            'remove':            self._equip.handle_remove,
            'take off':          self._equip.handle_remove,
            'unequip':           self._equip.handle_remove,
            # Container specific
            'look in':           self._container.handle_look_in,
            'take from':         self._container.handle_take_from,
            'put in':            self._container.handle_put_in,
            'place in':          self._container.handle_put_in,
            'put on':            self._container.handle_put_on,
            'place on':          self._container.handle_put_on,
        }


    def _resolve_for_verb(self, verb: str, args: str) -> str:
        """
        Resolve the args string to use IDs based on the verb.
        For preposition commands, resolves both item and target separately.
        """
        resolver_logger.info(f"[RESOLVER VERB] verb='{verb}' args='{args}'")
        if not args:
            return args

        # ── Inventory item verbs ──────────────────────────────
        if verb in ('drop', 'wear', 'equip'):
            return self._resolve(args, 'inventory')

        # ── Equipped item verbs ───────────────────────────────
        if verb in ('remove', 'take off', 'unequip'):
            return self._resolve(args, 'equipped')

        # ── Room portable item verbs ──────────────────────────
        if verb in ('take', 'get', 'pick up'):
            return self._resolve(args, 'room_portable')

        # ── Fixed object verbs ────────────────────────────────
        if verb in ('look in',):
            return self._resolve(args, 'room_fixed')

        # ── open/close — fixed objects only (doors handled in _route_open/close) ──
        if verb in ('open', 'close'):
            return self._resolve(args, 'room_fixed')

        # ── Preposition verbs — resolve both parts ────────────
        if verb == 'take from' and ' from ' in args.lower():
            parts     = args.lower().split(' from ', 1)
            item_part = self._resolve(parts[0].strip(), 'room_portable')
            cont_part = self._resolve(parts[1].strip(), 'room_fixed')
            return f"{item_part} from {cont_part}"

        if verb in ('put in', 'place in') and ' in ' in args.lower():
            parts     = args.lower().split(' in ', 1)
            item_part = self._resolve(parts[0].strip(), 'inventory')
            cont_part = self._resolve(parts[1].strip(), 'room_fixed')
            return f"{item_part} in {cont_part}"

        if verb in ('put on', 'place on') and ' on ' in args.lower():
            parts     = args.lower().split(' on ', 1)
            item_part = self._resolve(parts[0].strip(), 'inventory')
            surf_part = self._resolve(parts[1].strip(), 'room_fixed')
            return f"{item_part} on {surf_part}"

        # Movement, repair, lock, unlock — no item resolution needed
        return args

    def _route_open(self, args: str) -> dict:
        """
        Route 'open' to container or door handler.
        Container takes priority — returns None if no match, then door is tried.
        """
        if not args:
            return self._unknown_action("Open what?")

        container_result = self._container.handle_open(args)
        if container_result is not None:
            return container_result

        return self._door.handle_open(args)

    def _route_close(self, args: str) -> dict:
        """
        Route 'close' to container or door handler.
        Container takes priority — returns None if no match, then door is tried.
        """
        if not args:
            return self._unknown_action("Close what?")

        container_result = self._container.handle_close(args)
        if container_result is not None:
            return container_result

        return self._door.handle_close(args)


    def _resolve(self, target: str, scope: str) -> str:
        """
        Attempt to resolve a keyword or partial string to a concrete object ID.
        Returns the resolved ID if found, otherwise returns target unchanged.
        Prints a debug warning if resolution fails.

        scope values:
          'inventory'    — player loose inventory
          'equipped'     — player equipped slots
          'room_portable' — surfaces and floor in current room
          'room_fixed'   — containers and surfaces (fixed objects) in current room
        """
        from backend.models.interactable import StorageUnit, Surface, PortableItem
        player = game_manager.player
        room   = game_manager.get_current_room()
        t = target.strip().lower()
        resolver_logger.info(f"[RESOLVER] scope='{scope}' input='{t}'")

        if scope == 'inventory':
            for item in player.get_inventory():
                if item.id == t or item.matches(t):
                    if item.id != t:
                        resolver_logger.info(f"[RESOLVER] inventory: '{t}' → '{item.id}'")
                    return item.id

        elif scope == 'equipped':
            from backend.models.interactable import PortableItem
            for slot in player.EQUIP_SLOTS:
                item = getattr(player, f"{slot}_slot")
                if item and (item.id == t or item.matches(t)):
                    if item.id != t:
                        resolver_logger.info(f"[RESOLVER] equipped: '{t}' → '{item.id}'")
                    return item.id

        elif scope == 'room_portable':
            for obj in room.objects:
                if isinstance(obj, Surface):
                    for item in obj.contents:
                        if item.id == t or item.matches(t):
                            if item.id != t:
                                resolver_logger.info(f"[RESOLVER] surface '{obj.id}': '{t}' → '{item.id}'")
                            return item.id
                elif isinstance(obj, StorageUnit) and obj.is_open:
                    for item in obj.contents:
                        if item.id == t or item.matches(t):
                            if item.id != t:
                                resolver_logger.info(f"[RESOLVER] container '{obj.id}': '{t}' → '{item.id}'")
                            return item.id
            for item in room.floor:
                if item.id == t or item.matches(t):
                    if item.id != t:
                        resolver_logger.info(f"[RESOLVER] floor: '{t}' → '{item.id}'")
                    return item.id

        elif scope == 'room_fixed':
            for obj in room.objects:
                if isinstance(obj, (StorageUnit, Surface)):
                    if obj.id == t or obj.matches(t):
                        if obj.id != t:
                            resolver_logger.info(f"[RESOLVER] fixed: '{t}' → '{obj.id}'")
                        return obj.id

        resolver_logger.info(f"[RESOLVER FAIL] scope='{scope}' input='{t}' — no match found, passing through")
        return target

    def process(self, raw: str) -> dict:
        cmd = raw.strip().lower()
        if not cmd:
            return self._unknown('')

        # Special handling for preposition commands before verb matching
        if ' from ' in cmd and cmd.startswith('take '):
            parts = cmd.split(' from ', 1)
            return self._container.handle_take_from(
                f"{parts[0][5:].strip()} from {parts[1].strip()}"
            )

        if ' in ' in cmd and (cmd.startswith('put ') or cmd.startswith('place ')):
            prefix_len = 4 if cmd.startswith('put ') else 6
            parts = cmd.split(' in ', 1)
            return self._container.handle_put_in(
                f"{parts[0][prefix_len:].strip()} in {parts[1].strip()}"
            )

        if ' on ' in cmd and (cmd.startswith('put ') or cmd.startswith('place ')):
            prefix_len = 4 if cmd.startswith('put ') else 6
            parts = cmd.split(' on ', 1)
            return self._container.handle_put_on(
                f"{parts[0][prefix_len:].strip()} on {parts[1].strip()}"
            )

        words = cmd.split()

        for i in range(len(words), 0, -1):
            verb = ' '.join(words[:i])
            if verb in self.commands:
                args = ' '.join(words[i:])
                # ── Resolve target to ID before dispatching ───
                args = self._resolve_for_verb(verb, args)
                return self.commands[verb](args)

        return self._unknown(cmd)

    @staticmethod
    def _unknown_action(msg: str) -> dict:
        return {
            'response':     msg,
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': False,
        }

    @staticmethod
    def _unknown(cmd: str) -> dict:
        msg = f"Unknown command: '{cmd}'." if cmd else "Enter a command."
        return {
            'response':     msg,
            'action_type':  'instant',
            'lock_input':   False,
            'room_changed': False,
        }


# Single shared instance
command_handler = CommandHandler()
