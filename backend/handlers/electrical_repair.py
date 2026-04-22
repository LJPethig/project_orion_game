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
        return self._instant(f"Junction {junction.panel_id} found. Repair not yet implemented.")

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

        broken_components = self._broken_component_entries(junction, profile)

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
            'parts': [
                {
                    'name':     self._component_label(c),
                    'qty':      c.get('qty'),
                    'length_m': c.get('length_m'),
                }
                for c in broken_components
            ],
        }

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
        """Return human-readable fault names for all broken components."""
        return [
            self._component_label(c)
            for c in self._broken_component_entries(junction, profile)
        ]

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
        Returns list of human-readable missing part descriptions.
        Cable components also check for connectors.
        """
        missing   = []
        inventory = game_manager.player.get_inventory()

        for component in profile['components']:
            eid     = component.get('electrical_id')
            item_id = component['item_id']
            key     = item_id if eid is None else eid

            if key not in junction.broken_components:
                continue
            if key in junction.repaired_components:
                continue

            name = item_name(item_id)

            # ── Cable — check spool length and connectors ──────
            if 'length_m' in component:
                required = component['length_m']
                spool = next(
                    (i for i in inventory
                     if getattr(i, 'id', None) == item_id
                     and getattr(i, 'length_m', 0) >= required),
                    None
                )
                if not spool:
                    missing.append(f"{required}m {name}")

                connector_id  = component.get('connector_id')
                connector_qty = component.get('connector_qty', 0)
                if connector_id and connector_qty:
                    connector_name  = item_name(connector_id)
                    held = [i for i in inventory if getattr(i, 'id', None) == connector_id]
                    if len(held) < connector_qty:
                        missing.append(
                            f"{connector_qty}x {connector_name}"
                            if connector_qty > 1 else connector_name
                        )

            # ── Breaker or internal part — check qty ──────────
            else:
                qty_required = component.get('qty', 1)
                matches = [i for i in inventory if getattr(i, 'id', None) == item_id]
                if len(matches) < qty_required:
                    missing.append(name if qty_required == 1 else f"{qty_required}x {name}")

        return missing


electrical_repair_handler = ElectricalRepairHandler()
