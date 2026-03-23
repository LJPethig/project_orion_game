.
├── backend
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── command.py
│   │   └── game.py
│   ├── events
│   │   └── __init__.py
│   ├── handlers
│   │   ├── __init__.py
│   │   ├── base_handler.py
│   │   ├── command_handler.py
│   │   ├── door_handler.py
│   │   ├── item_handler.py
│   │   ├── movement_handler.py
│   │   └── repair_handler.py
│   ├── loaders
│   │   ├── __init__.py
│   │   └── item_loader.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── chronometer.py
│   │   ├── door.py
│   │   ├── game_manager.py
│   │   ├── interactable.py
│   │   ├── player.py
│   │   ├── room.py
│   │   └── ship.py
│   └── systems
│       ├── __init__.py
│       └── electrical
│           └── __init__.py
├── config.py
├── data
│   ├── __init__.py
│   ├── game
│   │   └── __init__.py
│   ├── items
│   │   ├── __init__.py
│   │   ├── consumables.json
│   │   ├── misc_items.json
│   │   ├── storage_units.json
│   │   ├── surfaces.json
│   │   ├── terminals.json
│   │   ├── tools.json
│   │   └── wearables.json
│   └── ship
│       ├── __init__.py
│       ├── structure
│       │   ├── __init__.py
│       │   ├── door_status.json
│       │   ├── initial_ship_state.json
│       │   ├── player_items.json
│       │   ├── ship_items.json
│       │   └── ship_rooms.json
│       └── systems
│           └── __init__.py
├── docs
│   ├── Project_Orion_Design_v4.md
│   └── UI_UX_Description_Panel_v2.md
├── frontend
│   ├── __init__.py
│   ├── static
│   │   ├── __init__.py
│   │   ├── css
│   │   │   ├── __init__.py
│   │   │   ├── game.css
│   │   │   └── splash.css
│   │   └── js
│   │       ├── __init__.py
│   │       ├── components
│   │       │   └── __init__.py
│   │       ├── core
│   │       │   ├── __init__.py
│   │       │   ├── api.js
│   │       │   ├── constants.js
│   │       │   └── loop.js
│   │       └── screens
│   │           ├── __init__.py
│   │           ├── game.js
│   │           └── splash.js
│   └── templates
│       ├── __init__.py
│       ├── game.html
│       └── splash.html
├── main.py
├── project_structure.md
└── requirements.txt

24 directories, 65 files
