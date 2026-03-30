/* ============================================
   Vision System Monitor - Dashboard Logic
   ============================================ */

// --- Configuration ---
const CONFIG = {
    apiUrl: 'http://localhost:5000',
    pollInterval: 100,          // ms - how often to fetch state in LIVE mode
    mockCycleInterval: 500,     // ms - how often to advance mock state
    maxLogEntries: 20,
    mode: 'live'                // 'mock' or 'live'
};

// --- State ---
let mockStates = [];
let currentMockIndex = 0;
let commandLog = [];
let lastSeenCommand = null;
let fetching = false;
let pollTimer = null;
let mockTimer = null;

// ============================================
// State Provider
// ============================================

async function loadMockStates() {
    try {
        const response = await fetch('mock_states.json');
        mockStates = await response.json();
        console.log(`Loaded ${mockStates.length} mock states`);
    } catch (e) {
        console.error('Failed to load mock_states.json:', e);
        mockStates = [];
    }
}

function getMockState() {
    if (mockStates.length === 0) return null;
    const state = mockStates[currentMockIndex];
    currentMockIndex = (currentMockIndex + 1) % mockStates.length;
    return state;
}

async function fetchLiveState() {
    const url = document.getElementById('api-url').value || CONFIG.apiUrl;
    const response = await fetch(url + '/api/state', { signal: AbortSignal.timeout(2000) });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    const state = await response.json();
    console.log('[DBG-UI] /api/state last_command=' + state.last_command + '  lamps=' + JSON.stringify(state.lamps));
    return state;
}

async function fetchState() {
    if (CONFIG.mode === 'mock') {
        return getMockState();
    } else {
        return await fetchLiveState();
    }
}

// ============================================
// Command Log Accumulation
// ============================================

function updateCommandLog(state) {
    if (!state || !state.last_command) {
        console.log('[DBG-UI] updateCommandLog: SKIPPED - no last_command');
        return;
    }
    if (state.last_command === lastSeenCommand) {
        console.log('[DBG-UI] updateCommandLog: SKIPPED - same as lastSeenCommand=' + lastSeenCommand);
        return;
    }
    console.log('[DBG-UI] updateCommandLog: NEW command=' + state.last_command + '  (was ' + lastSeenCommand + ')');
    lastSeenCommand = state.last_command;

    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', {
        hour12: false,
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    }) + '.' + String(now.getMilliseconds()).padStart(3, '0');

    commandLog.unshift({
        time: timeStr,
        command: state.last_command
    });

    if (commandLog.length > CONFIG.maxLogEntries) {
        commandLog.pop();
    }
}

// ============================================
// Render Functions
// ============================================

function renderGuideMotors(state) {
    if (!state) return;

    const guides = [
        { prefix: 'guide-top', data: state.guide_top },
        { prefix: 'guide-bottom', data: state.guide_bottom }
    ];

    guides.forEach(({ prefix, data }) => {
        const bar = document.getElementById(`${prefix}-bar`);
        const posText = document.getElementById(`${prefix}-pos`);
        const movingDot = document.getElementById(`${prefix}-moving`);

        // Position bar width and class
        bar.className = 'position-bar';
        if (data.position === 'open') {
            bar.classList.add('open');
            bar.style.width = '100%';
        } else if (data.position === 'moving') {
            bar.classList.add('moving');
            bar.style.width = '50%';
        } else {
            bar.classList.add('closed');
            bar.style.width = '5%';
        }

        // Position text
        posText.textContent = data.position.toUpperCase();

        // Moving indicator
        movingDot.className = 'motor-moving';
        if (data.moving) {
            movingDot.classList.add('active');
        }
    });
}

function renderReelerMotors(state) {
    if (!state) return;

    const reelers = [
        { prefix: 'reeler-top', data: state.reeler_top },
        { prefix: 'reeler-bottom', data: state.reeler_bottom }
    ];

    reelers.forEach(({ prefix, data }) => {
        const dot = document.getElementById(`${prefix}-dot`);
        const speed = document.getElementById(`${prefix}-speed`);
        const pos = document.getElementById(`${prefix}-pos`);

        dot.className = 'reeler-indicator';
        if (data.running) {
            dot.classList.add('running');
        }

        speed.textContent = data.speed;
        pos.textContent = `pos: ${data.position}`;
    });

    document.getElementById('reeler-teeth').textContent = `Teeth: ${state.reeler_top.teeth}`;
    document.getElementById('reeler-init').textContent = `Init: ${state.reeler_initialized ? 'YES' : 'NO'}`;
}

