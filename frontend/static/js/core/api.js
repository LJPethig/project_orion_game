// frontend/static/js/core/api.js
// All fetch calls to the Flask backend.
// One function per endpoint — nothing else lives here.

const API = {

    // ── Game state ───────────────────────────────────────────

    async getState() {
        const r = await fetch('/api/game/state');
        return r.json();
    },

    async newGame() {
        const r = await fetch('/api/game/new', { method: 'POST' });
        return r.json();
    },

    async getRoom() {
        const r = await fetch('/api/game/room');
        return r.json();
    },

    async tick() {
        const r = await fetch('/api/game/tick', { method: 'POST' });
        return r.json();
    },

    // ── Commands ─────────────────────────────────────────────

    async sendCommand(command) {
        const r = await fetch('/api/command', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ command }),
        });
        return r.json();
    },

    async completeSwipe(door_id, pending_move, door_action) {
        const r = await fetch('/api/command/swipe', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ door_id, pending_move, door_action }),
        });
        return r.json();
    },

    async submitPin(door_id, pending_move, pin, door_action) {
        const r = await fetch('/api/command/pin', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ door_id, pending_move, pin, door_action }),
        });
        return r.json();
    },

    async completeDiagnosis(panel_id, door_id, game_minutes) {
        const r = await fetch('/api/command/diagnose_complete', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ panel_id, door_id, game_minutes }),
        });
        return r.json();
    },

    async completeRepair(panel_id, door_id, component_id, exit_label) {
        const r = await fetch('/api/command/repair_complete', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ panel_id, door_id, component_id, exit_label }),
        });
        return r.json();
    },

    async repairNext(panel_id, door_id, exit_label) {
        const r = await fetch('/api/command/repair_next', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ panel_id, door_id, exit_label }),
        });
        return r.json();
    },

    async getInventory() {
        const r = await fetch('/api/game/inventory');
        return r.json();
    },

    async getTerminalContent(terminal_type, action) {
        const r = await fetch('/api/game/terminal/content', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ terminal_type, action }),
        });
        return r.json();
    },

};
