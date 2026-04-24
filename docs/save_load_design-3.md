# Project Orion — Save/Load System Design
**Status: In progress — agreed decisions only**
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
