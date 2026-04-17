// frontend/static/js/screens/terminal_engineering.js
// Engineering terminal — electrical sub-menu and power map rendering.
// Depends on: terminal_core.js (terminalSubMenu, currentTerminal, closeTerminalPanel,
//                               _renderTerminal, _returnToMainMenu)
//             map.js (_applyMapTransformToContainer, _updateRoomColours, _initMapHovers,
//                     _mapPanX, _mapPanY, _mapScale, _mapSvgEl, resetMapState,
//                     MAP_PAN_STEP, MAP_SCALE_STEP, MAP_SCALE_MIN, MAP_SCALE_MAX)
//             api.js (API.getTerminalContent)
//             game.js (clearResponse, appendResponse)

// ── State ─────────────────────────────────────────────────────

let _electricalSubMenuData = null;   // electrical sub-menu data for back navigation

// ── Electrical sub-menu ───────────────────────────────────────

function _openElectricalSubMenu(data) {
    _electricalSubMenuData = data;
    terminalSubMenu = data;
    const inner = document.getElementById('terminal-panel-inner');
    inner.innerHTML = '';

    const title = document.createElement('div');
    title.className   = 'term-title';
    title.textContent = data.title;
    inner.appendChild(title);

    const menu = document.createElement('div');
    menu.className = 'term-menu';
    data.menu.forEach(item => {
        const row = document.createElement('div');
        row.className   = 'term-menu-item';
        row.textContent = item.label;
        menu.appendChild(row);
    });
    inner.appendChild(menu);

    const prompt = document.createElement('div');
    prompt.className = 'term-prompt';
    prompt.appendChild(document.createTextNode('Enter Command: '));
    const cursor = document.createElement('span');
    cursor.className = 'term-cursor';
    prompt.appendChild(cursor);
    inner.appendChild(prompt);
}

// ── Electrical map ────────────────────────────────────────────

async function _openElectricalMap(title) {
    const inner = document.getElementById('terminal-panel-inner');
    inner.innerHTML = '';

    // Title
    const titleEl = document.createElement('div');
    titleEl.className   = 'term-title';
    titleEl.textContent = title;
    inner.appendChild(titleEl);

    // Commands
    const commands = document.createElement('div');
    commands.className   = 'term-submenu-commands';
    commands.textContent = '[R] Return    [X] Exit    Arrow keys pan    [+][-] zoom    [0] Reset view';
    inner.appendChild(commands);

    // Map container
    const mapContainer = document.createElement('div');
    mapContainer.className = 'term-map-container';
    mapContainer.id        = 'term-map-container';
    inner.appendChild(mapContainer);

    // Load SVG
    try {
        const response = await fetch('/static/images/ship_layout.svg');
        const svgText  = await response.text();
        mapContainer.innerHTML = svgText;
        _mapSvgEl = mapContainer.querySelector('svg');
        if (_mapSvgEl) {
            _mapSvgEl.style.transformOrigin = '0 0';
            _mapPanX  = 0;
            _mapPanY  = 0;
            _mapScale = 0.35;
            _applyMapTransformToContainer('term-map-container');
            await _updateRoomColours();
            _initMapHovers();
        }
    } catch (e) {
        mapContainer.textContent = 'Map unavailable.';
    }

    // Set sub-menu state so R/X keys work
    terminalSubMenu = { view: 'electrical_map', title, _parent: _electricalSubMenuData };
}
