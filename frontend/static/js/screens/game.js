// frontend/static/js/screens/game.js
// Main orchestrator — initialisation, room loading, state variables.

// frontend/static/js/screens/game.js
// Main game screen — thin orchestrator.

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
        document.getElementById('tab-strip').classList.toggle('term-active', panelId === 'panel-terminal');
    } else {
        document.getElementById('tab-strip').classList.remove('term-active');
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
    setRoomImage(`/static/${room.background_image}`);
    renderDescription(room);

    // Close any open slide panels only on room change
    if (roomChanged) {
        document.querySelectorAll('.slide-panel').forEach(p => p.classList.remove('open'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    }
}

// ── Description rendering ────────────────────────────────────
