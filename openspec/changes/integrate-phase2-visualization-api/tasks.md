## 1. API Layer Implementation

- [x] 1.1 Copy state_export.py from Test-repository to firmware_emulator/src/
- [x] 1.2 Copy api_server.py from Test-repository to firmware_emulator/src/
- [x] 1.3 Update imports in state_export.py: `from device_state import` → `from firmware_emulator.src.device_state import`
- [x] 1.4 Update imports in api_server.py: `from state_export import` → `from firmware_emulator.src.state_export import`
- [x] 1.5 Create firmware_emulator/requirements.txt with: pyserial, flask, flask-cors, pytest
- [x] 1.6 Run `pip install -r firmware_emulator/requirements.txt` to verify dependencies install

## 2. Emulator Integration

- [x] 2.1 Modify firmware_emulator/src/main.py to import StateExporter and APIServer
- [x] 2.2 Add StateExporter instantiation in EmulatorEngine.__init__ (after dispatcher)
- [x] 2.3 Add APIServer instantiation in EmulatorEngine.__init__ with port parameter
- [x] 2.4 Ensure API server starts in background thread (already handled by APIServer.start())
- [x] 2.5 Add command-line argument parsing for --api-port (optional, default 5000)
- [x] 2.6 Add command-line argument parsing for --no-api flag (optional, disables API)
- [x] 2.7 Update console output to show "API server started on port X" when enable_api=True

## 3. Testing - Existing Test Suite

- [x] 3.1 Run `pytest firmware_emulator/tests/test_device_state.py -v` (verify 100% pass)
- [x] 3.2 Run `pytest firmware_emulator/tests/test_command_parser.py -v` (verify 100% pass)
- [x] 3.3 Run `pytest firmware_emulator/tests/test_opcode_dispatcher.py -v` (verify 100% pass)
- [x] 3.4 Run `pytest firmware_emulator/tests/ -v` (full suite, must all pass)
- [x] 3.5 Document test results (count, any failures, timing)

## 4. Testing - API Layer

- [x] 4.1 Copy test_state_export.py from Test-repository to firmware_emulator/tests/
- [x] 4.2 Copy test_api_server.py from Test-repository to firmware_emulator/tests/
- [x] 4.3 Update imports in test files to use absolute paths
- [x] 4.4 Run `pytest firmware_emulator/tests/test_state_export.py -v` (verify 100% pass)
- [x] 4.5 Run `pytest firmware_emulator/tests/test_api_server.py -v` (verify 100% pass)
- [x] 4.6 Document test results and coverage

## 5. Testing - Manual API Verification

- [ ] 5.1 Start emulator: `python firmware_emulator/src/main.py --port COM3` (or virtual port)
- [ ] 5.2 Test health endpoint: `curl http://localhost:5000/health` (expect JSON response)
- [ ] 5.3 Test full state endpoint: `curl http://localhost:5000/api/state` (expect JSON with all fields)
- [ ] 5.4 Test summary endpoint: `curl http://localhost:5000/api/state/summary` (expect compact JSON <150 bytes)
- [ ] 5.5 Send a command via serial (QUERY, TPGOP, etc) and verify state updates via API
- [ ] 5.6 Verify response times: /health <5ms, /state/summary <20ms, /state <100ms
- [ ] 5.7 Stop emulator and verify API becomes unreachable (connection refused)

## 6. Visualizer Integration

