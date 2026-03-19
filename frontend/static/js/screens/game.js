// frontend/static/js/screens/game.js
// Main game screen — thin orchestrator.
// Wires up the input, starts the polling loop, handles command submission.
// All fetch calls go through API. All state updates go through Loop.

document.addEventListener('DOMContentLoaded', () => {
    init();
});

async function init() {
    // Verify the game is initialised (in case someone navigates directly to /game)
    const state = await API.getState();

    if (!state.initialised) {
        // Not started via splash — redirect back
        window.location.href = '/';
        return;
    }

    // Update ship name and time immediately
    Loop.updateShipName(state.ship_name);
    Loop.updateShipTime(state.ship_time);

    // Start the polling loop
    Loop.start();

    // Wire up command input
    const input = document.getElementById('command-input');
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleCommand();
    });

    // Enable input and focus
    input.disabled = false;
    input.focus();

    // Placeholder description until Phase 7 (room loading)
    setDescription([
        { type: 'title', text: "SHIP SYSTEMS ONLINE" },
        { type: 'desc',  text: "Awaiting ship data..." },
    ]);
}

// ── Command handling ─────────────────────────────────────────

async function handleCommand() {
    if (Loop.isLocked()) return;

    const input = document.getElementById('command-input');
    const cmd   = input.value.trim();
    if (!cmd) return;

    input.value = '';

    // Echo the command in the response panel
    appendResponse(cmd, 'player-cmd');

    // TODO Phase 8: send to POST /api/command and handle response
    // For now just echo back
    appendResponse("Command system not yet implemented.", 'response-line');
}

// ── Description panel ────────────────────────────────────────

function setDescription(lines) {
    const content = document.getElementById('description-content');
    content.innerHTML = '';

    lines.forEach(line => {
        const el = document.createElement('div');

        switch (line.type) {
            case 'title':
                el.className = 'room-title';
                break;
            case 'desc':
                el.className = 'room-desc';
                break;
            case 'label':
                el.className = 'section-label';
                break;
            case 'exit':
                el.className = 'exit-item';
                break;
            case 'fixed':
                el.className = 'fixed-item';
                break;
            case 'portable':
                el.className = 'portable-item';
                break;
            default:
                el.className = 'room-desc';
        }

        el.textContent = line.text;
        content.appendChild(el);
    });
}

// ── Response panel ───────────────────────────────────────────

function appendResponse(text, cssClass = 'response-line') {
    const content = document.getElementById('response-content');
    const el      = document.createElement('div');
    el.className  = `response-line ${cssClass}`;
    el.textContent = text;
    content.appendChild(el);

    // Auto-scroll to latest response
    content.scrollTop = content.scrollHeight;
}

function clearResponse() {
    document.getElementById('response-content').innerHTML = '';
}

// ── Room image ───────────────────────────────────────────────

function setRoomImage(imagePath) {
    const img         = document.getElementById('room-image');
    const placeholder = document.getElementById('room-image-placeholder');

    if (imagePath) {
        img.src          = imagePath;
        img.style.display = 'block';
        placeholder.style.display = 'none';
    } else {
        img.style.display = 'none';
        placeholder.style.display = 'block';
    }
}
