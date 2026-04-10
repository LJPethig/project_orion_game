# PROJECT ORION GAME
## Design Addendum — Phase 19: Ship Inventory System
### April 2026

---

## PURPOSE

This addendum captures the detailed design for the Phase 19 ship inventory system. It supplements the Master Design Document (Section 19) which contains only a high-level summary. All implementation decisions are recorded here.

---

## 1. OVERVIEW

The ship inventory system introduces one automated storage facility in the storage room. This is distinct from all existing container types. It is not browsable in the room description and has its own dedicated verb pair: `store` and `retrieve`.

The cargo bay is a freight space. It has no automated storage facility. Cargo is managed via a shipping manifest that exists before cargo comes aboard. The cargo bay terminal displays this manifest read-only. Cargo moves physically via the cargo handler and sack barrow — not via commands.

---

## 2. STORAGE ROOM — AUTOMATED STORAGE FACILITY

### Purpose
The storage room exists to store and track ship consumables. Two categories:

**Repair consumables** — cables, relays, logic boards, interconnects, wire. Items consumed by the repair system and needing replenishment at port.

**Crew consumables** — pre-packed MRE style meals. Bland, nutritious, unexciting. Designed for long haul crew sustenance. Also synth-coffee — freeze dried grounds, lab engineered, visually similar in colour to real ground coffee but bearing no other resemblance. Highly caffeinated, highly addictive.

### The automated storage facility
A single automated storage facility with terminal in the storage room. Works exactly as designed — `store` and `retrieve` commands, manifest tracked on GameManager, terminal displays contents with retrieve option.

**Justification** — the storage room is a controlled inventory environment. The ship needs to know exactly what consumables remain. Running out of relay switches or MRE packs mid-voyage is a serious operational problem. The automated system exists to prevent that. This is standard on any working vessel.

---

## 3. CARGO BAY — FREIGHT SPACE

### Purpose
The cargo bay is a freight space, not a warehouse. Cargo arrives pre-loaded, secured, and manifested before it ever comes aboard. The shipping manifest is transmitted to the ship's mainframe at time of loading. Jack did not load this cargo — Enso VeilTech's logistics system did.

**There is no automated storage facility in the cargo bay.** You do not take freight and put it in a bin. The manifest already exists.

### The cargo handler
A compact sit-on industrial machine — forklift style forks, operator cab, designed to be as small as practical for the confined space of a small freighter bay. Think Aliens P-5000 loader crossed with a small industrial forklift, but smaller and not wearable. The only way to move pallet platforms and large containers.

### The sack barrow
A manual device. One person. Can only move a single small container at a time. Allows Jack to move small containers from the cargo bay through the wider corridor doors to engineering and propulsion bay. All other cargo movement requires the cargo handler.

### Wider doors
The Tempus Fugit was designed as a working freighter. Doors to engineering and propulsion bay are intentionally wider than crew quarter doors — designed to allow equipment movement through the ship. Small containers can be sack-barrowed along this path.

---

## 4. CONTAINER SYSTEM — DIMENSIONS AND HIERARCHY

All containers are steel or composite construction. No wood anywhere.

### Container dimensions

| Type | Length | Width | Height | Movement | Notes |
|------|--------|-------|--------|----------|-------|
| Large container | 1200mm | 800mm | 900mm | Cargo handler only | Integral forklift pockets in base, stands alone on floor |
| Medium container | 600mm | 800mm | 900mm | Cargo handler only | Half pallet footprint, sits on platform, 2 per platform |
| Small container | 600mm | 400mm | 900mm | Cargo handler or sack barrow | Quarter pallet footprint, sits on platform, 4 per platform |
| Pallet platform | 1200mm | 800mm | 150mm | Cargo handler only | Steel/composite, forklift pockets, no lid, cargo strapped to it |

### Stacking compatibility
- All units share a 400mm grid module — small, medium and large are all compatible
- Small containers stack on medium, medium stack on large
- Four small containers fill one large container footprint
- Two medium containers fill one large container footprint
- Pallet platforms are the base unit for medium and small containers
- Large containers have integral forklift pockets — no platform needed
- Awkward or oversized items (steel plating, heavy machinery) strap directly to a pallet platform

### Movement rules
- **Cargo handler** — moves pallet platforms (loaded or empty) and large containers
- **Sack barrow** — moves one small container only, through wider doors to engineering/propulsion
- **By hand** — individual loose items taken from inside any open container

---

## 5. CARGO BAY CAPACITY

**Bay dimensions:** 10.0m x 8.5m x 4.5m high

### Operational constraints
The cargo handler must be able to place and retrieve every container. All doors must remain accessible at all times. The following zones are kept permanently clear:

- **External cargo doors** (x2, long wall) — 2.5m clear zone across full bay width for handler approach and loading/unloading
- **Internal door to sub corridor** (short wall) — 2.0m clear zone
- **Airlock door** (side wall) — 2.0m clear zone  
- **Central working aisle** — 2.5m wide running the length of the bay, cargo handler turning radius requirement
- **Fixtures corner** — existing storage unit, shelving, desk and cargo terminal (~3 sqm)

**Usable cargo floor after all clearances: ~34 sqm**

### Safe operational capacity
**Large container footprint:** 1.2m x 0.8m = 0.96 sqm

**Floor positions:** ~35

