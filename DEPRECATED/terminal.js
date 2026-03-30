// frontend/static/js/screens/terminal.js
// Terminal panel — renders terminal menu, handles navigation, exit.

let currentTerminal      = null;   // current terminal data from backend
let terminalMenuIndex    = 0;      // currently highlighted menu item
let terminalSubMenu = null;   // null = main menu, object = sub-menu content

function isTerminalOpen() {
    const panel = document.getElementById('panel-terminal');
    return panel && panel.classList.contains('open');
}

function openTerminalPanel(terminalData) {
    currentTerminal   = terminalData;
    terminalMenuIndex = 0;
    _renderTerminal();

    // Show TERM tab
    const tab = document.getElementById('tab-term');
    tab.classList.remove('hidden');

    // Open panel, close any others
    document.querySelectorAll('.slide-panel').forEach(p => p.classList.remove('open'));
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.getElementById('panel-terminal').classList.add('open');
    tab.classList.add('active');
    document.getElementById('tab-strip').classList.add('term-active');

    _setupTerminalKeys();
}

function hideTerminalPanel() {
    // Close the panel visually but keep the session — tab stays visible
    document.getElementById('panel-terminal').classList.remove('open');
    document.getElementById('tab-term').classList.remove('active');
    document.getElementById('tab-strip').classList.remove('term-active');
}

function closeTerminalPanel() {
    currentTerminal = null;
    terminalSubMenu = null;
    document.getElementById('panel-terminal').classList.remove('open');
    const tab = document.getElementById('tab-term');
    tab.classList.remove('active');
    tab.classList.add('hidden');
    document.getElementById('tab-strip').classList.remove('term-active');
    document.removeEventListener('keydown', _terminalKeyHandler);
}

function _renderTerminal() {
    const inner = document.getElementById('terminal-panel-inner');
    inner.innerHTML = '';

    const title = document.createElement('div');
    title.className   = 'term-title';
    title.textContent = terminalSubMenu ? terminalSubMenu.title : currentTerminal.terminal_name;
    inner.appendChild(title);

    if (terminalSubMenu) {
        // ── Sub-menu — text content + Return ─────────────
        const content = document.createElement('div');
        content.className = 'term-content';
        terminalSubMenu.text.forEach(line => {
            const row = document.createElement('div');
            row.className   = line === '' ? 'term-content-blank' : 'term-content-line';
            row.textContent = line;
            content.appendChild(row);
        });
        inner.appendChild(content);

        const menu = document.createElement('div');
        menu.className = 'term-menu';
        menu.id        = 'term-menu';
        const returnRow = document.createElement('div');
        returnRow.className   = 'term-menu-item term-selected';
        returnRow.textContent = 'Return';
        returnRow.addEventListener('click', () => _returnToMainMenu());
        menu.appendChild(returnRow);
        inner.appendChild(menu);
    } else {
        // ── Main menu ─────────────────────────────────────
        const menu = document.createElement('div');
        menu.className = 'term-menu';
        menu.id        = 'term-menu';
        currentTerminal.menu.forEach((item, idx) => {
            const row = document.createElement('div');
            row.className   = 'term-menu-item' + (idx === terminalMenuIndex ? ' term-selected' : '');
            row.dataset.idx = idx;
            row.textContent = item.label;
            row.addEventListener('click', () => _selectMenuItem(idx));
            menu.appendChild(row);
        });
        inner.appendChild(menu);
    }
}

function _selectMenuItem(idx) {
    terminalMenuIndex = idx;
    _renderTerminal();

    const item = currentTerminal.menu[idx];
    if (item.action === 'exit') {
        closeTerminalPanel();
        return;
    }

    // Fetch sub-menu content from backend
    API.getTerminalContent(currentTerminal.terminal_type, item.action).then(data => {
        if (data.error) return;
        terminalSubMenu = data;
        _renderTerminal();
    });
}

function _setupTerminalKeys() {
    document.removeEventListener('keydown', _terminalKeyHandler);
    document.addEventListener('keydown', _terminalKeyHandler);
}

function _terminalKeyHandler(e) {
    if (!isTerminalOpen()) return;

    if (terminalSubMenu) {
        if (e.key === 'Enter') {
            e.preventDefault();
            _returnToMainMenu();
        }
        return;
    }

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        terminalMenuIndex = Math.min(terminalMenuIndex + 1, currentTerminal.menu.length - 1);
        _renderTerminal();
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        terminalMenuIndex = Math.max(terminalMenuIndex - 1, 0);
        _renderTerminal();
    } else if (e.key === 'Enter') {
        e.preventDefault();
        _selectMenuItem(terminalMenuIndex);
    }
}

function _returnToMainMenu() {
    terminalSubMenu   = null;
    terminalMenuIndex = 0;
    _renderTerminal();
}
