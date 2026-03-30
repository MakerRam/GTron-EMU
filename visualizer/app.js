/* ============================================
   Vision System Monitor - Dashboard Logic
   ============================================ */

// --- Configuration ---
const CONFIG = {
    apiUrl: 'http://localhost:5000',
    pollInterval: 100,          // ms - how often to fetch state in LIVE mode
    mockCycleInterval: 500,     // ms - how often to advance mock state (Mock 1)
    mock2PollInterval: 100,     // ms - how often to poll Mock 2 engine state
    maxLogEntries: 20,
    mode: 'live'                // 'mock1', 'mock2', or 'live'
};

// --- State ---
let mockStates = [];
let currentMockIndex = 0;
let commandLog = [];
let lastSeenCommand = null;
let fetching = false;
let pollTimer = null;
let mockTimer = null;
let previousState = null;  // Track previous state for blink-on-change detection

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
    if (CONFIG.mode === 'mock1') {
        return getMockState();
    } else if (CONFIG.mode === 'mock2') {
        return Mock2Engine.getState();
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
        { id: 'sag-top-upper', triggered: state.sag_top_upper, prevKey: 'sag_top_upper' },
        { id: 'sag-top-lower', triggered: state.sag_top_lower, prevKey: 'sag_top_lower' },
        { id: 'sag-btm-upper', triggered: state.sag_bottom_upper, prevKey: 'sag_bottom_upper' },
        { id: 'sag-btm-lower', triggered: state.sag_bottom_lower, prevKey: 'sag_bottom_lower' }
    ];

    sags.forEach(({ id, triggered, prevKey }) => {
        const indicator = document.getElementById(id);
        const text = document.getElementById(id + '-text');

        // Detect state change for blink
        const changed = previousState && previousState[prevKey] !== triggered;

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

        // Trigger blink on state change
        if (changed) {
            indicator.classList.add('blink');
            indicator.addEventListener('animationend', () => {
                indicator.classList.remove('blink');
            }, { once: true });
        }
    });

    // Proximity sensors
    const sensors = [
        { id: 'sensor-top', data: state.sensor_top, prevData: previousState ? previousState.sensor_top : null },
        { id: 'sensor-btm', data: state.sensor_bottom, prevData: previousState ? previousState.sensor_bottom : null }
    ];

    sensors.forEach(({ id, data, prevData }) => {
        const indicator = document.getElementById(id);
        const text = document.getElementById(id + '-text');

        // Detect state change for blink
        const changed = prevData && (prevData.triggered !== data.triggered || prevData.powered !== data.powered);

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

        // Trigger blink on state change
        if (changed) {
            indicator.classList.add('blink');
            indicator.addEventListener('animationend', () => {
                indicator.classList.remove('blink');
            }, { once: true });
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

    for (let i = 1; i <= 6; i++) {
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

    const lightPower = document.getElementById('light-power');
    const lightRun = document.getElementById('light-run');
    const lightPause = document.getElementById('light-pause');
    const lightStop = document.getElementById('light-stop');
    const lightBuzzer = document.getElementById('light-buzzer-off');
    const lightEstop = document.getElementById('light-estop');

    // Reset all lights
    lightPower.className = 'control-light';
    lightRun.className = 'control-light';
    lightPause.className = 'control-light';
    lightStop.className = 'control-light';
    lightBuzzer.className = 'control-light';
    lightEstop.className = 'control-light';

    // Power On light: active when power_on is true
    if (state.power_on) {
        lightPower.classList.add('active-power');
    }

    // Button indicator lamps driven by IET opcodes (IESEL, IERUN, IEPAU, IEFAI, etc.)
    const bl = state.button_lamps || {};
    if (bl.run) {
        lightRun.classList.add('active-run');
    }
    if (bl.pause) {
        lightPause.classList.add('active-pause');
    }
    if (bl.stop) {
        lightStop.classList.add('active-stop');
    }
    if (bl.buzzer) {
        lightBuzzer.classList.add('active-buzzer');
    }

    // Emergency Exit light: active when estop_pressed is true
    if (state.estop_pressed) {
        lightEstop.classList.add('active-estop');
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
    renderQueryStatus(state, (CONFIG.mode === 'mock1' || CONFIG.mode === 'mock2') ? 'mock' : 'connected');
    renderCommandLog();
    renderCycleLabel(state);

    // Save state for blink-on-change detection in next render cycle
    previousState = state;
}

// ============================================
// Mode Toggle
// ============================================

function setMode(mode) {
    // Tear down Mock 2 if leaving it
    if (CONFIG.mode === 'mock2' && mode !== 'mock2') {
        Mock2Engine.destroy();
    }

    CONFIG.mode = mode;

    // Toggle body class for mock2-specific CSS overrides (e.g., white camera flash)
    document.body.classList.toggle('mock2-mode', mode === 'mock2');

    // Update button styles (3 buttons)
    document.getElementById('btn-mock1').classList.toggle('active', mode === 'mock1');
    document.getElementById('btn-mock2').classList.toggle('active', mode === 'mock2');
    document.getElementById('btn-live').classList.toggle('active', mode === 'live');

    // Show/hide API URL input
    document.getElementById('api-url').classList.toggle('visible', mode === 'live');

    // Reset state
    lastSeenCommand = null;
    commandLog = [];
    currentMockIndex = 0;

    // Update connection status
    if (mode === 'mock1' || mode === 'mock2') {
        renderConnectionStatus('mock');
    } else {
        renderConnectionStatus('connected');
    }

    // Initialize Mock 2 engine when entering that mode
    if (mode === 'mock2') {
        Mock2Engine.init();
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
 * @param {string} opcode - One of RUN, PAU, STP, BOF, PWRON, EMEXI
 * @param {string} buttonId - DOM id of the button that was clicked
 */
async function sendControlCommand(opcode, buttonId) {
    if (CONFIG.mode === 'mock1') return; // no-op in mock1 mode

    const btn = document.getElementById(buttonId);
    if (!btn || btn.disabled) return;

    // In mock2 mode, route to Mock2Engine
    if (CONFIG.mode === 'mock2') {
        Mock2Engine.handleButton(opcode);
        return;
    }

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
        if (btn && CONFIG.mode !== 'mock1') {
            btn.disabled = false;
        }
    }, 500);
}

/**
 * Enable or disable all control buttons based on current mode.
 * In mock1 mode, buttons are disabled and greyed out.
 * In mock2 and live mode, buttons are enabled.
 */
function updateControlButtonsDisabled() {
    const isMock1 = CONFIG.mode === 'mock1';
    const buttons = ['btn-power', 'btn-run', 'btn-pause', 'btn-stop', 'btn-buzzer-off', 'btn-estop'];
    buttons.forEach(id => {
        const btn = document.getElementById(id);
        if (btn) {
            btn.disabled = isMock1;
            btn.classList.toggle('mock-disabled', isMock1);
        }
    });
}

/**
 * onclick handler wired from HTML buttons.
 * Maps opcode to button ID and delegates to sendControlCommand.
 */
function onControlClick(opcode) {
    const opcodeToButton = {
        'PWRON': 'btn-power',
        'RUN': 'btn-run',
        'PAU': 'btn-pause',
        'STP': 'btn-stop',
        'BOF': 'btn-buzzer-off',
        'EMEXI': 'btn-estop'
    };
    const buttonId = opcodeToButton[opcode];
    if (buttonId) {
        sendControlCommand(opcode, buttonId);
    }
}

/**
 * onclick handler for clickable sensor rows (sag sensors, proximity sensors).
 * Sends a placeholder opcode to the API and triggers a blink on the indicator.
 * Backend handlers for these opcodes will be added later.
 *
 * Placeholder opcodes:
 *   STTU = Sag Toggle Top Upper
 *   STTL = Sag Toggle Top Lower
 *   STBU = Sag Toggle Bottom Upper
 *   STBL = Sag Toggle Bottom Lower
 *   PTST = Proximity Toggle Sensor Top
 *   PTSB = Proximity Toggle Sensor Bottom
 *
 * @param {string} opcode - Placeholder opcode to send
 * @param {string} indicatorId - DOM id of the indicator element to blink
 */
async function onSensorClick(opcode, indicatorId) {
    if (CONFIG.mode === 'mock1' || CONFIG.mode === 'mock2') return;

    const indicator = document.getElementById(indicatorId);
    if (!indicator) return;

    // Trigger blink animation
    indicator.classList.add('blink');
    indicator.addEventListener('animationend', () => {
        indicator.classList.remove('blink');
    }, { once: true });

    // Send command to API (will return FLS until backend handlers are added)
    try {
        const url = document.getElementById('api-url').value || CONFIG.apiUrl;
        await fetch(url + '/api/command', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ command: opcode }),
            signal: AbortSignal.timeout(2000)
        });
    } catch (e) {
        console.error(`Sensor command ${opcode} error:`, e);
    }
}

// ============================================
// Polling Loop
// ============================================

function startPolling() {
    if (CONFIG.mode === 'mock1') {
        // Mock 1: cycle through pre-baked states at mockCycleInterval
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
    } else if (CONFIG.mode === 'mock2') {
        // Mock 2: poll Mock2Engine state at mock2PollInterval
        // Note: command log is updated by Mock2Engine's log callback (setLogCallback),
        // NOT by updateCommandLog(), because auto-transitions happen faster than polls
        // and updateCommandLog's dedup would miss intermediate commands.
        mockTimer = setInterval(() => {
            const state = Mock2Engine.getState();
            if (state) {
                renderAll(state);
            }
        }, CONFIG.mock2PollInterval);

        // Render initial state immediately
        const initState = Mock2Engine.getState();
        if (initState) {
            renderAll(initState);
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

    // Load mock states for Mock 1 (available for manual switch)
    await loadMockStates();

    // Set up Mock 2 log callback so transitions appear in command log
    Mock2Engine.setLogCallback((command) => {
        const now = new Date();
        const timeStr = now.toLocaleTimeString('en-US', {
            hour12: false,
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        }) + '.' + String(now.getMilliseconds()).padStart(3, '0');

        commandLog.unshift({ time: timeStr, command: command });
        if (commandLog.length > CONFIG.maxLogEntries) {
            commandLog.pop();
        }
    });

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
