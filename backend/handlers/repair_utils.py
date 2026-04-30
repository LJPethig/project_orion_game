# backend/handlers/repair_utils.py
"""
Shared utilities for all repair handlers.

Pure functions — no handler state, no repair-type-specific logic.
Used by door_panel_repair.py and any future repair handlers
(electrical_repair.py, fixed_object_repair.py).

Item registry is loaded once at module import time and cached for
the lifetime of the process — avoids repeated disk I/O on every
name lookup.
"""

from backend.loaders.item_loader import load_item_registry
from config import REPAIR_TIME_BASE_SECONDS, REPAIR_TIME_SCALE_SECONDS, \
                   REPAIR_TIME_PIVOT_MINUTES, REPAIR_TIME_CAP_SECONDS

# ── Item registry — loaded once at import ─────────────────────
# Read-only template cache — item definitions never change at runtime.
# Does not need to be serialised for save/load.
_item_registry: dict = load_item_registry()


# ── Time scaling ──────────────────────────────────────────────

def calc_repair_real_seconds(game_minutes: int) -> int:
    """Real wait time for a repair action, scaled to game time with cap."""
    total = round(REPAIR_TIME_BASE_SECONDS + (game_minutes / REPAIR_TIME_PIVOT_MINUTES) * REPAIR_TIME_SCALE_SECONDS)
    if total > REPAIR_TIME_CAP_SECONDS:
        total = REPAIR_TIME_CAP_SECONDS
    return total


def calc_diagnose_real_seconds(game_minutes: int) -> int:
    """Real wait time for a diagnosis action, scaled to game time with cap.
    NOTE: Currently identical to calc_repair_real_seconds. Kept separate
    in anticipation that diagnosis and repair may scale differently in future
    (e.g. Phase 24 electrical repair). Revisit after Phase 24 is complete.
    """
    total = round(REPAIR_TIME_BASE_SECONDS + (game_minutes / REPAIR_TIME_PIVOT_MINUTES) * REPAIR_TIME_SCALE_SECONDS)
    if total > REPAIR_TIME_CAP_SECONDS:
        total = REPAIR_TIME_CAP_SECONDS
    return total


# ── Item name lookup ──────────────────────────────────────────

def item_name(item_id: str) -> str:
    """Look up item display name from registry. Falls back to item_id."""
    data = _item_registry.get(item_id)
    return data['name'] if data else item_id


def component_display_name(component: dict) -> str:
    """Return display name for a profile component, appending length for cable."""
    if component.get('type') == 'actuator_reset':
        return 'Emergency release actuator reset'
    name = item_name(component['item_id'])
    if 'length_m' in component:
        return f"{name} ({component['length_m']}m)"
    return name


# ── Tool check ────────────────────────────────────────────────

def check_tools(tool_ids: list, player) -> list:
    """
    Return list of tool ids the player is missing.
    Checks both inventory and equipped items.
    """
    all_items = player.get_inventory() + player.equipped_items
    held_ids = {getattr(item, 'id', None) for item in all_items if item}
    return [t for t in tool_ids if t not in held_ids]


# ── Duration formatting ───────────────────────────────────────

def format_duration(minutes: int) -> str:
    """Format a duration in minutes as a human-readable string."""
    hours = minutes // 60
    mins = minutes % 60
    if hours and mins:
        return f"{hours} hour{'s' if hours > 1 else ''} {mins} minute{'s' if mins > 1 else ''}"
    if hours:
        return f"{hours} hour{'s' if hours > 1 else ''}"
    return f"{mins} minute{'s' if mins > 1 else ''}"
