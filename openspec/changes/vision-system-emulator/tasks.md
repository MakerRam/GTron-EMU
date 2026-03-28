## 1. Project Setup

- [x] 1.1 Create Python project structure (firmware_emulator/)
- [x] 1.2 Initialize git repo and add .gitignore
- [x] 1.3 Create requirements.txt with pyserial dependency
- [x] 1.4 Create README.md with setup and usage instructions
- [x] 1.5 Set up logging configuration (Python logging module)
- [x] 1.6 Create config parser for Machine Interface Parameters.json

## 2. Device State Machine (Core)

- [x] 2.1 Implement DeviceState class with all state attributes (guide, reeler, sensors, encoders, lamps, cameras, door, estop)
- [x] 2.2 Implement GuideState dataclass (position, moving, reached_limit, target_position)
- [x] 2.3 Implement ReelerState dataclass (speed, teeth, running, position)
- [x] 2.4 Implement SensorState dataclass (attached, powered, triggered)
- [x] 2.5 Implement EncoderState dataclass (initialized, enabled, position, initial_angle, teeth_count)
- [x] 2.6 Implement CameraState dataclass (flags dict, active_sequence, timestamp_enabled)
- [x] 2.7 Implement state reset and serialization methods
- [x] 2.8 Create unit tests for state transitions

## 3. Opcode Parser and Handler Framework

- [ ] 3.1 Create OpcodeHandler base class with dispatch mechanism
- [ ] 3.2 Parse incoming 5-byte buffer into opcode string
- [ ] 3.3 Create opcode mapping from Machine Interface Parameters.json
- [ ] 3.4 Implement error handling for unknown opcodes (return "FLS")
- [ ] 3.5 Create handler function template/base class
- [ ] 3.6 Implement logging of all commands and responses

## 4. Core Command Handlers (Phase 1)

- [ ] 4.1 Implement QUERY handler → "YES" response
- [ ] 4.2 Implement EMSTP handler → "MP1"/"MP0" based on estop state
- [ ] 4.3 Implement DOORC handler → "DL1"/"DL0" based on door lock state
- [ ] 4.4 Implement tpLSC handler → "tpOL1"/"tpOL0" based on limit switch state
- [ ] 4.5 Implement tpGOP handler (guide open) → set state, delay 2000ms, return "tpGOR"
- [ ] 4.6 Implement tpGCL handler (guide close) → set state, delay 2000ms, return "tpGCR"
- [ ] 4.7 Implement tpATS handler (attach sensor top) → set sensor_top.attached = true
- [ ] 4.8 Implement tpDTS handler (detach sensor top) → set sensor_top.attached = false
- [ ] 4.9 Implement POS01-08 handlers (sensor power on) → set sensor power state
- [ ] 4.10 Implement PFS01-08 handlers (sensor power off) → clear sensor power state

## 5. Camera Sequence Handlers

- [ ] 5.1 Implement LCS01-07 handlers (light-camera sequences) → trigger virtual camera
- [ ] 5.2 Implement LCSI0-6 handlers (camera sequence flags) → set camera flags in state
- [ ] 5.3 Implement TSENB handler (timestamp enable) → set timestamp flag
- [ ] 5.4 Implement LCStp handler (all top cameras) → trigger all top sequences
- [ ] 5.5 Implement LCSbm handler (all bottom cameras) → trigger all bottom sequences

## 6. Lamp and Indicator Handlers

- [ ] 6.1 Implement TRED1/0 handlers (tower lamp red)
- [ ] 6.2 Implement TYEL1/0 handlers (tower lamp yellow)
- [ ] 6.3 Implement TGRN1/0 handlers (tower lamp green)
- [ ] 6.4 Implement TBZR1/0 handlers (buzzer)
- [ ] 6.5 Implement solenoid handlers (SOLON/SOLOF)

## 7. Reeler and Encoder Handlers

- [ ] 7.1 Implement tpRTR handler (rotate reeler)
- [ ] 7.2 Implement tpRSP handler (reeler speed set) → parse speed parameter
- [ ] 7.3 Implement tpRTH handler (reeler teeth) → parse teeth parameter
- [ ] 7.4 Implement tpSTR handler (start reeler) → set reeler_top.running = true
- [ ] 7.5 Implement tpSTP handler (stop reeler) → set reeler_top.running = false
- [ ] 7.6 Implement tpENI handler (encoder initialize top)
- [ ] 7.7 Implement tpEEN handler (encoder enable top) → set encoder enabled flag
- [ ] 7.8 Implement tpEDB handler (encoder disable top) → clear encoder enabled flag
- [ ] 7.9 Implement tpINA handler (encoder initial angle) → parse angle parameter
- [ ] 7.10 Create stubs for bottom rack equivalents (bmRTR, bmRSP, etc.)

