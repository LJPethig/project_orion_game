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

    // ── Commands ─────────────────────────────────────────────

    async sendCommand(command) {
        const r = await fetch('/api/command', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ command }),
        });
        return r.json();
    },

};
