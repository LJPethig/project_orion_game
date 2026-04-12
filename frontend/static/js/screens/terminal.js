// frontend/static/js/screens/terminal.js
// Terminal panel — renders terminal menu, handles keypress navigation, exit.

// ── Constants ─────────────────────────────────────────────────
const TERM_CHAR_SPEED_MS   = 20;    // Base ms per character
const TERM_JITTER_MIN      = 0.6;   // Minimum jitter multiplier
const TERM_JITTER_MAX      = 2.2;   // Maximum jitter multiplier
const TERM_LINE_PAUSE_MS   = 80;    // Extra pause between lines
const TERM_BLANK_PAUSE_MS  = 120;   // Pause for blank lines

// ── State ─────────────────────────────────────────────────────
let currentTerminal      = null;   // current terminal data from backend
let terminalSubMenu      = null;   // null = main menu, object = sub-menu content
let _typewriterActive    = false;  // true while typing is in progress
let _typewriterCancelled = false;  // set to true to abort current typewriter
let _electricalSubMenuData = null;   // electrical sub-menu data for back navigation


// ── Terminal mode — blocks command input ──────────────────────

function setTerminalMode(active) {
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

// ── Panel open/close ──────────────────────────────────────────

function isTerminalOpen() {
    const panel = document.getElementById('panel-terminal');
    return panel && panel.classList.contains('open');
}

function isTerminalSessionActive() {
    return currentTerminal !== null;
}

function openTerminalPanel(terminalData) {
    currentTerminal = terminalData;
    terminalSubMenu = null;

    if (terminalData.terminal_type === 'storage_room') {
        _openStorageManifest();
    } else if (terminalData.terminal_type === 'cargo_bay') {
        _openCargoManifest();
    } else {
        _renderTerminal();
    }

    // Show TERM tab, hide PAD tab — mutually exclusive
    const tab = document.getElementById('tab-term');
    tab.classList.remove('hidden');
    const padTab = document.getElementById('tab-pad');
    if (padTab) padTab.classList.add('hidden');

    // Close datapad session if open
    if (typeof _closeDatapadFromMenu === 'function') _closeDatapadFromMenu();

    // Open panel, close any others
    document.querySelectorAll('.slide-panel').forEach(p => p.classList.remove('open'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('panel-terminal').classList.add('open');
    tab.classList.add('active');
    document.getElementById('tab-strip').classList.add('term-active');

    setTerminalMode(true);
    _setupTerminalKeys();
}

function hideTerminalPanel() {
    // Close the panel visually but keep the session — tab stays visible
    // Typewriter continues in background
    document.getElementById('panel-terminal').classList.remove('open');
    document.getElementById('tab-term').classList.remove('active');
    document.getElementById('tab-strip').classList.remove('term-active');
}

function closeTerminalPanel() {
    _cancelTypewriter();
    currentTerminal = null;
    terminalSubMenu = null;
    document.getElementById('panel-terminal').classList.remove('open');
    const tab = document.getElementById('tab-term');
    tab.classList.remove('active');
    tab.classList.add('hidden');
    document.getElementById('tab-strip').classList.remove('term-active');
    document.removeEventListener('keydown', _terminalKeyHandler);
    setTerminalMode(false);
    API.terminalClose().then(() => {
        API.getState().then(state => updateDatapadTab(state.has_datapad || false));
    });
}

// ── Rendering ─────────────────────────────────────────────────

function _renderTerminal() {
    const inner = document.getElementById('terminal-panel-inner');
    inner.innerHTML = '';

    const title = document.createElement('div');
    title.className   = 'term-title';
    title.textContent = terminalSubMenu ? terminalSubMenu.title : currentTerminal.terminal_name;
    inner.appendChild(title);

    if (terminalSubMenu) {
        // ── Sub-menu — type out text content, then show Return prompt ─
        const content = document.createElement('div');
        content.className = 'term-content';

        const lineDivs = terminalSubMenu.text.map(line => {
            const row = document.createElement('div');
            row.className = line === '' ? 'term-content-blank' : 'term-content-line';
            content.appendChild(row);
            return { el: row, text: line };
        });

        inner.appendChild(content);

        // Commands line — hidden until typing completes
        const commands = document.createElement('div');
        commands.className = 'term-submenu-commands';
        commands.textContent = '[R] Return    [X] Exit';
        commands.style.visibility = 'hidden';
        inner.appendChild(commands);

        // Enter Command prompt — hidden until typing completes
        const prompt = document.createElement('div');
        prompt.className = 'term-prompt';
        prompt.style.visibility = 'hidden';

        const promptText = document.createTextNode('Enter Command: ');
        prompt.appendChild(promptText);

        const cursor = document.createElement('span');
        cursor.className = 'term-cursor';
        prompt.appendChild(cursor);

        inner.appendChild(prompt);

        _typewriteLines(lineDivs, () => {
            commands.style.visibility = 'visible';
            prompt.style.visibility = 'visible';
        });

    } else {
        // ── Main menu ─────────────────────────────────────
        const menu = document.createElement('div');
        menu.className = 'term-menu';
        menu.id        = 'term-menu';

        currentTerminal.menu.forEach(item => {
            const row = document.createElement('div');
            row.className   = 'term-menu-item';
            row.textContent = item.label;
            menu.appendChild(row);
        });

        inner.appendChild(menu);

        // Enter Command prompt with blinking cursor
        const prompt = document.createElement('div');
        prompt.className = 'term-prompt';

        const promptText = document.createTextNode('Enter Command: ');
        prompt.appendChild(promptText);

        const cursor = document.createElement('span');
        cursor.className = 'term-cursor';
        prompt.appendChild(cursor);

        inner.appendChild(prompt);
    }
}

// ── Typewriter ────────────────────────────────────────────────

function _cancelTypewriter() {
    _typewriterCancelled = true;
    _typewriterActive    = false;
}

function _jitteredDelay() {
    const multiplier = TERM_JITTER_MIN + Math.random() * (TERM_JITTER_MAX - TERM_JITTER_MIN);
    return TERM_CHAR_SPEED_MS * multiplier;
}

function _typewriteLines(lineDivs, onComplete) {
    _typewriterCancelled = false;
    _typewriterActive    = true;

    let lineIdx = 0;
    const cursor = document.createElement('span');
    cursor.className = 'term-cursor typing';

    function typeNextLine() {
        if (_typewriterCancelled) return;
        if (lineIdx >= lineDivs.length) {
            _typewriterActive = false;
            cursor.remove();
            if (onComplete) onComplete();
            return;
        }

        const { el, text } = lineDivs[lineIdx];
        lineIdx++;

        if (text === '') {
            el.appendChild(cursor);
            setTimeout(() => {
                cursor.remove();
                typeNextLine();
            }, TERM_BLANK_PAUSE_MS);
            return;
        }

        let charIdx = 0;

        function typeNextChar() {
            if (_typewriterCancelled) return;
            if (charIdx >= text.length) {
                cursor.remove();
                setTimeout(typeNextLine, TERM_LINE_PAUSE_MS);
                return;
            }
            el.insertBefore(document.createTextNode(text[charIdx]), cursor);
            charIdx++;
            setTimeout(typeNextChar, _jitteredDelay());
        }

        el.appendChild(cursor);
        typeNextChar();
    }

    typeNextLine();
}

// ── Menu interaction ──────────────────────────────────────────

function _handleMenuKey(key) {
    // ── Storage terminal — X to exit, arrows to navigate ─────
    if (currentTerminal && currentTerminal.terminal_type === 'storage_room') {
        if (key === 'x') {
            const name = currentTerminal.terminal_name;
            closeTerminalPanel();
            clearResponse();
            appendResponse(`You close the ${name}.`);
        }
        if (key === 'arrowdown') {
            const next = Math.min(_storageSelectedIndex + 1, _storageManifestData.length - 1);
            _storageSelectItem(next);
        }
        if (key === 'arrowup') {
            const prev = Math.max(_storageSelectedIndex - 1, 0);
            _storageSelectItem(prev);
        }
        if (key === 'r' && _storageSelectedIndex >= 0 && _storageManifestData.length > 0) {
            const entry = _storageManifestData[_storageSelectedIndex];
            if (entry) _retrieveFromStorage(entry.instance_id);
        }
        return;
    }

    // ── Cargo bay terminal — X to exit, arrows to navigate ───
    if (currentTerminal && currentTerminal.terminal_type === 'cargo_bay') {
        if (key === 'x') {
            const name = currentTerminal.terminal_name;
            closeTerminalPanel();
            clearResponse();
            appendResponse(`You close the ${name}.`);
        }
        if (key === 'arrowdown') {
            const next = Math.min(_cargoSelectedIndex + 1, _cargoManifestData.length - 1);
            _cargoSelectItem(next);
        }
        if (key === 'arrowup') {
            const prev = Math.max(_cargoSelectedIndex - 1, 0);
            _cargoSelectItem(prev);
        }
        return;
    }

    if (_typewriterActive) return;

    const menu = terminalSubMenu ? null : currentTerminal.menu;

    if (terminalSubMenu) {
        // ── Electrical sub-menu ───────────────────────────
        if (terminalSubMenu.view === 'electrical_menu') {
            const item = terminalSubMenu.menu.find(m => m.key === key);
            if (!item) return;
            if (item.action === 'return') { _returnToMainMenu(); return; }
            if (item.action === 'exit') {
                const name = currentTerminal.terminal_name;
                closeTerminalPanel();
                clearResponse();
                appendResponse(`You close the ${name}.`);
                return;
            }
            API.getTerminalContent(currentTerminal.terminal_type, item.action).then(data => {
                if (data.error) return;
                if (data.view === 'electrical_map') {
                    _openElectricalMap(data.title);
                } else {
                    terminalSubMenu = data;
                    _renderTerminal();
                }
            });
            return;
        }
        // ── Map pan/zoom ──────────────────────────────────
        if (terminalSubMenu.view === 'electrical_map') {
            if (key === 'arrowup')    { _mapPanY += MAP_PAN_STEP;_applyMapTransformToContainer('term-map-container'); return; }
            if (key === 'arrowdown')  { _mapPanY -= MAP_PAN_STEP;_applyMapTransformToContainer('term-map-container'); return; }
            if (key === 'arrowleft')  { _mapPanX += MAP_PAN_STEP;_applyMapTransformToContainer('term-map-container'); return; }
            if (key === 'arrowright') { _mapPanX -= MAP_PAN_STEP;_applyMapTransformToContainer('term-map-container'); return; }
            if (key === '+' || key === '=') {
                _mapScale = Math.min(MAP_SCALE_MAX, _mapScale + MAP_SCALE_STEP);
                _applyMapTransformToContainer('term-map-container'); return;
            }
            if (key === '-') {
                _mapScale = Math.max(MAP_SCALE_MIN, _mapScale - MAP_SCALE_STEP);
                _applyMapTransformToContainer('term-map-container'); return;
            }
            if (key === '0') {
            resetMapState();
            _applyMapTransformToContainer('term-map-container');
            return;
        }
        }
        if (key === 'r') {
            // If we came from electrical sub-menu, go back there
            if (terminalSubMenu && terminalSubMenu._parent) {
                _openElectricalSubMenu(terminalSubMenu._parent);
            } else {
                _returnToMainMenu();
            }
        }
        if (key === 'x') {
            const name = currentTerminal.terminal_name;
            closeTerminalPanel();
            clearResponse();
            appendResponse(`You close the ${name}.`);
        }
        return;
    }

    // Main menu — find matching key
    const item = menu.find(m => m.key === key);
    if (!item) return;

    if (item.action === 'exit') {
        const name = currentTerminal.terminal_name;
        closeTerminalPanel();
        clearResponse();
        appendResponse(`You close the ${name}.`);
        return;
    }

    API.getTerminalContent(currentTerminal.terminal_type, item.action).then(data => {
        if (data.error) return;
        if (data.view === 'electrical_map') {
            _openElectricalMap(data.title);
        } else if (data.view === 'electrical_menu') {
            _openElectricalSubMenu(data);
        } else {
            terminalSubMenu = data;
            _renderTerminal();
        }
    });
}

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

function _returnToMainMenu() {
    _cancelTypewriter();
    terminalSubMenu = null;
    _renderTerminal();
}

// ── Keyboard ──────────────────────────────────────────────────

function _setupTerminalKeys() {
    document.removeEventListener('keydown', _terminalKeyHandler);
    document.addEventListener('keydown', _terminalKeyHandler);
}

function _terminalKeyHandler(e) {
    if (!isTerminalSessionActive()) return;

    // Allow tab switching
    if (e.key === 'Tab') return;

    // Allow debug console input through
    if (document.activeElement === document.getElementById('debug-input')) return;

    // Swallow all other keys when terminal is active
    e.preventDefault();
    e.stopPropagation();

    const key = e.key.toLowerCase();
    _handleMenuKey(key);
}

// ── Storage manifest ──────────────────────────────────────────

let _storageManifestData  = [];
let _storageSelectedIndex = -1;

async function _openStorageManifest() {
    const inner = document.getElementById('terminal-panel-inner');
    inner.innerHTML = '';

    const title = document.createElement('div');
    title.className   = 'term-title';
    title.textContent = currentTerminal.terminal_name;
    inner.appendChild(title);

    const commands = document.createElement('div');
    commands.className   = 'term-submenu-commands';
    commands.textContent = 'UP/DOWN arrow keys to navigate    [R] Retrieve    [X] Exit';
    inner.appendChild(commands);

    const list = document.createElement('div');
    list.className = 'term-manifest-list';
    list.id        = 'term-manifest-list';
    inner.appendChild(list);

    await _renderStorageManifest();
}

async function _renderStorageManifest() {
    const data = await API.getStorageManifest();
    _storageManifestData  = data.manifest || [];
    _storageSelectedIndex = _storageManifestData.length > 0 ? 0 : -1;

    const list = document.getElementById('term-manifest-list');
    if (!list) return;
    list.innerHTML = '';

    if (_storageManifestData.length === 0) {
        const empty = document.createElement('div');
        empty.className   = 'term-content-line';
        empty.textContent = 'No items are currently stored or the database is corrupted.';
        empty.style.paddingLeft = '24px';
        list.appendChild(empty);
        return;
    }

    _storageManifestData.forEach((entry, idx) => {
        const row = document.createElement('div');
        row.className = 'term-manifest-item' + (idx === _storageSelectedIndex ? ' selected' : '');
        row.dataset.idx = idx;

        const name = document.createElement('span');
        name.textContent = entry.display_name;

        const qty = document.createElement('span');
        qty.textContent = `x${entry.quantity}`;

        const btn = document.createElement('button');
        btn.className   = 'term-manifest-retrieve';
        btn.textContent = 'RETRIEVE';
        btn.addEventListener('click', () => _retrieveFromStorage(entry.instance_id));

        row.appendChild(name);
        row.appendChild(qty);
        row.appendChild(btn);
        row.addEventListener('click', () => _storageSelectItem(idx));
        list.appendChild(row);
    });
}

function _storageSelectItem(idx) {
    _storageSelectedIndex = idx;
    let selectedEl = null;
    document.querySelectorAll('.term-manifest-item').forEach(row => {
        const isSelected = parseInt(row.dataset.idx) === idx;
        row.classList.toggle('selected', isSelected);
        if (isSelected) selectedEl = row;
    });
    if (selectedEl) {
        selectedEl.scrollIntoView({ block: 'nearest' });
    }
}

async function _retrieveFromStorage(instanceId) {
    const savedIndex = _storageSelectedIndex;
    const result = await API.retrieveItem(instanceId);
    clearResponse();
    handleResult(result);
    refreshInventoryIfOpen();
    await _renderStorageManifest();
    if (_storageManifestData.length > 0) {
        _storageSelectItem(Math.min(savedIndex, _storageManifestData.length - 1));
    }
}

// ── Cargo manifest ────────────────────────────────────────────

let _cargoManifestData  = [];
let _cargoSelectedIndex = -1;

async function _openCargoManifest() {
    const inner = document.getElementById('terminal-panel-inner');
    inner.innerHTML = '';

    const title = document.createElement('div');
    title.className   = 'term-title';
    title.textContent = currentTerminal.terminal_name;
    inner.appendChild(title);

    const commands = document.createElement('div');
    commands.className   = 'term-submenu-commands';
    commands.textContent = 'UP/DOWN arrow keys to navigate    [X] Exit';
    inner.appendChild(commands);

    const list = document.createElement('div');
    list.className = 'term-manifest-list';
    list.id        = 'term-cargo-list';
    inner.appendChild(list);

    await _renderCargoManifest();
}

async function _renderCargoManifest() {
    const data = await API.getCargoManifest();
    const list = document.getElementById('term-cargo-list');
    if (!list) return;
    list.innerHTML = '';

    // Header row
    const header = document.createElement('div');
    header.className = 'term-manifest-header';
    ['Container', 'Type', 'Contents'].forEach(label => {
        const span = document.createElement('span');
        span.textContent = label;
        header.appendChild(span);
    });
    list.appendChild(header);

    const containers     = data.containers || [];
    const pallets        = data.pallets    || [];
    const visiblePallets = pallets.filter(p => p.attached_items && p.attached_items.length > 0);

    const sizeOrder = { small: 0, medium: 1, large: 2 };
    containers.sort((a, b) => (sizeOrder[a.container_size] ?? 99) - (sizeOrder[b.container_size] ?? 99));
    _cargoManifestData  = [...containers, ...visiblePallets];
    _cargoSelectedIndex = _cargoManifestData.length > 0 ? 0 : -1;

    if (_cargoManifestData.length === 0) {
        const empty = document.createElement('div');
        empty.className   = 'term-content-line';
        empty.textContent = 'No cargo on manifest.';
        empty.style.paddingLeft = '24px';
        list.appendChild(empty);
        return;
    }

    containers.forEach((c, idx) => {
        const row = document.createElement('div');
        row.className = 'term-manifest-item' + (idx === _cargoSelectedIndex ? ' selected' : '');
        row.dataset.idx = idx;

        const ref = document.createElement('span');
        ref.textContent = c.name;

        const type = document.createElement('span');
        type.textContent = c.type_name || '';

        const contents = document.createElement('span');
        contents.textContent = c.contents.length > 0
            ? c.contents.join(', ')
            : 'Empty';

        row.appendChild(ref);
        row.appendChild(type);
        row.appendChild(contents);
        row.addEventListener('click', () => _cargoSelectItem(idx));
        list.appendChild(row);
    });

    visiblePallets.forEach((p, i) => {
        const idx = containers.length + i;
        const row = document.createElement('div');
        row.className = 'term-manifest-item' + (idx === _cargoSelectedIndex ? ' selected' : '');
        row.dataset.idx = idx;

        const ref = document.createElement('span');
        ref.textContent = p.name;

        const type = document.createElement('span');
        type.textContent = p.type_name || '';

        const items = document.createElement('span');
        items.textContent = p.attached_items.map(a => `${a.item} x${a.quantity}`).join(', ');

        row.appendChild(ref);
        row.appendChild(type);
        row.appendChild(items);
        row.addEventListener('click', () => _cargoSelectItem(idx));
        list.appendChild(row);
    });
}

function _cargoSelectItem(idx) {
    _cargoSelectedIndex = idx;
    document.querySelectorAll('#term-cargo-list .term-manifest-item').forEach(row => {
        row.classList.toggle('selected', parseInt(row.dataset.idx) === idx);
    });
    const selectedEl = document.querySelector('#term-cargo-list .term-manifest-item.selected');
    if (selectedEl) selectedEl.scrollIntoView({ block: 'nearest' });
}