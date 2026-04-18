# backend/api/events.py
"""
Events API routes.
/api/events/check  — check for due events at current ship time

Event delivery is frontend-driven — the poll calls /api/events/check every 15 seconds
when no timed action or repair is in progress.

NOTE: Long repairs (multi-hour component jobs) need a break point between components
so survival mechanics can fire and the player can choose to rest. This will be addressed
by an auto-chain threshold — repairs over N game minutes per component pause after
completion and require the player to explicitly continue rather than auto-chaining.
Implement when Phase 21 survival mechanics are built.
"""

from flask import Blueprint, jsonify
from backend.models.game_manager import game_manager

events_bp = Blueprint('events', __name__)


@events_bp.route('/check', methods=['GET'])
def check_events():
    """
    Check for any events due at the current ship time.
    Called by the frontend poll when no timed action is in progress.
    Returns a list of due event dicts.
    """
    if not game_manager.initialised:
        return jsonify({'events': []})

    current_minutes = game_manager.chronometer.get_total_minutes()
    start_minutes   = game_manager.event_start_minutes
    elapsed         = current_minutes - start_minutes

    due = game_manager.event_system.check(elapsed)
    return jsonify({'events': due})


@events_bp.route('/active', methods=['GET'])
def active_events():
    """
    Return all fired but unresolved events.
    Called on page load to restore event strip messages after a refresh.
    """
    if not game_manager.initialised:
        return jsonify({'events': []})

    return jsonify({'events': game_manager.event_system.get_active_events()})
