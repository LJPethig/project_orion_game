// frontend/static/js/screens/game.js
// Main game screen — thin orchestrator.

// Current room exit data — used for door state tooltips
let currentExits = {};

// PIN mode state
let pendingPin = null;   // null or { door_id, door_action }

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
    if (room.error) { console.error('Room load error:', room.error); return; }
    updateRoom(room);
}

function updateRoom(room) {
    currentExits = room.exits || {};
    setRoomImage(`/static/${room.background_image}`);
    renderDescription(room);
}

// ── Description rendering ────────────────────────────────────

function renderDescription(room) {
    const content = document.getElementById('description-content');
    content.innerHTML = '';

    const title = document.createElement('div');
    title.className = 'room-title';
    title.textContent = room.name;
    content.appendChild(title);

    room.description.forEach(line => {
        const el = document.createElement('div');
        el.className = 'room-desc';
        el.appendChild(parseMarkup(line));
        content.appendChild(el);
    });

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
            fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
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

            const state = exitData.door_state || 'none';
            const label = exitData.label || exitKey;

            tooltip.innerHTML = `
                <div style="color:var(--col-title)">${label}</div>
                <div style="color:${doorStateColour(state)};font-size:11px">${doorStateText(state)}</div>
            `;
            tooltip.classList.remove('hidden');

            // Position will be set on mousemove
        });

        span.addEventListener('mousemove', (e) => {
            const tt   = document.getElementById('exit-tooltip');
            const tw   = tt.offsetWidth;
            const th   = tt.offsetHeight;
            const margin = 14;
            let left = e.clientX + margin;
            let top  = e.clientY + margin;

            // Flip left if tooltip would go off right edge
            if (left + tw > window.innerWidth) {
                left = e.clientX - tw - margin;
            }
            // Flip up if tooltip would go off bottom edge
            if (top + th > window.innerHeight) {
                top = e.clientY - th - margin;
            }

            tt.style.left = left + 'px';
            tt.style.top  = top  + 'px';
        });

        span.addEventListener('mouseleave', () => {
            tooltip.classList.add('hidden');
        });
    });
}

function findExitData(exitKey) {
    if (currentExits[exitKey]) return currentExits[exitKey];
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

    // ── PIN mode — route input as PIN ─────────────────────
    if (pendingPin) {
        appendResponse(`> ****`, 'player-cmd');
        await submitPin(cmd);
        return;
    }

    // ── Normal command ────────────────────────────────────
    appendResponse(`> ${cmd}`, 'player-cmd');
    const result = await API.sendCommand(cmd);
    handleResult(result);
}

function refreshExits() {
    API.getRoom().then(room => { if (!room.error) currentExits = room.exits || {}; });
}

function handleResult(result) {
    if (result.response) appendResponse(result.response);
    if (result.ship_time) Loop.updateShipTime(result.ship_time);

    // ── Door locked — show closed hatch image, stay on it ────
    if (result.action_type === 'door_locked') {
        setDoorImage('closed');
        refreshExits();
        return;
    }

    // ── Panel damaged — show damaged panel image, stay on it ─
    if (result.action_type === 'panel_damaged') {
        setDamagedPanelImage(result.security_level);
        refreshExits();
        return;
    }

    // ── Repair panel — show damaged image, lock input, wait, complete ──
    if (result.action_type === 'repair_panel') {
        setDamagedPanelImage(result.security_level);
        showRepairAnimation();
        Loop.lockInput(result.real_seconds, async () => {
            hideRepairAnimation();
            const repairResult = await API.completeRepair(
                result.panel_id,
                result.door_id,
                result.exit_label
            );
            clearResponse();
            handleResult(repairResult);
        });
        return;
    }

    // ── Card swipe — show panel image, scanning animation, lock input ──
    if (result.action_type === 'card_swipe') {
        setPanelImage(result.security_level);
        showScanAnimation();
        Loop.lockInput(result.real_seconds, async () => {
            hideScanAnimation();
            const swipeResult = await API.completeSwipe(
                result.door_id,
                result.pending_move,
                result.door_action
            );
            clearResponse();
            handleResult(swipeResult);
        });
        return;
    }

    // ── PIN required — switch input to PIN mode ───────────
    if (result.action_type === 'pin_required') {
        pendingPin = {
            door_id:     result.door_id,
            door_action: result.door_action,
        };
        setInputMode('pin');
        return;
    }

    // ── Always clear PIN mode before processing result ────
    pendingPin = null;
    setInputMode('normal');

    // Repair complete — show repaired panel image, then restore room
if (result.action_type === 'repair_complete') {
    setPanelImage(result.security_level);   // ← add this line
    refreshExits();
    setTimeout(() => loadRoom(), CONSTANTS.DOOR_IMAGE_DISPLAY_MS);
    return;
}

    // Swipe completed — show open or closed hatch then restore room
    if (result.swipe_complete) {
        const imgState = result.swipe_action === 'lock' ? 'closed' : 'open';
        setDoorImage(imgState);
        refreshExits();
        setTimeout(() => loadRoom(), CONSTANTS.DOOR_IMAGE_DISPLAY_MS);
        return;
    }

    // Normal room change — just update room directly
    if (result.room_changed && result.room) {
        updateRoom(result.room);
        return;
    }

    // Instant door image — open or close without card swipe
    if (result.door_image) {
        setDoorImage(result.door_image);
        refreshExits();
        setTimeout(() => loadRoom(), CONSTANTS.DOOR_IMAGE_DISPLAY_MS);
        return;
    }

    // Card invalidated — restore room image immediately
    if (result.card_invalidated) {
        loadRoom();
        return;
    }

    // Refresh exit states after any other instant action
    if (result.action_type === 'instant') {
        refreshExits();
    }
}

