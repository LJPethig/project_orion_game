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
CARD_SWIPE_REAL_SECONDS    = 5    # Real-world wait during card swipe
CARD_SWIPE_GAME_MINUTES    = 0

# ── Debug flags ──────────────────────────────────────────────
DEBUG_HAS_REPAIR_TOOL   = True   # Phase 12: replace with real tool inventory check

# ── Data file paths ──────────────────────────────────────────
import os
ROOMS_JSON_PATH         = os.path.join('data', 'ship', 'structure', 'ship_rooms.json')
DOORS_JSON_PATH         = os.path.join('data', 'ship', 'structure', 'door_status.json')
INITIAL_STATE_JSON_PATH = os.path.join('data', 'ship', 'structure', 'initial_ship_state.json')
SHIP_ITEMS_JSON_PATH    = os.path.join('data', 'ship', 'structure', 'ship_items.json')
PLAYER_ITEMS_JSON_PATH  = os.path.join('data', 'ship', 'structure', 'player_items.json')

ITEM_FILES = [
    os.path.join('data', 'items', 'tools.json'),
    os.path.join('data', 'items', 'wearables.json'),
    os.path.join('data', 'items', 'misc_items.json'),
    os.path.join('data', 'items', 'consumables.json'),
]
TERMINALS_JSON_PATH     = os.path.join('data', 'items', 'terminals.json')
STORAGE_UNITS_JSON_PATH = os.path.join('data', 'items', 'storage_units.json')
SURFACES_JSON_PATH      = os.path.join('data', 'items', 'surfaces.json')

# ── Flask ────────────────────────────────────────────────────
DEBUG = True
PORT  = 5001
