# backend/systems/electrical/electrical_system.py
"""
Electrical System - Power distribution management
Loads electrical.json and manages all power components
"""

import json
from typing import Dict, Optional


class PowerSource:
    """Base class for power generation sources"""

    def __init__(self, id: str, name: str, location: str):
        self.id = id
        self.name = name
        self.location = location


class FissionReactor(PowerSource):
    """Thermionic fission reactor - primary power source"""

    def __init__(self, id: str, name: str, location: str, output_kw: float,
                 critical_temp: int, normal_temp: int):
        super().__init__(id, name, location)
        self.output_kw = output_kw
        self.critical_temp = critical_temp
        self.normal_temp = normal_temp

        # Runtime state (defaults)
        self.operational = True
        self.temperature = normal_temp
        self.ejected = False


class BackupBattery(PowerSource):
    """Emergency backup battery for critical systems"""

    def __init__(self, id: str, name: str, location: str, capacity_kwh: int,
                 powers_room: str, auto_activate: bool):
        super().__init__(id, name, location)
        self.capacity_kwh = capacity_kwh
        self.powers_room = powers_room
        self.auto_activate = auto_activate

        # Runtime state (defaults)
        self.active = False
        self.charge_percent = 100


class CircuitPanel:
    """Circuit breaker panel containing multiple breakers"""

    def __init__(self, id: str, type: str, name: str, location: str, breaker_count: int):
        self.id = id
        self.type = type
        self.name = name
        self.location = location
        self.breaker_count = breaker_count

        # Runtime state (defaults)
        self.operational = True


class Breaker:
    """Individual circuit breaker protecting one circuit"""

    def __init__(self, id: str, panel_id: str, name: str, feeds: str, rating_amps: int):
        self.id = id
        self.panel_id = panel_id
        self.name = name
        self.feeds = feeds
        self.rating_amps = rating_amps

        # Runtime state (defaults)
        self.damaged = False
        self.tripped = False

    @property
    def operational(self) -> bool:
        """A breaker is operational only when neither damaged nor tripped."""
        return not self.damaged and not self.tripped


class PowerCable:
    """Power cable connecting two components"""

    def __init__(self, id: str, from_id: str, to_id: str, name: str, location: str):
        self.id = id
        self.from_id = from_id
        self.to_id = to_id
        self.name = name
        self.location = location

        # Runtime state (defaults)
        self.intact = True
        self.connected = True


