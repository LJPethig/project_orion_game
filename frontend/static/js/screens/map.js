// frontend/static/js/screens/map.js
// Shared ship power map logic — used by both terminal.js and datapad.js.
// Loaded before terminal.js and datapad.js in game.html.

// ── SVG room ID mapping ───────────────────────────────────────

const SVG_ROOM_MAP = {
    'rec-room-fill':           'recreation_room',
    'cockpit-fill':            'cockpit',
    'storage-fill':            'storage_room',
    'medbay-fill':             'med_bay',
    'stasis-room-fill':        'hypersleep_chamber',
    'galley-fill':             'galley',
    'corridor-main-fill':      'main_corridor',
    'corridor-sub-fill':       'sub_corridor',
    'bathroom-sub-fill':       'head',
    'mainframe-sub-fill':      'mainframe_room',
    'cargo-bay-sub-fill':      'cargo_bay',
    'airlock-sub-fill':        'airlock',
    'engineering-sub-fill':    'engineering',
    'propulsion-sub-fill':     'propulsion_bay',
    'captains-cabin-sub-fill': 'captains_quarters',
    'crew-quarters-sub-fill':  'crew_cabin',
    'life-support-sub-fill':   'life_support',
};

// ── Shared map state ──────────────────────────────────────────

let _mapPanX  = 0;
let _mapPanY  = 0;
let _mapScale = 0.35;
let _mapSvgEl = null;

// ── Map constants ─────────────────────────────────────────────

const MAP_SCALE_MIN  = 0.2;
const MAP_SCALE_MAX  = 1.0;
const MAP_SCALE_STEP = 0.05;
const MAP_PAN_STEP   = 30;
const MAP_INITIAL_SCALE = 0.35;

// ── Cached electrical status for hover tooltips ───────────────

let _lastElectricalStatus = null;

// ── Shared map functions ──────────────────────────────────────

function resetMapState() {
    _mapPanX  = 0;
    _mapPanY  = 0;
    _mapScale = MAP_INITIAL_SCALE;
}

function _applyMapTransformToContainer(containerId) {
    if (!_mapSvgEl) return;
    const container = document.getElementById(containerId);
    if (container) {
        const cw = container.clientWidth;
        const ch = container.clientHeight;
        const sw = _mapSvgEl.viewBox.baseVal.width  * _mapScale;
        const sh = _mapSvgEl.viewBox.baseVal.height * _mapScale;
        const minX = -(sw - cw * 0.25);
        const maxX =   cw * 0.75;
        const minY = -(sh - ch * 0.25);
        const maxY =   ch * 0.75;
        _mapPanX = Math.max(minX, Math.min(maxX, _mapPanX));
        _mapPanY = Math.max(minY, Math.min(maxY, _mapPanY));
    }
    _mapSvgEl.style.transform = `translate(${_mapPanX}px, ${_mapPanY}px) scale(${_mapScale})`;
}

async function _updateRoomColours() {
    try {
        const r    = await fetch('/api/systems/electrical/status');
        const data = await r.json();
        _lastElectricalStatus = data;
        const roomPower = data.room_power || {};

        for (const [svgId, roomId] of Object.entries(SVG_ROOM_MAP)) {
            const el = _mapSvgEl ? _mapSvgEl.getElementById(svgId) : document.getElementById(svgId);
            if (!el) continue;
            el.classList.remove('room-powered', 'room-unpowered');
            el.classList.add(roomPower[roomId] ? 'room-powered' : 'room-unpowered');
        }
        _updatePowerSourceColours();
    } catch (e) {
        console.error('Could not load electrical status:', e);
    }
}

// ── Hover tooltips for power sources ─────────────────────────

const _MAP_HOVER_SOURCES = [
    { svgId: 'icon-reactor_core',       dataId: 'reactor_core',       type: 'reactor' },
    { svgId: 'icon-propulsion_reactor', dataId: 'propulsion_reactor', type: 'reactor' },
    { svgId: 'icon-BAT-LS-01',          dataId: 'BAT-LS-01',          type: 'battery' },
    { svgId: 'icon-BAT-MF-01',      dataId: 'BAT-MF-01',                      type: 'battery' },
    { svgId: 'icon-sublight_left',  dataId: 'propulsion_bay_sublight_engine', type: 'engine'  },
    { svgId: 'icon-sublight_right', dataId: 'propulsion_bay_sublight_engine', type: 'engine'  },
    { svgId: 'icon-ftl_engine',     dataId: 'propulsion_bay_ftl_engine',      type: 'engine'  },
];

