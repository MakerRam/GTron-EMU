## Context

The vision system is an in-line gauging tool for automotive parts (stamped/formed) at ~1200 parts/minute. It consists of:
- **LabVIEW Application**: Existing, unmodifiable vision processing and device control application
- **Arduino Firmware** (TimeMachine V4.2): Controls guide motors (actuators for part width), reeler motors (pull parts at rated speed), trigger mechanisms (encoder or sensor based), and light-camera sequences
- **Physical Hardware**: Stepper motor drivers, encoders, limit switches, IR sensors, tower lamps, solenoid valves, 6 cameras with lights (Top/Side/Front for 2 racks)

The firmware communicates via serial UART at 9600 baud using 5-byte ASCII opcodes. LabVIEW uses IMAQDX to acquire images when triggered. The system lacks a testing/validation environment without physical hardware.

## Goals / Non-Goals

**Goals (Phase 1):**
- Enable LabVIEW to run and communicate with emulated firmware via serial
- Correctly emulate all 70+ firmware opcodes with accurate state transitions and response timing
- Simulate light-camera sequences (timing, triggers, flags) to enable LabVIEW image acquisition
- Simulate front panel operations (buttons, lamps, states) as LabVIEW expects
- Monitor part sag position sensor states for sag control logic
- Load and deliver pre-captured images from local folder via IMAQDX (Top Rack cameras only: Top, Side, Front)
- Create foundation for future phases (trigger simulation, motor control, visualizer, multi-rack support)
- Maintain architectural clarity: firmware emulator as core, camera as plugin, visualizer deferred

**Non-Goals (Phase 1):**
- Synthetic image generation (use folder-based images instead)
- Detailed motor movement timing simulation (respond to requests, no physics)
- Encoder-based trigger generation (Phase 2+)
- 2D visualizer UI (Phase 2+)
- Test replay/recording system (Phase 2+)
- Bottom Rack support (Phase 2+)
- Multi-part scenario simulation (Phase 2+)

## Decisions

### 1. Python-Based Emulator with pyserial
**Decision**: Implement firmware emulator in Python using `pyserial` for serial communication via com0com virtual COM ports.

**Rationale**: Python provides rapid prototyping, platform compatibility, and easy integration with external tools. pyserial is industry-standard for serial communication. com0com (Windows) creates true virtual COM ports that LabVIEW sees as real devices without modification.

**Alternatives Considered**:
- C++ DLL: More performant but complex build/deployment
- TCP socket wrapper: Requires LabVIEW configuration change (rejected—user requires COM port)
- USB HID emulation: Over-complex for this use case

### 2. State Machine Architecture
**Decision**: Device state is immutable, command-driven. Each opcode transitions state and generates response. No polling or background threads modify state (except event simulators).

**Rationale**: Deterministic—same command sequence always produces same state. Easier to test and replay. Clear cause-effect relationship between LabVIEW commands and device behavior.

**Alternatives Considered**:
- Event-driven with background threads: More realistic but harder to debug/replay
- Continuous polling of hardware: Not applicable to virtual environment

### 3. Modular Architecture
**Decision**: Four independent modules: (a) firmware emulator, (b) virtual camera, (c) event simulator, (d) visualizer. Each can be upgraded/replaced independently.

**Rationale**: Supports incremental enhancement. Camera and visualizer can be improved without rewriting firmware logic. Clean interfaces between modules.

### 4. Synchronous Command-Response (Phase 1)
**Decision**: Each command produces an immediate response. Timing simulations use simple delays (config-driven). No background ISR simulation in Phase 1.

**Rationale**: Simplest to implement and test. Sufficient for LabVIEW polling workflows. Phase 2 can add asynchronous event generation.

**Alternatives Considered**:
- Async interrupt simulation: More realistic but requires threading/event queues
- Real-time kernel: Overkill for validation environment

### 5. Configuration-Driven Timing
**Decision**: All delays (motor movement, camera exposure, sensor debounce) sourced from `Machine Interface Parameters.json`. Firmware behavior is parameterizable.

**Rationale**: Supports different machine variants without code changes. Matches real firmware (which reads MI JSON).

### 6. Image Loading from Folder (Phase 1)
**Decision**: Virtual camera loads pre-captured images from a local folder instead of generating synthetic images.