function renderSagSensors(state) {
    if (!state) return;

    const sags = [
        { id: 'sag-top-upper', triggered: state.sag_top_upper },
        { id: 'sag-top-lower', triggered: state.sag_top_lower },
        { id: 'sag-btm-upper', triggered: state.sag_bottom_upper },
        { id: 'sag-btm-lower', triggered: state.sag_bottom_lower }
    ];

    sags.forEach(({ id, triggered }) => {
        const indicator = document.getElementById(id);
        const text = document.getElementById(id + '-text');

        indicator.className = 'sag-indicator';
        if (triggered) {
            indicator.classList.add('triggered');
            text.textContent = 'TRIGGERED';
            text.style.color = 'var(--red)';
        } else {
            indicator.classList.add('pass');
            text.textContent = 'PASS';
            text.style.color = 'var(--green)';
        }
    });

    // Proximity sensors
    const sensors = [
        { id: 'sensor-top', data: state.sensor_top },
        { id: 'sensor-btm', data: state.sensor_bottom }
    ];

    sensors.forEach(({ id, data }) => {
        const indicator = document.getElementById(id);
        const text = document.getElementById(id + '-text');

        indicator.className = 'sag-indicator';
        if (data.triggered) {
            indicator.classList.add('triggered');
            text.textContent = 'TRIG';
        } else if (data.powered) {
            indicator.classList.add('pass');
            text.textContent = 'OK';
        } else {
            text.textContent = 'OFF';
        }
    });
}

function renderLamps(state) {
    if (!state) return;

    const lamps = [
        { id: 'lamp-red', circleClass: 'lamp-red-circle', on: state.lamps.red },
        { id: 'lamp-yellow', circleClass: 'lamp-yellow-circle', on: state.lamps.yellow },
        { id: 'lamp-green', circleClass: 'lamp-green-circle', on: state.lamps.green },
        { id: 'lamp-buzzer', circleClass: 'lamp-buzzer-circle', on: state.lamps.buzzer }
    ];

    lamps.forEach(({ id, circleClass, on }) => {
        const circle = document.getElementById(id).querySelector('.lamp-circle');
        circle.className = `lamp-circle ${circleClass}`;
        if (on) {
            circle.classList.add('on');
        }
    });
}

function renderCameras(state) {
    if (!state) return;

    for (let i = 0; i <= 6; i++) {
        const dot = document.getElementById(`cam-${i}`).querySelector('.cam-dot');
        dot.className = 'cam-dot';
        if (state.cameras.flags[String(i)]) {
            dot.classList.add('active');
        }
    }

    const activeSeq = state.cameras.active_sequence;
    document.getElementById('cam-active-seq').textContent =
        activeSeq === -1 ? 'None' : `Camera ${activeSeq}`;

    document.getElementById('cam-timestamp').textContent =
        state.cameras.timestamp_enabled ? 'ENABLED' : 'DISABLED';
}

function renderControlButtons(state) {
    if (!state) return;

    const lightRun = document.getElementById('light-run');
    const lightPause = document.getElementById('light-pause');
    const lightStop = document.getElementById('light-stop');
    const lightBuzzer = document.getElementById('light-buzzer-off');

    // Reset all lights
    lightRun.className = 'control-light';
    lightPause.className = 'control-light';
    lightStop.className = 'control-light';
    lightBuzzer.className = 'control-light';

    // Set active light based on run_state
    const runState = state.run_state || 'running';
    if (runState === 'running') {
        lightRun.classList.add('active-run');
    } else if (runState === 'paused') {
        lightPause.classList.add('active-pause');
    } else if (runState === 'stopped') {
        lightStop.classList.add('active-stop');
    }

    // Buzzer override light
    if (state.buzzer_override) {
        lightBuzzer.classList.add('active-buzzer');
    }
}

function renderLightChannels(state) {
    if (!state) return;

    const channels = state.light_channels || {};
    for (let i = 1; i <= 6; i++) {
        const el = document.getElementById(`light-ch-${i}`);
        if (!el) continue;
        const dot = el.querySelector('.light-ch-dot');
        dot.className = 'light-ch-dot';
        if (channels[String(i)]) {
            dot.classList.add('active');
        }
    }
}