function _initMapHovers() {
    const tooltip = document.getElementById('map-tooltip');
    if (!tooltip || !_mapSvgEl) return;

    _MAP_HOVER_SOURCES.forEach(source => {
        const el = _mapSvgEl.getElementById(source.svgId);
        if (!el) return;

        el.style.cursor = 'pointer';

        el.addEventListener('mouseenter', (e) => {
            const text = _buildTooltipText(source);
            if (!text) return;
            tooltip.textContent = text;
            tooltip.classList.remove('hidden');
            _positionTooltip(e);
        });

        el.addEventListener('mousemove', (e) => {
            _positionTooltip(e);
        });

        el.addEventListener('mouseleave', () => {
            tooltip.classList.add('hidden');
        });
    });
}

function _updatePowerSourceColours() {
    if (!_lastElectricalStatus || !_mapSvgEl) return;

    const reactors  = _lastElectricalStatus.reactors  || {};
    const batteries = _lastElectricalStatus.batteries || {};

    _MAP_HOVER_SOURCES.forEach(source => {
        const el = _mapSvgEl.getElementById(source.svgId);
        if (!el) return;

        let colour;
        if (source.type === 'reactor') {
            const reactor = reactors[source.dataId];
            colour = (reactor && reactor.operational) ? '#00ff44' : '#ff4444';
        } else if (source.type === 'battery') {
            const battery = batteries[source.dataId];
            if (!battery) return;
            if (battery.active)                          colour = '#00ff44';
            else if (battery.charge_percent > 0)         colour = '#ffaa00';
            else                                         colour = '#ff4444';
        }

        if (source.type === 'battery') {
            el.querySelectorAll('rect, path').forEach(child => {
                const id = child.id || '';
                if (id.endsWith('-body')) {
                    child.style.stroke = colour;
                } else {
                    child.style.fill = colour;
                }
            });
        } else if (source.type === 'reactor') {
            const ejectEl = _mapSvgEl.getElementById(source.svgId + '-ejected');
            const reactor = (_lastElectricalStatus.reactors || {})[source.dataId];
            if (ejectEl) {
                ejectEl.style.display = (reactor && reactor.ejected) ? '' : 'none';
                el.style.display      = (reactor && reactor.ejected) ? 'none' : '';
            }
            el.querySelectorAll('circle').forEach(child => {
                const fill = child.getAttribute('fill');
                if (fill === '#001a00') { child.style.stroke = colour; }
                else                   { child.style.fill   = colour; }
            });
            el.querySelectorAll('line').forEach(child => {
                child.style.stroke = colour;
            });
        } else if (source.type === 'engine') {
            const engines = (_lastElectricalStatus.engines || {});
            const engine  = engines[source.dataId];
            colour = (engine && engine.powered) ? '#00ff44' : '#ff4444';
            el.querySelectorAll('rect').forEach(child => {
                const fill = child.getAttribute('fill');
                if (fill === '#001a00' || fill === '#002800') { child.style.stroke = colour; }
                else                                          { child.style.fill   = colour; }
            });
            el.querySelectorAll('circle').forEach(child => {
                const fill = child.getAttribute('fill');
                if (fill === '#002800' || fill === '#004400') { child.style.stroke = colour; }
                else                                          { child.style.fill   = colour; }
            });
            el.querySelectorAll('line').forEach(child => {
                child.style.stroke = colour;
            });
        }
    });
}

function _buildTooltipText(source) {
    if (!_lastElectricalStatus) return null;

    if (source.type === 'reactor') {
        const reactors = _lastElectricalStatus.reactors || {};
        const reactor  = reactors[source.dataId];
        if (!reactor) return null;
        const state = reactor.operational ? 'Operational' : 'Offline';
        return `${reactor.name}  |  ${state}  |  Output: ${reactor.output_kw} kW`;
    }

    if (source.type === 'battery') {
        const batteries = _lastElectricalStatus.batteries || {};
        const battery   = batteries[source.dataId];
        if (!battery) return null;
        const state = battery.active ? 'Active' : 'Standby';
        return `${battery.name}  |  ${state}  |  Charge: ${battery.charge_percent}%`;
    }

    if (source.type === 'engine') {
        const engine = (_lastElectricalStatus.engines || {})[source.dataId];
        if (!engine) return null;
        return `${engine.name}  |  ${engine.powered ? 'Powered' : 'No power'}  |  ${engine.online ? 'Online' : 'Offline'}`;
    }

    return null;
}

function _positionTooltip(e) {
    const tooltip = document.getElementById('map-tooltip');
    if (!tooltip) return;
    tooltip.style.left = (e.clientX + 14) + 'px';
    tooltip.style.top  = (e.clientY - 28) + 'px';
}
