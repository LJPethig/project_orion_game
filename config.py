# config.py
# All game constants for Project Orion

# ── Ship & Player ────────────────────────────────────────────
SHIP_NAME       = "Tempus Fugit"
PLAYER_NAME     = "Jack Harrow"
STARTING_ROOM   = "engineering"

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

# ── Timed Actions ────────────────────────────────────────────
CARD_SWIPE_REAL_SECONDS   = 5

# Repair/diagnosis real-time scaling
# real_seconds = REPAIR_TIME_BASE + (game_minutes / REPAIR_TIME_PIVOT) * REPAIR_TIME_SCALE
# capped at REPAIR_TIME_CAP
REPAIR_TIME_BASE_SECONDS  = 8
REPAIR_TIME_SCALE_SECONDS = 8
REPAIR_TIME_PIVOT_MINUTES = 30
REPAIR_TIME_CAP_SECONDS   = 20
DIAG_ACCESS_OVERHEAD      = 0.25  # 25% of component diag time added for panel access
DIAG_TIME_JITTER          = 0.10  # ±10% random variation on diagnosis time

# ── Data file paths ──────────────────────────────────────────
import os

# Ship structure
ROOMS_JSON_PATH            = os.path.join('data', 'ship', 'structure', 'ship_rooms.json')
DOORS_JSON_PATH            = os.path.join('data', 'ship', 'structure', 'door_status.json')
DOOR_PANEL_TYPES_PATH      = os.path.join('data', 'ship', 'structure', 'door_access_panel_types.json')
INITIAL_STATE_JSON_PATH    = os.path.join('data', 'ship', 'structure', 'initial_ship_state.json')
SHIP_ITEMS_JSON_PATH       = os.path.join('data', 'ship', 'structure', 'initial_ship_items.json')
PLAYER_ITEMS_JSON_PATH     = os.path.join('data', 'ship', 'structure', 'player_items.json')
CARGO_JSON_PATH            = os.path.join('data', 'ship', 'structure', 'initial_cargo.json')
ELECTRICAL_JSON_PATH       = os.path.join('data', 'ship', 'systems', 'electrical.json')
EVENTS_JSON_PATH           = os.path.join('data', 'game', 'events.json')

# Items
ITEM_FILES = [
    os.path.join('data', 'items', 'tools.json'),
    os.path.join('data', 'items', 'wearables.json'),
    os.path.join('data', 'items', 'misc_items.json'),
    os.path.join('data', 'items', 'consumables.json'),
    os.path.join('data', 'items', 'trade_items.json'),
]
TERMINALS_JSON_PATH        = os.path.join('data', 'items', 'terminals.json')
STORAGE_UNITS_JSON_PATH    = os.path.join('data', 'items', 'storage_units.json')
SURFACES_JSON_PATH         = os.path.join('data', 'items', 'surfaces.json')
ENGINES_JSON_PATH          = os.path.join('data', 'items', 'engines.json')
CARGO_CONTAINERS_JSON_PATH = os.path.join('data', 'items', 'cargo_containers.json')
PALLET_PLATFORMS_JSON_PATH = os.path.join('data', 'items', 'pallet_platforms.json')

# Repair
REPAIR_PROFILES_PATH       = os.path.join('data', 'repair', 'repair_profiles.json')

# Terminal content
TERMINAL_CONTENT_PATH      = os.path.join('data', 'terminals')

# ── Flask ────────────────────────────────────────────────────
DEBUG = True
PORT  = 5001
