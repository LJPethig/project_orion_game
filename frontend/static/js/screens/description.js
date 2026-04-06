// frontend/static/js/screens/description.js
// Description panel — rendering, markup parser, tooltips, click handlers.

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
        el.appendChild(parseMarkup(line, room.object_states || {}));
        content.appendChild(el);
    });

    // ── Layer 2 — open container contents ────────────────
    const objectStates = room.object_states || {};
    Object.entries(objectStates).forEach(([id, state]) => {
        if (state.type === 'container' && state.is_open) {
            const row = document.createElement('div');
            row.className = 'layer2-container';
            row.dataset.containerId = id;

            const nameSpan = document.createElement('span');
            nameSpan.className = 'layer2-container-name';
            nameSpan.textContent = _getObjectName(id, objectStates) + ' (open)';
            nameSpan.addEventListener('click', () => {
                clearResponse();
                API.sendCommand(`close ${id}`).then(result => handleResult(result));
            });
            row.appendChild(nameSpan);

            if (state.contents && state.contents.length > 0) {
                const sep = document.createTextNode('  ');
                row.appendChild(sep);
                state.contents.forEach((item, idx) => {
                    const itemSpan = document.createElement('span');
                    itemSpan.className = 'layer2-item';
                    itemSpan.textContent = item.name;
                    itemSpan.dataset.itemId = item.id;
                    itemSpan.addEventListener('click', () => {
                        clearResponse();
                        API.sendCommand(`take ${item.instance_id || item.id} from ${id}`).then(result => handleResult(result));
                    });
                    row.appendChild(itemSpan);
                    if (idx < state.contents.length - 1) {
                        row.appendChild(document.createTextNode(', '));
                    }
                });
            } else {
                row.appendChild(document.createTextNode('  Empty'));
            }

            content.appendChild(row);
        }
    });

    // ── Layer 3 — expanded surface contents ──────────────
    if (expandedSurface) {
        const state = objectStates[expandedSurface];
        if (state && state.type === 'surface' && state.has_items) {
            const row = document.createElement('div');
            row.className = 'layer3-surface';
            row.dataset.surfaceId = expandedSurface;

            const nameSpan = document.createElement('span');
            nameSpan.className = 'layer3-surface-name';
            nameSpan.textContent = _getObjectName(expandedSurface, objectStates);
            nameSpan.addEventListener('click', () => {
                expandedSurface = null;
                loadRoom();
            });
            row.appendChild(nameSpan);

            if (state.contents && state.contents.length > 0) {
                const sep = document.createTextNode('  ');
                row.appendChild(sep);
                state.contents.forEach((item, idx) => {
                    const itemSpan = document.createElement('span');
                    itemSpan.className = 'layer3-item';
                    itemSpan.textContent = item.name;
                    itemSpan.dataset.itemId = item.id;
                    itemSpan.addEventListener('click', () => {
                        clearResponse();
                        API.sendCommand(`take ${item.instance_id || item.id}`).then(result => handleResult(result));
                    });
                    row.appendChild(itemSpan);
                    if (idx < state.contents.length - 1) {
                        row.appendChild(document.createTextNode(', '));
                    }
                });
            }

            content.appendChild(row);
        } else {
            // Surface no longer has items or doesn't exist — collapse
            expandedSurface = null;
        }
    }

    // ── Floor — items with no surface ───────────────────
    const floorItems = room.floor_items || [];
    if (floorItems.length > 0) {
        const row = document.createElement('div');
        row.className = 'floor-items';

        const label = document.createElement('span');
        label.className = 'floor-label';
        label.textContent = 'Floor: ';
        row.appendChild(label);

        floorItems.forEach((item, idx) => {
            const itemSpan = document.createElement('span');
            itemSpan.className = 'floor-item';
            itemSpan.textContent = item.name;
            itemSpan.dataset.itemId = item.id;
            itemSpan.addEventListener('click', () => {
                clearResponse();
                API.sendCommand(`take ${item.instance_id || item.id}`).then(result => handleResult(result));
            });
            row.appendChild(itemSpan);
            if (idx < floorItems.length - 1) {
                row.appendChild(document.createTextNode(', '));
            }
        });

        content.appendChild(row);
    }

    setupObjectTooltips(content);
    setupClickHandlers(content);
}

