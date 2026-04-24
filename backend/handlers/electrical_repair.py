# backend/handlers/electrical_repair.py
"""
ElectricalRepairHandler — diagnosis and repair of electrical junction panels.

Stateful, data-driven repair system. Reads electrical_repair_profiles.json
for component lists, tool requirements, diagnosis and repair times.

Keyed by panel_id (e.g. 'PNL-REC-SUB-C') — each entry covers all components
owned by that junction: internal parts (logic board, bus bar, surge protector,
smoothing capacitor, isolation switch), breakers, and cables.

Broken component state is determined by reading the live electrical system —
not randomly selected. The event system sets damage before diagnosis runs.

Repair state (broken_components, repaired_components) is stored on the
PowerJunction fixed object in the room.

Sub-handler of repair_handler.py. Shares utilities from repair_utils.py.

State machine per junction:
  broken_components empty
    → diagnosis stage: check tools, read electrical state, timed action

  broken_components populated, unrepaired components remain
    → repair stage: check tools + parts, timed action per component

  repaired_components == broken_components
    → repair complete, fix called for each component, state cleared
"""

import json
import random
from backend.handlers.base_handler import BaseHandler
from backend.models.game_manager import game_manager
from backend.handlers.repair_utils import (
    calc_diagnose_real_seconds,
    calc_repair_real_seconds,
    item_name,
    check_tools,
    format_duration,
)
from config import ELECTRICAL_REPAIR_PROFILES_PATH, DIAG_ACCESS_OVERHEAD, DIAG_TIME_JITTER


# Maps profile item_id → CircuitPanel flag name for internal components
_INTERNAL_COMPONENT_FLAGS = {
    'hv_logic_board':         'logic_board_intact',
    'hv_bus_bar':             'bus_bar_intact',
    'hv_surge_protector':     'surge_protector_intact',
    'hv_smoothing_capacitor': 'smoothing_capacitor_intact',
    'hv_isolation_switch':    'isolation_switch_intact',
}


