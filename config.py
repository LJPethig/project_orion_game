# config.py
# All game constants for Project Orion

# ── Ship & Player ────────────────────────────────────────────
SHIP_NAME       = "Tempus Fugit"
PLAYER_NAME     = "Jack Harrow"
STARTING_ROOM   = "head"

# ── Game Clock ───────────────────────────────────────────────
# Simple calendar: 30 days/month, 360 days/year — no leap years
# Tuple: (year, month, day, hour, minute)
START_DATE_TIME = (2276, 1, 1, 0, 0)

# ── Room Temperature Presets (°C) ────────────────────────────
ROOM_TEMP_PRESETS = {
    "cold":   11.0,
    "cool":   16.5,
    "normal": 21.5,
    "warm":   23.5,
    "hot":    25.5,
}

# ── Timed Actions (real seconds → game minutes) ──────────────
REPAIR_PANEL_REAL_SECONDS  = 8
REPAIR_PANEL_GAME_MINUTES  = 30
CARD_SWIPE_REAL_SECONDS    = 8    # Real-world wait during card swipe
CARD_SWIPE_GAME_MINUTES    = 0

# ── Debug flags (replaced by inventory checks when items are implemented) ──
DEBUG_HAS_LOW_SEC_CARD  = True
DEBUG_HAS_HIGH_SEC_CARD = True

# ── Data file paths ──────────────────────────────────────────
import os
ROOMS_JSON_PATH = os.path.join('data', 'ship', 'structure', 'ship_rooms.json')
DOORS_JSON_PATH = os.path.join('data', 'ship', 'structure', 'door_status.json')

# ── Flask ────────────────────────────────────────────────────
DEBUG = True
PORT  = 5001
