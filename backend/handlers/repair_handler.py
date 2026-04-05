# backend/handlers/repair_handler.py
"""
RepairHandler — handles 'repair <target>' command.

Stateful, data-driven repair system. Reads repair_profiles.json for tool
requirements, component lists, diagnosis and repair times.

State machine per panel:
  is_broken = False
    → already operational, nothing to do

  is_broken = True, broken_components empty
    → diagnosis stage: check diag tools + scan tool manual, timed action

  is_broken = True, broken_components populated, unrepaired components remain
    → repair stage: check repair tools + parts for next component, timed action

Repair is per-component. Player may leave between components and resume.
Diagnosis is atomic — cannot be interrupted.

Completion: repaired_components == broken_components
Post-repair failure roll: hook only — always succeeds for now.
"""

import json
import random
from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager
from config import REPAIR_REAL_SECONDS, DIAGNOSE_REAL_SECONDS, \
                   REPAIR_PROFILES_PATH, DOOR_PANEL_TYPES_PATH


def calc_repair_real_seconds(game_minutes: int) -> int:
    """
    Calculate real seconds for a repair action from total game minutes.
    TODO: implement proper scaling with cap when difficulty system is built.
    Delete REPAIR_REAL_SECONDS from config.py at that point.
    """
    return REPAIR_REAL_SECONDS


def calc_diagnose_real_seconds(game_minutes: int) -> int:
    """
    Calculate real seconds for a diagnosis action from total game minutes.
    TODO: implement proper scaling with cap when difficulty system is built.
    Delete DIAGNOSE_REAL_SECONDS from config.py at that point.
    """
    return DIAGNOSE_REAL_SECONDS


