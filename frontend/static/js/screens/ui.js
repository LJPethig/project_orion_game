// frontend/static/js/screens/ui.js
// UI utilities — animations, images, response panel, input mode.

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
