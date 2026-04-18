// frontend/static/js/core/loop.js
// Frontend polling loop.
// Polls the backend every 10 seconds for ship time and any passive state changes.
// Also handles input locking for timed actions (repairs, waits, etc.)

const Loop = (() => {

    const POLL_INTERVAL_MS  = 10000;   // 10 seconds — passive state polling
    const TICK_INTERVAL_MS  = 40000;   // 40 seconds — real-time clock advance (1.5x ship time)
    const EVENT_INTERVAL_MS = 15000;   // 15 seconds — event check
    let   pollTimer         = null;
    let   tickTimer         = null;
    let   eventTimer        = null;
    let   inputLocked       = false;
    // repairInProgress covers the brief window between component repairs where
    // inputLocked is momentarily false (between unlockInput() and the next lockInput()
    // in the repair chain callback). Without this flag an event could theoretically
    // fire during that ~50-100ms gap. The flag is set for the entire repair chain.
    let   repairInProgress = false;


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

    async function checkEvents() {
        // Skip if any timed action or PIN entry is in progress
        if (inputLocked) return;
        if (repairInProgress) return;
        if (typeof pendingPin !== 'undefined' && pendingPin) return;
        try {
            const data = await API.checkEvents();
            if (data.events && data.events.length > 0) {
                data.events.forEach(ev => {
                    if (ev.message) appendEventStrip(ev.message, ev.event_id);
                });
                // Refresh map if currently visible
                if (typeof _updateRoomColours === 'function' && _mapSvgEl) {
                    _updateRoomColours();
                }
                // Reload room to update description addendum if power state changed
                loadRoom();
            }
        } catch (err) {
            console.error('Event check error:', err);
        }
    }

    function startPolling() {
        poll();                                                   // Immediate first poll
        pollTimer  = setInterval(poll,        POLL_INTERVAL_MS);
        tickTimer  = setInterval(tick,        TICK_INTERVAL_MS); // Real-time clock
        eventTimer = setInterval(checkEvents, EVENT_INTERVAL_MS);
    }

    function stopPolling() {
        if (pollTimer)  { clearInterval(pollTimer);  pollTimer  = null; }
        if (tickTimer)  { clearInterval(tickTimer);  tickTimer  = null; }
        if (eventTimer) { clearInterval(eventTimer); eventTimer = null; }
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
            // unlockInput fires before the callback so the callback can chain a new lockInput()
            // without it being immediately cancelled.
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
        checkEvents:     checkEvents,
        lockInput:       lockInput,
        unlockInput:     unlockInput,
        isLocked:        isLocked,
        setRepairInProgress: (v) => { repairInProgress = v; },
        isRepairInProgress:  () => repairInProgress,
        updateShipTime:  updateShipTime,
        updateShipName:  updateShipName,
    };

})();