- [x] 6.1 Copy visualizer/ directory from Test-repository to project root
- [x] 6.2 Verify visualizer/index.html exists and is readable
- [x] 6.3 Verify visualizer/app.js, styles.css, mock_states.json exist
- [x] 6.4 Open visualizer/index.html in browser (file:// URL or via http server)
- [x] 6.5 Verify Mock mode works: states cycle every 500ms, UI updates smoothly
- [x] 6.6 Verify Live mode works: toggle to Live, connect to http://localhost:5000

## 7. Testing - Visualizer with Running Emulator

- [ ] 7.1 Start emulator on COM3 (or virtual port)
- [ ] 7.2 Open visualizer/index.html in Chrome or Firefox
- [ ] 7.3 Toggle Live mode (LIVE button)
- [ ] 7.4 Verify "Connected" status appears (green dot)
- [ ] 7.5 Send serial command (QUERY via LabVIEW or serial monitor)
- [ ] 7.6 Verify visualizer updates within 100ms
- [ ] 7.7 Verify command log shows new command
- [ ] 7.8 Stop emulator and verify "Disconnected" appears
- [ ] 7.9 Restart emulator and verify auto-reconnect works

## 8. Testing - Visualizer Features

- [ ] 8.1 Verify Guide Motors panel shows position bars and status text
- [ ] 8.2 Verify Reeler Motors panel shows speed gauges and position
- [ ] 8.3 Verify Sag Sensors panel shows 4 sensors with color coding (green/red)
- [ ] 8.4 Verify Tower Lamp panel shows RGB lamp states
- [ ] 8.5 Verify Cameras panel shows 7 camera flags and active sequence
- [ ] 8.6 Verify System Status panel shows door, E-stop, power, last command
- [ ] 8.7 Verify Command Log shows last 20 commands with timestamps
- [ ] 8.8 Verify Mock/Live toggle switches modes without errors
- [ ] 8.9 Verify API URL input field allows custom endpoints (test with 192.168.x.x)

## 9. Cross-browser Testing

- [ ] 9.1 Test visualizer in Google Chrome (latest)
- [ ] 9.2 Test visualizer in Mozilla Firefox (latest)
- [ ] 9.3 Test visualizer in Safari (if macOS available)
- [ ] 9.4 Verify layout renders correctly on all browsers
- [ ] 9.5 Verify no console errors in browser DevTools
- [ ] 9.6 Verify responsive design works on 1920x1080, 1366x768, iPad landscape

## 10. Integration Testing with LabVIEW

- [ ] 10.1 Start emulator with API enabled
- [ ] 10.2 Open LabVIEW application and connect to serial port (COM3 or virtual)
- [ ] 10.3 Open visualizer in browser and toggle to Live mode
- [ ] 10.4 Execute LabVIEW command: QUERY (handshake)
- [ ] 10.5 Verify visualizer updates correctly
- [ ] 10.6 Execute LabVIEW command: TPGOP (open guide)
- [ ] 10.7 Verify visualizer shows guide_top.position = "moving" then "open"
- [ ] 10.8 Execute camera sequence commands (LCS01, etc)
- [ ] 10.9 Verify visualizer shows camera flags activating
- [ ] 10.10 Run extended sequence of commands and verify timeline consistency

## 11. Performance Testing

- [ ] 11.1 Monitor emulator CPU usage while API polls: should be <5% additional
- [ ] 11.2 Monitor memory usage: should remain stable after 10min of polling
- [ ] 11.3 Measure API response time under load: send 100 requests, check latency
- [ ] 11.4 Verify serial communication latency unchanged: measure before/after API
- [ ] 11.5 Verify no commands are lost or delayed due to API activity

## 12. Documentation

- [x] 12.1 Document API endpoints in README: /health, /api/state, /api/state/summary
- [x] 12.2 Document state JSON schema with example responses
- [x] 12.3 Document visualizer usage: how to open, mock vs live modes, API URL configuration
- [x] 12.4 Document deployment options: same machine, network, Docker (future)
- [x] 12.5 Create quick-start guide: "Get visualization up in 5 minutes"
- [x] 12.6 Add troubleshooting section: common issues and solutions
- [x] 12.7 Document CORS configuration and security considerations

## 13. Code Review

- [x] 13.1 Review all code changes for style consistency
- [x] 13.2 Verify no debug statements or print() calls left in code
- [x] 13.3 Verify all imports are correct and tested
- [x] 13.4 Verify no hardcoded values (use command-line args instead)
- [x] 13.5 Remove any test files or temporary scripts from repository
- [x] 13.6 Verify .gitignore includes: __pycache__/, *.pyc, .venv/, .pytest_cache/

## 14. Final Verification

- [ ] 14.1 Run full test suite one more time: `pytest firmware_emulator/tests/ -v`
- [ ] 14.2 Verify all 40+ Phase 1 tests pass (no new failures)
- [ ] 14.3 Verify all new API tests pass
- [ ] 14.4 Test emulator with --no-api flag (API disabled)
- [ ] 14.5 Test visualizer in mock mode (offline)
- [ ] 14.6 Test visualizer in live mode (connected to emulator)
- [ ] 14.7 Verify no warnings in emulator logs
- [ ] 14.8 Verify no errors in browser console

## 15. Git & Commit

- [x] 15.1 Add all new files to git: `git add firmware_emulator/src/state_export.py api_server.py visualizer/ requirements.txt`
- [x] 15.2 Add modified files: `git add firmware_emulator/src/main.py tests/`
- [x] 15.3 Create commit with message: "feat: add Phase 2 visualization API and dashboard"
- [x] 15.4 Push to develop branch: `git push origin develop`
- [ ] 15.5 Create pull request against master branch for review

## 16. Handoff & Archive

- [ ] 16.1 Create summary of all changes for release notes
- [ ] 16.2 Verify all artifacts from openspec are complete and committed
- [ ] 16.3 Run `openspec status --change "integrate-phase2-visualization-api"` (should show complete)
- [ ] 16.4 Archive change: `openspec archive "integrate-phase2-visualization-api"`
- [ ] 16.5 Update main specs if needed (sync any delta specs to openspec/specs/)
- [ ] 16.6 Commit all documentation and closed artifacts
