# backend/systems/event_system.py
"""
EventSystem — schedules and fires game events based on ship time.
Events are scheduled at game start with a trigger_minutes threshold.
check() is called by the frontend poll and returns any due events.
"""


class GameEvent:
    """A single scheduled game event."""

    def __init__(self, event_id: str, trigger_minutes: int, handler):
        self.event_id        = event_id
        self.trigger_minutes = trigger_minutes
        self.handler         = handler   # callable → returns event dict
        self.fired           = False
        self.resolved        = False


class EventSystem:
    """
    Manages all scheduled game events.
    Events fire when ship time reaches their trigger threshold,
    provided the caller has already checked that no timed action is in progress.
    Resolution is set externally (e.g. by repair handler) when the event cause is fixed.
    """

    def __init__(self):
        self._events: list[GameEvent] = []

    def schedule(self, event_id: str, trigger_minutes: int, handler) -> None:
        """Schedule a new event."""
        self._events.append(GameEvent(event_id, trigger_minutes, handler))

    def check(self, current_minutes: int) -> list[dict]:
        """
        Check for due events at the given ship time.
        Returns a list of event dicts for any events that are due and not yet fired.
        Each dict contains: event_id, message, log_entry.
        """
        due = []
        for event in self._events:
            if not event.fired and current_minutes >= event.trigger_minutes:
                event.fired = True
                result = event.handler()
                result['event_id'] = event.event_id
                due.append(result)
        return due

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

    def get_active_events(self) -> list[dict]:
        """Return all fired but unresolved events — for restoring event strip on page load."""
        return [
            {'event_id': e.event_id}
            for e in self._events
            if e.fired and not e.resolved
        ]
