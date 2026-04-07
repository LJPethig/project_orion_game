// frontend/static/js/screens/commands.js
// Command handling — handleCommand, handleResult, submitPin, refreshDescription.

function findExitData(exitKey) {
    if (currentExits[exitKey]) return currentExits[exitKey];
    for (const [key, data] of Object.entries(currentExits)) {
        if (key.toLowerCase() === exitKey.toLowerCase()) return data;
        if ((data.label || '').toLowerCase().replace(/\s+/g, '_') === exitKey) return data;
    }
    return null;
}

function doorStateText(state) {
    switch (state) {
        case 'open':   return 'Door is open';
        case 'closed': return 'Door is closed';
        case 'locked': return 'Door is locked';
        default:       return 'No door';
    }
}

function doorStateColour(state) {
    switch (state) {
        case 'open':   return 'var(--col-prompt)';
        case 'closed': return 'var(--col-text)';
        case 'locked': return 'var(--col-alert)';
        default:       return 'var(--col-text)';
    }
}

// ── Command handling ─────────────────────────────────────────

async function handleCommand() {
    if (isTerminalSessionActive()) return;
    if (Loop.isLocked()) return;

    const input = document.getElementById('command-input');
    const cmd   = input.value.trim();
    if (!cmd) return;

    input.value = '';
    clearResponse();

    // ── PIN mode — route input as PIN ─────────────────────
    if (pendingPin) {
        appendResponse(`> ****`, 'player-cmd');
        await submitPin(cmd);
        return;
    }

    // ── Quit ─────────────────────────────────────────────
    if ((cmd.toLowerCase() === 'quit' || cmd.toLowerCase() === 'exit') && !isTerminalOpen()) {
        appendResponse(`> ${cmd}`, 'player-cmd');
        appendResponse('Are you sure you want to quit?');
        const container = document.createElement('div');
        container.className = 'clarification-options';
        ['Yes', 'No'].forEach((label, i) => {
            const span = document.createElement('span');
            span.className   = 'clarification-option';
            span.textContent = label;
            span.addEventListener('click', () => {
                if (i === 0) {
                    window.location.href = '/';
                } else {
                    clearResponse();
                }
                document.getElementById('command-input').focus();
            });
            container.appendChild(span);
            if (i === 0) container.appendChild(document.createTextNode('| '));
        });
        document.getElementById('response-content').appendChild(container);
        document.getElementById('command-input').focus();
        return;
    }

    // ── Normal command ────────────────────────────────────
    appendResponse(`> ${cmd}`, 'player-cmd');
    const result = await API.sendCommand(cmd);
    handleResult(result);
}

// currentObjects must stay in sync so tooltips (terminals, containers) reflect live state
// updates both currentExits and currentObjects
function refreshDescription() {
    API.getRoom().then(room => {
        if (!room.error) {
            currentExits   = room.exits || {};
            currentObjects = room.object_states || {};
        }
    });
}

