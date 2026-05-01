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
                    handleResult(Object.assign({}, result, { action_type: 'diagnose_panel', response: `Connecting scan tool to ${result.exit_label} access panel. Running diagnostics...` }));
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

    // ── Emergency release prompt — Yes/No choice ──────────
    if (result.action_type === 'emergency_release_prompt') {
        const container = document.createElement('div');
        container.className = 'clarification-options';
        ['Yes', 'No'].forEach((label, i) => {
            const span = document.createElement('span');
            span.className   = 'clarification-option';
            span.textContent = label;
            span.addEventListener('click', () => {
                clearResponse();
                if (i === 0) {
                    // Activate emergency release — 5s lever animation
                    appendResponse('You locate the emergency release lever below the panel. Following the instructions, you work it free from its flush position, then turn it repeatedly. It is stiff — this takes some effort...');
                    showLeverAnimation(5);
                    Loop.lockInput(5, async () => {
                        hideRepairAnimation();
                        const releaseResult = await API.completeEmergencyRelease(result.door_id);
                        clearResponse();
                        handleResult(releaseResult);
                    });
                }
                document.getElementById('command-input').focus();
            });
            container.appendChild(span);
            if (i === 0) container.appendChild(document.createTextNode(' | '));
        });
        document.getElementById('response-content').appendChild(container);
        return;
    }


    // ── Elec diagnose panel — lock input, wait, call elec_diagnose_complete ──
    if (result.action_type === 'elec_diagnose_panel') {
        setJunctionImage(result.panel_id, 'closed');
        showJunctionDiagnosisAnimation(result.real_seconds, result.panel_id);
        Loop.lockInput(result.real_seconds, async () => {
            hideRepairAnimation();
            const diagResult = await API.completeElecDiagnosis(
                result.panel_id,
                result.game_minutes
            );
            clearResponse();
            setJunctionImage(result.panel_id, diagResult.no_faults ? 'intact' : 'burnt');
            handleResult(diagResult);
        });
        return;
    }


    // ── Diagnose panel no power — short timed action, no diagnosis state set ──
    if (result.action_type === 'diagnose_panel_no_power') {
        setDamagedPanelImage(result.security_level);
        showDiagnosisAnimation(result.real_seconds);
        Loop.lockInput(result.real_seconds, async () => {
            hideRepairAnimation();
            const diagResult = await API.completeNoPowerDiagnosis(
                result.panel_model,
                result.game_minutes
            );
            clearResponse();
            handleResult(diagResult);
        });
        return;
    }

    // ── Diagnose panel — lock input, wait, call diagnose_complete ──
    if (result.action_type === 'diagnose_panel') {
        setDamagedPanelImage(result.security_level);
        showDiagnosisAnimation(result.real_seconds);
        Loop.lockInput(result.real_seconds, async () => {
            hideRepairAnimation();
            const diagResult = await API.completeDiagnosis(
                result.panel_id,
                result.door_id,
                result.game_minutes,
                result.exit_label
            );
            clearResponse();
            handleResult(diagResult);
        });
        return;
    }

    // ── Elec repair component — lock input, wait, call elec_repair_complete ──
    if (result.action_type === 'elec_repair_component') {
        Loop.setRepairInProgress(true);
        setJunctionImage(result.panel_id, 'burnt');
        showJunctionRepairAnimation(result.real_seconds, result.panel_id);
        Loop.lockInput(result.real_seconds, async () => {
            hideRepairAnimation();
            const repairResult = await API.completeElecRepair(
                result.panel_id,
                result.component_key
            );
            clearResponse();
            handleResult(repairResult);
        });
        return;
    }

    // ── Repair component — lock input, wait, call repair_complete ──
    if (result.action_type === 'repair_component') {
        Loop.setRepairInProgress(true);
        setDamagedPanelImage(result.security_level);
        showRepairAnimation(result.real_seconds);
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

    // ── Rest — show rest animation, lock input, call rest_complete ──
    if (result.action_type === 'rest') {
        showRestAnimation(result.real_seconds, CONSTANTS.REST_SHIP_HOURS);
        Loop.lockInput(result.real_seconds, async () => {
            hideRestAnimation();
            const restResult = await API.completeRest();
            clearResponse();
            handleResult(restResult);
        });
        return;
    }

    // ── Card swipe — show panel image, scanning animation, lock input ──
    if (result.action_type === 'card_swipe') {
        setPanelImage(result.security_level);
        showScanAnimation(result.real_seconds);
        Loop.lockInput(result.real_seconds, async () => {
            hideScanAnimation();
            const swipeResult = await API.completeSwipe(
                result.door_id,
                result.pending_move,
                result.door_action
            );
            clearResponse();
            if (swipeResult.swipe_complete) {
                const imgState = swipeResult.swipe_action === 'open' ? 'open' : 'closed';
                setDoorImage(imgState);
                if (swipeResult.ship_time) Loop.updateShipTime(swipeResult.ship_time);
                refreshDescription();
                Loop.lockInput(CONSTANTS.DOOR_IMAGE_DISPLAY_MS / 1000, () => loadRoom());
            } else {
                handleResult(swipeResult);
            }
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

    // ── Datapad open ──────────────────────────────────────────
    if (result.action_type === 'datapad_open') {
        const panel = document.getElementById('panel-datapad');
        const tab   = document.querySelector('.tab[data-panel="panel-datapad"]');
        document.querySelectorAll('.slide-panel').forEach(p => p.classList.remove('open'));
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        if (panel) panel.classList.add('open');
        if (tab)   tab.classList.add('active');
        openDatapadPanel();
        return;
    }

    // ── Emergency release complete — door slams open ──────
    if (result.action_type === 'emergency_release_complete') {
        setDoorImage('open');
        refreshDescription();
        Loop.lockInput(CONSTANTS.DOOR_IMAGE_DISPLAY_MS / 1000, () => loadRoom());
        return;
    }

    // ── Rest complete — show get up / quit choice ─────────
    if (result.action_type === 'rest_complete') {
        const container = document.createElement('div');
        container.className = 'clarification-options';
        [
            { label: 'Get up', action: 'get_up' },
            { label: 'Quit',   action: 'quit'   },
        ].forEach((choice, i, arr) => {
            const span = document.createElement('span');
            span.className   = 'clarification-option';
            span.textContent = choice.label;
            span.addEventListener('click', async () => {
                if (choice.action === 'quit') {
                    await API.saveGame();
                    window.location.href = '/';
                } else {
                    await API.saveGame();
                    clearResponse();
                    document.getElementById('command-input').focus();
                }
            });
            container.appendChild(span);
            if (i < arr.length - 1) container.appendChild(document.createTextNode('| '));
        });
        document.getElementById('response-content').appendChild(container);
        return;
    }


    // ── Always clear PIN mode before processing result ────
    pendingPin = null;
    setInputMode('normal');

    // Elec repair complete — panel restored or auto-chain to next component
    if (result.action_type === 'elec_repair_complete') {
        if (result.panel_restored) {
            Loop.setRepairInProgress(false);
            setJunctionImage(result.panel_id, 'intact');
            if (result.resolved_events) {
                result.resolved_events.forEach(ev => showEventResolved(ev.event_id, ev.message));
            }
            setTimeout(() => loadRoom(), CONSTANTS.DOOR_IMAGE_DISPLAY_MS);
        } else {
            setTimeout(async () => {
                const nextResult = await API.elecRepairNext(result.panel_id);
                clearResponse();
                handleResult(nextResult);
            }, CONSTANTS.REPAIR_COMPONENT_PAUSE_MS);
        }
        return;
    }

    // Repair complete — panel restored or auto-chain to next component
    if (result.action_type === 'repair_complete') {
        if (result.panel_restored) {
            Loop.setRepairInProgress(false);
            setPanelImage(result.security_level);
            refreshDescription();
            if (result.resolved_events) {
                result.resolved_events.forEach(ev => showEventResolved(ev.event_id, ev.message));
            }
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
        const imgState = result.swipe_action === 'open' ? 'open' : 'closed';
        setDoorImage(imgState);
        refreshDescription();
        Loop.lockInput(CONSTANTS.DOOR_IMAGE_DISPLAY_MS / 1000, () => loadRoom());
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
        Loop.lockInput(CONSTANTS.DOOR_IMAGE_DISPLAY_MS / 1000, () => loadRoom());
        return;
    }

    // Card invalidated — restore room image immediately
    if (result.card_invalidated) {
        loadRoom();
        return;
    }

    // Instant action — reload room if contents changed (take/drop), otherwise just refresh exits
    if (result.action_type === 'instant') {
        if (result.room_contents_changed || result.power_changed) {
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

