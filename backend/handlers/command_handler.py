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

Resolver:
  - _resolve(target, scope) — returns single best ID match or original string
  - _resolve_all(target, scope) — returns list of all (id, name) matches
  - _resolve_for_verb(verb, args) — maps verb to correct scope
  - Multiple matches → clarification_required response with clickable options
"""

from backend.handlers.movement_handler import MovementHandler
from backend.handlers.door_handler import DoorHandler
from backend.handlers.repair_handler import RepairHandler
from backend.handlers.item_handler import ItemHandler
from backend.handlers.container_handler import ContainerHandler
from backend.handlers.equip_handler import EquipHandler
from backend.handlers.terminal_handler import TerminalHandler
from backend.models.game_manager import game_manager
from backend.models.interactable import Surface as SurfaceModel, StorageUnit, Surface

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
        self._terminal   = TerminalHandler()

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
            # Terminals
            'access':            self._terminal.handle_terminal_access,
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
            'put on':            self._route_put_on,
            'place on':          self._route_put_on,
        }

    # ── Resolver ─────────────────────────────────────────────

    def _resolve(self, target: str, scope: str) -> str:
        """
        Resolve a keyword to a single object ID.
        Returns the first matching ID, or the original string if no match.
        """
        matches = self._resolve_all(target, scope)
        if matches:
            resolved_id = matches[0][0]
            if resolved_id != target.strip().lower():
                resolver_logger.info(f"[RESOLVER] {scope}: '{target.strip().lower()}' → '{resolved_id}'")
            return resolved_id
        resolver_logger.info(f"[RESOLVER FAIL] scope='{scope}' input='{target.strip().lower()}' — no match found, passing through")
        return target

    def _resolve_all(self, target: str, scope: str) -> list:
        """
        Find all matching objects for a keyword in the given scope.
        Returns list of (id, name) tuples — empty list if no matches.

        scope values:
          'inventory'     — player loose inventory
          'equipped'      — player equipped slots
          'room_portable' — surfaces, open containers and floor in current room
          'room_fixed'    — containers and surfaces (fixed objects) in current room
        """
        player = game_manager.player
        room   = game_manager.get_current_room()
        t      = target.strip().lower()
        resolver_logger.info(f"[RESOLVER] scope='{scope}' input='{t}'")
        matches = []

        if scope == 'inventory':
            for item in player.get_inventory():
                if item.id == t or item.matches(t):
                    matches.append((item.id, item.name))

        elif scope == 'equipped':
            for slot in player.EQUIP_SLOTS:
                item = getattr(player, f"{slot}_slot")
                if item and (item.id == t or item.matches(t)):
                    matches.append((item.id, item.name))

        elif scope == 'room_portable':
            for obj in room.objects:
                if isinstance(obj, Surface):
                    for item in obj.contents:
                        if item.id == t or item.matches(t):
                            matches.append((item.id, item.name))
                elif isinstance(obj, StorageUnit) and obj.is_open:
                    for item in obj.contents:
                        if item.id == t or item.matches(t):
                            matches.append((item.id, item.name))
            for item in room.floor:
                if item.id == t or item.matches(t):
                    matches.append((item.id, item.name))

        elif scope == 'room_fixed':
            for obj in room.objects:
                if isinstance(obj, (StorageUnit, Surface)):
                    if obj.id == t or obj.matches(t):
                        matches.append((obj.id, obj.name))

        return matches

    def _resolve_for_verb(self, verb: str, args: str) -> str:
        """
        Resolve the args string to use IDs based on the verb.
        For preposition commands, resolves both item and target separately.
        Returns resolved args string — ambiguity is handled in process() before this is called.
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

        # ── open/close — filter by actionable state ──────────
        if verb in ('open', 'close'):
            matches = self._resolve_all(args, 'room_fixed')
            if len(matches) > 1:
                room = game_manager.get_current_room()
                container_index = {
                    obj.id: obj for obj in room.objects if isinstance(obj, StorageUnit)
                }
                if verb == 'open':
                    matches = [(i, n) for i, n in matches
                               if i in container_index and not container_index[i].is_open]
                else:
                    matches = [(i, n) for i, n in matches
                               if i in container_index and container_index[i].is_open]
                if matches:
                    return matches[0][0]
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

        if verb in ('put on', 'place on'):
            if ' on ' in args.lower():
                parts     = args.lower().split(' on ', 1)
                item_part = self._resolve(parts[0].strip(), 'inventory')
                surf_part = self._resolve(parts[1].strip(), 'room_fixed')
                return f"{item_part} on {surf_part}"
            else:
                return self._resolve(args, 'inventory')

        # Movement, repair, lock, unlock — no item resolution needed
        return args

    def _clarification_response(self, message: str, options: list) -> dict:
        """
        Build a clarification_required response with clickable options.
        options: list of {'label': str, 'command': str}
        """
        return {
            'response':     message,
            'action_type':  'clarification_required',
            'lock_input':   False,
            'room_changed': False,
            'options':      options,
        }

    def _check_ambiguity(self, verb: str, args: str) -> dict | None:
        """
        Check if the given verb+args produces multiple matches.
        Returns a clarification_required response if ambiguous, None if unambiguous.
        Only checks single-target verbs — preposition verbs handled separately.
        """
        scope_map = {
            'take':     'room_portable',
            'get':      'room_portable',
            'pick up':  'room_portable',
            'drop':     'inventory',
            'wear':     'inventory',
            'equip':    'inventory',
            'remove':   'equipped',
            'take off': 'equipped',
            'unequip':  'equipped',
            'open':     'room_fixed',
            'close':    'room_fixed',
            'look in':  'room_fixed',
        }

        # ── Special case: drop — surface may be ambiguous ────
        if verb == 'drop' and args:
            item_matches = self._resolve_all(args, 'inventory')
            seen = set()
            deduped = [(i, n) for i, n in item_matches if not (n in seen or seen.add(n))]
            if len(deduped) == 1:
                item_id, item_name = deduped[0]
                room = game_manager.get_current_room()
                surfaces = [o for o in room.objects if isinstance(o, SurfaceModel)]
                if len(surfaces) > 1:
                    options = [
                        {'label': s.name, 'command': f"put {item_id} on {s.id}"}
                        for s in surfaces
                    ]
                    return self._clarification_response(
                        f"Where do you want to put the {item_name}?",
                        options
                    )

        scope = scope_map.get(verb)
        if not scope or not args:
            return None

        matches = self._resolve_all(args, scope)
        if len(matches) <= 1:
            return None

        # ── For open/close, filter to only actionable containers ─
        if verb in ('open', 'close'):
            room = game_manager.get_current_room()
            container_index = {
                obj.id: obj for obj in room.objects if isinstance(obj, StorageUnit)
            }
            if verb == 'open':
                matches = [(i, n) for i, n in matches
                           if i in container_index and not container_index[i].is_open]
            else:
                matches = [(i, n) for i, n in matches
                           if i in container_index and container_index[i].is_open]
            if len(matches) <= 1:
                return None
            # No name dedup needed for open/close — just build options and return
            options = [
                {'label': name, 'command': f"{verb} {item_id}"}
                for item_id, name in matches
            ]
            return self._clarification_response(f"Which {args}?", options)

        # Deduplicate by name — identical items are interchangeable, show only one
        seen_names = set()
        deduped = []
        for item_id, name in matches:
            if name not in seen_names:
                seen_names.add(name)
                deduped.append((item_id, name))
        matches = deduped

        if len(matches) == 1:
            return None  # Only one distinct item after dedup — no clarification needed

        # Build verb-appropriate command for each option
        options = [
            {'label': name, 'command': f"{verb} {item_id}"}
            for item_id, name in matches
        ]

        return self._clarification_response(
            f"Which {args}?",
            options
        )

    # ── Routing ──────────────────────────────────────────────

    def _route_open(self, args: str) -> dict:
        """Route 'open' to container or door handler."""
        if not args:
            return self._unknown_action("Open what?")
        container_result = self._container.handle_open(args)
        if container_result is not None:
            return container_result
        result = self._door.handle_open(args)
        if result.get('response') == "There's no exit that way.":
            return self._unknown_action("You can't open that.")
        return result

    def _route_close(self, args: str) -> dict:
        """Route 'close' to container or door handler."""
        if not args:
            return self._unknown_action("Close what?")
        container_result = self._container.handle_close(args)
        if container_result is not None:
            return container_result
        result = self._door.handle_close(args)
        if result.get('response') == "There's no exit that way.":
            return self._unknown_action("You can't close that.")
        return result

    def _route_put_on(self, args: str) -> dict:
        """Route 'put on <item>' — equip if wearable, surface placement otherwise."""
        if not args:
            return self._unknown_action("Put what on?")
        if ' on ' in args:
            return self._container.handle_put_on(args)
        return self._equip.handle_wear(args)

    # ── Main process ─────────────────────────────────────────

    def process(self, raw: str) -> dict:
        cmd = raw.strip().lower()
        if not cmd:
            return self._unknown('')

        # Special handling for preposition commands before verb matching
        if ' from ' in cmd and cmd.startswith('take '):
            parts = cmd.split(' from ', 1)
            item_part = parts[0][5:].strip()
            cont_part = parts[1].strip()

            # Resolve the container first, then check for ambiguous items within it
            cont_id = self._resolve(cont_part, 'room_fixed')
            room = game_manager.get_current_room()
            cont_obj = next(
                (o for o in room.objects
                 if isinstance(o, (StorageUnit, Surface)) and o.id == cont_id),
                None
            )
            if cont_obj:
                contents = getattr(cont_obj, 'contents', [])
                t = item_part.strip().lower()
                matches = [(i.id, i.name) for i in contents if i.id == t or i.matches(t)]
                seen = set()
                deduped = [(i, n) for i, n in matches if not (n in seen or seen.add(n))]
                if len(deduped) > 1:
                    options = [
                        {'label': name, 'command': f"take {item_id} from {cont_id}"}
                        for item_id, name in deduped
                    ]
                    return self._clarification_response(f"Which {item_part}?", options)

            return self._container.handle_take_from(
                f"{item_part} from {cont_part}"
            )

        if ' in ' in cmd and (cmd.startswith('put ') or cmd.startswith('place ')):
            prefix_len = 4 if cmd.startswith('put ') else 6
            parts = cmd.split(' in ', 1)
            item_part = parts[0][prefix_len:].strip()
            cont_part = parts[1].strip()
            item_matches = self._resolve_all(item_part, 'inventory')
            if len(item_matches) > 1:
                options = [
                    {'label': name, 'command': f"put {item_id} in {cont_part}"}
                    for item_id, name in item_matches
                ]
                return self._clarification_response(f"Which {item_part}?", options)
            return self._container.handle_put_in(
                f"{item_part} in {cont_part}"
            )

        if ' on ' in cmd and (cmd.startswith('put ') or cmd.startswith('place ')):
            prefix_len = 4 if cmd.startswith('put ') else 6
            parts = cmd.split(' on ', 1)
            item_part = parts[0][prefix_len:].strip()
            if item_part:
                surf_part = parts[1].strip()
                item_matches = self._resolve_all(item_part, 'inventory')
                seen = set()
                item_matches = [(i, n) for i, n in item_matches if not (n in seen or seen.add(n))]
                if len(item_matches) > 1:
                    options = [
                        {'label': name, 'command': f"put {item_id} on {surf_part}"}
                        for item_id, name in item_matches
                    ]
                    return self._clarification_response(f"Which {item_part}?", options)
                resolved = self._resolve(item_part, 'inventory')
                item_obj = next(
                    (i for i in game_manager.player.get_inventory() if i.id == resolved),
                    None
                )
                surface_resolved = self._resolve(surf_part, 'room_fixed')
                surface_obj = next(
                    (o for o in game_manager.get_current_room().objects
                     if isinstance(o, SurfaceModel) and o.id == surface_resolved),
                    None
                )
                if item_obj and getattr(item_obj, 'equip_slot', None) and not surface_obj:
                    return self._equip.handle_wear(resolved)
                return self._container.handle_put_on(
                    f"{item_part} on {surf_part}"
                )

        words = cmd.split()

        for i in range(len(words), 0, -1):
            verb = ' '.join(words[:i])
            if verb in self.commands:
                args = ' '.join(words[i:])

                # ── Check for ambiguity before dispatching ────
                clarification = self._check_ambiguity(verb, args)
                if clarification:
                    return clarification

                # ── Resolve target to ID before dispatching ───
                args = self._resolve_for_verb(verb, args)
                return self.commands[verb](args)

        return self._unknown(cmd)

    # ── Helpers ──────────────────────────────────────────────

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
