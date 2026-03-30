/* ============================================
   Mock 2 Engine - Interactive State Machine
   ============================================
   A self-contained state machine that generates dashboard state objects
   dynamically based on user button interactions and timed transitions.

   Phases:
     DEFAULT -> POWER_ON -> QUERY -> INIT_PERIPHERALS -> INIT_MOTORS
     -> GUIDE_OPEN -> GUIDE_CLOSE -> WAITING_FOR_RUN -> RUNNING
     Buttons: PAUSE -> PAUSED, RUN -> RUNNING (resume), STOP -> DEFAULT
     E-EXIT toggles EMERGENCY overlay on/off (saves & restores pre-emergency state)
   ============================================ */

const Mock2Engine = (() => {
    'use strict';

    // --- Phase enum ---
    const PHASE = {
        DEFAULT:          'DEFAULT',
        POWER_ON:         'POWER ON',
        QUERY:            'QUERY',
        INIT_PERIPHERALS: 'INIT PERIPHERALS',
        INIT_MOTORS:      'INIT MOTORS',
        GUIDE_OPEN:       'GUIDE OPEN',
        GUIDE_CLOSE:      'GUIDE CLOSE',
        WAITING_FOR_RUN:  'WAITING FOR RUN',
        RUNNING:          'RUNNING',
        PAUSED:           'PAUSED',
        EMERGENCY:        'EMERGENCY'
    };

    // --- Timing constants (ms) ---
    const TIMING = {
        powerToQuery:         200,
        queryToPeripherals:   100,
        peripheralsToMotors:  2000,
        motorBlinkInterval:   200,
        motorBlinkCount:      4,     // blinks before going solid
        guideOpenDuration:    5000,
        guideCloseDuration:   5000,
        cameraOnDuration:     100,
        cameraOffGap:         100,
        reelerTickInterval:   100    // how often reeler position increments
    };

    // --- Internal state ---
    let phase = PHASE.DEFAULT;
    let timers = [];          // all setTimeout/setInterval IDs for cleanup
    let cameraTimer = null;   // camera cycling interval
    let reelerTimer = null;   // reeler position counter
    let blinkTimer = null;    // motor init blink interval
    let guideTimer = null;    // guide animation interval

    // Snapshot saved before EMERGENCY so we can restore
    let preEmergencyPhase = null;
    let preEmergencyState = null;

    // Dynamic state fields
    let powerOn = false;
    let queryResponsive = false;
    let stampingRelay = false;
    let doorLocked = false;
    let estopPressed = false;
    let stepperInitialized = false;
    let reelerInitialized = false;
    let initBlinkOn = false;       // blink state for stepper/reeler init indicators

    let guideTopPosition = 'closed';    // 'closed' | 'moving' | 'open'
    let guideTopMoving = false;
    let guideBottomPosition = 'closed';
    let guideBottomMoving = false;

    let reelerTopRunning = false;
    let reelerTopSpeed = 0;
    let reelerTopPosition = 0;

    let sagTopLower = false;

    let cameraFlags = { '1': false, '2': false, '3': false, '4': false, '5': false, '6': false };
    let lightChannels = { '1': false, '2': false, '3': false, '4': false, '5': false, '6': false };
    let activeCameraIndex = 0;     // cycles 0,1,2 => cameras 1,2,3
    let activeSequence = -1;

    let lampsRed = false;
    let lampsYellow = false;
    let lampsGreen = false;
    let lampsBuzzer = false;

    let buttonLampRun = false;
    let buttonLampPause = false;
    let buttonLampStop = false;
    let buttonLampBuzzer = false;

    let lastCommand = null;

    // Command log callback (set by app.js)
    let _logCallback = null;

    // --- Helpers ---

    function scheduleTimeout(fn, delay) {
        const id = setTimeout(fn, delay);
        timers.push({ type: 'timeout', id });
        return id;
    }

    function scheduleInterval(fn, interval) {
        const id = setInterval(fn, interval);
        timers.push({ type: 'interval', id });
        return id;
    }

    function clearAllTimers() {
        timers.forEach(t => {
            if (t.type === 'timeout') clearTimeout(t.id);
            else clearInterval(t.id);
        });
        timers = [];
        cameraTimer = null;
        reelerTimer = null;
        blinkTimer = null;
        guideTimer = null;
    }

    function log(command) {
        lastCommand = command;
        if (_logCallback) _logCallback(command);
    }

    function resetAllFields() {
        powerOn = false;
        queryResponsive = false;
        stampingRelay = false;
        doorLocked = false;
        estopPressed = false;
        stepperInitialized = false;
        reelerInitialized = false;
        initBlinkOn = false;

        guideTopPosition = 'closed';
        guideTopMoving = false;
        guideBottomPosition = 'closed';
        guideBottomMoving = false;

        reelerTopRunning = false;
        reelerTopSpeed = 0;
        reelerTopPosition = 0;

        sagTopLower = false;

        cameraFlags = { '1': false, '2': false, '3': false, '4': false, '5': false, '6': false };
        lightChannels = { '1': false, '2': false, '3': false, '4': false, '5': false, '6': false };
        activeCameraIndex = 0;
        activeSequence = -1;

        lampsRed = false;
        lampsYellow = false;
        lampsGreen = false;
        lampsBuzzer = false;

        buttonLampRun = false;
        buttonLampPause = false;
        buttonLampStop = false;
        buttonLampBuzzer = false;

        lastCommand = null;
        preEmergencyPhase = null;
        preEmergencyState = null;
    }

    // --- Phase transitions ---

    function enterDefault() {
        clearAllTimers();
        resetAllFields();
        phase = PHASE.DEFAULT;
        log('RESET');
    }

    function enterPowerOn() {
        phase = PHASE.POWER_ON;
        powerOn = true;
        log('PWRON');

        // Auto-advance to QUERY after 200ms
        scheduleTimeout(() => enterQuery(), TIMING.powerToQuery);
    }

    function enterQuery() {
        phase = PHASE.QUERY;
        queryResponsive = true;
        log('QUERY');

        // Auto-advance to INIT_PERIPHERALS after 100ms
        scheduleTimeout(() => enterInitPeripherals(), TIMING.queryToPeripherals);
    }

    function enterInitPeripherals() {
        phase = PHASE.INIT_PERIPHERALS;
        stampingRelay = true;
        doorLocked = true;
        estopPressed = false;
        lampsYellow = true;
        lampsRed = false;
        lampsGreen = false;
        log('STMON');

        // Auto-advance to INIT_MOTORS after 2000ms
        scheduleTimeout(() => enterInitMotors(), TIMING.peripheralsToMotors);
    }

    function enterInitMotors() {
        phase = PHASE.INIT_MOTORS;
        log('SMINI');

        // Blink stepper/reeler init indicators
        let blinkCount = 0;
        initBlinkOn = false;

        blinkTimer = scheduleInterval(() => {
            initBlinkOn = !initBlinkOn;
            // If blink is ON, show as initialized; if OFF, show as not
            stepperInitialized = initBlinkOn;
            reelerInitialized = initBlinkOn;
            blinkCount++;

            if (blinkCount >= TIMING.motorBlinkCount * 2) {
                // Done blinking - go solid ON
                clearInterval(blinkTimer);
                stepperInitialized = true;
                reelerInitialized = true;
                initBlinkOn = false;
                log('RMINI');

                // Advance to guide open
                scheduleTimeout(() => enterGuideOpen(), 200);
            }
        }, TIMING.motorBlinkInterval);
    }

    function enterGuideOpen() {
        phase = PHASE.GUIDE_OPEN;
        lampsRed = true;
        lampsYellow = false;
        lampsGreen = false;

        guideTopPosition = 'moving';
        guideTopMoving = true;
        // Bottom guide stays closed throughout Mock 2
        log('GOPN1');

        // After guideOpenDuration, top guide fully open -> start closing
        guideTimer = scheduleTimeout(() => {
            guideTopPosition = 'open';
            guideTopMoving = false;
            log('GOPN1');  // guide reached open limit

            // Brief pause then start closing
            scheduleTimeout(() => enterGuideClose(), 500);
        }, TIMING.guideOpenDuration);
    }

    function enterGuideClose() {
        phase = PHASE.GUIDE_CLOSE;

        guideTopPosition = 'moving';
        guideTopMoving = true;
        // Bottom guide stays closed throughout Mock 2
        log('GCLS1');

        guideTimer = scheduleTimeout(() => {
            guideTopPosition = 'closed';
            guideTopMoving = false;
            log('GCLS1');  // guide reached closed limit

            // Advance to waiting for RUN
            scheduleTimeout(() => enterWaitingForRun(), 200);
        }, TIMING.guideCloseDuration);
    }

    function enterWaitingForRun() {
        phase = PHASE.WAITING_FOR_RUN;
        lampsRed = true;
        lampsYellow = false;
        lampsGreen = false;
        log('IESEL');   // Select state - waiting for operator
    }

    function enterRunning() {
        phase = PHASE.RUNNING;

        // Button lamps
        buttonLampRun = true;
        buttonLampPause = false;
        buttonLampStop = false;

        // Tower lamp GREEN
        lampsRed = false;
        lampsYellow = false;
        lampsGreen = true;

        // X Flow: sag top lower ON, reeler top running
        sagTopLower = true;
        reelerTopRunning = true;
        reelerTopSpeed = 500;
        log('RUN');

        // Reeler position counter
        reelerTimer = scheduleInterval(() => {
            reelerTopPosition += Math.round(reelerTopSpeed * (TIMING.reelerTickInterval / 1000));
        }, TIMING.reelerTickInterval);

        // Y Flow: camera cycling (cameras 1-3 with lights)
        // Start after 400ms delay
        scheduleTimeout(() => startCameraCycle(), 400);
    }

    function startCameraCycle() {
        if (phase !== PHASE.RUNNING) return;

        activeCameraIndex = 0;
        cameraCycleStep();
    }

    function cameraCycleStep() {
        if (phase !== PHASE.RUNNING) return;

        const camNum = activeCameraIndex + 1; // 1, 2, or 3

        // Turn ON camera + light
        cameraFlags = { '1': false, '2': false, '3': false, '4': false, '5': false, '6': false };
        lightChannels = { '1': false, '2': false, '3': false, '4': false, '5': false, '6': false };
        cameraFlags[String(camNum)] = true;
        lightChannels[String(camNum)] = true;
        activeSequence = camNum;

        // After cameraOnDuration, turn OFF
        cameraTimer = scheduleTimeout(() => {
            cameraFlags[String(camNum)] = false;
            lightChannels[String(camNum)] = false;
            activeSequence = -1;

            // After cameraOffGap, advance to next camera (or loop)
            cameraTimer = scheduleTimeout(() => {
                activeCameraIndex = (activeCameraIndex + 1) % 3;
                cameraCycleStep();
            }, TIMING.cameraOffGap);
        }, TIMING.cameraOnDuration);
    }

    function stopXYFlows() {
        // Stop camera cycling - clear all camera/light timers
        // We need to clear only the camera-related and reeler timers
        // Since we can't selectively clear, we track and cancel carefully
        // Actually, the camera cycle uses scheduleTimeout which adds to timers[]
        // We'll just stop advancing by checking phase in cameraCycleStep

        // Stop reeler
        reelerTopRunning = false;
        reelerTopSpeed = 0;
        if (reelerTimer) {
            clearInterval(reelerTimer);
            reelerTimer = null;
        }

        // Reset cameras and lights
        cameraFlags = { '1': false, '2': false, '3': false, '4': false, '5': false, '6': false };
        lightChannels = { '1': false, '2': false, '3': false, '4': false, '5': false, '6': false };
        activeSequence = -1;
        sagTopLower = false;
    }

    function enterPaused() {
        phase = PHASE.PAUSED;
        stopXYFlows();

        // Button lamps
        buttonLampRun = false;
        buttonLampPause = true;
        buttonLampStop = false;

        // Tower lamp YELLOW
        lampsRed = false;
        lampsYellow = true;
        lampsGreen = false;

        log('PAU');
    }

    function enterEmergency() {
        // Save current state snapshot for restore
        preEmergencyPhase = phase;
        preEmergencyState = {
            lampsRed, lampsYellow, lampsGreen, lampsBuzzer,
            buttonLampRun, buttonLampPause, buttonLampStop, buttonLampBuzzer,
            reelerTopRunning, reelerTopSpeed, sagTopLower,
            cameraFlags: { ...cameraFlags },
            lightChannels: { ...lightChannels },
            activeSequence
        };

        // Stop active flows
        stopXYFlows();

        phase = PHASE.EMERGENCY;
        estopPressed = true;
        lampsRed = true;
        lampsYellow = false;
        lampsGreen = false;
        lampsBuzzer = true;
        buttonLampRun = false;
        buttonLampPause = false;
        buttonLampStop = false;
        buttonLampBuzzer = true;

        log('EMEXI');
    }

    function exitEmergency() {
        if (!preEmergencyPhase || !preEmergencyState) {
            // No saved state, go to default
            enterDefault();
            return;
        }

        phase = preEmergencyPhase;
        estopPressed = false;
        lampsBuzzer = false;
        buttonLampBuzzer = false;

        // Restore pre-emergency visual state
        const s = preEmergencyState;
        lampsRed = s.lampsRed;
        lampsYellow = s.lampsYellow;
        lampsGreen = s.lampsGreen;
        lampsBuzzer = s.lampsBuzzer;
        buttonLampRun = s.buttonLampRun;
        buttonLampPause = s.buttonLampPause;
        buttonLampStop = s.buttonLampStop;
        buttonLampBuzzer = s.buttonLampBuzzer;

        preEmergencyPhase = null;
        preEmergencyState = null;

        log('EMEXI');  // E-EXIT clear

        // If we were in RUNNING, restart X+Y flows
        if (phase === PHASE.RUNNING) {
            sagTopLower = true;
            reelerTopRunning = true;
            reelerTopSpeed = 500;

            reelerTimer = scheduleInterval(() => {
                reelerTopPosition += Math.round(reelerTopSpeed * (TIMING.reelerTickInterval / 1000));
            }, TIMING.reelerTickInterval);

            scheduleTimeout(() => startCameraCycle(), 400);
        }
    }

    // --- Public API ---

    /**
     * Handle a button click in Mock 2 mode.
     * @param {string} opcode - PWRON, RUN, PAU, STP, EMEXI
     */
    function handleButton(opcode) {
        switch (opcode) {
            case 'PWRON':
                if (phase === PHASE.DEFAULT) {
                    enterPowerOn();
                } else if (phase !== PHASE.EMERGENCY) {
                    // Power toggle off -> reset to default
                    enterDefault();
                }
                break;

            case 'RUN':
                if (phase === PHASE.WAITING_FOR_RUN) {
                    enterRunning();
                } else if (phase === PHASE.PAUSED) {
                    // Resume
                    enterRunning();
                }
                break;

            case 'PAU':
                if (phase === PHASE.RUNNING) {
                    enterPaused();
                }
                break;

            case 'STP':
                if (phase !== PHASE.DEFAULT && phase !== PHASE.EMERGENCY) {
                    enterDefault();
                }
                break;

            case 'BOF':
                // Buzzer off - just clear buzzer
                lampsBuzzer = false;
                buttonLampBuzzer = false;
                log('BOF');
                break;

            case 'EMEXI':
                if (phase === PHASE.EMERGENCY) {
                    exitEmergency();
                } else if (phase !== PHASE.DEFAULT) {
                    enterEmergency();
                }
                break;

            default:
                // Ignore unknown opcodes
                break;
        }
    }

    /**
     * Build a complete state object matching the /api/state JSON shape.
     * Called by app.js polling loop to render the dashboard.
     */
    function getState() {
        return {
            _label: phase,
            guide_top: {
                position: guideTopPosition,
                moving: guideTopMoving,
                reached_limit: guideTopPosition === 'open'
            },
            guide_bottom: {
                position: guideBottomPosition,
                moving: guideBottomMoving,
                reached_limit: guideBottomPosition === 'open'
            },
            reeler_top: {
                speed: reelerTopSpeed,
                teeth: 48,
                running: reelerTopRunning,
                position: reelerTopPosition
            },
            reeler_bottom: {
                speed: 0,
                teeth: 48,
                running: false,
                position: 0
            },
            sensor_top: {
                attached: true,
                powered: powerOn,
                triggered: false
            },
            sensor_bottom: {
                attached: true,
                powered: powerOn,
                triggered: false
            },
            encoder_top: {
                initialized: stepperInitialized,
                enabled: stepperInitialized,
                position: reelerTopPosition,
                initial_angle: 0,
                teeth_count: stepperInitialized ? 48 : 0
            },
            encoder_bottom: {
                initialized: stepperInitialized,
                enabled: stepperInitialized,
                position: 0,
                initial_angle: 0,
                teeth_count: stepperInitialized ? 48 : 0
            },
            lamps: {
                red: lampsRed,
                yellow: lampsYellow,
                green: lampsGreen,
                buzzer: lampsBuzzer
            },
            cameras: {
                flags: { ...cameraFlags },
                active_sequence: activeSequence,
                timestamp_enabled: phase === PHASE.RUNNING
            },
            sag_top_upper: false,
            sag_top_lower: sagTopLower,
            sag_bottom_upper: false,
            sag_bottom_lower: false,
            solenoid_top: guideTopPosition !== 'closed',
            solenoid_bottom: false,
            stamping_relay: stampingRelay,
            stepper_initialized: stepperInitialized,
            reeler_initialized: reelerInitialized,
            door_locked: doorLocked,
            estop_pressed: estopPressed,
            power_on: powerOn,
            last_command: lastCommand,
            last_command_time: lastCommand ? Date.now() / 1000 : null,
            run_state: phase === PHASE.RUNNING ? 'running'
                     : phase === PHASE.PAUSED ? 'paused'
                     : phase === PHASE.DEFAULT ? 'stopped'
                     : 'running',
            buzzer_override: false,
            query_responsive: queryResponsive,
            light_channels: { ...lightChannels },
            button_lamps: {
                run: buttonLampRun,
                pause: buttonLampPause,
                stop: buttonLampStop,
                buzzer: buttonLampBuzzer
            }
        };
    }

    /**
     * Initialize / reset the engine. Called when entering Mock 2 mode.
     */
    function init() {
        clearAllTimers();
        resetAllFields();
        phase = PHASE.DEFAULT;
    }

    /**
     * Tear down the engine. Called when leaving Mock 2 mode.
     */
    function destroy() {
        clearAllTimers();
        resetAllFields();
        phase = PHASE.DEFAULT;
    }

    /**
     * Set callback for command log entries.
     * @param {function(string)} cb - called with opcode string on each transition
     */
    function setLogCallback(cb) {
        _logCallback = cb;
    }

    /**
     * Get current phase name.
     */
    function getPhase() {
        return phase;
    }

    // --- Expose public API ---
    return {
        handleButton,
        getState,
        init,
        destroy,
        setLogCallback,
        getPhase,
        PHASE
    };
})();
