// frontend/static/js/screens/inventory.js
// Inventory panel — renders equipped slots and carried items.
// Handles keyboard navigation, item selection, and item actions.

let inventoryData     = null;   // latest data from /api/game/inventory
let selectedItemIndex = -1;     // -1 = nothing selected
let selectedItemList  = [];     // flat list of all selectable items in display order

// ── Public entry point ───────────────────────────────────────

async function renderInventory() {
    const data = await API.getInventory();
    if (data.error) { console.error('Inventory load error:', data.error); return; }
    inventoryData = data;
    _buildInventoryPanel(data);
    _setupInventoryKeys();
}

// ── Panel builder ────────────────────────────────────────────

function _buildInventoryPanel(data) {
    const panel = document.querySelector('#panel-inventory .slide-panel-inner');
    panel.innerHTML = '';
    selectedItemIndex = -1;
    selectedItemList  = [];

    // ── Header ───────────────────────────────────────────────
    const header = document.createElement('div');
    header.className = 'inv-header';
    header.innerHTML = `
        <span class="inv-title">${data.player_name}</span>
        <span class="inv-weight">${data.carry_current.toFixed(1)} / ${data.carry_max.toFixed(1)} kg</span>
    `;
    panel.appendChild(header);

    // ── Layout: left list + right detail ─────────────────────
    const layout = document.createElement('div');
    layout.className = 'inv-layout';

    const listCol = document.createElement('div');
    listCol.className = 'inv-list-col';

    const detailCol = document.createElement('div');
    detailCol.id = 'inv-detail-col';
    detailCol.className = 'inv-detail-col';
    _renderDetailEmpty(detailCol);

    // ── Equipped slots ────────────────────────────────────────
    const equippedLabel = document.createElement('div');
    equippedLabel.className = 'inv-section-label';
    equippedLabel.textContent = 'EQUIPPED';
    listCol.appendChild(equippedLabel);

    const slotOrder = ['head', 'body', 'torso', 'waist', 'feet'];
    slotOrder.forEach(slot => {
        const slotData = data.equipped[slot];
        const row      = document.createElement('div');
        row.className  = 'inv-slot-row';
        row.dataset.slot = slot;

        const slotLabel = document.createElement('span');
        slotLabel.className   = 'inv-slot-label';
        slotLabel.textContent = slot.toUpperCase();

        const slotItem = document.createElement('span');
        slotItem.className   = slotData.id ? 'inv-slot-item' : 'inv-slot-empty';
        slotItem.textContent = slotData.name || '—';

        row.appendChild(slotLabel);
        row.appendChild(slotItem);

        if (slotData.id) {
            const idx = selectedItemList.length;
            selectedItemList.push({ type: 'equipped', slot, data: slotData });
            row.dataset.idx = idx;
            row.addEventListener('click', () => _selectItem(idx));
        }

        listCol.appendChild(row);
    });

    // ── Carried items ─────────────────────────────────────────
    const carriedLabel = document.createElement('div');
    carriedLabel.className = 'inv-section-label';
    carriedLabel.textContent = `CARRYING  (${data.carried.length})`;
    listCol.appendChild(carriedLabel);

    if (data.carried.length === 0) {
        const empty = document.createElement('div');
        empty.className   = 'inv-slot-empty';
        empty.textContent = 'Nothing carried.';
        listCol.appendChild(empty);
    } else {
        data.carried.forEach(item => {
            const row  = document.createElement('div');
            row.className = 'inv-item-row';
            const idx  = selectedItemList.length;
            selectedItemList.push({ type: 'carried', data: item });
            row.dataset.idx = idx;

            const nameSpan = document.createElement('span');
            nameSpan.className   = 'inv-item-name';
            nameSpan.textContent = item.name;

            const massSpan = document.createElement('span');
            massSpan.className   = 'inv-item-mass';
            massSpan.textContent = `${item.mass.toFixed(1)} kg`;

            row.appendChild(nameSpan);
            row.appendChild(massSpan);
            row.addEventListener('click', () => _selectItem(idx));
            listCol.appendChild(row);
        });
    }

    layout.appendChild(listCol);
    layout.appendChild(detailCol);
    panel.appendChild(layout);
}

// ── Item selection ───────────────────────────────────────────

function _selectItem(idx) {
    selectedItemIndex = idx;

    document.querySelectorAll('.inv-slot-row, .inv-item-row').forEach(row => {
        row.classList.toggle('inv-selected', parseInt(row.dataset.idx) === idx);
    });

    const entry     = selectedItemList[idx];
    const detailCol = document.getElementById('inv-detail-col');
    _renderDetail(detailCol, entry);
}

function _renderDetailEmpty(col) {
    col.innerHTML = '<div class="inv-detail-hint">Select an item to inspect it.</div>';
}

function _renderDetail(col, entry) {
    const item = entry.data;
    col.innerHTML = '';

    // Image
    const img = document.createElement('img');
    img.className = 'inv-item-image';
    img.src       = `/static/${item.image}`;
    img.onerror   = () => { img.src = '/static/images/image_missing.png'; img.onerror = null; };
    col.appendChild(img);

    // Name
    const name = document.createElement('div');
    name.className   = 'inv-detail-name';
    name.textContent = item.name;
    col.appendChild(name);

    // Mass
    const mass = document.createElement('div');
    mass.className   = 'inv-detail-mass';
    mass.textContent = `${item.mass.toFixed(1)} kg`;
    col.appendChild(mass);

    // Description
    const desc = document.createElement('div');
    desc.className   = 'inv-detail-desc';
    desc.textContent = item.description || '';
    col.appendChild(desc);

    // Actions
    const actions = document.createElement('div');
    actions.className = 'inv-actions';

    if (entry.type === 'carried') {
        if (item.equip_slot) {
            _addAction(actions, 'Wear', () => _invCommand(`wear ${item.id}`));
        }
        _addAction(actions, 'Drop', () => _invCommand(`drop ${item.id}`));
    } else if (entry.type === 'equipped') {
        _addAction(actions, 'Remove', () => _invCommand(`remove ${item.id}`));
    }

    col.appendChild(actions);
}

function _addAction(container, label, handler) {
    const btn = document.createElement('button');
    btn.className   = 'inv-action-btn';
    btn.textContent = label;
    btn.addEventListener('click', handler);
    container.appendChild(btn);
}

async function _invCommand(cmd) {
    clearResponse();
    appendResponse(`> ${cmd}`, 'player-cmd');
    const result = await API.sendCommand(cmd);
    handleResult(result);
    renderInventory();
}

// ── Keyboard navigation ──────────────────────────────────────

function _setupInventoryKeys() {
    document.removeEventListener('keydown', _inventoryKeyHandler);
    document.addEventListener('keydown', _inventoryKeyHandler);
}

function _inventoryKeyHandler(e) {
    const panel = document.getElementById('panel-inventory');
    if (!panel || !panel.classList.contains('open')) return;
    if (selectedItemList.length === 0) return;

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        const next = selectedItemIndex < selectedItemList.length - 1
            ? selectedItemIndex + 1 : selectedItemIndex;
        _selectItem(selectedItemIndex === -1 ? 0 : next);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        const prev = selectedItemIndex > 0 ? selectedItemIndex - 1 : 0;
        _selectItem(prev);
    }
}
