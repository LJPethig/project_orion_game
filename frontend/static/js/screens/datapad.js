// frontend/static/js/screens/datapad.js
// Datapad panel — portable device UI, menu navigation, power map access.

// ── State ─────────────────────────────────────────────────────
let _datapadSubMenu = null;   // null = main menu, string = current sub-menu id
let _datapadParentMenu = null;  // tracks parent for R (return) from views

// ── Panel open/close ──────────────────────────────────────────

function isDatapadOpen() {
    const panel = document.getElementById('panel-datapad');
    return panel && panel.classList.contains('open');
}

function openDatapadPanel() {
    _datapadSubMenu = null;
    _setDatapadMode(true);
    _renderDatapad();
    _setupDatapadKeys();
}

function closeDatapadIfOpen() {
    const panel = document.getElementById('panel-datapad');
    const tab   = document.querySelector('.tab[data-panel="panel-datapad"]');
    if (panel && panel.classList.contains('open')) {
        panel.classList.remove('open');
        if (tab) tab.classList.remove('active');
    }
}

function _setDatapadMode(active) {
    const input  = document.getElementById('command-input');
    const prompt = document.getElementById('input-prompt');
    if (active) {
        input.disabled = true;
        input.blur();
        prompt.style.visibility = 'hidden';
    } else {
        input.disabled = false;
        input.focus();
        prompt.style.visibility = 'visible';
    }
}

// ── Rendering ─────────────────────────────────────────────────

function _renderDatapad() {
    const inner = document.getElementById('datapad-panel-inner');
    inner.innerHTML = '';

    // Header
    const header = document.createElement('div');
    header.className   = 'pad-header';
    header.textContent = 'TEMPUS FUGIT';
    inner.appendChild(header);

    const subheader = document.createElement('div');
    subheader.className   = 'pad-subheader';
    subheader.textContent = _datapadSubMenu ? _getSubMenuTitle(_datapadSubMenu) : 'DATAPAD';
    inner.appendChild(subheader);

    const menu = document.createElement('div');
    menu.className = 'pad-menu';

    const items = _getMenuItems();
    items.forEach(item => {
        const row = document.createElement('div');
        row.className   = 'pad-menu-item';
        row.textContent = item.label;
        menu.appendChild(row);
    });

    inner.appendChild(menu);

    const prompt = document.createElement('div');
    prompt.className   = 'pad-prompt';
    prompt.textContent = 'Select:';
    inner.appendChild(prompt);
}

function _getSubMenuTitle(subMenu) {
    if (subMenu === 'ship_systems') return 'SHIP SYSTEMS';
    if (subMenu === 'data')         return 'DATA';
    return 'DATAPAD';
}

function _getMenuItems() {
    if (!_datapadSubMenu) {
        return [
            { key: 's', label: '[S] Ship Systems' },
            { key: 'd', label: '[D] Data' },
            { key: 'x', label: '[X] Close' },
        ];
    }
    if (_datapadSubMenu === 'ship_systems') {
        return [
            { key: 'p', label: '[P] Power Map' },
            { key: 'c', label: '[C] Circuit Diagram' },
            { key: 'r', label: '[R] Return' },
            { key: 'x', label: '[X] Close' },
        ];
    }
    if (_datapadSubMenu === 'data') {
        return [
            { key: 'n', label: '[N] Notes' },
            { key: 'l', label: "[L] Ship's Log" },
            { key: 'm', label: '[M] Messages' },
            { key: 'r', label: '[R] Return' },
            { key: 'x', label: '[X] Close' },
        ];
    }
    return [];
}

// ── Menu interaction ──────────────────────────────────────────

function _handleDatapadKey(key) {
    if (!_datapadSubMenu) {
        if (key === 's') { _datapadSubMenu = 'ship_systems'; _renderDatapad(); return; }
        if (key === 'd') { _datapadSubMenu = 'data';         _renderDatapad(); return; }
        if (key === 'x') { _closeDatapadFromMenu(); return; }
        return;
    }

    if (_datapadSubMenu === 'ship_systems') {
        if (key === 'p') { _openPowerMap();       return; }
        if (key === 'c') { _openCircuitDiagram(); return; }
        if (key === 'r') { _datapadSubMenu = null; _renderDatapad(); return; }
        if (key === 'x') { _closeDatapadFromMenu(); return; }
        return;
    }

    if (_datapadSubMenu === 'data') {
        if (key === 'n') { _openNotes();   return; }
        if (key === 'l') { _openShipLog(); return; }
        if (key === 'm') { _openMessages(); return; }
        if (key === 'r') { _datapadSubMenu = null; _renderDatapad(); return; }
        if (key === 'x') { _closeDatapadFromMenu(); return; }
        return;
    }

    // View sub-states — R returns to parent menu
    if (key === 'r') { _datapadSubMenu = _datapadParentMenu; _renderDatapad(); return; }
    if (key === 'x') { _closeDatapadFromMenu(); return; }

    // Map pan/zoom — reuse terminal map constants
    if (_datapadSubMenu === 'power_map') {
        if (key === 'arrowup')    { _mapPanY += MAP_PAN_STEP; _applyMapTransform(); return; }
        if (key === 'arrowdown')  { _mapPanY -= MAP_PAN_STEP; _applyMapTransform(); return; }
        if (key === 'arrowleft')  { _mapPanX += MAP_PAN_STEP; _applyMapTransform(); return; }
        if (key === 'arrowright') { _mapPanX -= MAP_PAN_STEP; _applyMapTransform(); return; }
        if (key === '+' || key === '=') {
            _mapScale = Math.min(MAP_SCALE_MAX, _mapScale + MAP_SCALE_STEP);
            _applyMapTransform(); return;
        }
        if (key === '-') {
            _mapScale = Math.max(MAP_SCALE_MIN, _mapScale - MAP_SCALE_STEP);
            _applyMapTransform(); return;
        }
    }
}

