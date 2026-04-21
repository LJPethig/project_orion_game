# backend/handlers/repair_handler.py
"""
RepairHandler — dispatcher for all repair and diagnosis commands.

Routes 'diagnose' and 'repair' verbs to the appropriate sub-handler
based on what is in the current room and what the player is targeting.

Routing order:
  1. Unambiguous electrical keywords        → electrical handler
  2. Unambiguous fixed object keywords      → fixed object handler (future stub)
  3. Unambiguous door target                → door handler
  4. Generic/ambiguous args                 → check room contents:
       No damaged door panels, no junction  → door handler (no panels message)
       No damaged door panels, junction     → electrical handler
       Damaged door panels, no junction     → door handler
       Both present                         → clarification prompt
  5. Unrecognised args                      → "You can't diagnose that."

Sub-handlers:
  door_panel_repair.py     — door access panel diagnosis and repair
  electrical_repair.py     — electrical junction diagnosis and repair
  fixed_object_repair.py   — engines, reactors, life support etc. (future)

Shared utilities:
  repair_utils.py          — time scaling, item name lookup, tool checks,
                             duration formatting
"""

from backend.handlers.door_panel_repair import door_panel_repair_handler
from backend.handlers.electrical_repair import electrical_repair_handler
from backend.models.interactable import PowerJunction
from backend.models.game_manager import game_manager


# ── Keyword sets ──────────────────────────────────────────────

# Unambiguously target an electrical junction
_ELECTRICAL_KEYWORDS = {
    'junction',
    'junction box',
    'electrical junction',
    'power junction',
    'electrical junction panel',
    'electrical panel'
}

# Too vague to commit — trigger room contents check
_AMBIGUOUS_KEYWORDS = {
    'panel',
}

# Words that unambiguously target a door panel — stripped before exit matching
_DOOR_NOISE_WORDS = {
    'access panel',
    'door panel',
    'door access panel',
    'access',
}


# ── Room helpers ──────────────────────────────────────────────

def _get_junction(room) -> 'PowerJunction | None':
    """Return the PowerJunction in the room, or None."""
    return next((o for o in room.objects if isinstance(o, PowerJunction)), None)


def _is_electrical_target(args: str) -> bool:
    """Return True if args unambiguously target an electrical junction."""
    cleaned = args.strip().lower()
    if cleaned in _ELECTRICAL_KEYWORDS:
        return True
    # PNL- prefix anywhere in args
    if 'pnl-' in cleaned:
        return True
    # Any electrical keyword contained within args
    for keyword in _ELECTRICAL_KEYWORDS:
        if keyword in cleaned:
            return True
    return False


def _is_fixed_object_target(args: str, room) -> bool:
    """
    Return True if args match a repairable fixed object in the room.
    Stub — no fixed objects are repairable yet.
    """
    return False


def _is_door_target(args: str, room) -> bool:
    """
    Return True if args unambiguously target a door panel.
    Strips door noise words then checks against exit labels and shortcuts.
    Also returns True for bare door noise words with no exit specified.
    """
    if not args:
        return False
    cleaned = args.strip().lower()

    # Bare door noise word — unambiguously a door target
    if cleaned in _DOOR_NOISE_WORDS:
        return True

    # Strip noise words and check what remains against exits
    stripped = cleaned
    for noise in sorted(_DOOR_NOISE_WORDS, key=len, reverse=True):
        stripped = stripped.replace(noise, '').strip()

    if not stripped:
        return True

    for exit_data in room.exits.values():
        label = exit_data.get('label', '').lower()
        shortcuts = [s.lower() for s in exit_data.get('shortcuts', [])]
        if stripped == label or stripped in shortcuts:
            return True
        # Substring match — 'cockpit door' contains 'cockpit'
        if stripped in label or label in stripped:
            return True
        for shortcut in shortcuts:
            if stripped in shortcut or shortcut in stripped:
                return True

    return False


def _is_ambiguous(args: str) -> bool:
    """Return True if args are too vague to commit to a handler."""
    return args.strip().lower() in _AMBIGUOUS_KEYWORDS or not args.strip()


def _instant(msg: str) -> dict:
    return {
        'response':     msg,
        'action_type':  'instant',
        'lock_input':   False,
        'room_changed': False,
    }


def _clarification(message: str, options: list) -> dict:
    return {
        'response':     message,
        'action_type':  'clarification_required',
        'lock_input':   False,
        'room_changed': False,
        'options':      options,
    }


# ── Handler ───────────────────────────────────────────────────

class RepairHandler:

    def handle_diagnose(self, args: str) -> dict:
        """Route 'diagnose' to the appropriate sub-handler."""
        return self._route(args, verb='diagnose')

    def handle_repair(self, args: str) -> dict:
        """Route 'repair' to the appropriate sub-handler."""
        return self._route(args, verb='repair')

    def _route(self, args: str, verb: str) -> dict:
        room = game_manager.get_current_room()

        # ── 1. Unambiguous electrical target ──────────────────
        if _is_electrical_target(args):
            junction = _get_junction(room)
            if not junction:
                return _instant("There is no electrical junction panel in this room.")
            return _instant(f"[STUB] Electrical handler — {verb} {junction.panel_id}")

        # ── 2. Fixed object target (future) ───────────────────
        if _is_fixed_object_target(args, room):
            return _instant("[STUB] Fixed object handler — not yet implemented.")

        # ── 3. Unambiguous door target ────────────────────────
        if _is_door_target(args, room):
            return door_panel_repair_handler.handle_diagnose(args) \
                if verb == 'diagnose' \
                else door_panel_repair_handler.handle_repair(args)

        # ── 4. Ambiguous or empty args — check room contents ──
        if _is_ambiguous(args):
            broken_door_panels = game_manager.ship.get_broken_panels_in_room(room.id)
            junction           = _get_junction(room)

            if not broken_door_panels and not junction:
                return door_panel_repair_handler.handle_diagnose(args) \
                    if verb == 'diagnose' \
                    else door_panel_repair_handler.handle_repair(args)

            if not broken_door_panels and junction:
                return _instant(f"[STUB] Electrical handler — {verb} {junction.panel_id}")

            if broken_door_panels and not junction:
                return door_panel_repair_handler.handle_diagnose(args) \
                    if verb == 'diagnose' \
                    else door_panel_repair_handler.handle_repair(args)

            # Both present — clarification
            return _instant("Door panel or junction panel?")

        # ── 5. Unrecognised args ──────────────────────────────
        return _instant("You can't diagnose that.")

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