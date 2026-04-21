# backend/handlers/repair_handler.py
"""
RepairHandler — dispatcher for all repair and diagnosis commands.

Routes 'diagnose' and 'repair' verbs to the appropriate sub-handler
based on what is in the current room. Currently only door access panels
are supported. Electrical and fixed object repair handlers will be added
as further repair types are implemented.

Sub-handlers:
  door_panel_repair.py     — door access panel diagnosis and repair
  electrical_repair.py     — electrical cabinet diagnosis and repair (future)
  fixed_object_repair.py   — engines, reactors, life support etc. (future)

Shared utilities:
  repair_utils.py          — time scaling, item name lookup, tool checks,
                             duration formatting
"""

from backend.handlers.door_panel_repair import door_panel_repair_handler
from backend.handlers.electrical_repair import electrical_repair_handler


class RepairHandler:

    def handle_diagnose(self, args: str) -> dict:
        """Route 'diagnose' to the appropriate sub-handler."""
        return door_panel_repair_handler.handle_diagnose(args)

    def handle_repair(self, args: str) -> dict:
        """Route 'repair' to the appropriate sub-handler."""
        return door_panel_repair_handler.handle_repair(args)

    def begin_next_repair(self, panel, door, exit_label: str) -> dict:
        """Delegate to door panel handler — called by command.py repair_next endpoint."""
        return door_panel_repair_handler.begin_next_repair(panel, door, exit_label)

    def complete_diagnosis(self, panel_id: str, door_id: str, game_minutes: int,
                           exit_label: str = 'unknown') -> dict:
        """Delegate to door panel handler — called by command.py diagnose_complete endpoint."""
        return door_panel_repair_handler.complete_diagnosis(panel_id, door_id, game_minutes, exit_label)

    def complete_component_repair(self, panel_id: str, door_id: str,
                                  component_id: str, exit_label: str) -> dict:
        """Delegate to door panel handler — called by command.py repair_complete endpoint."""
        return door_panel_repair_handler.complete_component_repair(panel_id, door_id, component_id, exit_label)


repair_handler = RepairHandler()
