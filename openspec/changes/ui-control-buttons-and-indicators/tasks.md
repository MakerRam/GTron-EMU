## 1. Phase 1A: UI - Control Buttons Panel (HTML/CSS only)

- [x] 1.1 Add "Emulator Control" panel HTML to `visualizer/index.html` with Run, Pause, Stop, Buzzer Off buttons and status light dots
- [x] 1.2 Add CSS styles for control buttons panel in `visualizer/styles.css` (button colors: Run=green, Pause=yellow, Stop=red, Buzzer Off=blue; status light dot styles matching existing indicator pattern)
- [x] 1.3 Add `renderControlButtons(state)` function in `visualizer/app.js` that reads `run_state` and `buzzer_override` from state and updates status lights (green/yellow/red/grey)
- [x] 1.4 Wire `renderControlButtons` into `renderAll()` function call chain

## 2. Phase 1B: UI - Query Status Indicator in Header

- [x] 2.1 Add query status indicator HTML to the header bar in `visualizer/index.html` (between cycle-label and connection-status divs): dot + "QRY" label
- [x] 2.2 Add CSS styles for query status indicator in `visualizer/styles.css` (green=OK, red=FAIL, grey=disconnected)
- [x] 2.3 Add `renderQueryStatus(state)` function in `visualizer/app.js` that reads `query_responsive` field and updates dot color and label text
- [x] 2.4 Wire `renderQueryStatus` into `renderAll()` and handle disconnected fallback (grey/QRY --)

## 3. Phase 1C: UI - Camera Light Indicators

- [x] 3.1 Add 6 light indicator HTML elements (L1-L6) below the camera grid inside `#panel-cameras` in `visualizer/index.html`
- [x] 3.2 Add CSS styles for light indicators in `visualizer/styles.css` (reuse `.cam-dot` pattern with green glow for on, grey for off)
- [x] 3.3 Add `renderLightChannels(state)` function in `visualizer/app.js` that reads `light_channels` object and toggles active class on L1-L6 dots
- [x] 3.4 Wire `renderLightChannels` into `renderAll()` function

## 4. Phase 1D: Mock Data Update

- [x] 4.1 Update `visualizer/mock_states.json` to include `run_state`, `buzzer_override`, `query_responsive`, and `light_channels` fields in all 10 mock states
- [x] 4.2 Verify mock mode cycles through new UI elements correctly (manual browser test)

## 5. Phase 2A: Backend - DeviceState Extensions

- [x] 5.1 Add `RunState` enum (RUNNING, PAUSED, STOPPED) to `firmware_emulator/src/device_state.py`
- [x] 5.2 Add `run_state`, `buzzer_override`, `query_responsive`, and `light_channels` fields to `DeviceState.__init__()` with safe defaults
- [x] 5.3 Update `DeviceState.to_dict()` to serialize new fields (run_state as string, light_channels as dict)
- [x] 5.4 Update `DeviceState.reset()` to reset new fields to defaults
- [x] 5.5 Write unit tests for new DeviceState fields (default values, serialization, reset)

## 6. Phase 2B: Backend - State Export & API

- [x] 6.1 Update `StateExporter.export_summary()` in `firmware_emulator/src/state_export.py` to include `run_state`, `buzzer_override`, `query_responsive`, `light_channels`
- [x] 6.2 Verify `GET /api/state` response includes new fields (automatic via `to_dict()` pipeline)
- [x] 6.3 Write integration test: `GET /api/state` returns new fields with correct defaults

## 7. Phase 2C: Backend - Opcode Handlers

- [x] 7.1 Register `EMRUN` opcode handler in `firmware_emulator/src/opcode_handler.py` that sets `run_state=RUNNING` and returns `EMROK`
- [x] 7.2 Register `EMPAU` opcode handler that sets `run_state=PAUSED` and returns `EMPOK`
- [x] 7.3 Register `EMSTP` opcode handler that sets `run_state=STOPPED` and returns `EMSOK`
- [x] 7.4 Register `BZZOF` opcode handler that sets `buzzer_override=True` and returns `BZZOK`
- [x] 7.5 Write unit tests for all 4 new opcode handlers (state transitions, response values)

## 8. Phase 3: Full Integration - Button Click Handlers

- [x] 8.1 Add `sendControlCommand(opcode)` function in `visualizer/app.js` that sends `POST /api/command` with the opcode and handles success/error
- [x] 8.2 Wire button `onclick` handlers to call `sendControlCommand` with appropriate opcodes (EMRUN, EMPAU, EMSTP, BZZOF)
- [x] 8.3 Add click debounce: disable button for 500ms after click, re-enable on next successful state poll
- [x] 8.4 Disable control buttons in mock mode (grey out, no-op on click)
- [x] 8.5 End-to-end test: click Run button -> verify state changes to RUNNING -> verify status light turns green

## 9. Phase 3B: Polish & Verification

- [x] 9.1 Run all existing tests (`pytest firmware_emulator/tests/`) to verify no regressions
- [x] 9.2 Manual browser test: verify all 3 new UI features (control buttons, query status, light indicators) work in both mock and live modes
- [x] 9.3 Verify control button status lights update correctly when polling live state
