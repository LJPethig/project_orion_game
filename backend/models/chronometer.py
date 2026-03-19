# backend/models/chronometer.py
"""
Ship chronometer — tracks game time in minutes.
Simple calendar: 30 days/month, 360 days/year. No leap years.
Time only advances when a game action causes it to (repairs, waits, etc.)
Not real-time — the frontend polls for display updates only.
"""

from config import START_DATE_TIME


class Chronometer:
    """
    Tracks total minutes elapsed since game start.
    Converts to/from a human-readable date string for display.
    """

    def __init__(self):
        year, month, day, hour, minute = START_DATE_TIME
        self.total_minutes = self._to_minutes(year, month, day, hour, minute)

    # ── Time conversion ──────────────────────────────────────

    @staticmethod
    def _to_minutes(year: int, month: int, day: int, hour: int, minute: int) -> int:
        """Convert a date/time to total minutes since year 0."""
        days = (year * 360) + ((month - 1) * 30) + (day - 1)
        return (days * 24 * 60) + (hour * 60) + minute

    @staticmethod
    def _from_minutes(total: int) -> tuple[int, int, int, int, int]:
        """Convert total minutes back to (year, month, day, hour, minute)."""
        minutes_per_day = 24 * 60
        days        = total // minutes_per_day
        remaining   = total % minutes_per_day

        year        = days // 360
        day_of_year = days % 360
        month       = (day_of_year // 30) + 1
        day         = (day_of_year % 30) + 1
        hour        = remaining // 60
        minute      = remaining % 60

        return year, month, day, hour, minute

    # ── Public interface ─────────────────────────────────────

    def advance(self, minutes: int) -> None:
        """Advance ship time by the given number of minutes."""
        self.total_minutes += int(minutes)

    def get_formatted(self) -> str:
        """Return ship time as a display string: 'DD-MM-YYYY  HH:MM'"""
        year, month, day, hour, minute = self._from_minutes(self.total_minutes)
        return f"{day:02d}-{month:02d}-{year:04d}  {hour:02d}:{minute:02d}"

    def get_total_minutes(self) -> int:
        """Return raw total minutes (for event checking)."""
        return self.total_minutes
