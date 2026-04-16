// frontend/static/js/screens/ui.js
// UI utilities — animations, images, response panel, input mode.

let _progressInterval = null;

function _startProgressCounter(realSeconds, spanId) {
    const span = document.getElementById(spanId);
    if (!span) return;
    let elapsed = 0;
    const totalMs = realSeconds * 1000;
    const stepMs  = 200;
    _progressInterval = setInterval(() => {
        elapsed += stepMs;
        const pct = Math.min(100, Math.round((elapsed / totalMs) * 100));
        span.textContent = `${pct}%`;
        if (pct >= 100) _stopProgressCounter();
    }, stepMs);
}

function _stopProgressCounter() {
    if (_progressInterval) {
        clearInterval(_progressInterval);
        _progressInterval = null;
    }
}

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

function showScanAnimation(realSeconds) {
    const content = document.getElementById('response-content');
    const el      = document.createElement('div');
    el.id         = 'scan-animation';
    el.className  = 'scan-animation';
    el.innerHTML  = `
        <span>SCANNING ACCESS CARD</span>
        <div class="scan-dots">
            <span></span><span></span><span></span><span></span><span></span>
        </div>
        <span id="scan-progress" class="scan-progress">0%</span>
    `;
    content.appendChild(el);
    _startProgressCounter(realSeconds, 'scan-progress');
}

function hideScanAnimation() {
    _stopProgressCounter();
    const el = document.getElementById('scan-animation');
    if (el) el.remove();
}

// ── Repair animation ─────────────────────────────────────────

function showRepairAnimation(realSeconds) {
    const content = document.getElementById('response-content');
    const el      = document.createElement('div');
    el.id         = 'repair-animation';
    el.className  = 'scan-animation';   // reuse existing scan-animation CSS
    el.innerHTML  = `
        <span>REPAIRING ACCESS PANEL</span>
        <div class="scan-dots">
            <span></span><span></span><span></span><span></span><span></span>
        </div>
        <span id="scan-progress" class="scan-progress">0%</span>
    `;
    content.appendChild(el);
    _startProgressCounter(realSeconds, 'scan-progress');
}

function hideRepairAnimation() {
    _stopProgressCounter();
    const el = document.getElementById('repair-animation');
    if (el) el.remove();
}

function showDiagnosisAnimation(realSeconds) {
    const content = document.getElementById('response-content');
    const el      = document.createElement('div');
    el.id         = 'repair-animation';
    el.className  = 'scan-animation';
    el.innerHTML  = `
        <span>DIAGNOSING ACCESS PANEL</span>
        <div class="scan-dots">
            <span></span><span></span><span></span><span></span><span></span>
        </div>
        <span id="scan-progress" class="scan-progress">0%</span>
    `;
    content.appendChild(el);
    _startProgressCounter(realSeconds, 'scan-progress');
}

// ── Repair message ────────────────────────────────────────────

function appendRepairMessage(result) {
    const content = document.getElementById('response-content');

    // Intro line
    if (result.response) {
        const intro = document.createElement('div');
        intro.className   = 'response-line';
        intro.textContent = result.response;
        content.appendChild(intro);
    }

    // Failed components
    if (result.faults && result.faults.length > 0) {
        const faultsLabel = document.createElement('div');
        faultsLabel.className   = 'response-line';
        faultsLabel.textContent = result.faults_label || 'You have discovered the following failed components:';
        content.appendChild(faultsLabel);

        const faultsEl = document.createElement('div');
        faultsEl.className = 'response-line';
        faultsEl.innerHTML = `&nbsp;&nbsp;<span style="color:var(--col-portable)">${result.faults.join(', ')}</span>`;
        content.appendChild(faultsEl);
    }

    // Tools required
    if (result.tools && result.tools.length > 0) {
        const toolsLabel = document.createElement('div');
        toolsLabel.className   = 'response-line';
        toolsLabel.textContent = result.tools_label || 'The repair will require the following tools:';
        content.appendChild(toolsLabel);

        const toolsEl = document.createElement('div');
        toolsEl.className = 'response-line';
        toolsEl.innerHTML = `&nbsp;&nbsp;<span style="color:var(--col-portable)">${result.tools.join(', ')}</span>`;
        content.appendChild(toolsEl);
    }

    // Missing items — only shown if player is missing something
    if (result.missing_items && result.missing_items.length > 0) {
        const missingLabel = document.createElement('div');
        missingLabel.className   = 'response-line';
        missingLabel.textContent = 'You need to source these missing items before repairing:';
        content.appendChild(missingLabel);

        const missingEl = document.createElement('div');
        missingEl.className = 'response-line';
        missingEl.innerHTML = `&nbsp;&nbsp;<span style="color:var(--col-alert)">${result.missing_items.join(', ')}</span>`;
        content.appendChild(missingEl);
    }

    content.scrollTop = content.scrollHeight;
}

// ── Event strip ──────────────────────────────────────────────

function appendEventStrip(message, eventId) {
    const el       = document.getElementById('event-left');
    if (!el) return;
    const span     = document.createElement('span');
    span.className = 'event-message';
    if (eventId) span.dataset.eventId = eventId;
    span.textContent = message;
    el.appendChild(span);
}

function clearEventStrip(eventId) {
    const el = document.getElementById('event-left');
    if (!el) return;
    if (eventId) {
        el.querySelectorAll(`[data-event-id="${eventId}"]`).forEach(s => s.remove());
    } else {
        el.innerHTML = '';
    }
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
    closeInventoryIfOpen()
    closeDatapadIfOpen();
    const path = PANEL_IMAGES[securityLevel] || PANEL_IMAGES[1];
    setRoomImage(path);
}

function setDamagedPanelImage(securityLevel) {
    closeInventoryIfOpen()
    closeDatapadIfOpen();
    const path = DAMAGED_PANEL_IMAGES[securityLevel] || DAMAGED_PANEL_IMAGES[1];
    setRoomImage(path);
}

function setDoorImage(state) {
    closeInventoryIfOpen()
    closeDatapadIfOpen();
    const path = state === 'open'
        ? '/static/images/doors/open_hatch.png'
        : '/static/images/doors/closed_hatch.png';
    setRoomImage(path);
}
