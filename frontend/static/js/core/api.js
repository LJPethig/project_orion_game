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

    async saveStatus() {
        const r = await fetch('/api/game/save_status');
        return r.json();
    },

    async loadGame() {
        const r = await fetch('/api/game/load', { method: 'POST' });
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

    async completeDiagnosis(panel_id, door_id, game_minutes, exit_label) {
        const r = await fetch('/api/command/diagnose_complete', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ panel_id, door_id, game_minutes, exit_label }),
        });
        return r.json();
    },

    async completeNoPowerDiagnosis(panel_model, game_minutes) {
        const r = await fetch('/api/command/no_power_diagnose_complete', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ panel_model, game_minutes }),
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

    async completeElecRepair(panel_id, component_key) {
        const r = await fetch('/api/command/elec_repair_complete', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ panel_id, component_key }),
        });
        return r.json();
    },

    async elecRepairNext(panel_id) {
        const r = await fetch('/api/command/elec_repair_next', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ panel_id }),
        });
        return r.json();
    },

    async completeElecDiagnosis(panel_id, game_minutes) {
        const r = await fetch('/api/command/elec_diagnose_complete', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ panel_id, game_minutes }),
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

    async saveGame() {
        const r = await fetch('/api/command/save', { method: 'POST' });
        return r.json();
    },

    async completeRest() {
        const r = await fetch('/api/command/rest_complete', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({}),
        });
        return r.json();
    },

    async completeEmergencyRelease(door_id) {
        const r = await fetch('/api/command/emergency_release_complete', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ door_id }),
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

    async getDatapadData() {
        const r = await fetch('/api/game/datapad');
        return r.json();
    },

    async terminalClose() {
        const r = await fetch('/api/game/terminal/close', { method: 'POST' });
        return r.json();
    },

    async storeItem(instance_id) {
        const r = await fetch('/api/game/storage/store', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ instance_id }),
        });
        return r.json();
    },

    async retrieveItem(instance_id) {
        const r = await fetch('/api/game/storage/retrieve', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body:    JSON.stringify({ instance_id }),
        });
        return r.json();
    },

    async getStorageManifest() {
        const r = await fetch('/api/game/storage/manifest');
        return r.json();
    },

    async getCargoManifest() {
        const r = await fetch('/api/game/cargo/manifest');
        return r.json();
    },

    // ── Events ───────────────────────────────────────────────

    async checkEvents() {
        const r = await fetch('/api/events/check');
        return r.json();
    },

    async getActiveEvents() {
        const r = await fetch('/api/events/active');
        return r.json();
    },
};