**Rationale**: Eliminates complexity of image synthesis in Phase 1. Real test images provide better fidelity. Folder-based approach is simple and extensible.

**Alternatives Considered**:
- Synthetic image generation: More complex, requires image libs, Phase 1 image quality is arbitrary
- Hard-coded test patterns: Less realistic, less flexible
- Real-time camera feed capture: Over-complex for validation environment

### 7. Camera Scope: Top Rack Only (Phase 1)
**Decision**: Phase 1 supports only Top Rack cameras (Top, Side, Front). Bottom Rack deferred to Phase 2.

**Rationale**: Reduces Phase 1 scope significantly. Top Rack is primary inspection path. Bottom Rack adds 50% more code with similar logic. Easy to duplicate in Phase 2.

### 8. Light-Camera Sequence Simulation
**Decision**: Firmware emulator simulates light-camera sequence timing (light on/off delays, camera trigger pulse, flag states).

**Rationale**: LabVIEW relies on proper sequence timing. Must match real firmware behavior. Drives image acquisition flow.

### 9. Part Sag Position Monitoring
**Decision**: Emulator tracks sag sensor states (upper/lower for each rack) and responds to sag sensor queries.

**Rationale**: Critical for LabVIEW logic that monitors part width and sag position. Must be simulated for complete workflow testing.

### 10. Front Panel Simulation
**Decision**: Emulator tracks and responds to front panel button states, tower lamp colors, door lock, and E-stop.

**Rationale**: LabVIEW queries these states during operation. Proper responses required for realistic workflow.

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| **com0com driver unavailable/unstable** | Use open-source nullserial or similar; test extensively before deployment |
| **Image folder missing or corrupted** | Provide default test images; validate folder on startup with helpful errors |
| **Light-camera sequence timing complex** | Study firmware LightCam_Sequence.ino carefully; implement delay states correctly |
| **Timing precision (microseconds) not achievable** | Acceptable: Python/Windows can't guarantee µs precision; LabVIEW uses polling (millisecond tolerances) |
| **State explosion if tracking 100s of parameters** | Mitigate: Focus only on essential state (guide, sensors, camera flags, sag, lamps); defer complex state to Phase 2+ |
| **Opcode parser maintenance burden** | Mitigate: Auto-generate parser from MI JSON; keep opcode handlers simple |

## Migration Plan

**Phase 1 (Current)**:
1. Build firmware emulator with opcode parser and all 70+ command handlers
2. Integrate pyserial + com0com for serial communication
3. Simulate light-camera sequences (timing, flags, triggering)
4. Simulate front panel (buttons, lamps, door lock, E-stop)
5. Simulate part sag monitoring (sensor states)
6. Load pre-captured images from local folder via virtual camera (Top Rack only)
7. Manual testing: verify LabVIEW connects, issues commands, acquires images

**Phase 2**:
1. Add Bottom Rack support (cameras 4/5/6)
2. Implement reeler motor timing simulation
3. Implement encoder-based trigger generation
4. Add deterministic trigger simulation (debounce, sequencing)
5. Create 2D realistic visualizer UI
6. Implement test scenario recording and replay

**Phase 3+**:
1. Advanced motor movement simulation (acceleration, ramping)
2. Complex sag position logic and monitoring
3. Multi-part scenario generation and replay
4. Stress testing (high-frequency triggers)
5. CI/CD integration

## Open Questions

1. **Image Folder Structure**: How should pre-captured images be organized in the folder? By camera name? Numbered? Format (JPG/PNG)?
   - Action: Define folder structure and naming convention
   
2. **Light-Camera Sequence Timing**: What are the exact delays in the light-camera sequences (LIGHT_ONDELAY, CAMERA_ONDELAY, etc.)?
   - Action: Extract from firmware code and Machine Interface Parameters.json

3. **Part Sag Position Thresholds**: What are the upper/lower limits for sag sensor detection? How do they relate to part width?
   - Action: Review firmware Sag_Logic.ino and sag sensor configuration

4. **com0com Robustness**: Are there known stability issues or Windows version incompatibilities?
   - Action: Test on target Windows versions before deployment
   
5. **LabVIEW Test Plan**: What constitutes successful Phase 1 completion? Should we create test LabVIEW scripts?
   - Action: Clarify acceptance criteria with user after design review
