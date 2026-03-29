## Why

The existing vision system requires physical hardware (cameras, controllers, stepper motors) to test and validate LabVIEW applications. This creates barriers to rapid development cycles, makes regression testing difficult, and prevents the software team from testing during hardware downtime or in offline environments. Building a comprehensive emulator allows the LabVIEW application to run, test, and validate against a completely virtualized environment—enabling faster iteration, better test coverage, and deterministic replay of complex machine behaviors.

## What Changes

- **Firmware API Emulation**: Replace real firmware communication with a Python-based emulator that responds to all opcodes with proper state management and timing.
- **Virtual Serial Communication**: Intercept LabVIEW's serial commands via a virtual COM port (com0com on Windows) that routes to the Python emulator.
- **Virtual Camera Module**: Provide IMAQDX-compatible virtual camera that loads pre-captured images from a local folder when triggered by firmware events (Top Rack cameras only).
- **Simulation Engine**: Core state machine that tracks device state and simulates light-camera sequences, front panel operations, and part sag position monitoring.
- **2D System Visualizer** (Phase 2+): Realistic 2D diagram showing machine state, actuator positions, and part positioning (deferred to Phase 2+).

## Capabilities

### New Capabilities

- `firmware-api-emulation`: Full opcode parser and command handler that emulates Arduino firmware behavior. Supports all 70+ opcodes with proper state transitions and response timing.
- `virtual-serial-com-port`: Windows com0com integration allowing LabVIEW to communicate with the emulator as if it were a real serial device.
- `virtual-camera-module`: IMAQDX-compatible camera that loads and delivers pre-captured images from local folder when triggered by firmware (Top Rack cameras: Top, Side, Front).
- `light-camera-sequence-simulation`: Simulates light-camera sequence timing, triggers, and responses (LCSI0-2, TSENB, LCS01-03, etc.).
- `front-panel-simulation`: Simulates front panel operations (buttons, lamps, tower lamp states, door lock, E-stop).
- `part-sag-position-monitoring`: Tracks part sag sensor states and monitors sag position limits (upper/lower sensors for part width control).
- `device-state-machine`: Tracks essential device state (guide positions, sensor attachment, camera flags, lamp states, sag sensor states).
- `system-visualizer-ui` (Phase 2+): 2D realistic visualization panel showing machine state, part positioning, actuator positions, and sag monitoring.

### Modified Capabilities

- No modifications to existing capabilities; this is purely additive.

## Impact

- **LabVIEW Application**: No changes required; it continues to use existing serial and IMAQDX APIs unchanged.
- **Project Structure**: Adds `/firmware_emulator/` directory with Python modules, configuration files, and documentation.
- **Development Workflow**: Developers can now run full system tests offline without hardware; CI/CD pipelines can validate firmware behavior deterministically.
- **Testing**: Enables unit testing of LabVIEW logic, integration testing of command sequences, and regression testing via replay.
- **Dependencies**: Requires `pyserial` (Python serial communication), `com0com` (Windows virtual COM port driver), and optionally `opencv` or PIL for image generation.
