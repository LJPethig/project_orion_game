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
    _setDatapadMode(true);
    _setupDatapadKeys();

    // Restore previous state
    if (_datapadSubMenu === 'power_map')      { _openPowerMap();       return; }
    if (_datapadSubMenu === 'circuit_diagram'){ _openCircuitDiagram(); return; }
    if (_datapadSubMenu === 'notes')          { _openNotes();          return; }
    if (_datapadSubMenu === 'ship_s_log')     { _openShipLog();        return; }
    if (_datapadSubMenu === 'messages')       { _openMessages();       return; }

    // Menu states and null all render fine via _renderDatapad
    _renderDatapad();
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
        if (key === 'arrowup')    { _mapPanY += MAP_PAN_STEP; _applyPadMapTransform(); return; }
        if (key === 'arrowdown')  { _mapPanY -= MAP_PAN_STEP; _applyPadMapTransform(); return; }
        if (key === 'arrowleft')  { _mapPanX += MAP_PAN_STEP; _applyPadMapTransform(); return; }
        if (key === 'arrowright') { _mapPanX -= MAP_PAN_STEP; _applyPadMapTransform(); return; }
        if (key === '+' || key === '=') {
            _mapScale = Math.min(MAP_SCALE_MAX, _mapScale + MAP_SCALE_STEP);
            _applyPadMapTransform(); return;
        }
        if (key === '-') {
            _mapScale = Math.max(MAP_SCALE_MIN, _mapScale - MAP_SCALE_STEP);
            _applyPadMapTransform(); return;
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
    _datapadSubMenu    = null;
    _datapadParentMenu = null;
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
            _applyPadMapTransform();
            await _updateRoomColours();
        }
    } catch (e) {
        mapContainer.textContent = 'Map unavailable.';
    }
}

function _applyPadMapTransform() {
    if (!_mapSvgEl) return;
    const container = document.getElementById('pad-map-container');
    if (container) {
        const cw = container.clientWidth;
        const ch = container.clientHeight;
        const sw = _mapSvgEl.viewBox.baseVal.width  * _mapScale;
        const sh = _mapSvgEl.viewBox.baseVal.height * _mapScale;
        const minX = -(sw - cw * 0.25);
        const maxX =   cw * 0.75;
        const minY = -(sh - ch * 0.25);
        const maxY =   ch * 0.75;
        _mapPanX = Math.max(minX, Math.min(maxX, _mapPanX));
        _mapPanY = Math.max(minY, Math.min(maxY, _mapPanY));
    }
    _mapSvgEl.style.transform = `translate(${_mapPanX}px, ${_mapPanY}px) scale(${_mapScale})`;
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


function _openMessages() {
    _renderStubView('MESSAGES', 'No messages.');
}

function _openNotes() {
    _datapadParentMenu = 'data';
    _datapadSubMenu    = 'notes';
    _renderDataView('NOTES', async () => {
        const data  = await API.getDatapadData();
        const notes = data.tablet_notes || [];
        if (notes.length === 0) return [{ text: 'No active notes.', style: 'pad-empty-line' }];
        const lines = [];
        notes.forEach(note => {
            lines.push({ text: note.timestamp, style: 'pad-log-timestamp' });
            lines.push({ text: note.location_str, style: 'pad-log-location' });
            if (note.faults && note.faults.length > 0) {
                lines.push({ text: 'Faulty components:', style: 'pad-note-label' });
                lines.push({ text: '  ' + note.faults.join(', '), style: 'pad-note-value' });
            }
            if (note.tools && note.tools.length > 0) {
                lines.push({ text: 'Tools required:', style: 'pad-note-label' });
                lines.push({ text: '  ' + note.tools.join(', '), style: 'pad-note-value' });
            }
            if (note.missing && note.missing.length > 0) {
                lines.push({ text: 'Missing at time of diagnosis:', style: 'pad-note-label' });
                lines.push({ text: '  ' + note.missing.join(', '), style: 'pad-note-missing' });
            }
            lines.push({ text: '─'.repeat(36), style: 'pad-log-divider' });
        });
        return lines;
    });
}

function _openShipLog() {
    _datapadParentMenu = 'data';
    _datapadSubMenu    = 'ship_s_log';
    _renderDataView("SHIP'S LOG", async () => {
        const data = await API.getDatapadData();
        const log  = data.ship_log || [];
        if (log.length === 0) return [{ text: 'No log entries.', style: 'pad-empty-line' }];
        const lines = [];
        log.forEach((entry, idx) => {
            lines.push({ text: entry.timestamp, style: 'pad-log-timestamp' });
            lines.push({ text: entry.event,     style: 'pad-log-event' });
            lines.push({ text: entry.detail,    style: 'pad-log-detail' });
            lines.push({ text: '─'.repeat(36),  style: 'pad-log-divider' });
        });
        return lines;
    });
}

async function _renderDataView(title, dataFn) {
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
    content.className = 'pad-data-content';
    inner.appendChild(content);

    const commands = document.createElement('div');
    commands.className   = 'pad-commands';
    commands.textContent = '[R] Return    [X] Close';
    inner.appendChild(commands);

    // Load data and render lines
    const lines = await dataFn();
    lines.forEach(line => {
        const el = document.createElement('div');
        el.className   = line.style;
        el.textContent = line.text;
        content.appendChild(el);
    });
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