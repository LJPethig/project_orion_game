# Project Orion — Save/Load System Design
**Status: Complete — agreed decisions only**
**Phase: 19.5**

This document contains only finalised, agreed design decisions.
Nothing is added until it has been explicitly discussed and confirmed.

---

## Philosophy

- Autosave only — no manual save, no scum saving.
- One save slot. One backup slot. No other save files.
- Jack's death is permanent — no reloading past a death.
- The monologue system (`monologue.json`) handles hopeless situations — Jack's survival
  instinct fires as internal monologue, guiding the player. This replaces any need for
  a mechanical lucky break system.

---

## Save files

Two files written simultaneously on every save:
- `save.json` — primary save file
- `save_backup.json` — identical backup

On load, `save.json` is tried first. If it cannot be read or fails validation,
`save_backup.json` is loaded automatically. The player never needs to know the
backup exists.

On death, the dead flag is written to both files simultaneously. Neither file can
be used to reload past a death.

---

## Splash screen

- **New Game** — always available.
- **Load Game** — greyed out if no save file exists.

Selecting New Game when a save file exists shows an explicit two-step warning:
*"Starting a new game will permanently delete your current save. This cannot be undone."*
Player must confirm before the save is deleted and a new game begins.

If `save.json` exists but cannot be loaded, `save_backup.json` is tried automatically
before showing any error to the player.

---

## Save triggers

The game maintains a real-time autosave timer (default 5 minutes — defined in
`config.py`). When the timer fires, the game waits for the next saveable moment
then saves immediately.

The game is in a saveable state when ALL of the following are true:
- No timed action is currently running
- No terminal, datapad, or inventory panel is open
- Jack is not mid-repair timed action (between components is saveable — during
  the timed action itself is not)

Timed actions are capped at a short real-time duration (`REPAIR_TIME_CAP_SECONDS`
in `config.py`), so the maximum delay between the timer firing and the save
completing is bounded and always short.

### Quit behaviour
The player quits the game by resting Jack. This is an in-world action — no meta
quit command exists. Resting is only available at designated rest locations when
the game is in a saveable state.

**Designated rest locations:**
- Captain's quarters bunk — available now
- Hypersleep pod — deferred, used for long-distance travel (future phase)

When Jack rests:
1. Game saves both `save.json` and `save_backup.json`
2. Player is offered the option to quit or continue
3. Future: integrates with fatigue/hunger survival mechanics — resting becomes
   a survival necessity as well as a save/quit point

The real-time autosave timer still runs in the background to protect against
crashes. Rest is the player-initiated save and quit point — the timer is the
crash protection fallback.

---

## Death state

When Jack dies:
- Dead flag written to both `save.json` and `save_backup.json` simultaneously.
- On next launch, Load Game shows a death screen. Only New Game is available.

---

## Save file format

JSON. No other format considered — JSON is already used throughout the project,
requires no new dependencies, is human-readable (useful during development), and
adding any other format would introduce complexity with no benefit.

---

## Serialisation rules

**Save everything except:**

1. **Static data** loaded from JSON files at startup — item registry, repair profiles,
   room definitions, electrical.json etc. These never change at runtime and are always
   reloaded fresh from disk on startup.

2. **Derived/computed properties** that recalculate themselves automatically from saved
   state — these do not need saving because they will be correct after load:
   - `Engine.powered` — derived from electrical trace
   - `CircuitPanel.operational` — derived from the five internal component flags
   - `Breaker.operational` — derived from `damaged` and `tripped`

3. **Transient UI state** that resets automatically on page load:
   - Frontend globals (`pendingPin`, `currentRoomId`, `currentRoomPowered` etc.)
   - `datapad_suppressed` — always `False` at save time by design

Everything else is serialised.

---

## Instance ID counters

`instance_id` values must be persisted and restored from the save file — never
regenerated on load. On load, the counter must be initialised past the highest
`instance_id` found anywhere in the save file, so new items created after loading
never receive a duplicate ID.

This rule was established during the instance ID refactor (March 2026) and must
be respected by the save/load implementation.

---

## Full serialisation list

Everything listed here must be written to the save file and restored on load.

### Meta
- `dead` — bool. Written to both files simultaneously on death.
- `ship_time` — current ship time in minutes (chronometer state).

### Player
- `current_room_id` — the room Jack is currently in.
- `inventory` — full list of carried `PortableItem` instances with all instance state.
- `equipped_slots` — all five slots (head, body, torso, waist, feet), occupied or empty.
- Note: `max_carry_mass` is a config constant — not saved. `current_carry_mass` is
  recalculated from inventory items on load — not saved.

### Portable items — per instance
Every `PortableItem` instance (in inventory, equipped, on surfaces, in containers,
on floors, in storage manifest) must save:
- `id` — item type ID
- `instance_id` — unique runtime ID, must be preserved exactly
- All mutable fields: `length_m` (cables, decremented on use), `installed_manuals`
  (scan tool), any other fields that can change at runtime

### Rooms — per room
- `floor` — list of item instances currently on the room floor
- Open/closed state of every `StorageUnit` in the room
- Contents of every `StorageUnit` and `Surface` in the room

### Door state — per door
- `state` — open / closed / locked
- `is_broken` flag on each security panel

### Repair state — per panel
- `SecurityPanel.broken_components` — list of component IDs found at diagnosis
- `SecurityPanel.repaired_components` — list of component IDs successfully repaired
- `PowerJunction.broken_components` — same for electrical junctions
- `PowerJunction.repaired_components` — same for electrical junctions
- `game_manager.tablet_notes` — entire dict (keyed by panel_id). Must be saved and
  restored alongside repair state — repair completion reads the note and crashes if
  it is missing.

### Electrical system — per component
**FissionReactor:** `operational`, `ejected`, `temperature`
Two instances: `reactor_core` (main, 25kW, engineering) and `propulsion_reactor`
(propulsion, 120kW, propulsion bay). Both must be saved, keyed by their `id`.
Note: `operational` is currently a direct flag. When reactor internal components are
implemented it will become a derived property (same pattern as `CircuitPanel.operational`)
and the internal flags will be saved instead.
**BackupBattery:** `active`, `charge_percent`
**CircuitPanel:** `logic_board_intact`, `bus_bar_intact`, `surge_protector_intact`,
  `smoothing_capacitor_intact`, `isolation_switch_intact`
**Breaker:** `damaged`, `tripped`
**PowerCable:** `intact`, `connected`

### Engine state — per engine
- `online` — damaged/undamaged flag. Currently a direct flag. When engine internal
  components are implemented it will become derived and the internal flags saved instead.
- Note: `powered` is derived from electrical trace on load — not saved

### Event system — per event
- `fired` — bool
- `resolved` — bool
- Note: if not restored, events re-fire on load

### Storage and cargo
- `game_manager.storage_manifest` — full dict of stored items with all instance state
- `game_manager.cargo_manifest` — containers and pallets with contents

### Ship log
- `game_manager.ship_log` — full list of structured log entries
  (`timestamp`, `event`, `location`, `detail`)

### Not saved — future systems
These systems do not exist yet. Listed here so save/load is extended correctly
when they are implemented:
- Survival state (hunger, thirst, fatigue)
- Room atmosphere state (temperature, pressure)
- Monologue fired keys (one-shot trigger tracking)
- `jury_rigged_power` flag on fixed objects (jury-rigging system)
- `room.room_states` dict (room state token system)
- Sack barrow loaded container reference