function _getObjectName(id, objectStates) {
    const state = objectStates[id];
    if (state && state.name) return state.name;
    // Fallback — humanise ID suffix
    const parts = id.split('_');
    return parts.slice(1).map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ');
}

// ── Markup parser ────────────────────────────────────────────

function parseMarkup(text, objectStates = {}) {
    const fragment  = document.createDocumentFragment();
    // Matches *exit*, %container%, !terminal!, #surface#
    const regex     = /(\*[^*]+\*|%[^%]+%|![^!]+!|#[^#]+#)/g;
    let lastIndex   = 0;
    let match;

    while ((match = regex.exec(text)) !== null) {
        if (match.index > lastIndex) {
            fragment.appendChild(document.createTextNode(text.slice(lastIndex, match.index)));
        }

        const raw   = match[0];
        const inner = raw.slice(1, -1);
        const span  = document.createElement('span');
        span.textContent = inner;

        if (raw.startsWith('*')) {
            // Exit — hover only
            span.className       = 'markup-exit';
            span.dataset.exit    = inner.toLowerCase().replace(/\s+/g, '_');

        } else if (raw.startsWith('%')) {
            // Container — cyan always
            span.className          = 'markup-container';
            span.dataset.container  = inner.toLowerCase().replace(/\s+/g, '_');

        } else if (raw.startsWith('!')) {
            // Terminal — cyan always
            span.className         = 'markup-terminal';
            span.dataset.terminal  = inner.toLowerCase().replace(/\s+/g, '_');

        } else if (raw.startsWith('#')) {
            // Surface — grey bold when empty, purple bold when has items
            const key      = inner.toLowerCase().replace(/\s+/g, '_');
            const objState = _findObjectState(objectStates, key);
            const hasItems = objState && objState.has_items;
            span.className       = hasItems ? 'markup-surface markup-surface-items' : 'markup-surface';
            span.dataset.surface = key;
        }

        fragment.appendChild(span);
        lastIndex = regex.lastIndex;
    }

    if (lastIndex < text.length) {
        fragment.appendChild(document.createTextNode(text.slice(lastIndex)));
    }
    return fragment;
}

function _findObjectState(objectStates, spanKey) {
    // Match span keyword against object_states keys (id-based)
    for (const [id, state] of Object.entries(objectStates)) {
        // Direct key match or id ends with the span key
        if (id.toLowerCase().replace(/\s+/g, '_') === spanKey) return state;
        if (id.toLowerCase().endsWith('_' + spanKey)) return state;
    }
    return null;
}

// ── Object hover tooltips (exits, containers, terminals, surfaces) ──────────

function setupObjectTooltips(container) {
    const tooltip = document.getElementById('exit-tooltip');
    if (!tooltip) return;

    // ── Exits — door state ────────────────────────────────
    container.querySelectorAll('.markup-exit').forEach(span => {
        span.addEventListener('mouseenter', (e) => {
            const exitKey  = e.target.dataset.exit;
            const exitData = findExitData(exitKey);
            if (!exitData) return;
            const state   = exitData.door_state || 'none';
            const label   = exitData.label || exitKey;
            const powered = exitData.panel_powered !== false;
            const stateText = powered ? doorStateText(state) : doorStateText(state) + ' — Offline';
            const stateCol  = powered ? doorStateColour(state) : 'var(--col-alert)';
            tooltip.innerHTML = `
                <div style="color:var(--col-title)">${label}</div>
                <div style="color:${stateCol};font-size:11px">${stateText}</div>
            `;
            tooltip.classList.remove('hidden');
        });
        _bindTooltipMove(span, tooltip);
        span.addEventListener('mouseleave', () => tooltip.classList.add('hidden'));
    });

    // ── Containers — open/closed state ───────────────────
    container.querySelectorAll('.markup-container').forEach(span => {
        span.addEventListener('mouseenter', (e) => {
            const key      = e.target.dataset.container;
            const objState = _findObjectState(currentObjects, key);
            const stateStr = objState ? (objState.is_open ? 'Open' : 'Closed') : 'Closed';
            const colour   = objState && objState.is_open ? 'var(--col-prompt)' : 'var(--col-text)';
            tooltip.innerHTML = `<div style="color:${colour};font-size:11px">${stateStr}</div>`;
            tooltip.classList.remove('hidden');
        });
        _bindTooltipMove(span, tooltip);
        span.addEventListener('mouseleave', () => tooltip.classList.add('hidden'));
    });

    // ── Terminals ─────────────────────────────────────────
    container.querySelectorAll('.markup-terminal').forEach(span => {
        span.addEventListener('mouseenter', (e) => {
            const key      = e.target.dataset.terminal;
            const objState = _findObjectState(currentObjects, key);
            const powered  = objState ? objState.powered !== false : true;
            const text     = powered ? 'Online' : 'Offline';
            const colour   = powered ? 'var(--col-prompt)' : 'var(--col-alert)';
            tooltip.innerHTML = `<div style="color:${colour};font-size:11px">${text}</div>`;
            tooltip.classList.remove('hidden');
        });
        _bindTooltipMove(span, tooltip);
        span.addEventListener('mouseleave', () => tooltip.classList.add('hidden'));
    });

    // ── Surfaces — empty or item count ───────────────────
    container.querySelectorAll('.markup-surface').forEach(span => {
        span.addEventListener('mouseenter', (e) => {
            const key      = e.target.dataset.surface;
            const objState = _findObjectState(currentObjects, key);
            const hasItems = objState && objState.has_items;
            const text     = hasItems ? 'Has items' : 'Empty';
            const colour   = hasItems ? 'var(--col-portable)' : 'var(--col-text)';
            tooltip.innerHTML = `<div style="color:${colour};font-size:11px">${text}</div>`;
            tooltip.classList.remove('hidden');
        });
        _bindTooltipMove(span, tooltip);
        span.addEventListener('mouseleave', () => tooltip.classList.add('hidden'));
    });
}

function _bindTooltipMove(span, tooltip) {
    span.addEventListener('mousemove', (e) => {
        const tw     = tooltip.offsetWidth;
        const th     = tooltip.offsetHeight;
        const margin = 14;
        let left = e.clientX + margin;
        let top  = e.clientY + margin;
        if (left + tw > window.innerWidth)  left = e.clientX - tw - margin;
        if (top  + th > window.innerHeight) top  = e.clientY - th - margin;
        tooltip.style.left = left + 'px';
        tooltip.style.top  = top  + 'px';
    });
}


// ── Click handlers (containers, terminals, surfaces) ─────────

function setupClickHandlers(container) {

    // ── Containers — toggle open/close ───────────────────
    container.querySelectorAll('.markup-container').forEach(span => {
        span.addEventListener('click', (e) => {
            if (isTerminalSessionActive()) return;
            const key      = e.target.dataset.container;
            const objState = _findObjectState(currentObjects, key);
            const verb     = objState && objState.is_open ? 'close' : 'open';
            // Find the full object id via endsWith match
            const id = Object.keys(currentObjects).find(oid =>
                oid.toLowerCase() === key || oid.toLowerCase().endsWith('_' + key)
            );
            if (id) {
                clearResponse();
                appendResponse(`> ${verb} ${e.target.textContent}`, 'player-cmd');
                API.sendCommand(`${verb} ${id}`).then(result => handleResult(result));
            }
        });
    });

    // ── Terminals — open terminal panel ──────────────────
    container.querySelectorAll('.markup-terminal').forEach(span => {
        span.addEventListener('click', (e) => {
            if (isTerminalSessionActive()) return;
            const id = Object.keys(currentObjects).find(oid => {
                const key = e.target.dataset.terminal;
                return oid.toLowerCase() === key || oid.toLowerCase().endsWith('_' + key);
            });
            if (id) {
                clearResponse();
                appendResponse(`> access terminal`, 'player-cmd');
                API.sendCommand(`access ${id}`).then(result => handleResult(result));
            }
        });
    });

    // ── Surfaces — expand/collapse Layer 3 ───────────────
    container.querySelectorAll('.markup-surface').forEach(span => {
        span.addEventListener('click', (e) => {
            if (isTerminalSessionActive()) return;
            const key      = e.target.dataset.surface;
            const objState = _findObjectState(currentObjects, key);
            if (!objState || !objState.has_items) return;

            const id = Object.keys(currentObjects).find(oid =>
                oid.toLowerCase() === key || oid.toLowerCase().endsWith('_' + key)
            );
            if (!id) return;

            if (expandedSurface === id) {
                expandedSurface = null;
            } else {
                expandedSurface = id;
            }
            loadRoom();
        });
    });
}

