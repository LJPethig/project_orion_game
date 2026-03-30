// frontend/static/js/screens/terminal.js
// Terminal panel — renders terminal menu, handles navigation, exit.

let currentTerminal      = null;   // current terminal data from backend
let terminalMenuIndex    = 0;      // currently highlighted menu item

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

    _setupTerminalKeys();
}

function hideTerminalPanel() {
    // Close the panel visually but keep the session — tab stays visible
    document.getElementById('panel-terminal').classList.remove('open');
    document.getElementById('tab-term').classList.remove('active');
}

function closeTerminalPanel() {
    // Full exit — destroy session and hide tab
    currentTerminal = null;
    document.getElementById('panel-terminal').classList.remove('open');
    const tab = document.getElementById('tab-term');
    tab.classList.remove('active');
    tab.classList.add('hidden');
    document.removeEventListener('keydown', _terminalKeyHandler);
}

function _renderTerminal() {
    const inner = document.getElementById('terminal-panel-inner');
    inner.innerHTML = '';

    // Title
    const title = document.createElement('div');
    title.className   = 'term-title';
    title.textContent = currentTerminal.terminal_name;
    inner.appendChild(title);

    // Menu
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

function _selectMenuItem(idx) {
    terminalMenuIndex = idx;
    _renderTerminal();

    const item = currentTerminal.menu[idx];
    if (item.action === 'exit') {
        closeTerminalPanel();
        return;
    }

    // Future: dispatch other actions
}

function _setupTerminalKeys() {
    document.removeEventListener('keydown', _terminalKeyHandler);
    document.addEventListener('keydown', _terminalKeyHandler);
}

function _terminalKeyHandler(e) {
    if (!isTerminalOpen()) return;

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