function renderSystemStatus(state) {
    if (!state) return;

    const statuses = [
        { id: 'sys-door', on: state.door_locked, onText: 'LOCKED', offText: 'UNLOCKED', alertWhenOff: true },
        { id: 'sys-estop', on: state.estop_pressed, onText: 'PRESSED', offText: 'CLEAR', alertWhenOn: true },
        { id: 'sys-power', on: state.power_on, onText: 'ON', offText: 'OFF', alertWhenOff: true },
        { id: 'sys-sol-top', on: state.solenoid_top, onText: 'ON', offText: 'OFF' },
        { id: 'sys-sol-btm', on: state.solenoid_bottom, onText: 'ON', offText: 'OFF' },
        { id: 'sys-stamping', on: state.stamping_relay, onText: 'ON', offText: 'OFF' },
        { id: 'sys-stepper', on: state.stepper_initialized, onText: 'YES', offText: 'NO' },
        { id: 'sys-reeler-init', on: state.reeler_initialized, onText: 'YES', offText: 'NO' }
    ];

    statuses.forEach(({ id, on, onText, offText, alertWhenOn, alertWhenOff }) => {
        const indicator = document.getElementById(id);
        const text = document.getElementById(id + '-text');

        indicator.className = 'status-indicator';
        if (on) {
            if (alertWhenOn) {
                indicator.classList.add('alert');
            } else {
                indicator.classList.add('on');
            }
            text.textContent = onText;
        } else {
            if (alertWhenOff) {
                indicator.classList.add('alert');
            } else {
                indicator.classList.add('off');
            }
            text.textContent = offText;
        }
    });
}

function renderCommandLog() {
    const container = document.getElementById('command-log');

    if (commandLog.length === 0) {
        container.innerHTML = '<div class="log-empty">Waiting for commands...</div>';
        return;
    }

    let html = '';
    commandLog.forEach(entry => {
        html += `<div class="log-entry">
            <span class="log-time">[${entry.time}]</span>
            <span class="log-command">${entry.command}</span>
        </div>`;
    });
    container.innerHTML = html;
}

function renderConnectionStatus(status) {
    const dot = document.getElementById('status-dot');
    const text = document.getElementById('status-text');

    dot.className = 'status-dot';

    if (status === 'connected') {
        dot.classList.add('connected');
        text.textContent = 'Connected';
    } else if (status === 'mock') {
        dot.classList.add('mock');
        text.textContent = 'Mock Mode';
    } else {
        dot.classList.add('disconnected');
        text.textContent = 'Disconnected';
    }
}

function renderQueryStatus(state, connectionStatus) {
    const dot = document.getElementById('query-dot');
    const text = document.getElementById('query-text');

    dot.className = 'query-dot';

    if (connectionStatus === 'disconnected') {
        dot.classList.add('unknown');
        text.textContent = 'QRY --';
    } else {
        const responsive = state && state.query_responsive !== undefined
            ? state.query_responsive
            : true; // default to true if field not present
        if (responsive) {
            dot.classList.add('ok');
            text.textContent = 'QRY OK';
        } else {
            dot.classList.add('fail');
            text.textContent = 'QRY FAIL';
        }
    }
}

function renderCycleLabel(state) {
    const label = document.getElementById('cycle-label');
    if (state && state._label) {
        label.textContent = state._label;
    } else {
        label.textContent = '--';
    }
}

function renderAll(state) {
    renderGuideMotors(state);
    renderReelerMotors(state);
    renderSagSensors(state);
    renderLamps(state);
    renderCameras(state);
    renderSystemStatus(state);
    renderControlButtons(state);
    renderLightChannels(state);
    renderQueryStatus(state, CONFIG.mode === 'mock' ? 'mock' : 'connected');
    renderCommandLog();
    renderCycleLabel(state);
}

// ============================================
// Mode Toggle
// ============================================

function setMode(mode) {
    CONFIG.mode = mode;

    // Update button styles
    document.getElementById('btn-mock').classList.toggle('active', mode === 'mock');
    document.getElementById('btn-live').classList.toggle('active', mode === 'live');

    // Show/hide API URL input
    document.getElementById('api-url').classList.toggle('visible', mode === 'live');

    // Reset state
    lastSeenCommand = null;
    commandLog = [];
    currentMockIndex = 0;

    // Update connection status
    if (mode === 'mock') {
        renderConnectionStatus('mock');
    } else {
        renderConnectionStatus('connected');
    }

    // Update control button state for mock mode
    updateControlButtonsDisabled();

    // Restart polling
    stopPolling();
    startPolling();
}

