// frontend/static/js/screens/game.js
// Main game screen — orchestrator, room loading, state variables.

// Current room exit data — used for door state tooltips
let currentExits = {};

// Current room object states — used for container/surface tooltips
let currentObjects = {};

// PIN mode state
let pendingPin = null;   // null or { door_id, door_action }

// Currently expanded surface ID in Layer 3 (null = collapsed)
let expandedSurface = null;

// Current room ID — used to detect room changes
let currentRoomId = null;

// Current room power state — used to detect addendum state changes
let currentRoomPowered = null;

// Current reactor state — used to detect addendum state changes
let currentReactorState = null;

document.addEventListener('DOMContentLoaded', () => {
    init();
});

async function init() {
    const state = await API.getState();
    if (!state.initialised) {
        window.location.href = '/';
        return;
    }

    Loop.updateShipName(state.ship_name);
    Loop.updateShipTime(state.ship_time);
    await loadRoom();
    Loop.start();

    const input = document.getElementById('command-input');
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleCommand();
    });

    input.disabled = false;
    input.focus();

    // ── Refocus input after any click ────────────────────
    document.addEventListener('click', () => {
        if (!Loop.isLocked() && !isTerminalSessionActive()) {
            input.focus();
        }
    });

    // ── Tab strip ────────────────────────────────────────
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            togglePanel(tab.dataset.panel, tab);
        });
    });
}

// ── Slide panel toggle ───────────────────────────────────────