function handleResult(result) {
    if (result.ship_time) Loop.updateShipTime(result.ship_time);

    // ── Diagnosis complete — render styled result ─────────────
    if (result.action_type === 'diagnose_complete' || result.action_type === 'repair_message') {
        appendRepairMessage(result);
        return;
    }

    // ── Diagnose panel warning — no manual, ask to confirm ───
    if (result.action_type === 'diagnose_panel_warning') {
        appendResponse(result.response, 'alert');
        const container = document.createElement('div');
        container.className = 'clarification-options';
        ['Yes', 'No'].forEach((label, i) => {
            const span = document.createElement('span');
            span.className   = 'clarification-option';
            span.textContent = label;
            span.addEventListener('click', () => {
                clearResponse();
                if (i === 0) {
                    handleResult(Object.assign({}, result, { action_type: 'diagnose_panel', response: '' }));
                }
                document.getElementById('command-input').focus();
            });
            container.appendChild(span);
            if (i === 0) container.appendChild(document.createTextNode('| '));
        });
        document.getElementById('response-content').appendChild(container);
        return;
    }

    if (result.response) appendResponse(result.response);

    // ── Door locked — show closed hatch image, stay on it ────
    if (result.action_type === 'door_locked') {
        setDoorImage('closed');
        refreshDescription();
        return;

    }

    // ── Panel damaged — show damaged panel image, stay on it ─
    if (result.action_type === 'panel_damaged') {
        setDamagedPanelImage(result.security_level);
        refreshDescription();
        return;
    }


    // ── Diagnose panel — lock input, wait, call diagnose_complete ──
    if (result.action_type === 'diagnose_panel') {
        setDamagedPanelImage(result.security_level);
        showDiagnosisAnimation();
        Loop.lockInput(result.real_seconds, async () => {
            hideRepairAnimation();
            const diagResult = await API.completeDiagnosis(
                result.panel_id,
                result.door_id
            );
            clearResponse();
            handleResult(diagResult);
        });
        return;
    }

    // ── Repair component — lock input, wait, call repair_complete ──
    if (result.action_type === 'repair_component') {
        setDamagedPanelImage(result.security_level);
        showRepairAnimation();
        Loop.lockInput(result.real_seconds, async () => {
            hideRepairAnimation();
            const repairResult = await API.completeRepair(
                result.panel_id,
                result.door_id,
                result.component_id,
                result.exit_label
            );
            clearResponse();
            handleResult(repairResult);
        });
        return;
    }

    // ── Card swipe — show panel image, scanning animation, lock input ──
    if (result.action_type === 'card_swipe') {
        setPanelImage(result.security_level);
        showScanAnimation();
        Loop.lockInput(result.real_seconds, async () => {
            hideScanAnimation();
            const swipeResult = await API.completeSwipe(
                result.door_id,
                result.pending_move,
                result.door_action
            );
            clearResponse();
            handleResult(swipeResult);
        });
        return;
    }

    // ── PIN required — switch input to PIN mode ───────────
    if (result.action_type === 'pin_required') {
        pendingPin = {
            door_id:     result.door_id,
            door_action: result.door_action,
        };
        setInputMode('pin');
        return;
    }

    // ── Clarification required — render clickable options ─
    if (result.action_type === 'clarification_required') {
        if (result.options && result.options.length > 0) {
            const container = document.createElement('div');
            container.className = 'clarification-options';
            result.options.forEach(opt => {
                const span = document.createElement('span');
                span.className   = 'clarification-option';
                span.textContent = opt.label;
                span.addEventListener('click', async () => {
                    clearResponse();
                    const r = await API.sendCommand('clarified:' + opt.command);
                    handleResult(r);
                });
                container.appendChild(span);
                if (opt !== result.options[result.options.length - 1]) {
                    container.appendChild(document.createTextNode('| '));
                }
            });
            document.getElementById('response-content').appendChild(container);
        }
        return;
    }

    // ── Terminal open ─────────────────────────────────────
    if (result.action_type === 'terminal_open') {
        openTerminalPanel(result);
        return;
    }

    // ── Always clear PIN mode before processing result ────
    pendingPin = null;
    setInputMode('normal');

    // Repair complete — panel restored or auto-chain to next component
    if (result.action_type === 'repair_complete') {
        if (result.panel_restored) {
            setPanelImage(result.security_level);
            refreshDescription();
            setTimeout(() => loadRoom(), CONSTANTS.DOOR_IMAGE_DISPLAY_MS);
        } else {
            // More components remain — auto-chain after pause for event check
            setTimeout(async () => {
                const nextResult = await API.repairNext(
                    result.panel_id,
                    result.door_id,
                    result.exit_label
                );
                clearResponse();
                handleResult(nextResult);
            }, CONSTANTS.REPAIR_COMPONENT_PAUSE_MS);
        }
        return;
    }

    // Swipe completed — show open or closed hatch then restore room
    if (result.swipe_complete) {
        const imgState = result.swipe_action === 'lock' ? 'closed' : 'open';
        setDoorImage(imgState);
        refreshDescription();
        setTimeout(() => loadRoom(), CONSTANTS.DOOR_IMAGE_DISPLAY_MS);
        return;
    }

    // Normal room change — just update room directly
    if (result.room_changed && result.room) {
        updateRoom(result.room);
        return;
    }

    // Instant door image — open or close without card swipe
    if (result.door_image) {
        setDoorImage(result.door_image);
        refreshDescription();
        setTimeout(() => loadRoom(), CONSTANTS.DOOR_IMAGE_DISPLAY_MS);
        return;
    }

    // Card invalidated — restore room image immediately
    if (result.card_invalidated) {
        loadRoom();
        return;
    }

    // Instant action — reload room if contents changed (take/drop), otherwise just refresh exits
    if (result.action_type === 'instant') {
        if (result.room_contents_changed) {
            loadRoom();
        } else {
            refreshDescription();
        }
    }

    refreshInventoryIfOpen();
}

async function submitPin(pin) {
    const result = await API.submitPin(
        pendingPin.door_id,
        null,
        pin,
        pendingPin.door_action
    );
    handleResult(result);
}

// ── Input mode ───────────────────────────────────────────────

