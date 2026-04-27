# backend/events/event_system.py
"""
EventSystem — loads, schedules and fires game events from events.json.

Events fire when ship time reaches their trigger threshold.
check() is called by the frontend poll and returns any due events.

Supported event types:
  impact_event      — breaks a list of components (electrical and/or door panels)
  message_event     — delivers a message notification (stub)

Unknown event types or component IDs raise ValueError immediately — bad data in events.json must be fixed.
"""

import json
from config import EVENTS_JSON_PATH


class GameEvent:
    """A single scheduled game event."""

    def __init__(self, event_id: str, trigger_minutes: int, data: dict):
        self.event_id        = event_id
        self.trigger_minutes = trigger_minutes
        self.data            = data    # full event dict from JSON
        self.fired           = False
        self.resolved        = False


class EventSystem:
    """
    Manages all scheduled game events.
    Events fire when ship time reaches their trigger threshold.
    Resolution is set externally when the event cause is fixed.
    """

    def __init__(self):
        self._events: list[GameEvent] = []

    def load_from_json(self) -> None:
        """Load and schedule all events from events.json."""
        with open(EVENTS_JSON_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)

        for event_data in data.get('events', []):
            event_id       = event_data['id']
            trigger_minutes = event_data['trigger_minutes']
            self._events.append(GameEvent(event_id, trigger_minutes, event_data))

    def check(self, current_minutes: int) -> list[dict]:
        """
        Check for due events at the given ship time.
        Fires due events, applies their effects, returns event dicts for the frontend.
        Each dict contains at minimum: event_id, message.
        """
        from backend.systems.electrical.electrical_service import break_component
        from backend.models.game_manager import game_manager

        due = []
        for event in self._events:
            if event.fired or current_minutes < event.trigger_minutes:
                continue

            event.fired = True
            event_type  = event.data.get('type')

            if event_type == 'impact_event':
                self._handle_impact_event(event, break_component, game_manager)
            elif event_type == 'message_event':
                # Stub — message delivery not yet implemented
                print(f"[EventSystem] message_event '{event.event_id}' fired — not yet implemented")
            else:
                raise ValueError(
                    f"[EventSystem] unknown event type '{event_type}' for event '{event.event_id}'. "
                    f"Check events.json."
                )

            due.append({
                'event_id': event.event_id,
                'message':  event.data.get('event_message', ''),
            })

        return due

    def _handle_impact_event(self, event: GameEvent, break_component, game_manager) -> None:
        """Break all affected components and write ship log."""
        from backend.systems.electrical.electrical_service import trip_component, break_panel_component
        components = event.data.get('affected_components', [])
        for entry in components:
            if isinstance(entry, dict):
                component_id = entry['id']
                mode = entry.get('mode', 'damaged')
                panel_component = entry.get('component')
            else:
                component_id = entry
                mode = 'damaged'
                panel_component = None

            if panel_component:
                result = break_panel_component(component_id, panel_component)
                if not result['success']:
                    print(f"[EventSystem] WARNING: {result['error']}")
            else:
                self._break_component_by_id(component_id, mode, break_component, trip_component, game_manager)

        game_manager.add_log_entry({
            'timestamp': game_manager.get_ship_time(),
            'event': event.data.get('event_log_name', event.event_id),
            'detail': event.data.get('event_log_detail', ''),
        })

    def _break_component_by_id(self, component_id: str, mode: str, break_component, trip_component,
                               game_manager) -> None:
        """
        Resolve a component ID against all damageable types and break it.
        mode: 'damaged' — physical damage, requires replacement part
              'tripped'  — overload trip, requires reset only (breakers only)

        Resolution order:
          1. Electrical components (cables, breakers, panels, power sources)
          2. Door panels

        # TODO: Add engine resolution when fixed object repair is implemented.
        #       engine.online = False when component_id matches an engine ID.
        # TODO: Add fixed object resolution for life support, cargo handler etc.
        """
        # ── 1. Electrical components ──────────────────────────
        if mode == 'tripped':
            result = trip_component(component_id)
        else:
            result = break_component(component_id)
        if result['success']:
            return

        # ── 2. Door panels ────────────────────────────────────
        panel_index = game_manager.ship.build_panel_index()
        panel = panel_index.get(component_id)
        if panel:
            panel.is_broken = True
            return

        # ── Not found ─────────────────────────────────────────
        raise ValueError(
            f"[EventSystem] component '{component_id}' not found in any damageable system. "
            f"Check affected_components in events.json."
        )

    def resolve(self, event_id: str) -> None:
        """Mark an event as resolved — clears the event strip message."""
        for event in self._events:
            if event.event_id == event_id:
                event.resolved = True

    def is_resolved(self, event_id: str) -> bool:
        """Return True if the event has been resolved."""
        for event in self._events:
            if event.event_id == event_id:
                return event.resolved
        return True   # unknown event ID — treat as resolved

    def is_fired(self, event_id: str) -> bool:
        """Return True if the event has been fired."""
        for event in self._events:
            if event.event_id == event_id:
                return event.fired
        return False

    def get_fired_state(self) -> dict:
        """Return fired and resolved state for all events — used by save/load."""
        return {
            event.event_id: {
                'fired': event.fired,
                'resolved': event.resolved,
            }
            for event in self._events
        }

    def restore_fired_state(self, state: dict) -> None:
        """Restore fired and resolved state from save data — called after load_from_json()."""
        for event in self._events:
            if event.event_id in state:
                event.fired = state[event.event_id]['fired']
                event.resolved = state[event.event_id]['resolved']

    def check_event_resolution(self, game_manager) -> list[dict]:
        """
        Check all fired-but-unresolved events to see if their affected components
        are now all repaired. Resolves any that pass and returns their event IDs.
        Called after any successful repair completes.
        """

        # Maps affected_components 'component' field names to CircuitPanel attribute names
        _INTERNAL_COMPONENT_ATTRS = {
            'hv_logic_board': 'logic_board_intact',
            'hv_bus_bar': 'bus_bar_intact',
            'hv_surge_protector': 'surge_protector_intact',
            'hv_smoothing_capacitor': 'smoothing_capacitor_intact',
            'hv_isolation_switch': 'isolation_switch_intact',
        }

        es = game_manager.electrical_system
        panel_index = game_manager.ship.build_panel_index()

        newly_resolved = []

        for event in self._events:
            if not event.fired or event.resolved:
                continue

            all_repaired = True

            for entry in event.data.get('affected_components', []):
                if isinstance(entry, dict):
                    component_id = entry['id']
                    panel_component = entry.get('component')

                    if panel_component:
                        # Junction internal component — check specific flag on CircuitPanel
                        attr = _INTERNAL_COMPONENT_ATTRS.get(panel_component)
                        if not attr:
                            raise ValueError(
                                f"[EventSystem] unknown internal component '{panel_component}' "
                                f"in event '{event.event_id}'. Check affected_components in events.json."
                            )
                        circuit_panel = es.panels.get(component_id)
                        if not circuit_panel or not getattr(circuit_panel, attr):
                            all_repaired = False
                            break

                    else:
                        # Breaker (mode: damaged or tripped) — check operational
                        breaker = es.breakers.get(component_id)
                        if not breaker or not breaker.operational:
                            all_repaired = False
                            break

                else:
                    # Plain string — cable or door panel
                    cable = es.cables.get(entry)
                    if cable is not None:
                        if not cable.intact:
                            all_repaired = False
                            break
                    else:
                        # Door panel
                        panel = panel_index.get(entry)
                        if not panel:
                            raise ValueError(
                                f"[EventSystem] component '{entry}' in event '{event.event_id}' "
                                f"not found as cable or door panel during resolution check."
                            )
                        if panel.is_broken:
                            all_repaired = False
                            break

            if all_repaired:
                resolved_message = event.data.get('event_resolved_message', '')
                if not resolved_message:
                    raise ValueError(
                        f"[EventSystem] event '{event.event_id}' has no event_resolved_message. "
                        f"Add it to events.json."
                    )
                resolved_log_detail = event.data.get('event_resolved_log_detail', '')
                if not resolved_log_detail:
                    raise ValueError(
                        f"[EventSystem] event '{event.event_id}' has no event_resolved_log_detail. "
                        f"Add it to events.json."
                    )
                self.resolve(event.event_id)
                newly_resolved.append({
                    'event_id': event.event_id,
                    'message': resolved_message,
                })
                game_manager.add_log_entry({
                    'timestamp': game_manager.get_ship_time(),
                    'event': 'Repairs Complete',
                    'detail': resolved_log_detail,
                })

        return newly_resolved

    def get_active_events(self) -> list[dict]:
        """Return all fired but unresolved events — for restoring event strip on page load."""
        return [
            {'event_id': e.event_id, 'message': e.data.get('event_message', '')}
            for e in self._events
            if e.fired and not e.resolved
        ]
