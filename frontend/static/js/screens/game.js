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
        window.location.href = '/';
        return;
    }

    // Update ship name and time immediately
    Loop.updateShipName(state.ship_name);
    Loop.updateShipTime(state.ship_time);

    // Load and display the current room
    await loadRoom();

    // Start the polling loop
    Loop.start();

    // Wire up command input
    const input = document.getElementById('command-input');
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') handleCommand();
    });

    input.disabled = false;
    input.focus();
}

// ── Room loading ─────────────────────────────────────────────

async function loadRoom() {
    const room = await API.getRoom();
    if (room.error) {
        console.error('Room load error:', room.error);
        return;
    }

    // Set room image — falls back to image_missing.png on error
    setRoomImage(`/static/${room.background_image}`);

    // Render full room description
    renderDescription(room);
}

// ── Description rendering ────────────────────────────────────

function renderDescription(room) {
    const content = document.getElementById('description-content');
    content.innerHTML = '';

    // Room title
    const title = document.createElement('div');
    title.className = 'room-title';
    title.textContent = room.name;
    content.appendChild(title);

    // Description lines — parse *exit* and %object% markup
    room.description.forEach(line => {
        const el = document.createElement('div');
        el.className = 'room-desc';
        el.appendChild(parseMarkup(line));
        content.appendChild(el);
    });

    // Portable items — only shown when room has portables
    if (room.portable_objects && room.portable_objects.length > 0) {
        const label = document.createElement('div');
        label.className = 'section-label';
        label.textContent = 'YOU SEE';
        content.appendChild(label);

        room.portable_objects.forEach(obj => {
            const el = document.createElement('div');
            el.className = 'portable-item';
            el.dataset.object = obj.id;
            el.textContent = obj.name;
            content.appendChild(el);
        });
    }
}

// ── Markup parser ────────────────────────────────────────────
// Parses a description line containing:
//   *text*  → cyan span with data-exit attribute (future hover/click)
//   %text%  → cyan span with data-object attribute (future hover/click)
// Returns a DocumentFragment ready to append.

function parseMarkup(text) {
    const fragment = document.createDocumentFragment();
    const regex    = /(\*[^*]+\*|%[^%]+%)/g;
    let lastIndex  = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
        // Plain text before this match
        if (match.index > lastIndex) {
            fragment.appendChild(
                document.createTextNode(text.slice(lastIndex, match.index))
            );
        }

        const raw    = match[0];
        const inner  = raw.slice(1, -1);              // Strip delimiters
        const isExit = raw.startsWith('*');
        const span   = document.createElement('span');

        span.className   = 'markup-highlight';
        span.textContent = inner;

        // Data attributes are hooks for future hover/click context menus
        if (isExit) {
            span.dataset.exit = inner.toLowerCase().replace(/\s+/g, '_');
        } else {
            span.dataset.object = inner.toLowerCase().replace(/\s+/g, '_');
        }

        fragment.appendChild(span);
        lastIndex = regex.lastIndex;
    }

    // Remaining plain text after last match
    if (lastIndex < text.length) {
        fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
    }

    return fragment;
}

// ── Command handling ─────────────────────────────────────────

async function handleCommand() {
    if (Loop.isLocked()) return;

    const input = document.getElementById('command-input');
    const cmd   = input.value.trim();
    if (!cmd) return;

    input.value = '';

    // Echo the command in the response panel
    appendResponse(`> ${cmd}`, 'player-cmd');

    // TODO: send to POST /api/command and handle response
    appendResponse("Command system not yet implemented.", 'response-line');
}

// ── Response panel ───────────────────────────────────────────

function appendResponse(text, cssClass = 'response-line') {
    const content  = document.getElementById('response-content');
    const el       = document.createElement('div');
    el.className   = `response-line ${cssClass}`;
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
        img.src           = imagePath;
        img.style.display = 'block';
        placeholder.style.display = 'none';

        // Fall back to image_missing.png if image fails to load
        img.onerror = () => {
            img.src     = '/static/images/image_missing.png';
            img.onerror = null;
        };
    } else {
        img.style.display         = 'none';
        placeholder.style.display = 'block';
    }
}