function togglePanel(panelId, tab) {
    const panel      = document.getElementById(panelId);
    const isOpen     = panel.classList.contains('open');

    // Close all panels and deactivate all tabs first
    document.querySelectorAll('.slide-panel').forEach(p => p.classList.remove('open'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    if (typeof hideTerminalPanel === 'function') hideTerminalPanel();

    // If it wasn't open, open it now
    if (!isOpen) {
        panel.classList.add('open');
        tab.classList.add('active');
        if (panelId === 'panel-inventory') renderInventory();
        if (panelId === 'panel-datapad') openDatapadPanel();
        document.getElementById('tab-strip').classList.toggle('term-active', panelId === 'panel-terminal');
    } else {
        document.getElementById('tab-strip').classList.remove('term-active');
    }
}

function updateDatapadTab(hasDatapad) {
    const tab = document.getElementById('tab-pad');
    if (!tab) return;
    if (hasDatapad) {
        tab.classList.remove('hidden');
    } else {
        tab.classList.add('hidden');
        // Close panel if open and datapad removed
        const panel = document.getElementById('panel-datapad');
        if (panel && panel.classList.contains('open')) {
            panel.classList.remove('open');
            tab.classList.remove('active');
        }
    }
}

// ── Room loading ─────────────────────────────────────────────

async function loadRoom() {
    const room = await API.getRoom();
    if (room.error) { console.error('Room load error:', room.error); return; }
    updateRoom(room);
}

function updateRoom(room) {
    const roomChanged = room.id !== currentRoomId;
    currentRoomId  = room.id;
    currentExits   = room.exits || {};
    currentObjects = room.object_states || {};

    // ── Terminal power cut — close terminal if room loses power ──
    if (!room.room_powered && isTerminalSessionActive()) {
        closeTerminalPanel();
        clearResponse();
        appendResponse('The terminal goes offline.');
        appendMonologue('Dammit, a power failure? As if I don\'t have enough reports to file already.');
    }
    const powerStateChanged    = currentRoomPowered !== null && currentRoomPowered !== room.room_powered;
    const reactorStateChanged  = currentReactorState !== null && currentReactorState !== room.reactor_state;
    currentRoomPowered   = room.room_powered !== false;
    currentReactorState  = room.reactor_state || 'online';

    // Select room image based on power and reactor state
    const baseImage     = room.background_image.replace(/(\.[^.]+)$/, '');
    const ext           = room.background_image.match(/(\.[^.]+)$/)?.[1] || '.png';
    const reactorOff    = currentReactorState === 'offline' || currentReactorState === 'ejected';
    const unpoweredSuffix = currentRoomPowered ? '' : '_unpowered';
    const reactorSuffix   = reactorOff ? '_reactor_off' : '';
    const imagePath     = `/static/${baseImage}${unpoweredSuffix}${reactorSuffix}${ext}`;
    setRoomImage(imagePath);

    renderDescription(room, powerStateChanged, reactorStateChanged);

    // Close any open slide panels only on room change
    if (roomChanged) {
        document.querySelectorAll('.slide-panel').forEach(p => p.classList.remove('open'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    }
    // Refresh datapad tab visibility
    API.getState().then(state => {
        if (state.has_datapad !== undefined) updateDatapadTab(state.has_datapad);
    });
}

// ── Debug console ─────────────────────────────────────────────

document.addEventListener('keydown', (e) => {
    if (e.ctrlKey && e.key === 'd') {
        e.preventDefault();
        const panel = document.getElementById('debug-panel');
        panel.classList.toggle('hidden');
        if (!panel.classList.contains('hidden')) {
            document.getElementById('debug-input').focus();
        }
    }
});

document.getElementById('debug-input').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') _debugHandleCommand();
    if (e.key === 'Escape') {
        document.getElementById('debug-panel').classList.add('hidden');
    }
});

function _debugLog(msg, type = 'info') {
    const out  = document.getElementById('debug-output');
    const line = document.createElement('div');
    line.className = `debug-${type}`;
    const ts = new Date().toLocaleTimeString('en-US', { hour12: false });
    line.textContent = `[${ts}] ${msg}`;
    out.appendChild(line);
    out.scrollTop = out.scrollHeight;
    while (out.children.length > 100) out.removeChild(out.firstChild);
}

async function _debugHandleCommand() {
    const input = document.getElementById('debug-input');
    const raw   = input.value.trim();
    if (!raw) return;
    input.value = '';

    const parts = raw.split(/\s+/);
    const cmd   = parts[0].toLowerCase();
    const arg   = parts[1] || '';

    _debugLog(`> ${raw}`, 'cmd');

    if (cmd === 'break') {
        if (!arg) { _debugLog('Usage: break <component_id>', 'err'); return; }
        await _debugBreakFix('break', arg);
    } else if (cmd === 'fix') {
        if (!arg) { _debugLog('Usage: fix <component_id>', 'err'); return; }
        await _debugBreakFix('fix', arg);
    } else if (cmd === 'eject') {
        if (!arg) { _debugLog('Usage: eject <reactor_id>', 'err'); return; }
        await _debugReactorAction('eject', arg);
    } else if (cmd === 'install') {
        if (!arg) { _debugLog('Usage: install <reactor_id>', 'err'); return; }
        await _debugReactorAction('install', arg);
    } else {
        _debugLog(`Unknown command. Try: break <id> | fix <id> | eject <id> | install <id>`, 'err');
    }
}

async function _debugBreakFix(action, componentId) {
    try {
        const resp = await fetch(
            `/api/systems/electrical/${action}/${encodeURIComponent(componentId)}`,
            { method: 'POST' }
        );
        const data = await resp.json();

        if (!data.success) {
            _debugLog(`FAIL: ${data.error}`, 'err');
            return;
        }

        const powered = Object.values(data.room_power).filter(Boolean).length;
        const total   = Object.values(data.room_power).length;
        const type    = action === 'break' ? 'warn' : 'ok';
        _debugLog(`${data.component_type.toUpperCase()} [${data.component_id}] → ${data.action.toUpperCase()}`, type);
        _debugLog(`Rooms powered: ${powered}/${total}`, powered === total ? 'ok' : 'warn');

        // Refresh map colours if map is currently open
        if (typeof _updateRoomColours === 'function') {
            await _updateRoomColours();
        }
        loadRoom();

    } catch (err) {
        _debugLog(`Network error: ${err.message}`, 'err');
    }
}

async function _debugReactorAction(action, reactorId) {
    try {
        const resp = await fetch(
            `/api/systems/electrical/reactor/${action}/${encodeURIComponent(reactorId)}`,
            { method: 'POST' }
        );
        const data = await resp.json();

        if (!data.success) {
            _debugLog(`FAIL: ${data.error}`, 'err');
            return;
        }

        _debugLog(`REACTOR [${data.component_id}] → ${data.action.toUpperCase()}`, action === 'eject' ? 'warn' : 'ok');

        if (typeof _updateRoomColours === 'function') {
            await _updateRoomColours();
        }
        loadRoom();

    } catch (err) {
        _debugLog(`Network error: ${err.message}`, 'err');
    }
}
