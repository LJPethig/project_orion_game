// frontend/static/js/screens/game.js
// Main game screen — thin orchestrator.
// Wires up the input, starts the polling loop, handles command submission.
// All fetch calls go through API. All state updates go through Loop.

// Current room exit data — used for door state tooltips
let currentExits = {};

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
}

// ── Room loading ─────────────────────────────────────────────

async function loadRoom() {
    const room = await API.getRoom();
    if (room.error) {
        console.error('Room load error:', room.error);
        return;
    }
    updateRoom(room);
}

function updateRoom(room) {
    // Store exit data for tooltip use
    currentExits = room.exits || {};

    setRoomImage(`/static/${room.background_image}`);
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

    // Wire up exit hover tooltips after rendering
    setupExitTooltips(content);
}

// ── Markup parser ────────────────────────────────────────────

function parseMarkup(text) {
    const fragment = document.createDocumentFragment();
    const regex    = /(\*[^*]+\*|%[^%]+%)/g;
    let lastIndex  = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            fragment.appendChild(
                document.createTextNode(text.slice(lastIndex, match.index))
            );
        }

        const raw    = match[0];
        const inner  = raw.slice(1, -1);
        const isExit = raw.startsWith('*');
        const span   = document.createElement('span');

        span.className   = 'markup-highlight';
        span.textContent = inner;

        if (isExit) {
            span.dataset.exit = inner.toLowerCase().replace(/\s+/g, '_');
        } else {
            span.dataset.object = inner.toLowerCase().replace(/\s+/g, '_');
        }

        fragment.appendChild(span);
        lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
        fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
    }

    return fragment;
}

// ── Exit hover tooltips ──────────────────────────────────────

function setupExitTooltips(container) {
    const tooltip = document.getElementById('exit-tooltip');
    if (!tooltip) return;

    container.querySelectorAll('.markup-highlight[data-exit]').forEach(span => {
        span.addEventListener('mouseenter', (e) => {
            const exitKey  = e.target.dataset.exit;
            const exitData = findExitData(exitKey);
            if (!exitData) return;

            const state     = exitData.door_state || 'none';
            const label     = exitData.label || exitKey;
            const stateText = doorStateText(state);
            const stateCol  = doorStateColour(state);

            tooltip.innerHTML = `
                <div style="color:var(--col-title)">${label}</div>
                <div style="color:${stateCol};font-size:11px">${stateText}</div>
            `;
            tooltip.classList.remove('hidden');
        });

        span.addEventListener('mousemove', (e) => {
            tooltip.style.left = (e.clientX + 14) + 'px';
            tooltip.style.top  = (e.clientY + 14) + 'px';
        });

        span.addEventListener('mouseleave', () => {
            tooltip.classList.add('hidden');
        });
    });
}

function findExitData(exitKey) {
    // Direct key match
    if (currentExits[exitKey]) return currentExits[exitKey];
    // Fuzzy match — exitKey from span may differ slightly from room exit key
    for (const [key, data] of Object.entries(currentExits)) {
        if (key.toLowerCase() === exitKey.toLowerCase()) return data;
        if ((data.label || '').toLowerCase().replace(/\s+/g, '_') === exitKey) return data;
    }
    return null;
}

function doorStateText(state) {
    switch (state) {
        case 'open':   return 'Door is open';
        case 'closed': return 'Door is closed';
        case 'locked': return 'Door is locked';
        default:       return 'No door';
    }
}

function doorStateColour(state) {
    switch (state) {
        case 'open':   return 'var(--col-prompt)';
        case 'closed': return 'var(--col-text)';
        case 'locked': return 'var(--col-alert)';
        default:       return 'var(--col-text)';
    }
}

// ── Command handling ─────────────────────────────────────────

async function handleCommand() {
    if (Loop.isLocked()) return;

    const input = document.getElementById('command-input');
    const cmd   = input.value.trim();
    if (!cmd) return;

    input.value = '';

    clearResponse();
    appendResponse(`> ${cmd}`, 'player-cmd');

    const result = await API.sendCommand(cmd);

    if (result.response) {
        appendResponse(result.response);
    }

    if (result.ship_time) {
        Loop.updateShipTime(result.ship_time);
    }

    if (result.room_changed && result.room) {
        updateRoom(result.room);
    }
}

// ── Response panel ───────────────────────────────────────────

function appendResponse(text, cssClass = 'response-line') {
    const content  = document.getElementById('response-content');
    const el       = document.createElement('div');
    el.className   = `response-line ${cssClass}`;
    el.textContent = text;
    content.appendChild(el);
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

        img.onerror = () => {
            img.src     = '/static/images/image_missing.png';
            img.onerror = null;
        };
    } else {
        img.style.display         = 'none';
        placeholder.style.display = 'block';
    }
}
