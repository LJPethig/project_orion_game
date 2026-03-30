// frontend/static/js/screens/terminal.js
// Terminal panel — renders terminal menu, handles navigation, exit.

// ── Constants ─────────────────────────────────────────────────
const TERM_CHAR_SPEED_MS   = 20;    // Base ms per character
const TERM_JITTER_MIN      = 0.6;   // Minimum jitter multiplier
const TERM_JITTER_MAX      = 2.2;   // Maximum jitter multiplier
const TERM_LINE_PAUSE_MS   = 80;    // Extra pause between lines
const TERM_BLANK_PAUSE_MS  = 120;   // Pause for blank lines

// ── State ─────────────────────────────────────────────────────
let currentTerminal      = null;   // current terminal data from backend
let terminalMenuIndex    = 0;      // currently highlighted menu item
let terminalSubMenu      = null;   // null = main menu, object = sub-menu content
let _typewriterActive    = false;  // true while typing is in progress
let _typewriterCancelled = false;  // set to true to abort current typewriter

// ── Panel open/close ──────────────────────────────────────────

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
    // Typewriter continues in background
    document.getElementById('panel-terminal').classList.remove('open');
    document.getElementById('tab-term').classList.remove('active');
    document.getElementById('tab-strip').classList.remove('term-active');
}

function closeTerminalPanel() {
    _cancelTypewriter();
    currentTerminal = null;
    terminalSubMenu = null;
    document.getElementById('panel-terminal').classList.remove('open');
    const tab = document.getElementById('tab-term');
    tab.classList.remove('active');
    tab.classList.add('hidden');
    document.getElementById('tab-strip').classList.remove('term-active');
    document.removeEventListener('keydown', _terminalKeyHandler);
}

// ── Rendering ─────────────────────────────────────────────────

function _renderTerminal() {
    const inner = document.getElementById('terminal-panel-inner');
    inner.innerHTML = '';

    const title = document.createElement('div');
    title.className   = 'term-title';
    title.textContent = terminalSubMenu ? terminalSubMenu.title : currentTerminal.terminal_name;
    inner.appendChild(title);

    if (terminalSubMenu) {
        // ── Sub-menu — type out text content, then show Return ─
        const content = document.createElement('div');
        content.className = 'term-content';

        // Create empty line divs first
        const lineDivs = terminalSubMenu.text.map(line => {
            const row = document.createElement('div');
            row.className = line === '' ? 'term-content-blank' : 'term-content-line';
            content.appendChild(row);
            return { el: row, text: line };
        });

        inner.appendChild(content);

        // Return row — hidden until typing completes
        const menu = document.createElement('div');
        menu.className = 'term-menu';
        menu.id        = 'term-menu';
        const returnRow = document.createElement('div');
        returnRow.className   = 'term-menu-item term-selected';
        returnRow.textContent = 'Return';
        returnRow.style.visibility = 'hidden';
        returnRow.addEventListener('click', () => {
            if (!_typewriterActive) _returnToMainMenu();
        });
        menu.appendChild(returnRow);
        inner.appendChild(menu);

        // Start typewriter
        _typewriteLines(lineDivs, () => {
            returnRow.style.visibility = 'visible';
        });

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

// ── Typewriter ────────────────────────────────────────────────

function _cancelTypewriter() {
    _typewriterCancelled = true;
    _typewriterActive    = false;
}

function _jitteredDelay() {
    const multiplier = TERM_JITTER_MIN + Math.random() * (TERM_JITTER_MAX - TERM_JITTER_MIN);
    return TERM_CHAR_SPEED_MS * multiplier;
}

function _typewriteLines(lineDivs, onComplete) {
    _typewriterCancelled = false;
    _typewriterActive    = true;

    let lineIdx = 0;
    // Create cursor element
    const cursor = document.createElement('span');
    cursor.className = 'term-cursor';
    cursor.classList.add('typing');

    function typeNextLine() {
        if (_typewriterCancelled) return;
        if (lineIdx >= lineDivs.length) {
            _typewriterActive = false;
            cursor.classList.remove('typing');
            // Leave cursor blinking on last line
            const lastLine = lineDivs[lineDivs.length - 1].el;
            lastLine.appendChild(cursor);
            if (onComplete) onComplete();
            return;
        }

        const { el, text } = lineDivs[lineIdx];
        lineIdx++;

        if (text === '') {
            // Blank line — show cursor briefly then continue
            el.appendChild(cursor);
            setTimeout(() => {
                cursor.remove();
                typeNextLine();
            }, TERM_BLANK_PAUSE_MS);
            return;
        }

        // Type characters one by one
        let charIdx = 0;

        function typeNextChar() {
            if (_typewriterCancelled) return;
            if (charIdx >= text.length) {
                cursor.remove();
                setTimeout(typeNextLine, TERM_LINE_PAUSE_MS);
                return;
            }
            // Append character as text node, then re-append cursor
            el.insertBefore(document.createTextNode(text[charIdx]), cursor);
            charIdx++;
            setTimeout(typeNextChar, _jitteredDelay());
        }

        // Add cursor to the line before typing starts
        el.appendChild(cursor);
        typeNextChar();
    }

    typeNextLine();
}

// ── Menu interaction ──────────────────────────────────────────

function _selectMenuItem(idx) {
    if (_typewriterActive) return;   // Block during typewriter
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

function _returnToMainMenu() {
    _cancelTypewriter();
    terminalSubMenu   = null;
    terminalMenuIndex = 0;
    _renderTerminal();
}

// ── Keyboard ──────────────────────────────────────────────────

function _setupTerminalKeys() {
    document.removeEventListener('keydown', _terminalKeyHandler);
    document.addEventListener('keydown', _terminalKeyHandler);
}

function _terminalKeyHandler(e) {
    if (!isTerminalOpen()) return;

    if (terminalSubMenu) {
        if (e.key === 'Enter' && !_typewriterActive) {
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
