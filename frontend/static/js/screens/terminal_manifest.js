// frontend/static/js/screens/terminal_manifest.js
// Storage room and cargo bay manifest rendering.
// Depends on: terminal_core.js (currentTerminal, closeTerminalPanel)
//             api.js (API.getStorageManifest, API.getCargoManifest, API.retrieveItem)
//             game.js (clearResponse, handleResult, refreshInventoryIfOpen, appendResponse)

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
    ['Container', 'Type', 'Item', 'Qty'].forEach(label => {
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

        const item = document.createElement('span');
        const qty  = document.createElement('span');
        if (c.contents.length > 0) {
            item.textContent = c.contents[0].name;
            qty.textContent  = c.contents[0].quantity;
        } else {
            item.textContent = 'Empty';
            qty.textContent  = '—';
        }

        row.appendChild(ref);
        row.appendChild(type);
        row.appendChild(item);
        row.appendChild(qty);
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

        const item = document.createElement('span');
        const qty  = document.createElement('span');
        if (p.attached_items.length > 0) {
            item.textContent = p.attached_items[0].name;
            qty.textContent  = p.attached_items[0].quantity;
        } else {
            item.textContent = 'Empty';
            qty.textContent  = '—';
        }

        row.appendChild(ref);
        row.appendChild(type);
        row.appendChild(item);
        row.appendChild(qty);
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