// ============================================
// Control Command Sending
// ============================================

/** Set of button IDs currently debounced (waiting for next poll to re-enable). */
const debouncedButtons = new Set();

/**
 * Send a control command to the emulator via POST /api/command.
 * Handles debounce: disables the button for 500ms, then re-enables
 * on next successful state poll.
 *
 * @param {string} opcode - One of EMRUN, EMPAU, EMSTP, BZZOF
 * @param {string} buttonId - DOM id of the button that was clicked
 */
async function sendControlCommand(opcode, buttonId) {
    if (CONFIG.mode === 'mock') return; // no-op in mock mode

    const btn = document.getElementById(buttonId);
    if (!btn || btn.disabled) return;

    // Debounce: disable button immediately
    btn.disabled = true;
    debouncedButtons.add(buttonId);

    try {
        const url = document.getElementById('api-url').value || CONFIG.apiUrl;
        const response = await fetch(url + '/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: opcode }),
            signal: AbortSignal.timeout(2000)
        });
        if (!response.ok) {
            console.error(`Control command ${opcode} failed: HTTP ${response.status}`);
        }
    } catch (e) {
        console.error(`Control command ${opcode} error:`, e);
    }

    // Re-enable after 500ms minimum (polling will also clear debounce)
    setTimeout(() => {
        debouncedButtons.delete(buttonId);
        if (btn && CONFIG.mode !== 'mock') {
            btn.disabled = false;
        }
    }, 500);
}

/**
 * Enable or disable all control buttons based on current mode.
 * In mock mode, buttons are disabled and greyed out.
 */
function updateControlButtonsDisabled() {
    const isMock = CONFIG.mode === 'mock';
    const buttons = ['btn-run', 'btn-pause', 'btn-stop', 'btn-buzzer-off'];
    buttons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.disabled = isMock;
            btn.classList.toggle('mock-disabled', isMock);
        }
    });
}

/**
 * onclick handler wired from HTML buttons.
 * Maps opcode to button ID and delegates to sendControlCommand.
 */
function onControlClick(opcode) {
    const opcodeToButton = {
        'EMRUN': 'btn-run',
        'EMPAU': 'btn-pause',
        'EMSTP': 'btn-stop',
        'BZZOF': 'btn-buzzer-off'
    };
    const buttonId = opcodeToButton[opcode];
    if (buttonId) {
        sendControlCommand(opcode, buttonId);
    }
}

// ============================================
// Polling Loop
// ============================================

function startPolling() {
    if (CONFIG.mode === 'mock') {
        // Mock mode: cycle through states at mockCycleInterval
        mockTimer = setInterval(async () => {
            const state = getMockState();
            if (state) {
                updateCommandLog(state);
                renderAll(state);
            }
        }, CONFIG.mockCycleInterval);

        // Render first state immediately
        const firstState = getMockState();
        if (firstState) {
            updateCommandLog(firstState);
            renderAll(firstState);
        }
    } else {
        // Live mode: poll API at pollInterval
        pollTimer = setInterval(async () => {
            if (fetching) return;
            fetching = true;
            try {
                const state = await fetchLiveState();
                updateCommandLog(state);
                renderAll(state);
                renderConnectionStatus('connected');
            } catch (e) {
                renderConnectionStatus('disconnected');
                renderQueryStatus(null, 'disconnected');
            } finally {
                fetching = false;
            }
        }, CONFIG.pollInterval);
    }
}

function stopPolling() {
    if (pollTimer) { clearInterval(pollTimer); pollTimer = null; }
    if (mockTimer) { clearInterval(mockTimer); mockTimer = null; }
    fetching = false;
}

// ============================================
// Initialization
// ============================================

async function init() {
    console.log('Vision System Monitor starting...');

    // Load mock states (available for manual switch to mock mode)
    await loadMockStates();

    // Start in Live mode by default so real API data is shown immediately
    document.getElementById('api-url').classList.add('visible');
    renderConnectionStatus('connected');
    updateControlButtonsDisabled();

    // Start polling
    startPolling();

    console.log('Vision System Monitor ready.');
}

// Start when DOM is ready
document.addEventListener('DOMContentLoaded', init);
