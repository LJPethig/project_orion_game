# PROJECT ORION
## Space Survival Simulator
### Technical Design Document
**Version 1.2 - March 2026**  
**Updated with Phase 4 Completion - SVG Diagnostic Map**

---

## RECENT UPDATES (v1.2)

### Phase 4 Complete: Visual Diagnostic Map ✅
**Status:** Implemented and functional
**Completion Date:** March 2026

**Ship Layout SVG Created:**
- Manual SVG coding (1100×1480px viewBox)
- 17 rooms with unique IDs (all rooms from electrical system)
- Room fills with CSS classes for power status
- Wall outlines with door gaps
- Scale: 40 units per meter
- File: `frontend/static/images/ship_layout.svg`

**Interactive Diagnostic Map Features:**
- ✅ Auto-opens 2 seconds after electrical data loads
- ✅ Room colors: Green (powered), Red (unpowered)
- ✅ Real-time power status from electrical API
- ✅ Hover tooltips showing room name and power state
- ✅ Pan controls (Arrow keys)
- ✅ Zoom controls (+/- keys, constrained 0.6x-2x)
- ✅ Pan constraints (keeps SVG on screen)
- ✅ Close with ESC or X button
- ✅ Full-screen modal overlay

**Room ID Mapping:**
All 17 SVG room IDs mapped to backend electrical system:
- `rec-room-fill` → `recreation_room`
- `cockpit-fill` → `cockpit`
- `storage-fill` → `storage_room`
- `medbay-fill` → `med_bay`
- `stasis-room-fill` → `hypersleep_chamber`
- `galley-fill` → `galley`
- `corridor-main-fill` → `main_corridor`
- `corridor-sub-fill` → `sub_corridor`
- `bathroom-sub-fill` → `head`
- `mainframe-sub-fill` → `mainframe_room`
- `cargo-bay-sub-fill` → `cargo_bay`
- `airlock-sub-fill` → `airlock`
- `engineering-sub-fill` → `engineering`
- `propulsion-sub-fill` → `propulsion_bay`
- `captains-cabin-sub-fill` → `captains_quarters`
- `crew-quarters-sub-fill` → `crew_cabin`
- `life-support-sub-fill` → `life_support`

**Files Modified:**
- `frontend/templates/index.html` - Added SVG modal container
- `frontend/static/css/main.css` - Added modal and room status styles
- `frontend/static/js/game.js` - Added SVG loading, color updates, controls

**Technical Details:**
- SVG loads via fetch from static/images/
- Room colors updated by adding/removing CSS classes
- JavaScript reads electrical API data and applies classes
- Pan/zoom using CSS transforms
- Tooltip positioning with mouse tracking

---

## TABLE OF CONTENTS
1. Project Overview
2. Technology Stack
3. Ship Systems Architecture
4. File Structure
5. Development Roadmap **← UPDATED**
6. Key Design Decisions
7. Technical Specifications
8. Gameplay Scenarios & Priorities
9. JSON Data Schemas
10. SVG Ship Layout Specification **← NEW SECTION**
11. Next Steps **← UPDATED**

---

## 1. PROJECT OVERVIEW

### Game Concept
Project Orion is a space survival simulator set in 2275. The player operates a solo trader/explorer spacecraft (XS Stock Light Freighter from SWTOR) - pilotable by one person but with room for crew. The core gameplay revolves around maintaining ship systems, repairing failures, and surviving the dangers of deep space.

### Core Philosophy
"If the ship dies, you die." This is a serious survival simulator, not an arcade game. Systems fail, components break, and cascading failures can occur. The player must diagnose problems, gather the right tools and parts, and physically repair systems before critical failures occur. The game is designed as a "slow burner" with generous time windows, emphasizing thoughtful problem-solving over frantic action.

