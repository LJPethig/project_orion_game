# backend/handlers/electrical_repair.py
"""
ElectricalRepairHandler — diagnosis and repair of electrical junction panels.

Stateful, data-driven repair system. Reads electrical_repair_profiles.json
for component lists, tool requirements, diagnosis and repair times.

Keyed by panel_id (e.g. 'PNL-REC-SUB-C') — each entry covers all components
owned by that junction: internal parts (logic board, bus bar), breakers,
and cables.

Broken component state is determined by reading the live electrical system —
not randomly selected. The event system sets damage before diagnosis runs.

Repair state (broken_components, repaired_components) is stored on the
PowerJunction fixed object in the room.

Sub-handler of repair_handler.py. Shares utilities from repair_utils.py.
"""

import json
from backend.handlers.base_handler import BaseHandler
from config import ELECTRICAL_REPAIR_PROFILES_PATH


class ElectricalRepairHandler(BaseHandler):

    def __init__(self):
        with open(ELECTRICAL_REPAIR_PROFILES_PATH, 'r', encoding='utf-8') as f:
            self._profiles = json.load(f)

        if not self._profiles:
            raise ValueError(
                f"electrical_repair_profiles.json loaded empty — "
                f"check {ELECTRICAL_REPAIR_PROFILES_PATH}"
            )


electrical_repair_handler = ElectricalRepairHandler()