class RepairHandler(BaseHandler):

    def __init__(self):
        # Load repair profiles
        with open(REPAIR_PROFILES_PATH, 'r', encoding='utf-8') as f:
            self._profiles = json.load(f)

        # Load panel type definitions for model name lookup
        with open(DOOR_PANEL_TYPES_PATH, 'r', encoding='utf-8') as f:
            self._panel_types = json.load(f)

    def handle_diagnose(self, args: str) -> dict:
        """Entry point for 'diagnose <target>' command."""
        current_room = game_manager.get_current_room()
        broken = game_manager.ship.get_broken_panels_in_room(current_room.id)

        if not broken:
            return self._instant("There are no damaged door access panels in this room.")

        panel, door, exit_label = self._resolve_target(args, broken, verb='diagnose')
        if isinstance(panel, dict):
            return panel  # error or clarification response

        if panel.broken_components:
            profile     = self._profiles.get(panel.panel_type)
            fault_names = [self._item_name(c) for c in panel.broken_components]
            tool_names  = [self._item_name(t) for t in profile['repair_tools_required']]
            return {
                'response':     f"The {exit_label} access panel has already been diagnosed.",
                'action_type':  'repair_message',
                'lock_input':   False,
                'room_changed': False,
                'faults':       fault_names,
                'tools':        tool_names,
            }

        return self._begin_diagnosis(panel, door, exit_label)

    def handle_repair(self, args: str) -> dict:
        """Entry point for 'repair <target>' command."""
        current_room = game_manager.get_current_room()
        broken = game_manager.ship.get_broken_panels_in_room(current_room.id)

        if not broken:
            return self._instant("There are no damaged door access panels in this room.")

        panel, door, exit_label = self._resolve_target(args, broken, verb='repair')
        if isinstance(panel, dict):
            return panel  # error or clarification response

        if not panel.broken_components:
            return self._instant(
                f"The {exit_label} access panel needs to be diagnosed first "
                f"to determine any required repairs."
            )

        return self._begin_next_repair(panel, door, exit_label)

    def _resolve_target(self, args: str, broken: list, verb: str):
        """
        Resolve the target panel from args and broken panel list.
        Returns (panel, door, exit_label) on success.
        Returns a dict (error or clarification response) on failure.
        """
        current_room = game_manager.get_current_room()
        target  = args.strip().lower()
        noise   = ['door access panel', 'access panel', 'door panel',
                   'access door', 'access', 'panel', 'hatch', 'door', 'doors']
        cleaned = target
        for word in sorted(noise, key=len, reverse=True):
            cleaned = cleaned.replace(word, '').strip()

        if not target or not cleaned:
            if len(broken) == 1:
                return broken[0]  # (panel, door, exit_label)

            options = [
                {'label': label, 'command': f"{verb} panel {label.lower()}"}
                for _, _, label in broken
            ]
            return ({
                'response':     f"There are {len(broken)} damaged door access panels here. Which do you want to {verb}?",
                'action_type':  'clarification_required',
                'lock_input':   False,
                'room_changed': False,
                'options':      options,
            }, None, None)

        matched_exit = self._find_exit(current_room, target)
        if matched_exit:
            exit_data = current_room.exits[matched_exit]
            door = exit_data.get('door')
            if door:
                panel = door.get_panel_for_room(current_room.id)
                if panel and panel.is_broken:
                    target_room = game_manager.ship.get_room(door.get_other_room_id(current_room.id))
                    exit_label  = exit_data.get('label') or (target_room.name if target_room else target)
                    return panel, door, exit_label
                elif panel and not panel.is_broken:
                    target_room = game_manager.ship.get_room(door.get_other_room_id(current_room.id))
                    name = target_room.name if target_room else target
                    return self._instant(f"The {name} door access panel is operational."), None, None

        return self._instant(f"No damaged door access panel found for '{args.strip()}'."), None, None

    # ── Diagnosis stage ───────────────────────────────────────

    def _begin_diagnosis(self, panel, door, exit_label: str) -> dict:
        """
        Diagnosis stage — check tools and scan tool manual, return timed action.
        broken_components is populated by diagnose_complete endpoint.
        """
        profile = self._profiles.get(panel.panel_type)
        if not profile:
            return self._instant(f"No repair profile found for panel type '{panel.panel_type}'.")

        # ── Check diag tools ──────────────────────────────────
        missing_tools = self._check_tools(profile['diag_tools_required'])
        if missing_tools:
            names = [self._item_name(t) for t in missing_tools]
            return {
                'response': '',
                'action_type': 'repair_message',
                'lock_input': False,
                'room_changed': False,
                'tools': names,
                'tools_label': 'You require the following tools to carry out this diagnosis:',
            }

        # ── Check scan tool has the correct manual ────────────
        manual_check = self._check_scan_tool_manual(panel)
        if manual_check:
            return manual_check

        # ── Sum diagnosis time across all profile components ──
        total_diag_mins = sum(c['diag_time_mins'] for c in profile['components'])
        real_seconds    = calc_diagnose_real_seconds(total_diag_mins)

        panel_model = self._panel_types.get(panel.panel_type, {}).get('model', panel.panel_type)

        return {
            'response':        f"Connecting scan tool to {exit_label} access panel. Running diagnostics...",
            'action_type':     'diagnose_panel',
            'lock_input':      True,
            'real_seconds':    real_seconds,
            'game_minutes':    total_diag_mins,
            'room_changed':    False,
            'panel_id':        panel.panel_id,
            'door_id':         door.id,
            'exit_label':      exit_label,
            'panel_type':      panel.panel_type,
            'security_level': panel.security_level.value,
        }

    def _check_scan_tool_manual(self, panel) -> dict | None:
        """
        Check player carries a scan tool with the correct manual installed.
        Returns an error response if not, None if OK.
        """
        panel_model = self._panel_types.get(panel.panel_type, {}).get('model')
        if not panel_model:
            return self._instant(f"Panel type '{panel.panel_type}' has no model definition.")

        player = game_manager.player
        all_items = player.get_inventory() + player.equipped_items

        scan_tool = next(
            (item for item in all_items if item and getattr(item, 'id', None) == 'scan_tool'),
            None
        )
        if not scan_tool:
            return self._instant("You need a scan tool to diagnose this panel.")

        installed = getattr(scan_tool, 'installed_manuals', [])
        if panel_model not in installed:
            return self._instant(
                f"Your scan tool does not have a manual for the {panel_model}. "
                f"A software update is required."
            )
        return None

    # ── Repair stage ──────────────────────────────────────────

    def _begin_next_repair(self, panel, door, exit_label: str) -> dict:
        """
        Repair stage — find next unrepaired component, check tools and parts,
        return timed action for that component.
        """
        profile = self._profiles.get(panel.panel_type)
        if not profile:
            return self._instant(f"No repair profile found for panel type '{panel.panel_type}'.")

        # ── Check repair tools ────────────────────────────────
        missing_tools = self._check_tools(profile['repair_tools_required'])
        if missing_tools:
            names = [self._item_name(t) for t in missing_tools]
            return {
                'response': '',
                'action_type': 'repair_message',
                'lock_input': False,
                'room_changed': False,
                'tools': names,
                'tools_label': 'You are missing the following tools required for this repair:',
            }

        # ── Find next unrepaired component ────────────────────
        next_component = self._get_next_component(panel, profile)
        if not next_component:
            return self._instant("All diagnosed components have been repaired.")

        # ── Check parts in inventory ──────────────────────────
        parts_check = self._check_parts(next_component)
        if parts_check:
            return parts_check

        item_name    = self._item_name(next_component['item_id'])
        repair_mins  = next_component['repair_time_mins']
        real_seconds = calc_repair_real_seconds(repair_mins)

        remaining = len(panel.broken_components) - len(panel.repaired_components) - 1

        return {
            'response':        f"Replacing {item_name}...",
            'action_type':     'repair_component',
            'lock_input':      True,
            'real_seconds':    real_seconds,
            'game_minutes':    repair_mins,
            'room_changed':    False,
            'panel_id':        panel.panel_id,
            'security_level': panel.security_level.value,
            'door_id':         door.id,
            'exit_label':      exit_label,
            'component_id':    next_component['item_id'],
            'components_remaining': remaining,
        }

    def _get_next_component(self, panel, profile) -> dict | None:
        """Return the profile entry for the next unrepaired broken component."""
        for component in profile['components']:
            item_id = component['item_id']
            if item_id in panel.broken_components and item_id not in panel.repaired_components:
                return component
        return None

    def _check_parts(self, component: dict) -> dict | None:
        """
        Check player has required parts for this component.
        Returns error response if missing, None if OK.
        """
        item_id  = component['item_id']
        player   = game_manager.player
        all_items = player.get_inventory()

        if 'length_m' in component:
            required_length = component['length_m']
            spool = next(
                (item for item in all_items
                 if getattr(item, 'id', None) == item_id
                 and getattr(item, 'length_m', 0) >= required_length),
                None
            )
            if not spool:
                item_name = self._item_name(item_id)
                return self._instant(
                    f"You need at least {required_length}m of {item_name} to complete this repair."
                )
        else:
            qty_required = component.get('qty', 1)
            matches = [
                item for item in all_items
                if getattr(item, 'id', None) == item_id
            ]
            if len(matches) < qty_required:
                item_name = self._item_name(item_id)
                return self._instant(
                    f"You need {qty_required}x {item_name} to complete this repair."
                )
        return None

    # ── Completion (called from command.py endpoints) ─────────

    def complete_diagnosis(self, panel_id: str, door_id: str) -> dict:
        """
        Called by /diagnose_complete endpoint after timed action.
        Randomly selects broken components from profile, populates panel.broken_components.
        Returns diagnosis report.
        """
        door = game_manager.ship.get_door_by_id(door_id)
        if not door:
            return {'error': 'Door not found'}

        panel = next((p for p in door.panels.values() if p.panel_id == panel_id), None)
        if not panel:
            return {'error': 'Panel not found'}

        profile = self._profiles.get(panel.panel_type)
        if not profile:
            return {'error': f"No repair profile for '{panel.panel_type}'"}

        # ── Randomly select broken components ─────────────────
        # 1 to 3 components fail, weighted toward fewer failures
        all_components = profile['components']
        max_failures   = min(3, len(all_components))
        num_failures   = random.choices(
            range(1, max_failures + 1),
            weights=[60, 30, 10][:max_failures],
            k=1
        )[0]
        broken = random.sample(all_components, num_failures)
        panel.broken_components = [c['item_id'] for c in broken]

        # ── Advance ship time ─────────────────────────────────
        total_diag_mins = sum(c['diag_time_mins'] for c in broken)
        game_manager.advance_time(total_diag_mins)

        # ── Build response ────────────────────────────────────
        panel_model  = self._panel_types.get(panel.panel_type, {}).get('model', panel.panel_type)
        fault_names  = [self._item_name(c['item_id']) for c in broken]
        faults_str   = ', '.join(fault_names)

        # Parts needed
        parts_lines = []
        for c in broken:
            name = self._item_name(c['item_id'])
            if 'length_m' in c:
                parts_lines.append(f"  {c['length_m']}m {name}")
            else:
                parts_lines.append(f"  {c.get('qty', 1)}x {name}")

        tools_needed = ', '.join(self._item_name(t) for t in profile['repair_tools_required'])
        parts_str    = '\n'.join(parts_lines)

        return {
            'response':     f"Diagnostic tests on {panel_model} are complete.",
            'action_type':  'diagnose_complete',
            'lock_input':   False,
            'room_changed': False,
            'panel_id':     panel_id,
            'door_id':      door_id,
            'panel_model':  panel_model,
            'faults':       fault_names,
            'tools':        [self._item_name(t) for t in profile['repair_tools_required']],
            'parts':        [
                {'name': self._item_name(c['item_id']), 'qty': c.get('qty'), 'length_m': c.get('length_m')}
                for c in broken
            ],
        }

    def complete_component_repair(self, panel_id: str, door_id: str,
                                  component_id: str, exit_label: str) -> dict:
        """
        Called by /repair_complete endpoint after timed action.
        Consumes parts, marks component repaired, checks if panel is fully repaired.
        """
        door = game_manager.ship.get_door_by_id(door_id)
        if not door:
            return {'error': 'Door not found'}

        panel = next((p for p in door.panels.values() if p.panel_id == panel_id), None)
        if not panel:
            return {'error': 'Panel not found'}

        profile   = self._profiles.get(panel.panel_type)
        component = next((c for c in profile['components'] if c['item_id'] == component_id), None)
        if not component:
            return {'error': f"Component '{component_id}' not in profile"}

        # ── Consume parts from inventory ──────────────────────
        self._consume_parts(component)

        # ── Mark component repaired ───────────────────────────
        panel.repaired_components.append(component_id)
        game_manager.advance_time(component['repair_time_mins'])

        item_name = self._item_name(component_id)

        # ── Check if all broken components are repaired ───────
        if set(panel.repaired_components) == set(panel.broken_components):
            # TODO: post-repair failure roll — always succeeds for now
            panel.is_broken           = False
            panel.broken_components   = []
            panel.repaired_components = []

            return {
                'response':       f"{item_name} replaced. The {exit_label} access panel is now operational.",
                'action_type':    'repair_complete',
                'lock_input':     False,
                'room_changed':   False,
                'panel_restored': True,
                'security_level': door.security_level,
                'door_id':        door_id,
            }

        # ── More components to repair ─────────────────────────
        remaining = len(panel.broken_components) - len(panel.repaired_components)
        return {
            'response':        f"{item_name} replaced. {remaining} component{'s' if remaining > 1 else ''} remaining.",
            'action_type':     'repair_complete',
            'lock_input':      False,
            'room_changed':    False,
            'panel_restored':  False,
            'door_id':         door_id,
            'panel_id':        panel_id,
            'exit_label':      exit_label,
        }

    def _consume_parts(self, component: dict) -> None:
        """Remove required parts from player inventory."""
        item_id  = component['item_id']
        player   = game_manager.player

        if 'length_m' in component:
            required = component['length_m']
            spool = next(
                (item for item in player.get_inventory()
                 if getattr(item, 'id', None) == item_id
                 and getattr(item, 'length_m', 0) >= required),
                None
            )
            if spool:
                spool.length_m = round(spool.length_m - required, 4)
                spool.mass     = round(spool.length_m * spool.mass_per_metre, 4)
        else:
            qty = component.get('qty', 1)
            removed = 0
            for item in player.get_inventory():
                if getattr(item, 'id', None) == item_id and removed < qty:
                    player.remove_from_inventory(item)
                    removed += 1

    # ── Helpers ───────────────────────────────────────────────

    def _check_tools(self, tool_ids: list) -> list:
        """Return list of tool ids the player is missing."""
        player    = game_manager.player
        all_items = player.get_inventory() + player.equipped_items
        held_ids = {getattr(item, 'id', None) for item in all_items if item}
        return [t for t in tool_ids if t not in held_ids]

    def _item_name(self, item_id: str) -> str:
        """Look up item display name from registry. Falls back to item_id."""
        from backend.loaders.item_loader import load_item_registry
        registry = load_item_registry()
        data = registry.get(item_id)
        return data['name'] if data else item_id


repair_handler = RepairHandler()