### Key Features
• Realistic ship systems simulation (power, life support, propulsion, navigation)
• Physical infrastructure tracking (electrical cables, network connections, coolant pipes)
• **Interactive SVG diagnostic maps with live power status visualization** ✅
• Diagnostic tools and repair mechanics (scan, diagnose, repair with correct tools/parts)
• Interactive computer terminals with visual diagnostic maps
• Time management system (1:1 real-time with time-skip for long actions)
• Player physical state (temperature, oxygen, injuries, death)
• EVA mechanics for external repairs (spacewalks with O₂ management)
• Repair progress tracking (pause/resume multi-day repairs)
• Mass-based inventory system (worn items don't count toward carry limit)
• Save/Load with multiple slots
• Top-down ship layout maps
• Modular, extensible architecture for adding new systems and content

---

## 2. TECHNOLOGY STACK

### Backend: Python + Flask
All game logic runs in Python. Flask provides a lightweight web server and API endpoints. This allows leveraging Python's strengths for game logic while using web technologies for UI.

### Frontend: HTML + CSS + Vanilla JavaScript
No frameworks required. Plain HTML/CSS/JS provides maximum flexibility for terminal-style UIs, diagnostic maps, and interactive views. **SVG used for clickable ship diagrams with live power status**. Flexbox for responsive layouts. Floating popup windows for containers and item details.

### Data Format: JSON
All game content (rooms, items, ship systems, connections) defined in JSON files. This makes the game moddable and separates content from code.

### Development Tools
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Game Logic | Python 3.x | Ship systems, repairs, calculations |
| Web Server | Flask | API endpoints, serve frontend |
| UI Rendering | HTML/CSS/JS | Game views, terminals, maps |
| Layout | Flexbox | Responsive section arrangement |
| **Diagrams** | **SVG** | **Interactive ship layout with live power status** ✅ |
| Popups | CSS + JS | Container contents, item details |
| Data Storage | JSON | Ship config, items, systems |
| Save System | localStorage | Browser-based game saves |
| Version Control | Git | Code management |

---

## 3. SHIP SYSTEMS ARCHITECTURE

### Core Systems
The ship consists of 8 interconnected systems. Each system has components, connections, and can fail independently or trigger cascading failures.

1. **Power Supply** - Reactor generates electrical power for all systems. Located in Engineering. Requires coolant.
   - **Implementation Status:** ✅ COMPLETE (Phase 3)
   - 2 reactors (ship 25kW, propulsion 120kW)
   - 2 backup batteries (Life Support, Mainframe)
   - 4 circuit panels, 17 breakers, 28 cables
   - All 17 rooms powered and traced
   - **Visual diagnostic map operational** ✅

2. **Mainframe** - Central computer for monitoring and control. Automated emergency procedures. Located in dedicated Computer Room. Requires power and network connections to all systems.

3. **Life Support** - O₂ generation, CO₂ scrubbing, temperature control, pressure management. Located in Life Support Room.

4. **Propulsion** - Engines for sublight and FTL travel. Located in Propulsion Bay. Requires power, coolant, and fuel.

5. **Navigation** - Sensors, star charts, jump drive calculations. Located in Cockpit. Requires power and network.

6. **Sensors/Comms** - External sensors, scanners, communication arrays. Hull-mounted. Requires power and network.

7. **Hydraulics** - Landing gear, cargo ramp, airlock doors, control surfaces. Located in Engineering. Requires power and hydraulic fluid.

8. **Hull/Structure** - Physical containment. Can breach from micrometeorites or damage, causing pressure loss. Requires EVA for external repairs.

### Connection Types
| Type | Purpose | Failure Mode |
|------|---------|--------------|
| Electrical Cable | Power distribution | Open circuit (breaks) |
| Network Cable | Data/control signals | Breaks, loses connection |
| Coolant Pipe | Heat removal | Leaks, loses coolant |
| Hydraulic Line | Actuator control | Leaks, loses pressure |

### System Dependencies
Power Supply is the root system - everything requires power. Mainframe provides monitoring/control and automated emergency responses. Failures cascade: Power loss → Life Support offline → Temperature drops → Player freezing. Generous time windows allow thoughtful problem-solving rather than frantic responses.

---

## 4. FILE STRUCTURE

### Hyper-Organized Architecture
The project uses deep folder nesting to keep related files together. Each system has its own folder, handlers are categorized by type, and data is organized by domain.

```
project-orion/
├── main.py                          ← Flask entry point
├── config.py                        ← Game constants
├── requirements.txt
├── README.md
│
├── backend/                         ← All Python/game logic
│   ├── models/
│   │   ├── game/                    ← Game manager, time
│   │   ├── ship/                    ← Ship, rooms, doors
│   │   ├── player/                  ← Player state, inventory
│   │   └── objects/                 ← Items, terminals, storage
│   ├── systems/
│   │   ├── electrical/              ← Power distribution ✅ COMPLETE
│   │   ├── network/                 ← Data connections
│   │   ├── coolant/                 ← Heat management
│   │   ├── hydraulics/              ← Mechanical systems
│   │   ├── power/                   ← Reactor, batteries
│   │   ├── life_support/            ← Atmosphere, thermal
│   │   ├── navigation/              ← Sensors, jump drive
│   │   └── sensors/                 ← External sensors
│   ├── handlers/
│   │   ├── commands/                ← Player input processing
│   │   ├── repairs/                 ← Repair mechanics
│   │   └── terminals/               ← Terminal interactions
│   └── api/                         ← Flask routes
│       ├── game.py
│       ├── player.py
│       ├── systems.py
│       ├── terminals.py
│       └── save_load.py             ← Save/load system
│
├── frontend/                        ← All web UI
│   ├── templates/
│   │   └── index.html               ✅ Updated with SVG modal
│   └── static/
│       ├── css/
│       │   ├── main.css             ✅ Updated with modal styles
│       │   ├── popups.css           ← Floating window styles
│       │   └── diagnostics.css
│       ├── js/
│       │   ├── game.js              ✅ Updated with SVG functionality
│       │   ├── core/                ← Game loop, API
│       │   ├── views/               ← UI views
│       │   │   ├── ship_map_view.js ← Top-down layout
│       │   │   └── ...
│       │   └── components/          ← Reusable widgets
│       │       ├── popup.js         ← Container popups
│       │       └── ...
│       └── images/
│           ├── ship_layout.svg      ✅ NEW - Ship diagnostic map
│           ├── rooms/
│           └── items/
│
└── data/                            ← All JSON
    ├── ship/
    │   ├── structure/               ← Rooms, doors
    │   └── systems/
    │       └── electrical.json      ✅ Complete with 17 rooms
    ├── items/
    │   ├── equipment/               ← Tools, suits, parts
    │   └── containers/              ← Storage units
    └── game/
        └── starting_state.json
```

---

## 5. DEVELOPMENT ROADMAP

### Extended Build Plan
Build incrementally, proving each layer before adding the next. Focus on electrical system first to validate the architecture, then replicate the pattern for other systems.

#### Phase 1: Skeleton ✅ COMPLETE
- Flask server runs
- Basic HTML page displays
- Single API route: /api/status
- "Ship Online" message in browser
- **Deliverable:** Working web server

#### Phase 2: Ship + Rooms ✅ COMPLETE
- Ship and Room classes created
- Load 17 rooms from ship_rooms.json
- Display room list in browser
- API route: /api/ship
- **Deliverable:** Room data loaded and visible

#### Phase 3: Electrical System ✅ COMPLETE
- ElectricalSystem class with components
- Load electrical.json (components, cables)
- Power path tracing logic
- API route: /api/systems/electrical/status
- Display electrical status as text list
- **Added:** Propulsion bay and propulsion reactor (Phase 3c)
- **Deliverable:** Electrical system functional with 17 rooms

#### Phase 4: Visual Diagnostic Map ✅ COMPLETE
- **Manual SVG creation (ship_layout.svg)**
- **17 rooms with unique IDs and classes**
- **Auto-opening modal with full-screen view**
- **Live power status: Green (powered), Red (unpowered)**
- **Interactive controls: Pan (arrows), Zoom (+/-), Close (ESC)**
- **Hover tooltips with room names and power status**
- **Pan/zoom constraints to keep SVG visible**
- **Deliverable:** Interactive visual map with live electrical data ✅

#### Phase 5: Break/Repair (NEXT)
- RepairHandler class (generic)
- API routes: /api/break_cable, /api/repair_cable
- Break cable → map shows red
- Repair cable → map shows green
- Power path recalculated on changes
- **Deliverable:** Working damage/repair cycle

#### Phase 6: Save/Load System
- Serialize ship state to JSON
- localStorage for browser saves
- Multiple save slots
- Load game restores all systems
- **Deliverable:** Persistent game state

#### Phase 7: Repair Progress Tracking
- Components track repair_progress (0.0-1.0)
- Pause/resume multi-day repairs
- Handle "awaiting parts" scenarios
- Track why repair paused
- **Deliverable:** Realistic repair workflow

#### Phase 8: Electrical Schematic View
- Vertical flow diagram (reactor → rooms)
- All components visible with IDs
- Color-coded status (green/red)
- Grouped by panel branch
- **Deliverable:** Detailed electrical schematic

#### Phase 9: Player Body + EVA
- Player temperature/O₂ tracking
- Protective gear system
- External spacewalk locations
- EVA suit O₂ management
- **Deliverable:** Full EVA mechanics

#### Phase 10+: Extended Features
- Trading at space stations
- Random events during time skips
- Ship upgrades system
- Derelict exploration (later)
- Mainframe automated emergency procedures
- **Deliverable:** Complete gameplay loop

---

## 10. SVG SHIP LAYOUT SPECIFICATION **[NEW SECTION]**

### Ship Layout SVG Details

**File Location:** `frontend/static/images/ship_layout.svg`

**Dimensions:**
- ViewBox: 1100×1480 units
- Scale: 40 units per meter
- Background: Dark blue (#0a0e1a)

**Structure:**
1. **Wall elements** - `<line>` elements grouped in `<g class="wall">`
   - Stroke: #444 (dark grey)
   - Stroke-width: 6
   - Door gaps: breaks in wall lines

2. **Room fills** - `<rect>` elements with unique IDs
   - Class: `room-fill`
   - Default fill: #4a6fa5 (neutral blue)
   - Fill-opacity: 0.22
   - IDs follow pattern: `{room-name}-fill`

3. **Labels** - `<text>` elements (non-interactive)
   - Room names (18px)
   - Dimensions (13px, grey)
   - pointer-events: none

**CSS Classes Applied by JavaScript:**
```css
.room-powered {
    fill: rgba(0, 255, 0, 0.55) !important;  /* Bright green */
}

.room-unpowered {
    fill: rgba(255, 0, 0, 0.4) !important;   /* Red */
}
```

**Room ID Mapping (SVG → Backend):**
| SVG ID | Backend ID | Room Name |
|--------|-----------|-----------|
| rec-room-fill | recreation_room | Recreation Room |
| cockpit-fill | cockpit | Cockpit |
| storage-fill | storage_room | Storage Room |
| medbay-fill | med_bay | Med-Bay |
| stasis-room-fill | hypersleep_chamber | Hypersleep Chamber |
| galley-fill | galley | Galley |
| corridor-main-fill | main_corridor | Main Corridor CH-1 |
| corridor-sub-fill | sub_corridor | Sub Corridor CH-2 |
| bathroom-sub-fill | head | Head (Bathroom) |
| mainframe-sub-fill | mainframe_room | Mainframe Room |
| cargo-bay-sub-fill | cargo_bay | Cargo Bay |
| airlock-sub-fill | airlock | Airlock |
| engineering-sub-fill | engineering | Engineering |
| propulsion-sub-fill | propulsion_bay | Propulsion Bay |
| captains-cabin-sub-fill | captains_quarters | Captain's Quarters |
| crew-quarters-sub-fill | crew_cabin | Crew Cabin |
| life-support-sub-fill | life_support | Life Support |

**Interactive Features:**
- **Auto-open:** Modal opens 2 seconds after electrical data loads
- **Pan:** Arrow keys (constrained to keep SVG on screen)
- **Zoom:** +/- keys (0.6x to 2x range)
- **Reset:** R key (centers and resets zoom)
- **Close:** ESC key or X button
- **Hover:** Shows room name and power status in tooltip
- **Click:** Room elements have pointer cursor

**JavaScript Integration:**
```javascript
// SVG loaded via fetch
await fetch('/static/images/ship_layout.svg')

// Room colors updated from electrical API
electricalData.room_power[backendId] → CSS class added

// Transform applied for pan/zoom
svgElement.style.transform = 
    `translate(${x}px, ${y}px) scale(${scale})`
```

---

## 11. NEXT STEPS **[UPDATED]**

### Immediate Action Items
1. ~~Create SVG ship layout~~ ✅ COMPLETE
2. ~~Implement interactive diagnostic map~~ ✅ COMPLETE
3. ~~Add pan/zoom controls~~ ✅ COMPLETE
4. **Begin Phase 5:** Break/Repair mechanics
5. Create API routes for breaking/repairing components
6. Update SVG colors when components break/repair
7. Add terminal commands: BREAK CABLE, REPAIR CABLE (testing)

### Questions to Resolve
- Exact time scale for repairs (30min repair = how many real seconds?)
- Item image availability (do images exist or need placeholders?)
- Starting ship state (which systems broken initially for tutorial?)
- Player spawn location (Captains Quarters? Stasis pod?)
- Real-time wait durations for various time skips (repairs, stasis, jumps)

### Success Criteria for Phase 5
By the end of Phase 5, the following must be demonstrable:
- ✓ Terminal command to break any cable by ID
- ✓ SVG map updates immediately (red connection)
- ✓ Room power status recalculates
- ✓ Unpowered rooms show red fill
- ✓ Terminal command to repair cable
- ✓ SVG map updates (green connection)
- ✓ Power restored, rooms show green fill

---

## Context for Future Sessions
This document contains complete context for resuming development with any LLM. Key points:

- Developer is automotive mechanic (not professional programmer) working with AI assistance
- Previous iteration (Project Dark Star) used Python/Arcade, suffered from text rendering issues and technical debt
- New approach (Project Orion) uses Flask backend + web frontend for better UI flexibility
- Developer values organization, modular architecture, and thoughtful planning
- Goal is realistic ship simulation - "if ship dies, you die" - slow burner, generous time windows
- Build incrementally, validate each layer before proceeding
- Electrical system is proof-of-concept for all other systems (same pattern replicates)
- **Phase 4 complete:** SVG diagnostic map with live power visualization ✅
- **Ship model:** XS Stock Light Freighter from SWTOR (Corellian freighter)
- **Manual SVG creation** chosen over Blender workflow for simplicity
- All planned scenarios validated against architecture - no rewrites required
- Feature priorities: Core features (Phase 1-9), Important features (Phase 10+), Low priority (optional)

---

**END OF DOCUMENT**

*Project Orion Design Document v1.2*  
*Generated March 2026 - Phase 4 Complete*