class ElectricalSystem:
    """
    Main electrical system - manages all power distribution
    Loads configuration from JSON and maintains runtime state
    """

    def __init__(self):
        self.power_sources: Dict[str, PowerSource] = {}
        self.panels: Dict[str, CircuitPanel] = {}
        self.breakers: Dict[str, Breaker] = {}
        self.cables: Dict[str, PowerCable] = {}
        self.room_power_sources: Dict[str, str] = {}

    @classmethod
    def load_from_json(cls, filepath: str = "data/ship/systems/electrical.json") -> 'ElectricalSystem':
        """Load electrical system from JSON configuration file"""
        system = cls()

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Load power sources
        for ps_data in data.get('power_sources', []):
            if ps_data['type'] == 'fission_reactor':
                ps = FissionReactor(
                    id=ps_data['id'],
                    name=ps_data['name'],
                    location=ps_data['location'],
                    output_kw=ps_data['output_kw'],
                    critical_temp=ps_data['critical_temp'],
                    normal_temp=ps_data['normal_temp']
                )
            elif ps_data['type'] == 'backup_battery':
                ps = BackupBattery(
                    id=ps_data['id'],
                    name=ps_data['name'],
                    location=ps_data['location'],
                    capacity_kwh=ps_data['capacity_kwh'],
                    powers_room=ps_data['powers_room'],
                    auto_activate=ps_data['auto_activate']
                )
            else:
                continue

            system.power_sources[ps.id] = ps

        # Load panels
        for panel_data in data.get('panels', []):
            panel = CircuitPanel(
                id=panel_data['id'],
                type=panel_data['type'],
                name=panel_data['name'],
                location=panel_data['location'],
                breaker_count=panel_data['breaker_count']
            )
            system.panels[panel.id] = panel

        # Load breakers
        for breaker_data in data.get('breakers', []):
            breaker = Breaker(
                id=breaker_data['id'],
                panel_id=breaker_data['panel_id'],
                name=breaker_data['name'],
                feeds=breaker_data['feeds'],
                rating_amps=breaker_data['rating_amps']
            )
            system.breakers[breaker.id] = breaker

        # Load cables
        for cable_data in data.get('cables', []):
            cable = PowerCable(
                id=cable_data['id'],
                from_id=cable_data['from'],
                to_id=cable_data['to'],
                name=cable_data['name'],
                location=cable_data['location']
            )
            cable.intact = cable_data.get('intact', True)
            cable.connected = cable_data.get('connected', True)
            cable.emergency_bypass = cable_data.get('emergency_bypass', False)
            cable.length_m = cable_data.get('length_m', 0.0)
            system.cables[cable.id] = cable

        # Load room power source mappings
        system.room_power_sources = data.get('room_power_sources', {})

        return system

    def check_room_power(self, room_id: str) -> bool:
        """
        Check if a room has power.
        Returns True if mains path is intact OR an active backup battery covers it.
        """
        # Check for active backup battery first
        for source in self.power_sources.values():
            if isinstance(source, BackupBattery):
                if source.powers_room == room_id and source.active:
                    return True

        source_id = self.room_power_sources.get(room_id)
        if not source_id:
            return False

        # Check outgoing cable from source to room is intact
        outgoing = self._find_cable_from_to(source_id, room_id)
        if outgoing and not outgoing.intact:
            return False

        # Trace upstream from the source back to reactor
        return self._trace_power_to_source(source_id)

    def _trace_power_to_source(self, component_id: str, visited: Optional[set] = None) -> bool:
        """
        Recursively trace power from component back to reactor
        Returns True if path to operational reactor exists
        """
        if visited is None:
            visited = set()

        # Prevent infinite loops
        if component_id in visited:
            return False
        visited.add(component_id)

        # Check if we've reached a power source — any operational reactor terminates successfully
        if component_id in self.power_sources:
            source = self.power_sources[component_id]
            if isinstance(source, FissionReactor):
                return source.operational
            if isinstance(source, BackupBattery):
                return source.active

        # Check if component is a breaker
        if component_id in self.breakers:
            breaker = self.breakers[component_id]
            if not breaker.operational:
                return False
            # Breaker is in a panel, trace to panel
            return self._trace_power_to_source(breaker.panel_id, visited)

        # Check if component is a panel
        if component_id in self.panels:
            panel = self.panels[component_id]
            if not panel.operational:
                return False
            # Try all inbound cables — return True if any path succeeds
            for feeding_cable in self._find_cables_to(component_id):
                if not feeding_cable.intact:
                    continue
                if self._trace_power_to_source(feeding_cable.from_id, set(visited)):
                    return True
            return False

        # Check if component is a cable (cable-to-cable connection)
        if component_id in self.cables:
            cable = self.cables[component_id]
            if not cable.intact:
                return False
            # Continue tracing from cable source
            return self._trace_power_to_source(cable.from_id, visited)

        # Check if component is a room or engine (need to find feeding cable)
        for feeding_cable in self._find_cables_to(component_id):
            if not feeding_cable.intact:
                continue
            if self._trace_power_to_source(feeding_cable.from_id, set(visited)):
                return True
        return False

    def _find_cables_to(self, component_id: str) -> list:
        """Find all cables that feed power TO a component"""
        return [cable for cable in self.cables.values() if cable.to_id == component_id]

    def _find_cable_from_to(self, from_id: str, to_id: str) -> Optional[PowerCable]:
        """Find the cable running from a specific source to a specific destination"""
        for cable in self.cables.values():
            if cable.from_id == from_id and cable.to_id == to_id:
                return cable
        return None

    def update_battery_states(self):
        """
        Check all auto-activate batteries. If mains power to their room is lost,
        activate the battery. If mains is restored, deactivate it.
        Must be called after any component state change.
        """
        for battery_id, source in self.power_sources.items():
            if not isinstance(source, BackupBattery):
                continue
            if not source.auto_activate:
                continue
            if source.charge_percent <= 0:
                source.active = False
                continue

            # Temporarily deactivate so we test mains-only path
            source.active = False
            mains_ok = self.check_room_power(source.powers_room)
            source.active = not mains_ok

    def update_engine_states(self, engines: list) -> None:
        """
        Update the powered state of all engine objects based on electrical trace.
        engines — list of Engine instances from the ship's propulsion bay.
        Called after any component state change, alongside update_battery_states().
        """
        for engine in engines:
            engine.powered = self._trace_power_to_source(engine.id)

    def get_battery_states(self) -> dict:
        """Return battery states for API responses"""
        result = {}
        for bid, source in self.power_sources.items():
            if isinstance(source, BackupBattery):
                result[bid] = {
                    'name': source.name,
                    'active': source.active,
                    'charge_percent': source.charge_percent,
                    'powers_room': source.powers_room,
                    'auto_activate': source.auto_activate,
                }
        return result

    def get_system_status(self) -> dict:
        """Return complete electrical system status for API"""
        return {
            'reactors': {
                reactor_id: {
                    'name': reactor.name,
                    'operational': reactor.operational,
                    'temperature': reactor.temperature,
                    'output_kw': reactor.output_kw,
                    'ejected': reactor.ejected
                }
                for reactor_id, reactor in self.power_sources.items()
                if isinstance(reactor, FissionReactor)
            },
            'batteries': {
                battery_id: {
                    'name': battery.name,
                    'location': battery.location,
                    'active': battery.active,
                    'charge_percent': battery.charge_percent,
                    'capacity_kwh': battery.capacity_kwh,
                    'powers_room': battery.powers_room
                }
                for battery_id, battery in self.power_sources.items()
                if isinstance(battery, BackupBattery)
            },
            'panels': {
                panel_id: {
                    'name': panel.name,
                    'location': panel.location,
                    'operational': panel.operational
                }
                for panel_id, panel in self.panels.items()
            },
            'breakers': {
                breaker_id: {
                    'name': breaker.name,
                    'feeds': breaker.feeds,
                    'damaged': breaker.damaged,
                    'tripped': breaker.tripped,
                    'operational': breaker.operational
                }
                for breaker_id, breaker in self.breakers.items()
            },
            'cables': {
                cable_id: {
                    'name': cable.name,
                    'from': cable.from_id,
                    'to': cable.to_id,
                    'connected': cable.connected,
                    'intact': cable.intact
                }
                for cable_id, cable in self.cables.items()
            },
            'room_power': {
                room_id: self.check_room_power(room_id)
                for room_id in self.room_power_sources.keys()
            },
            'summary': {
                'total_panels': len(self.panels),
                'total_breakers': len(self.breakers),
                'total_cables': len(self.cables),
                'rooms_powered': sum(1 for room_id in self.room_power_sources.keys()
                                     if self.check_room_power(room_id)),
                'total_rooms': len(self.room_power_sources)
            }
        }