**Maximum safe stack height: 2 high**
Two high (1.8m) gives the handler operator clear sightlines to place and retrieve safely. Three high is physically possible within the 4.5m ceiling but retrieval becomes difficult and unsafe — not standard practice.

**Operational maximum: ~70 large containers**

This is a meaningful freight capacity for a small freighter. A mixed load — some large containers, some platforms with medium/small containers, some platform-strapped awkward cargo — would typically come in below this number, leaving the handler room to work efficiently.

### Trading significance
70 large containers represents a full working load. Individual containers are the unit of trade — buyers at port purchase one or more containers of a specific manifest line item. The cargo terminal displays per-container details to support this.

---

## 6. CARGO BAY ITEM CATEGORIES

### Pallet cargo — on manifest
Items officially loaded by Enso VeilTech logistics. Manifest transmitted to mainframe at load time. Displayed read-only in cargo terminal. Cannot be picked up or stored. Moved only by cargo handler or sack barrow (small containers only).

Flagged `"pallet": true` in `initial_ship_items.json`. Auto-logged to `game_manager.cargo_manifest` at game init.

### The unmarked container — not on manifest
A small container sitting among the official cargo. No sender. Not on the manifest. Powered — the stasis pod inside requires power to maintain preservation. Jack discovers it physically by being in the cargo bay.

Inside: a custom stasis pod containing 20 x 1kg casks of whole bean single-origin Ecuadorian coffee, nitrogen pressurised, preserved at peak roast condition. See Narrative Document Section 5 for full detail.

The individual coffee casks are takeable by hand once the container is opened. They can be stored in the storage room automated facility or carried in inventory.

### Existing storage units and surfaces
The cargo bay already has a standard storage unit and a surface containing items not on the manifest. These remain unchanged. Normal interaction — open, look in, take items.

---

## 7. CARGO BAY TERMINAL

Displays the shipping manifest only. Two sections:

**CARGO MANIFEST** — read-only list of all officially loaded cargo. Per container: container ID, description, declared value, destination. No interaction beyond viewing. The unmarked coffee container does not appear here.

**CARGO HANDLER STATUS** — operational state of the cargo handler. Whether it is functional, requires repair, fuel level (future).

No stored items section — there is no automated storage facility in the cargo bay.

---

---

## 8. AUTOMATED STORAGE FACILITY — DATA STRUCTURE

One instance only — in the storage room.

```python
self.storage_manifests = {
    'storage_room_auto_storage': {},  # instance_id → item dict
}
```

Each manifest entry:
```python
{
    'item_id':      'wire_low_voltage',
    'instance_id':  'wire_low_voltage_001',
    'display_name': 'Low Voltage Wire (2.5m)',
    'mass':         0.5,
}
```

Helper methods on GameManager:
- `store_item(item)` — removes from player inventory, adds to manifest
- `retrieve_item(instance_id)` — removes from manifest, adds to player inventory
- `get_storage_manifest()` — returns list for terminal display

---

## 9. NEW COMMANDS

### `store <item>`
- Player must be in storage room
- Item must be in carried inventory
- Response: `"Stored. [Item name] logged in ship stores."`

### `retrieve <item>`
- Player must be in storage room
- Item must be in storage manifest
- Response: `"Retrieved. [Item name] added to your inventory."`

Keyword variants: `store`, `stow`, `put away` / `retrieve`, `fetch`

Both routed to new `StorageHandler` in `command_handler.py`.

---

## 10. INVENTORY PANEL STORE BUTTON

When player is in the storage room, each carried item shows a contextual `Store` button alongside `Drop` and `Wear`. Sends `store <instance_id>` command. Storage room only — not cargo bay.

---

## 11. FILES TO CREATE OR MODIFY

### New files
- `backend/handlers/storage_handler.py`
- `data/terminals/cargo_bay.json`
- `data/terminals/storage_room.json`

### Modified files
- `backend/models/game_manager.py` — storage_manifests, cargo_manifest, helper methods
- `backend/handlers/command_handler.py` — store, retrieve verbs
- `backend/loaders/item_loader.py` — pallet flag handling, auto-log to cargo_manifest
- `backend/api/game.py` — storage and cargo manifest endpoints
- `frontend/static/js/screens/inventory.js` — contextual Store button (storage room only)
- `data/ship/structure/initial_ship_items.json` — pallet cargo, coffee container

---

## 12. DESIGN DECISIONS

**No automated storage in the cargo bay** — cargo bays don't work like warehouses. The manifest exists before cargo comes aboard, transmitted at load time. The terminal is read-only display of that manifest.

**Store/retrieve verbs only work in the storage room** — not the cargo bay. The cargo bay has no automated facility. Cargo moves physically via handler and sack barrow.

**Pallet cargo value display** — shown in credits for reference only. Since Jack is financially blacklisted, values are theoretical until barter is arranged at port. Terminal notes this.

**The coffee is not on the manifest** — deliberately. Someone used Enso VeilTech's logistics network to move it without their knowledge, or with knowledge they chose not to record. Either way it doesn't appear in the cargo terminal. Jack finds it by physically being in the cargo bay.

**224 large containers theoretical maximum** — relevant for future trading logic. A full load of large containers represents the ship's maximum freight value. Normal operating loads use 60-70% capacity. Individual containers are the unit of trade — buyers purchase one or more containers of a specific manifest line item.

---

*Project Orion Game — Design Addendum Phase 19*
*April 2026*