## 8. Serial Communication (Virtual COM Port)

- [ ] 8.1 Install and configure com0com on Windows (manual step, document in README)
- [ ] 8.2 Create SerialBridge class using pyserial
- [ ] 8.3 Implement serial port open/close logic
- [ ] 8.4 Implement 5-byte read from COM port
- [ ] 8.5 Implement response write to COM port
- [ ] 8.6 Add serial error handling (timeout, disconnection, corruption)
- [ ] 8.7 Test LabVIEW connection to virtual COM port (manual test)

## 9. Main Emulator Loop

- [ ] 9.1 Create EmulatorEngine class
- [ ] 9.2 Implement main event loop (read → parse → handle → respond → update state)
- [ ] 9.3 Implement command timeout logic (discard incomplete buffer after 5s)
- [ ] 9.4 Add structured logging of every cycle
- [ ] 9.5 Implement graceful shutdown on Ctrl+C
- [ ] 9.6 Add statistics tracking (commands/sec, response time, etc.)

## 10. Virtual Camera Module (Phase 1)

- [ ] 10.1 Create VirtualCamera class
- [ ] 10.2 Implement synthetic image generation (simple test pattern)
- [ ] 10.3 Create image buffer/queue for LabVIEW acquisition
- [ ] 10.4 Implement frame metadata (timestamp, trigger count, camera ID)
- [ ] 10.5 Stub interface for IMAQDX integration (detailed in Phase 2)
- [ ] 10.6 Test: Verify emulator can signal camera and retrieve frame

## 11. Event Simulator (Phase 1 Stub)

- [ ] 11.1 Create EventSimulator class
- [ ] 11.2 Implement sensor trigger simulation (debounce logic)
- [ ] 11.3 Create encoder position tracking
- [ ] 11.4 Stub async trigger generation (detailed in Phase 2)
- [ ] 11.5 Implement command-triggered trigger (for manual testing)

## 12. Configuration and Initialization

- [ ] 12.1 Parse Machine Interface Parameters.json at startup
- [ ] 12.2 Extract delay values (TimingUnitSetup, etc.)
- [ ] 12.3 Extract opcode definitions
- [ ] 12.4 Create config object accessible to all handlers
- [ ] 12.5 Validate config (warn if missing critical values)

## 13. Testing and Validation

- [ ] 13.1 Write unit tests for DeviceState transitions
- [ ] 13.2 Write unit tests for each opcode handler
- [ ] 13.3 Write integration test: LabVIEW QUERY → YES handshake
- [ ] 13.4 Write integration test: Guide open/close command sequence
- [ ] 13.5 Write integration test: Camera trigger and frame capture
- [ ] 13.6 Create test script for manual testing (send predefined commands)
- [ ] 13.7 Test with actual LabVIEW application (manual, documented in test plan)

## 14. Documentation

- [ ] 14.1 Write setup.md (com0com installation, Python environment, pyserial)
- [ ] 14.2 Write usage.md (starting emulator, configuring LabVIEW serial port, troubleshooting)
- [ ] 14.3 Create opcode reference document (all 70+ opcodes, responses, examples)
- [ ] 14.4 Document device state machine architecture
- [ ] 14.5 Create developer guide for adding new opcodes
- [ ] 14.6 Write architecture overview diagram/document

## 15. Phase 1 Completion and Review

- [ ] 15.1 Create test plan document (manual tests, LabVIEW integration tests)
- [ ] 15.2 Run full test suite (unit + integration)
- [ ] 15.3 Verify all Phase 1 tasks completed
- [ ] 15.4 Demo: Run LabVIEW against emulator successfully
- [ ] 15.5 Prepare Phase 2 roadmap document
- [ ] 15.6 Code review and cleanup (naming, comments, error handling)

## 16. Phase 2 Planning (Future)

- [ ] 16.1 Document trigger simulation design (sensor ISRs, encoder counting)
- [ ] 16.2 Design motor movement timing model (acceleration, ramping)
- [ ] 16.3 Design IMAQDX virtual camera integration
- [ ] 16.4 Design system visualizer architecture
- [ ] 16.5 Design deterministic test replay system
- [ ] 16.6 Create Phase 2 implementation tasks based on feedback
