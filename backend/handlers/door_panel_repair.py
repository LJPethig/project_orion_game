# backend/handlers/door_panel_repair.py
"""
DoorPanelRepairHandler — diagnosis and repair of door access panels.

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
from backend.handlers.repair_utils import (
    calc_repair_real_seconds,
    calc_diagnose_real_seconds,
    item_name,
    component_display_name,
    check_tools,
    format_duration,
)
from config import REPAIR_PROFILES_PATH, DOOR_PANEL_TYPES_PATH, \
                   DIAG_ACCESS_OVERHEAD, DIAG_TIME_JITTER


class DoorPanelRepairHandler(BaseHandler):

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

        if panel.is_diagnosed:
            # Actuator reset only — Jack can see the lever, no full diagnosis needed
            if panel.broken_components == ['actuator_reset']:
                return self._instant(
                    f"You can see the {exit_label} door emergency release lever has been activated. "
                    f"The mechanism needs resetting before the door can be operated."
                )
            profile = self._profiles.get(panel.panel_type)
            fault_names = []
            for c in panel.broken_components:
                if c == 'actuator_reset':
                    fault_names.append('Emergency release actuator reset required')
                else:
                    comp = next((x for x in profile['components'] if x.get('item_id') == c), None)
                    fault_names.append(component_display_name(comp) if comp else c)
            tool_names = [item_name(t) for t in profile['repair_tools_required']]
            return {
                'response': f"The {exit_label} access panel has already been diagnosed.",
                'action_type': 'repair_message',
                'lock_input': False,
                'room_changed': False,
                'faults': fault_names,
                'tools': tool_names,
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

        return self.begin_next_repair(panel, door, exit_label)

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
        broken_components is populated here before the timer starts, so diagnosis
        time reflects only what actually failed. diagnose_complete reads it back.
        """
        profile = self._profiles.get(panel.panel_type)
        if not profile:
            return self._instant(f"No repair profile found for panel type '{panel.panel_type}'.")

        # ── Check room power ──────────────────────────────────
        current_room = game_manager.get_current_room()
        if not game_manager.electrical_system.check_room_power(current_room.id):
            access_mins = 5
            real_seconds = calc_diagnose_real_seconds(access_mins)
            panel_model = self._panel_types.get(panel.panel_type, {}).get('model', panel.panel_type)
            return {
                'response': f"Opening the {exit_label} access panel...",
                'action_type': 'diagnose_panel_no_power',
                'lock_input': True,
                'real_seconds': real_seconds,
                'game_minutes': access_mins,
                'room_changed': False,
                'panel_model': panel_model,
            }

        # ── Check diag tools ──────────────────────────────────
        missing_tools = check_tools(profile['diag_tools_required'], game_manager.player)
        if missing_tools:
            names = [item_name(t) for t in missing_tools]
            return {
                'response': '',
                'action_type': 'repair_message',
                'lock_input': False,
                'room_changed': False,
                'tools': names,
                'tools_label': 'You require the following tools to carry out this diagnosis:',
            }

        # ── Check scan tool has the correct manual ────────────
        manual_warning = ''
        manual_check = self._check_scan_tool_manual(panel)
        if manual_check == 'NO_SCAN_TOOL':
            return self._instant("You need a scan tool to diagnose this panel.")
        elif manual_check:
            manual_warning = (
                f"WARNING : This scan tool does not have the required software "
                f"to diagnose {manual_check}. Proceeding with any diagnosis may result in "
                f"unexpected consequences. Enso VeilTech accepts no responsibility for any resulting damage to property or loss of life. "
                f"Failure to update this tool before proceeding will result in forfeiture "
                f"of any and all rights as specified in Section 15 subsection 13c of your employment contract. "
                f"Resulting in your immediate dismissal and subsequent punitive damages. \n\n"
            )

        # ── Calculate diagnosis time from pre-set broken components ───────────
        # broken_components are set at break time by the event system.
        # Diagnosis reveals what is already stored — no selection here.
        if not panel.broken_components:
            raise ValueError(
                f"[DoorPanelRepair] panel '{panel.panel_id}' is_broken=True but broken_components "
                f"is empty. Components must be set at break time by the event system."
            )
        broken = [
            c for c in profile['components']
            if c.get('item_id') in panel.broken_components
               or (c.get('type') == 'actuator_reset' and 'actuator_reset' in panel.broken_components)
        ]
        component_mins = sum(c['diag_time_mins'] for c in broken)
        access_mins = component_mins * DIAG_ACCESS_OVERHEAD
        jitter = random.uniform(1 - DIAG_TIME_JITTER, 1 + DIAG_TIME_JITTER)
        total_diag_mins = round((component_mins + access_mins) * jitter)
        real_seconds = calc_diagnose_real_seconds(total_diag_mins)

        if manual_warning:
            return {
                'response': manual_warning.strip(),
                'action_type': 'diagnose_panel_warning',
                'lock_input': False,
                'room_changed': False,
                'panel_id': panel.panel_id,
                'door_id': door.id,
                'exit_label': exit_label,
                'panel_type': panel.panel_type,
                'security_level': panel.security_level.value,
                'real_seconds': real_seconds,
                'game_minutes': total_diag_mins,
            }

        return {
            'response': f"Connecting scan tool to {exit_label} access panel. Running diagnostics...",
            'action_type': 'diagnose_panel',
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

    def complete_no_power_diagnosis(self, panel_model: str, game_minutes: int) -> dict:
        """
        Called by /no_power_diagnose_complete endpoint after timed action.
        Advances ship time and returns a message — no diagnosis state is set.
        """
        game_manager.advance_time(game_minutes)
        location_str = f"Location: {game_manager.get_current_room().name}  |  {panel_model}"
        game_manager.add_log_entry({
            'timestamp': game_manager.get_ship_time(),
            'event': 'Diagnosis incomplete',
            'location': location_str,
            'detail': 'No power — full diagnosis not possible.',
        })
        return {
            'response': f"You spent {format_duration(game_minutes)} testing the {panel_model}. "
                        f"This panel has no power — a full diagnosis is not possible until power is restored.",
            'action_type': 'instant',
            'lock_input': False,
            'room_changed': False,
        }

    def _check_scan_tool_manual(self, panel) -> str | None:
        """
        Check player carries a scan tool with the correct manual installed.
        Returns the missing manual name if not found, None if OK.
        Scan tool absence is still a hard block — returned as a string sentinel.
        """
        panel_model = self._panel_types.get(panel.panel_type, {}).get('model')
        if not panel_model:
            return None  # No model defined — skip manual check

        player = game_manager.player
        all_items = player.get_inventory() + player.equipped_items

        scan_tool = next(
            (item for item in all_items if item and getattr(item, 'id', None) == 'scan_tool'),
            None
        )
        if not scan_tool:
            return 'NO_SCAN_TOOL'

        installed = getattr(scan_tool, 'installed_manuals', [])
        if panel_model not in installed:
            return panel_model

        return None

    # ── Repair stage ──────────────────────────────────────────

    def begin_next_repair(self, panel, door, exit_label: str) -> dict:
        """
        Repair stage — check all missing tools and parts across all remaining
        unrepaired components upfront. Only begins timed action when everything
        is present.
        """
        profile = self._profiles.get(panel.panel_type)
        if not profile:
            return self._instant(f"No repair profile found for panel type '{panel.panel_type}'.")

        # ── Check repair tools — actuator_reset may override profile tools ────
        # If only actuator_reset remains: use its repair_tools_override exclusively.
        # If electronic components also remain: union of profile tools + override.
        remaining_components = [
            c for c in profile['components']
            if (c.get('item_id') in panel.broken_components or
                (c.get('type') == 'actuator_reset' and 'actuator_reset' in panel.broken_components))
               and (c.get('item_id') not in panel.repaired_components
                    and not ('actuator_reset' in panel.repaired_components and c.get('type') == 'actuator_reset'))
        ]
        actuator = next((c for c in remaining_components if c.get('type') == 'actuator_reset'), None)
        has_electronic = any(c for c in remaining_components if c.get('type') != 'actuator_reset')

        if actuator and not has_electronic and actuator.get('repair_tools_override'):
            effective_tools = list(actuator['repair_tools_override'])
        elif actuator and has_electronic and actuator.get('repair_tools_override'):
            effective_tools = list(set(profile['repair_tools_required']) | set(actuator['repair_tools_override']))
        else:
            effective_tools = profile['repair_tools_required']

        missing_tools = [item_name(t) for t in check_tools(effective_tools, game_manager.player)]

        # ── Check parts across all remaining components ───────
        missing_parts = self._check_all_parts(panel, profile)

        # ── If anything missing — return full summary ─────────
        if missing_tools or missing_parts:
            return {
                'response':     'You are missing the following items required for this repair:',
                'action_type':  'repair_message',
                'lock_input':   False,
                'room_changed': False,
                'faults':       missing_parts,
                'faults_label': 'Missing components:',
                'tools':        missing_tools,
                'tools_label':  'Missing tools:',
            }

        # ── Everything present — begin next component repair ──
        next_component = self._get_next_component(panel, profile)
        if not next_component:
            return self._instant("All diagnosed components have been repaired.")

        repair_mins = next_component['repair_time_mins']
        real_seconds = calc_repair_real_seconds(repair_mins)
        remaining = len(panel.broken_components) - len(panel.repaired_components) - 1

        # ── Actuator reset — no parts, special response ───────
        if next_component.get('type') == 'actuator_reset':
            return {
                'response': 'Resetting emergency release mechanism and reconnecting door actuator...',
                'action_type': 'repair_component',
                'lock_input': True,
                'real_seconds': real_seconds,
                'game_minutes': repair_mins,
                'room_changed': False,
                'panel_id': panel.panel_id,
                'security_level': panel.security_level.value,
                'door_id': door.id,
                'exit_label': exit_label,
                'component_id': 'actuator_reset',
                'components_remaining': remaining,
            }

        next_item_name = item_name(next_component['item_id'])
        return {
            'response': f"Replacing {next_item_name}...",
            'action_type': 'repair_component',
            'lock_input': True,
            'real_seconds': real_seconds,
            'game_minutes': repair_mins,
            'room_changed': False,
            'panel_id': panel.panel_id,
            'security_level': panel.security_level.value,
            'door_id': door.id,
            'exit_label': exit_label,
            'component_id': next_component['item_id'],
            'components_remaining': remaining,
        }

    def _get_next_component(self, panel, profile) -> dict | None:
        """Return the profile entry for the next unrepaired broken component."""
        for component in profile['components']:
            if component.get('type') == 'actuator_reset':
                if 'actuator_reset' in panel.broken_components and 'actuator_reset' not in panel.repaired_components:
                    return component
            else:
                item_id = component['item_id']
                if item_id in panel.broken_components and item_id not in panel.repaired_components:
                    return component
        return None

    def _check_all_parts(self, panel, profile) -> list:
        """
        Check player has all required parts across all remaining unrepaired components.
        Returns a list of human-readable missing part descriptions.
        """
        missing = []
        inventory = game_manager.player.get_inventory()

        for component in profile['components']:
            if component.get('type') == 'actuator_reset':
                continue  # No parts required for actuator reset
            item_id = component['item_id']
            if item_id not in panel.broken_components:
                continue
            if item_id in panel.repaired_components:
                continue

            name = item_name(item_id)

            if 'length_m' in component:
                required = component['length_m']
                spool = next(
                    (item for item in inventory
                     if getattr(item, 'id', None) == item_id
                     and getattr(item, 'length_m', 0) >= required),
                    None
                )
                if not spool:
                    missing.append(f"{required}m {name}")
            else:
                qty_required = component.get('qty', 1)
                matches = [
                    item for item in inventory
                    if getattr(item, 'id', None) == item_id
                ]
                if len(matches) < qty_required:
                    missing.append(name if qty_required == 1 else f"{qty_required}x {name}")

        return missing

    # ── Completion (called from repair_handler.py endpoints) ──

    def complete_diagnosis(self, panel_id: str, door_id: str, game_minutes: int,
                               exit_label: str = 'unknown') -> dict:
        """
        Called by /diagnose_complete endpoint after timed action.
        Broken components were already selected in _begin_diagnosis — this method
        reads them back, advances ship time, writes the log, and returns the
        diagnosis report.
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

        # ── Broken components already set in _begin_diagnosis ─────────────────
        # Reconstruct broken list from panel state for response building.
        all_components = profile['components']
        broken = [c for c in all_components if c.get('item_id') in panel.broken_components]
        if 'actuator_reset' in panel.broken_components:
            actuator_entry = next((c for c in all_components if c.get('type') == 'actuator_reset'), None)
            if actuator_entry:
                broken.append(actuator_entry)

        # ── Mark panel as diagnosed ───────────────────────────
        panel.is_diagnosed = True

        # ── Advance ship time ─────────────────────────────────
        # game_minutes was calculated in _begin_diagnosis and passed back
        # by the frontend unchanged via the diagnose_complete endpoint.
        total_diag_mins = game_minutes
        game_manager.advance_time(total_diag_mins)

        # ── Build response ────────────────────────────────────
        panel_model = self._panel_types.get(panel.panel_type, {}).get('model', panel.panel_type)
        fault_names = []
        for c in broken:
            if c.get('type') == 'actuator_reset':
                fault_names.append('Emergency release actuator reset required')
            else:
                fault_names.append(component_display_name(c))
        duration = format_duration(total_diag_mins)

        # Check what the player is missing for the repair
        missing_parts = self._check_all_parts(panel, profile)
        missing_tools = [item_name(t) for t in check_tools(profile['repair_tools_required'], game_manager.player)]
        missing_items = missing_tools + missing_parts

        # ── Write ship log and tablet note ────────────────────
        location_str = f"Location: {game_manager.get_current_room().name}  |  {exit_label} door panel  {panel_model}"
        fault_str = ', '.join(fault_names)
        game_manager.add_log_entry({
            'timestamp': game_manager.get_ship_time(),
            'event': 'Diagnosis complete',
            'location': location_str,
            'detail': f"Faults: {fault_str}",
        })
        game_manager.set_tablet_note(panel_id, {
            'timestamp': game_manager.get_ship_time(),
            'location_str': location_str,
            'faults': fault_names,
            'tools': [item_name(t) for t in profile['repair_tools_required']],
            'missing': missing_items,
            'panel_id': panel_id,
            'door_id': door_id,
        })

        return {
            'response': f"You spent {duration} diagnosing the {panel_model}.",
            'action_type': 'diagnose_complete',
            'lock_input': False,
            'room_changed': False,
            'panel_id': panel_id,
            'door_id': door_id,
            'panel_model': panel_model,
            'faults': fault_names,
            'faults_label': 'You determined these components are faulty:',
            'tools': [item_name(t) for t in profile['repair_tools_required']],
            'tools_label': 'This repair will require the following tools:',
            'missing_items': missing_items,
            'parts': [
                {'name': component_display_name(c), 'qty': c.get('qty'), 'length_m': c.get('length_m')}
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

        profile = self._profiles.get(panel.panel_type)

        # ── Resolve component — actuator_reset has no item_id ─
        if component_id == 'actuator_reset':
            component = next((c for c in profile['components'] if c.get('type') == 'actuator_reset'), None)
        else:
            component = next((c for c in profile['components'] if c.get('item_id') == component_id), None)

        if not component:
            return {'error': f"Component '{component_id}' not in profile"}

        # ── Consume parts from inventory (not for actuator_reset) ─
        if component_id != 'actuator_reset':
            self._consume_parts(component)

        # ── Mark component repaired ───────────────────────────
        panel.repaired_components.append(component_id)
        game_manager.advance_time(component['repair_time_mins'])

        repaired_item_name = 'Emergency release actuator' if component_id == 'actuator_reset' else item_name(
            component_id)

        # ── Check if all broken components are repaired ───────
        if set(panel.repaired_components) == set(panel.broken_components):
            # TODO: post-repair failure roll — always succeeds for now
            # ── Write ship log, delete tablet note ────────────
            panel_model = self._panel_types.get(panel.panel_type, {}).get('model', panel.panel_type)
            current_room = game_manager.get_current_room()
            location_str = f"Location: {current_room.name}  |  {exit_label} door panel  {panel_model}"
            components_str = ', '.join(
                'actuator reset' if c == 'actuator_reset' else item_name(c)
                for c in panel.broken_components
            )
            total_repair_mins = sum(
                c['repair_time_mins'] for c in profile['components']
                if c.get('item_id') in panel.broken_components
                or (c.get('type') == 'actuator_reset' and 'actuator_reset' in panel.broken_components)
            )
            repair_duration = format_duration(total_repair_mins)
            game_manager.add_log_entry({
                'timestamp': game_manager.get_ship_time(),
                'event': 'Repair complete',
                'location': location_str,
                'detail': f"Components Replaced: {components_str}",
            })
            game_manager.delete_tablet_note(panel_id)

            panel.is_broken = False
            panel.is_diagnosed = False
            panel.broken_components = []
            panel.repaired_components = []

            # ── Clear emergency_released if actuator was reset ─
            if 'actuator_reset' in panel.repaired_components or door.emergency_released:
                door.emergency_released = False

            resolved_events = game_manager.event_system.check_event_resolution(game_manager)

            return {
                'response': f"You spent {repair_duration} repairing the {panel_model} to {exit_label}. Another successful job completed.",
                'action_type': 'repair_complete',
                'lock_input': False,
                'room_changed': False,
                'panel_restored': True,
                'security_level': panel.security_level.value,
                'door_id': door_id,
                'resolved_events': resolved_events,
            }

        # ── More components to repair ─────────────────────────
        return {
            'response':        f"{repaired_item_name} replaced. Preparing next component.",
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


door_panel_repair_handler = DoorPanelRepairHandler()
