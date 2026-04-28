// frontend/static/js/screens/game_detail.js
// Ship details screen — shown after New Game or Continue.
// Reads game data from sessionStorage (written by start-screen.js).
// Shows ship status, then after 5s fade-in reveals "press any key" prompt.
// Any keypress or click after the prompt is visible navigates to /game.

document.addEventListener('DOMContentLoaded', () => {
    populateDetails();
    schedulePrompt();
});


// ── Populate data fields ─────────────────────────────────────

function populateDetails() {
    let data = {};

    try {
        const raw = sessionStorage.getItem('orion_game_data');
        if (raw) {
            data = JSON.parse(raw);
        }
    } catch (err) {
        console.error('Failed to read game data from sessionStorage:', err);
    }

    setValue('det-ship-name', data.ship_name && data.ship_type
        ? `${data.ship_name}  —  ${data.ship_type}`
        : data.ship_name || '—');
    setValue('det-location',  data.ship_location || '—');
    setValue('det-mission',   data.ship_mission  || '—');
    setValue('det-ship-time', data.ship_time     || '—');
}

function setValue(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text;
}


// ── Prompt timing ────────────────────────────────────────────
// CSS animates opacity 0 → 1 over 1.5s with a 5s delay.
// After the animation completes (6.5s total) we enable input.

function schedulePrompt() {
    const FADE_DELAY_MS    = 5000;   // matches animation-delay in CSS
    const FADE_DURATION_MS = 1500;   // matches animation duration in CSS
    const TOTAL_MS = FADE_DELAY_MS + FADE_DURATION_MS;

    setTimeout(() => {
        enableInput();
    }, TOTAL_MS);
}


// ── Input handling ───────────────────────────────────────────

let inputEnabled = false;

function enableInput() {
    inputEnabled = true;
    document.addEventListener('keydown', handleInput, { once: true });
    document.addEventListener('click',   handleInput, { once: true });
}

function handleInput() {
    if (!inputEnabled) return;
    inputEnabled = false;
    navigateToGame();
}

function navigateToGame() {
    const screen = document.getElementById('game-detail-screen');
    screen.classList.add('fade-out');
    screen.addEventListener('animationend', () => {
        sessionStorage.removeItem('orion_game_data');
        window.location.href = '/game';
    }, { once: true });
}