function _closeDatapadFromMenu() {
    const panel = document.getElementById('panel-datapad');
    const tab   = document.querySelector('.tab[data-panel="panel-datapad"]');
    if (panel) panel.classList.remove('open');
    if (tab)   tab.classList.remove('active');
    document.removeEventListener('keydown', _datapadKeyHandler);
    _setDatapadMode(false);
}

// ── Power map ─────────────────────────────────────────────────

async function _openPowerMap() {
    _datapadParentMenu = 'ship_systems';
    _datapadSubMenu = 'power_map';
    const inner = document.getElementById('datapad-panel-inner');
    inner.innerHTML = '';

    const header = document.createElement('div');
    header.className   = 'pad-header';
    header.textContent = 'TEMPUS FUGIT';
    inner.appendChild(header);

    const subheader = document.createElement('div');
    subheader.className   = 'pad-subheader';
    subheader.textContent = 'POWER MAP';
    inner.appendChild(subheader);

    const commands = document.createElement('div');
    commands.className   = 'pad-commands';
    commands.textContent = '[R] Return    [X] Close    Arrow keys pan    [+][-] zoom';
    inner.appendChild(commands);

    const mapContainer = document.createElement('div');
    mapContainer.className = 'pad-map-container';
    mapContainer.id        = 'pad-map-container';
    inner.appendChild(mapContainer);

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
            _applyMapTransform();
            await _updateRoomColours();
        }
    } catch (e) {
        mapContainer.textContent = 'Map unavailable.';
    }
}

// ── Circuit diagram ───────────────────────────────────────────

function _openCircuitDiagram() {
    _datapadParentMenu = 'ship_systems';
    _datapadSubMenu = 'circuit_diagram';
    const inner = document.getElementById('datapad-panel-inner');
    inner.innerHTML = '';

    const header = document.createElement('div');
    header.className   = 'pad-header';
    header.textContent = 'TEMPUS FUGIT';
    inner.appendChild(header);

    const subheader = document.createElement('div');
    subheader.className   = 'pad-subheader';
    subheader.textContent = 'CIRCUIT DIAGRAM';
    inner.appendChild(subheader);

    const placeholder = document.createElement('div');
    placeholder.className   = 'pad-placeholder';
    placeholder.textContent = 'Circuit diagram not yet available.';
    inner.appendChild(placeholder);

    const commands = document.createElement('div');
    commands.className   = 'pad-commands';
    commands.textContent = '[R] Return    [X] Close';
    inner.appendChild(commands);
}

// ── Stub views ────────────────────────────────────────────────

function _openNotes() {
    _renderStubView('NOTES', 'No active notes.');
}

function _openShipLog() {
    _renderStubView("SHIP'S LOG", 'No log entries.');
}

function _openMessages() {
    _renderStubView('MESSAGES', 'No messages.');
}

function _renderStubView(title, emptyText) {
    _datapadParentMenu = 'data';
    _datapadSubMenu = title.toLowerCase().replace(/[^a-z]/g, '_');
    const inner = document.getElementById('datapad-panel-inner');
    inner.innerHTML = '';

    const header = document.createElement('div');
    header.className   = 'pad-header';
    header.textContent = 'TEMPUS FUGIT';
    inner.appendChild(header);

    const subheader = document.createElement('div');
    subheader.className   = 'pad-subheader';
    subheader.textContent = title;
    inner.appendChild(subheader);

    const content = document.createElement('div');
    content.className   = 'pad-empty';
    content.textContent = emptyText;
    inner.appendChild(content);

    const commands = document.createElement('div');
    commands.className   = 'pad-commands';
    commands.textContent = '[R] Return    [X] Close';
    inner.appendChild(commands);
}

// ── Keyboard ──────────────────────────────────────────────────

function _setupDatapadKeys() {
    document.removeEventListener('keydown', _datapadKeyHandler);
    document.addEventListener('keydown', _datapadKeyHandler);
}

function _datapadKeyHandler(e) {
    if (!isDatapadOpen()) return;
    if (isTerminalSessionActive()) return;
    if (document.activeElement === document.getElementById('debug-input')) return;

    const key = e.key.toLowerCase();
    e.preventDefault();

    _handleDatapadKey(key);
}