async function submitPin(pin) {
    const result = await API.submitPin(
        pendingPin.door_id,
        null,
        pin,
        pendingPin.door_action
    );
    handleResult(result);
}

// ── Input mode ───────────────────────────────────────────────

function setInputMode(mode) {
    const input = document.getElementById('command-input');
    if (mode === 'pin') {
        input.placeholder = 'enter PIN...';
        input.type        = 'password';
    } else {
        input.placeholder = 'enter command...';
        input.type        = 'text';
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

// ── Scan animation ───────────────────────────────────────────

function showScanAnimation() {
    const content = document.getElementById('response-content');
    const el      = document.createElement('div');
    el.id         = 'scan-animation';
    el.className  = 'scan-animation';
    el.innerHTML  = `
        <span>SCANNING ACCESS CARD</span>
        <div class="scan-dots">
            <span></span><span></span><span></span><span></span><span></span>
        </div>
    `;
    content.appendChild(el);
}

function hideScanAnimation() {
    const el = document.getElementById('scan-animation');
    if (el) el.remove();
}

// ── Repair animation ─────────────────────────────────────────

function showRepairAnimation() {
    const content = document.getElementById('response-content');
    const el      = document.createElement('div');
    el.id         = 'repair-animation';
    el.className  = 'scan-animation';   // reuse existing scan-animation CSS
    el.innerHTML  = `
        <span>REPAIRING ACCESS PANEL</span>
        <div class="scan-dots">
            <span></span><span></span><span></span><span></span><span></span>
        </div>
    `;
    content.appendChild(el);
}

function hideRepairAnimation() {
    const el = document.getElementById('repair-animation');
    if (el) el.remove();
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

// ── Door / panel images ──────────────────────────────────────

const PANEL_IMAGES = {
    1: '/static/images/doors/panel_level1_swipe.png',
    2: '/static/images/doors/panel_level2_swipe.png',
    3: '/static/images/doors/panel_level3_swipe_pin.png',
};

const DAMAGED_PANEL_IMAGES = {
    1: '/static/images/doors/panel_level1_swipe_damaged.png',
    2: '/static/images/doors/panel_level2_swipe_damaged.png',
    3: '/static/images/doors/panel_level3_swipe_damaged.png',
};

function setPanelImage(securityLevel) {
    const path = PANEL_IMAGES[securityLevel] || PANEL_IMAGES[1];
    setRoomImage(path);
}

function setDamagedPanelImage(securityLevel) {
    const path = DAMAGED_PANEL_IMAGES[securityLevel] || DAMAGED_PANEL_IMAGES[1];
    setRoomImage(path);
}

function setDoorImage(state) {
    const path = state === 'open'
        ? '/static/images/doors/open_hatch.png'
        : '/static/images/doors/closed_hatch.png';
    setRoomImage(path);
}
