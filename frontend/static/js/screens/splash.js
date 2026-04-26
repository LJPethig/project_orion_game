// frontend/static/js/screens/splash.js
// Splash screen — New Game and Continue buttons.
// On load, queries the backend for save status and shows the correct buttons.

document.addEventListener('DOMContentLoaded', async () => {
    await initSplash();
});


// ── Initialise ───────────────────────────────────────────────

async function initSplash() {
    let saveExists = false;

    try {
        const status = await fetch('/api/game/save_status').then(r => r.json());
        saveExists = status.exists === true;

        // TODO — dead save handling (implement when death screen UI is built):
        // If status.dead === true, the player's last save cannot be continued.
        // The splash screen must:
        //   1. Show a death screen overlay (black bg, red-tinted title, message
        //      explaining Jack is dead and the save is permanent).
        //   2. Show only a 'New Game' button — no Continue button.
        //   3. When New Game is clicked from a dead save, call DELETE /api/game/save
        //      (endpoint to be created) to wipe both save files before starting,
        //      so save_status returns exists=false on the next launch.
        // For now, treat a dead save the same as no save — Continue stays hidden.
        if (status.dead) {
            saveExists = false;
        }

    } catch (err) {
        console.error('Save status check failed:', err);
        // If the check fails, assume no save — safer than showing a broken Continue.
        saveExists = false;
    }

    showButtons(saveExists);
    bindButtons(saveExists);
}


// ── UI helpers ───────────────────────────────────────────────

function showButtons(saveExists) {
    document.getElementById('splash-loading').classList.add('hidden');
    document.getElementById('splash-buttons').classList.remove('hidden');

    if (saveExists) {
        document.getElementById('btn-continue').classList.remove('hidden');
    }
}

function fadeOutThen(callback) {
    const screen = document.getElementById('splash-screen');
    screen.classList.add('fade-out');
    screen.addEventListener('animationend', callback, { once: true });
}


// ── Button wiring ────────────────────────────────────────────

function bindButtons(saveExists) {
    document.getElementById('btn-continue').addEventListener('click', () => {
        handleContinue();
    });

    document.getElementById('btn-new-game').addEventListener('click', () => {
        if (saveExists) {
            showConfirm();
        } else {
            handleNewGame();
        }
    });

    document.getElementById('btn-confirm-yes').addEventListener('click', () => {
        handleNewGame();
    });

    document.getElementById('btn-confirm-no').addEventListener('click', () => {
        hideConfirm();
    });
}


// ── Confirm overwrite panel ──────────────────────────────────

function showConfirm() {
    document.getElementById('splash-buttons').classList.add('hidden');
    document.getElementById('splash-confirm').classList.remove('hidden');
}

function hideConfirm() {
    document.getElementById('splash-confirm').classList.add('hidden');
    document.getElementById('splash-buttons').classList.remove('hidden');
}


// ── Game actions ─────────────────────────────────────────────

async function handleContinue() {
    disableAllButtons();

    try {
        const data = await fetch('/api/game/load', { method: 'POST' }).then(r => r.json());

        if (data.dead) {
            // Should not reach here — initSplash() hides Continue on dead saves.
            // Guard in case of a race condition between two browser tabs.
            console.warn('Load returned dead=true — save cannot be continued.');
            location.reload();
            return;
        }

        if (!data.success) {
            console.error('Load failed:', data);
            enableAllButtons();
            return;
        }

        // Restore event strip for any fired-but-unresolved events.
        // The game screen calls Loop.checkEvents() on init, which polls the
        // backend and restores the strip immediately — no extra work needed here.

        fadeOutThen(() => { window.location.href = '/game'; });

    } catch (err) {
        console.error('Error loading game:', err);
        enableAllButtons();
    }
}

async function handleNewGame() {
    disableAllButtons();

    try {
        const data = await fetch('/api/game/new', { method: 'POST' }).then(r => r.json());

        if (!data.success) {
            console.error('New game failed:', data);
            enableAllButtons();
            return;
        }

        fadeOutThen(() => { window.location.href = '/game'; });

    } catch (err) {
        console.error('Error starting new game:', err);
        enableAllButtons();
    }
}


// ── Button state helpers ─────────────────────────────────────

function disableAllButtons() {
    document.querySelectorAll('.splash-btn').forEach(b => b.disabled = true);
}

function enableAllButtons() {
    document.querySelectorAll('.splash-btn').forEach(b => b.disabled = false);
}
