// frontend/static/js/core/loop.js
// Frontend polling loop.
// Polls the backend every 10 seconds for ship time and any passive state changes.
// Also handles input locking for timed actions (repairs, waits, etc.)

const Loop = (() => {

    const POLL_INTERVAL_MS = 10000;   // 10 seconds — passive event checking
    const TICK_INTERVAL_MS = 60000;   // 60 seconds — real-time clock advance
    let   pollTimer        = null;
    let   tickTimer        = null;
    let   inputLocked      = false;

    // ── Ship time display ────────────────────────────────────

    function updateShipTime(timeStr) {
        const el = document.getElementById('ship-time-display');
        if (el) el.textContent = timeStr;
    }

    function updateShipName(nameStr) {
        const el = document.getElementById('ship-name-display');
        if (el) el.textContent = nameStr;
    }

    // ── Real-time clock tick ─────────────────────────────────
    // Advances ship time by 1 minute every 60 real seconds.
    // Runs independently of the poll — time passes even when idle.

    async function tick() {
        try {
            const data = await API.tick();
            if (data.ship_time) updateShipTime(data.ship_time);
        } catch (err) {
            console.error('Tick error:', err);
        }
    }

    // ── Polling ──────────────────────────────────────────────

    async function poll() {
        try {
            const data = await API.getState();
            if (data.ship_time) updateShipTime(data.ship_time);
            if (data.ship_name) updateShipName(data.ship_name);
        } catch (err) {
            console.error('Poll error:', err);
        }
    }

    function startPolling() {
        poll();                                              // Immediate first poll
        pollTimer = setInterval(poll, POLL_INTERVAL_MS);
        tickTimer = setInterval(tick, TICK_INTERVAL_MS);    // Real-time clock
    }

    function stopPolling() {
        if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
        if (tickTimer) { clearInterval(tickTimer); tickTimer = null; }
    }

    // ── Input locking (for timed actions) ───────────────────
    // When a timed action fires (repair, wait, etc.) the backend returns
    // lock_input: true, real_seconds: N, game_minutes: M.
    // The frontend locks input, waits N real seconds, then calls back
    // to complete the action and advance ship time.

    function lockInput(realSeconds, onComplete) {
        const input = document.getElementById('command-input');
        if (!input) return;

        inputLocked = true;
        input.disabled = true;
        const desc = document.getElementById('description-content');
        if (desc) desc.style.pointerEvents = 'none';

        setTimeout(async () => {
            unlockInput();
            if (onComplete) await onComplete();
        }, realSeconds * 1000);
    }

    function unlockInput() {
        const input = document.getElementById('command-input');
        if (!input) return;

        inputLocked = false;
        input.disabled = false;
        input.focus();
        const desc = document.getElementById('description-content');
        if (desc) desc.style.pointerEvents = '';
    }

    function isLocked() {
        return inputLocked;
    }

    // ── Public interface ─────────────────────────────────────

    return {
        start:           startPolling,
        stop:            stopPolling,
        poll:            poll,
        lockInput:       lockInput,
        unlockInput:     unlockInput,
        isLocked:        isLocked,
        updateShipTime:  updateShipTime,
        updateShipName:  updateShipName,
    };

})();