class ElectricalRepairHandler(BaseHandler):

    def __init__(self):
        with open(ELECTRICAL_REPAIR_PROFILES_PATH, 'r', encoding='utf-8') as f:
            self._profiles = json.load(f)

        if not self._profiles:
            raise ValueError(
                f"electrical_repair_profiles.json loaded empty — "
                f"check {ELECTRICAL_REPAIR_PROFILES_PATH}"
            )

    # ── Entry points ──────────────────────────────────────────

    def handle_diagnose(self, junction) -> dict:
        """Entry point for 'diagnose junction' command."""
        profile = self._profiles.get(junction.panel_id)
        if not profile:
            return self._instant(f"No repair profile found for junction '{junction.panel_id}'.")

        # ── Already diagnosed — return existing report ─────────
        if junction.broken_components:
            fault_names = self._fault_names_for(junction, profile)
            tool_names  = [item_name(t) for t in profile['repair_tools_required']]
            return {
                'response':     f"{junction.panel_id} has already been diagnosed.",
                'action_type':  'repair_message',
                'lock_input':   False,
                'room_changed': False,
                'faults':       fault_names,
                'tools':        tool_names,
            }

        return self._begin_diagnosis(junction, profile)

    def handle_repair(self, junction) -> dict:
        """Entry point for 'repair junction' command."""
        profile = self._profiles.get(junction.panel_id)
        if not profile:
            return self._instant(f"No repair profile found for junction '{junction.panel_id}'.")

        if not junction.broken_components:
            return self._instant(
                f"{junction.panel_id} needs to be diagnosed first "
                f"to determine any required repairs."
            )

        return self.begin_next_repair(junction, profile)

    def get_profile(self, panel_id: str) -> dict | None:
        """Return the repair profile for the given panel_id, or None if not found."""
        return self._profiles.get(panel_id)

    # ── Diagnosis stage ───────────────────────────────────────

    def _begin_diagnosis(self, junction, profile: dict) -> dict:
        """
        Diagnosis stage — check tools, read live electrical state to determine
        broken components, return timed action.
        broken_components populated here before timer starts.
        elec_diagnose_complete reads it back after the wait.
        """

        # ── Check diag tools ──────────────────────────────────
        missing_tools = check_tools(profile['diag_tools_required'], game_manager.player)
        if missing_tools:
            names = [item_name(t) for t in missing_tools]
            return {
                'response':     '',
                'action_type':  'repair_message',
                'lock_input':   False,
                'room_changed': False,
                'tools':        names,
                'tools_label':  'You require the following tools to carry out this diagnosis:',
            }

        # ── Read live electrical state — build broken list ────
        sys           = game_manager.electrical_system
        circuit_panel = sys.panels.get(junction.panel_id)
        broken_ids    = []

        for component in profile['components']:
            eid     = component.get('electrical_id')
            item_id = component['item_id']

            if eid is None:
                # Internal component — check its flag on the CircuitPanel
                flag = _INTERNAL_COMPONENT_FLAGS.get(item_id)
                if flag and circuit_panel and not getattr(circuit_panel, flag, True):
                    broken_ids.append(item_id)

            else:
                # Skip emergency bypass cables unless connected
                if component.get('emergency_bypass'):
                    cable = sys.cables.get(eid)
                    if cable and not cable.connected:
                        continue

                if eid in sys.breakers:
                    if not sys.breakers[eid].operational:
                        broken_ids.append(eid)
                elif eid in sys.cables:
                    if not sys.cables[eid].intact:
                        broken_ids.append(eid)
                elif eid in sys.panels:
                    if not sys.panels[eid].operational:
                        broken_ids.append(eid)

        junction.broken_components = broken_ids

        # ── Calculate diagnosis time ──────────────────────────
        component_mins = self._calc_diag_mins(broken_ids, profile)

        if component_mins == 0:
            # Nothing broken — short access time only
            access_mins  = round(5 * random.uniform(1 - DIAG_TIME_JITTER, 1 + DIAG_TIME_JITTER))
            real_seconds = calc_diagnose_real_seconds(access_mins)
            return {
                'response':     f"Opening junction panel {junction.panel_id}. Running diagnostics...",
                'action_type':  'elec_diagnose_panel',
                'lock_input':   True,
                'real_seconds': real_seconds,
                'game_minutes': access_mins,
                'room_changed': False,
                'panel_id':     junction.panel_id,
                'no_faults':    True,
            }

        access_mins     = component_mins * DIAG_ACCESS_OVERHEAD
        jitter          = random.uniform(1 - DIAG_TIME_JITTER, 1 + DIAG_TIME_JITTER)
        total_diag_mins = round((component_mins + access_mins) * jitter)
        real_seconds    = calc_diagnose_real_seconds(total_diag_mins)

        return {
            'response':     f"Opening junction panel {junction.panel_id}. Running diagnostics...",
            'action_type':  'elec_diagnose_panel',
            'lock_input':   True,
            'real_seconds': real_seconds,
            'game_minutes': total_diag_mins,
            'room_changed': False,
            'panel_id':     junction.panel_id,
            'no_faults':    False,
        }

    # ── Completion (called from command.py endpoints) ─────────

    def complete_diagnosis(self, panel_id: str, game_minutes: int) -> dict:
        """
        Called by /elec_diagnose_complete endpoint after timed action.
        broken_components already set in _begin_diagnosis.
        Advances ship time, writes log, returns diagnosis report.
        """
        junction = self._find_junction(panel_id)
        if not junction:
            return {'error': f"Junction '{panel_id}' not found in current room."}

        profile = self._profiles.get(panel_id)
        if not profile:
            return {'error': f"No repair profile for '{panel_id}'"}

        game_manager.advance_time(game_minutes)
        location_str = f"Location: {game_manager.get_current_room().name}  |  Junction {panel_id}"

        # ── No faults found ───────────────────────────────────
        if not junction.broken_components:
            duration = format_duration(game_minutes)
            game_manager.add_log_entry({
                'timestamp': game_manager.get_ship_time(),
                'event':     'Diagnosis complete',
                'location':  location_str,
                'detail':    'No faults found.',
            })
            return {
                'response':     f"You spent {duration} diagnosing {panel_id}. No faults found.",
                'action_type':  'diagnose_complete',
                'lock_input':   False,
                'room_changed': False,
                'panel_id':     panel_id,
                'faults':       [],
                'no_faults':    True,
            }

        # ── Faults found ──────────────────────────────────────
        fault_names   = self._fault_names_for(junction, profile)
        duration      = format_duration(game_minutes)
        missing_parts = self._check_all_parts(junction, profile)
        missing_tools = [item_name(t) for t in check_tools(profile['repair_tools_required'], game_manager.player)]
        missing_items = missing_tools + missing_parts

        game_manager.add_log_entry({
            'timestamp': game_manager.get_ship_time(),
            'event':     'Diagnosis complete',
            'location':  location_str,
            'detail':    f"Faults: {', '.join(fault_names)}",
        })
        game_manager.set_tablet_note(panel_id, {
            'timestamp':    game_manager.get_ship_time(),
            'location_str': location_str,
            'faults':       fault_names,
            'tools':        [item_name(t) for t in profile['repair_tools_required']],
            'missing':      missing_items,
            'panel_id':     panel_id,
        })

        return {
            'response':      f"You spent {duration} diagnosing {panel_id}.",
            'action_type':   'diagnose_complete',
            'lock_input':    False,
            'room_changed':  False,
            'panel_id':      panel_id,
            'faults':        fault_names,
            'faults_label':  'You determined these components are faulty:',
            'tools':         [item_name(t) for t in profile['repair_tools_required']],
            'tools_label':   'This repair will require the following tools:',
            'missing_items': missing_items,
            'no_faults':     False,
        }

    def begin_next_repair(self, junction, profile: dict) -> dict:
        """
        Repair stage — check all missing tools and parts across all remaining
        unrepaired components upfront. Only begins timed action when everything
        is present. Tripped breakers require no parts — reset only.
        """
        # ── Check repair tools ────────────────────────────────
        missing_tools = [item_name(t) for t in check_tools(profile['repair_tools_required'], game_manager.player)]

        # ── Check parts across all remaining components ───────
        missing_parts = self._check_all_parts(junction, profile)

        if missing_tools or missing_parts:
            return {
                'response': 'You are missing the following items required for this repair:',
                'action_type': 'repair_message',
                'lock_input': False,
                'room_changed': False,
                'faults': missing_parts,
                'faults_label': 'Missing components:',
                'tools': missing_tools,
                'tools_label': 'Missing tools:',
            }

        # ── Everything present — begin next component repair ──
        next_component = self._get_next_component(junction, profile)
        if not next_component:
            return self._instant("All diagnosed components have been repaired.")

        eid = next_component.get('electrical_id')
        item_id = next_component['item_id']
        sys = game_manager.electrical_system

        # Tripped breaker — reset only, use repair_time_tripped
        if eid and eid in sys.breakers:
            breaker = sys.breakers[eid]
            if breaker.tripped and not breaker.damaged:
                repair_mins = next_component.get('repair_time_tripped', 1)
                real_seconds = calc_repair_real_seconds(repair_mins)
                remaining = len(junction.broken_components) - len(junction.repaired_components) - 1
                return {
                    'response': f"Resetting {item_name(item_id)}...",
                    'action_type': 'elec_repair_component',
                    'lock_input': True,
                    'real_seconds': real_seconds,
                    'game_minutes': repair_mins,
                    'room_changed': False,
                    'panel_id': junction.panel_id,
                    'component_key': eid,
                    'components_remaining': remaining,
                }

        next_item_name = item_name(item_id)
        repair_mins = next_component['repair_time_mins']
        real_seconds = calc_repair_real_seconds(repair_mins)
        remaining = len(junction.broken_components) - len(junction.repaired_components) - 1

        return {
            'response': f"Replacing {next_item_name}...",
            'action_type': 'elec_repair_component',
            'lock_input': True,
            'real_seconds': real_seconds,
            'game_minutes': repair_mins,
            'room_changed': False,
            'panel_id': junction.panel_id,
            'component_key': eid if eid else item_id,
            'components_remaining': remaining,
        }

    def complete_component_repair(self, panel_id: str, component_key: str) -> dict:
        """
        Called by /elec_repair_complete endpoint after timed action.
        Consumes parts or resets tripped breaker, marks component repaired,
        calls fix_component() or fix_panel_component(), checks if all done.
        """
        junction = self._find_junction(panel_id)
        if not junction:
            return {'error': f"Junction '{panel_id}' not found in current room."}

        profile = self._profiles.get(panel_id)
        if not profile:
            return {'error': f"No repair profile for '{panel_id}'"}

        # Find the component entry by key
        component = self._get_component_by_key(component_key, profile)
        if not component:
            return {'error': f"Component '{component_key}' not in profile"}

        eid = component.get('electrical_id')
        item_id = component['item_id']
        sys = game_manager.electrical_system

        # ── Consume parts or reset tripped breaker ────────────
        if eid and eid in sys.breakers and sys.breakers[eid].tripped and not sys.breakers[eid].damaged:
            # Tripped breaker — reset only, no part consumed
            from backend.systems.electrical.electrical_service import fix_component
            fix_component(eid)
        elif eid:
            # Electrical component — consume parts and fix
            self._consume_parts(component)
            from backend.systems.electrical.electrical_service import fix_component
            fix_component(eid)
        else:
            # Internal panel component — consume parts and set flag
            self._consume_parts(component)
            circuit_panel = sys.panels.get(panel_id)
            if circuit_panel:
                flag = _INTERNAL_COMPONENT_FLAGS.get(item_id)
                if flag:
                    setattr(circuit_panel, flag, True)

        # ── Mark component repaired ───────────────────────────
        junction.repaired_components.append(component_key)
        game_manager.advance_time(component.get('repair_time_mins', component.get('repair_time_tripped', 1)))

        repaired_label = self._component_label(component)

        # ── Check if all broken components are repaired ───────
        if set(junction.repaired_components) == set(junction.broken_components):
            current_room = game_manager.get_current_room()
            location_str = f"Location: {current_room.name}  |  Junction {panel_id}"
            # Fault labels are read from the tablet note written at diagnosis time.
            # By this point fix_component() has already been called on all components
            # so live electrical state no longer reflects tripped/damaged distinction.
            # The tablet note preserves the correct labels — e.g. '32 Amp Circuit Breaker (Tripped)'.
            tablet_note = game_manager.tablet_notes[panel_id]
            components_str = ', '.join(tablet_note['faults'])
            total_repair_mins = sum(
                c.get('repair_time_mins', c.get('repair_time_tripped', 1))
                for c in profile['components']
                if (c.get('electrical_id') or c['item_id']) in junction.broken_components
            )
            repair_duration = format_duration(total_repair_mins)
            game_manager.add_log_entry({
                'timestamp': game_manager.get_ship_time(),
                'event': 'Repair complete',
                'location': location_str,
                'detail': f"Components repaired: {components_str}",
            })
            game_manager.delete_tablet_note(panel_id)

            junction.broken_components = []
            junction.repaired_components = []

            return {
                'response': f"You spent {repair_duration} repairing {panel_id}. Another successful job completed.",
                'action_type': 'elec_repair_complete',
                'lock_input': False,
                'room_changed': False,
                'panel_restored': True,
                'panel_id': panel_id,
            }

        # ── More components to repair ─────────────────────────
        return {
            'response': f"{repaired_label} repaired. Preparing next component.",
            'action_type': 'elec_repair_complete',
            'lock_input': False,
            'room_changed': False,
            'panel_restored': False,
            'panel_id': panel_id,
        }

    # ── Repair helpers ────────────────────────────────────────

    def _get_next_component(self, junction, profile: dict) -> dict | None:
        """Return the profile entry for the next unrepaired broken component."""
        for component in profile['components']:
            eid = component.get('electrical_id')
            item_id = component['item_id']
            key = item_id if eid is None else eid
            if key in junction.broken_components and key not in junction.repaired_components:
                return component
        return None

    def _get_component_by_key(self, component_key: str, profile: dict) -> dict | None:
        """Find a profile component by its electrical_id or item_id."""
        for component in profile['components']:
            eid = component.get('electrical_id')
            item_id = component['item_id']
            key = item_id if eid is None else eid
            if key == component_key:
                return component
        return None

    def _consume_parts(self, component: dict) -> None:
        """Remove required parts from player inventory."""
        item_id = component['item_id']
        player = game_manager.player

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
                spool.mass = round(spool.length_m * spool.mass_per_metre, 4)

            # Consume connectors
            connector_id = component.get('connector_id')
            connector_qty = component.get('connector_qty', 0)
            if connector_id and connector_qty:
                removed = 0
                for item in player.get_inventory():
                    if getattr(item, 'id', None) == connector_id and removed < connector_qty:
                        player.remove_from_inventory(item)
                        removed += 1
        else:
            qty = component.get('qty', 1)
            removed = 0
            for item in player.get_inventory():
                if getattr(item, 'id', None) == item_id and removed < qty:
                    player.remove_from_inventory(item)
                    removed += 1

    # ── Helpers ───────────────────────────────────────────────

    def _find_junction(self, panel_id: str):
        """Find the PowerJunction with the given panel_id in the current room."""
        from backend.models.interactable import PowerJunction
        room = game_manager.get_current_room()
        return next(
            (o for o in room.objects
             if isinstance(o, PowerJunction) and o.panel_id == panel_id),
            None
        )

    def _component_label(self, component: dict) -> str:
        """Human-readable label for a profile component."""
        if 'length_m' in component:
            return f"{item_name(component['item_id'])} ({component['length_m']}m)"
        eid = component.get('electrical_id')
        if eid:
            sys = game_manager.electrical_system
            breaker = sys.breakers.get(eid)
            if breaker and breaker.tripped and not breaker.damaged:
                return f"{item_name(component['item_id'])} (Tripped)"
        return item_name(component['item_id'])

    def _broken_component_entries(self, junction, profile: dict) -> list:
        """Return profile component entries for all broken components."""
        result = []
        for c in profile['components']:
            eid     = c.get('electrical_id')
            item_id = c['item_id']
            key     = item_id if eid is None else eid
            if key in junction.broken_components:
                result.append(c)
        return result

    def _fault_names_for(self, junction, profile: dict) -> list:
        """Return aggregated human-readable fault names for all broken components."""
        return self._aggregate_fault_names(self._broken_component_entries(junction, profile))

    def _aggregate_fault_names(self, component_entries: list) -> list:
        """
        Aggregate component entries into human-readable display strings.
        Cables of the same type are summed into a single length entry.
        Breakers are grouped by label — damaged and tripped variants stay separate
        since they require different repair actions.
        Internal parts are grouped by item_id.

        Returns a list of aggregated display strings ready for fault lists and logs.
        """
        # ── Cables — group by item_id, sum length_m and connector_qty ──────────
        cable_groups = {}
        for c in component_entries:
            if 'length_m' not in c:
                continue
            item_id = c['item_id']
            if item_id not in cable_groups:
                cable_groups[item_id] = {
                    'item_id': item_id,
                    'total_length': 0.0,
                    'connector_id': c.get('connector_id'),
                    'total_connectors': 0,
                }
            cable_groups[item_id]['total_length'] += c['length_m']
            cable_groups[item_id]['total_connectors'] += c.get('connector_qty', 0)

        # ── Non-cables — group by label (preserves Tripped distinction) ─────────
        label_counts = {}
        for c in component_entries:
            if 'length_m' in c:
                continue
            label = self._component_label(c)
            label_counts[label] = label_counts.get(label, 0) + 1

        # ── Build result list ─────────────────────────────────────────────────────
        result = []

        # Non-cables first — internal parts and breakers
        for label, count in label_counts.items():
            result.append(f"{count}x {label}" if count > 1 else label)

        # Cables
        for group in cable_groups.values():
            length = round(group['total_length'], 1)
            name = item_name(group['item_id'])
            result.append(f"{name} ({length}m)")

        return result

    def _calc_diag_mins(self, broken_ids: list, profile: dict) -> int:
        """Sum diag_time_mins for all broken components."""
        total = 0
        for component in profile['components']:
            eid     = component.get('electrical_id')
            item_id = component['item_id']
            key     = item_id if eid is None else eid
            if key in broken_ids:
                total += component['diag_time_mins']
        return total

    def _check_all_parts(self, junction, profile: dict) -> list:
        """
        Check player has all required parts for all remaining unrepaired components.
        Returns aggregated list of human-readable missing part descriptions.

        Cables of the same type are aggregated — total length checked against a
        single spool, total connectors checked against held stock.
        Breakers are aggregated by item_id — tripped breakers excluded (no part needed).
        """
        inventory = game_manager.player.get_inventory()
        sys = game_manager.electrical_system

        # ── Collect relevant components ───────────────────────────────────────────
        # Separate cables from non-cables for different aggregation logic.
        cable_components = []
        non_cable_components = []

        for component in profile['components']:
            eid = component.get('electrical_id')
            item_id = component['item_id']
            key = item_id if eid is None else eid

            if key not in junction.broken_components:
                continue
            if key in junction.repaired_components:
                continue

            # Tripped breakers need resetting only — no replacement part required
            if eid and eid in sys.breakers:
                breaker = sys.breakers.get(eid)
                if breaker and breaker.tripped and not breaker.damaged:
                    continue

            if 'length_m' in component:
                cable_components.append(component)
            else:
                non_cable_components.append(component)

        missing = []

        # ── Non-cables — group by item_id, check total qty needed ────────────────
        non_cable_totals = {}
        for c in non_cable_components:
            item_id = c['item_id']
            non_cable_totals[item_id] = non_cable_totals.get(item_id, 0) + c.get('qty', 1)

        for item_id, qty_needed in non_cable_totals.items():
            held = [i for i in inventory if getattr(i, 'id', None) == item_id]
            if len(held) < qty_needed:
                name = item_name(item_id)
                missing.append(name if qty_needed == 1 else f"{qty_needed}x {name}")

        # ── Cables — group by item_id, sum total length needed ───────────────────
        # A single spool must cover the total length required across all runs.
        cable_totals = {}
        for c in cable_components:
            item_id = c['item_id']
            if item_id not in cable_totals:
                cable_totals[item_id] = {
                    'total_length': 0.0,
                    'connector_id': c.get('connector_id'),
                    'total_connectors': 0,
                }
            cable_totals[item_id]['total_length'] += c['length_m']
            cable_totals[item_id]['total_connectors'] += c.get('connector_qty', 0)

        for item_id, totals in cable_totals.items():
            name = item_name(item_id)
            required = round(totals['total_length'], 1)
            spool = next(
                (i for i in inventory
                 if getattr(i, 'id', None) == item_id
                 and getattr(i, 'length_m', 0) >= required),
                None
            )
            if not spool:
                missing.append(f"{required}m {name}")

            connector_id = totals['connector_id']
            total_conn = totals['total_connectors']
            if connector_id and total_conn:
                connector_name = item_name(connector_id)
                held_conn = [i for i in inventory if getattr(i, 'id', None) == connector_id]
                if len(held_conn) < total_conn:
                    missing.append(
                        f"{total_conn}x {connector_name}"
                        if total_conn > 1 else connector_name
                    )

        return missing

electrical_repair_handler = ElectricalRepairHandler()
