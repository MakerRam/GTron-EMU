# Vision System Firmware Emulator

A comprehensive emulator for the GTRON vision system firmware that allows LabVIEW applications to validate against virtualized hardware without requiring physical equipment.

## Overview

This emulator implements the complete firmware API (61 opcodes) over a virtual COM port, enabling:
- Full communication protocol compliance (5-byte ASCII at 9600 baud)
- Device state machine with realistic command handling
- Virtual camera simulation with frame capture
- Sensor and encoder simulation
- Light-camera sequence timing
- Integration with LabVIEW via IMAQDX-compatible interface

## Phase 1 Scope

- **Firmware API**: All 61 opcode handlers (device readiness, sensors, light-camera, lamps, motors, encoders)
- **Serial Communication**: Virtual COM port via com0com, pyserial transport
- **Virtual Camera**: Synthetic image generation with metadata (timestamp, trigger count, camera ID)
- **Device State**: Immutable state machine with command-driven transitions
- **Configuration**: Machine Interface Parameters.json parsing
- **Top Rack Only**: 3 cameras (Top, Side, Front); Bottom Rack deferred to Phase 2

See **OPCODES_REFERENCE.md** for complete documentation of all 61 implemented opcodes.

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Virtual COM Port (Windows)

Download and install **com0com**:
1. Go to https://sourceforge.net/projects/com0com/
2. Install the latest stable release
3. Run `DevCon.exe` to create a virtual port pair (e.g., COM3 ↔ COM4)
   - Emulator connects to COM3
   - LabVIEW connects to COM4
4. Configure LabVIEW serial settings to COM4 (115200 baud, 8 data bits, no parity)

### 3. Verify Setup

```bash
python src/main.py --help
```

## Usage: Two-Terminal Workflow

### Terminal 1: Start Emulator (Backend Daemon)

```bash
# Basic startup (silently runs, logs to logs/ directory)
python3 firmware_emulator/src/main.py --port COM3

# With verbose output (see real-time commands/responses)
python3 firmware_emulator/src/main.py --port COM3 --verbose

# With hex protocol dump
python3 firmware_emulator/src/main.py --port COM3 --hex

# With debug breakpoints on specific opcodes
python3 firmware_emulator/src/main.py --port COM3 --debug tpGOP LCS01
```

### Terminal 2: Launch LabVIEW

```bash
# Open LabVIEW IDE or run compiled application
labview &

# In LabVIEW:
# 1. Configure serial port to COM4 (paired with emulator's COM3)
# 2. Click "Connect" or "Initialize Hardware"
# 3. App sends QUERY → emulator responds YES
# 4. Full communication begins automatically
```

### Monitoring Output Example

**Terminal 1 with --verbose:**
```
[2026-03-28 07:53:25.123] RECV: QUERY         → SEND: YES
[2026-03-28 07:53:26.045] RECV: tpGOP         → SEND: tpGOR [2000ms delay]
[2026-03-28 07:53:28.067] RECV: tpGCL         → SEND: tpGCR
[2026-03-28 07:53:28.234] RECV: LCS01         → CAMERA TRIGGER [id=0]
[2026-03-28 07:53:28.235] RECV: TSENB         → TIMESTAMP ENABLED
[2026-03-28 07:53:28.300] RECV: tpLSC         → SEND: tpOL1
```

**Logs Directory (automatic):**
```
logs/
├── emulator_20260328_075325.log     # Main events (startup, errors)
├── serial_20260328_075325.log       # Serial port events
├── commands_20260328_075325.log     # Every command with state before/after
└── debug_20260328_075325.log        # Detailed DEBUG-level messages
```

## Architecture

### Key Classes

- **DeviceState**: Immutable state object (guide, reeler, sensors, encoders, camera, lamps)
- **OpcodeHandler**: Dispatcher and handler registry for all firmware commands
- **SerialBridge**: Virtual COM port reader/writer with error handling
- **EmulatorEngine**: Main event loop (read → parse → handle → respond → update state)
- **VirtualCamera**: Synthetic image generation and frame metadata
- **EventSimulator**: Sensor triggers and encoder position tracking (Phase 2 expansion)
- **ConfigParser**: Machine Interface Parameters.json parser

### Design Patterns

- **Immutable State**: State objects never modified; handlers return new state
- **Command Dispatch**: Opcode → handler mapping, unknown opcodes → "FLS"
- **Structured Logging**: Every command and response logged with timestamp, context
- **Configuration-Driven**: All timing, delays, and opcode definitions from MI JSON

## Configuration

Edit `Machine Interface Parameters.json` to customize:
- **BaudRate**: 9600 (recommended)
- **DelayValuesInms**: Timing for various operations
- **CameraLightConfig**: Camera-to-light mappings
- **MachineInterfaceRecipeOpcodes**: All command definitions

## Troubleshooting

### Serial Port Not Found
- Verify com0com is installed and ports created
- Check Windows Device Manager for virtual ports
- Ensure no other application is using the port

### Timeout Errors
- Increase timeout in SerialBridge if network is slow
- Check LabVIEW serial configuration (baud rate, data bits, parity)

### Invalid Opcode Response
- Verify LabVIEW is sending 5-byte ASCII commands
- Check Machine Interface Parameters.json for opcode definitions
- Enable debug logging: `EMULATOR_LOG_LEVEL=DEBUG`

## Documentation

- **setup.md**: Detailed installation and configuration
- **usage.md**: Complete usage guide and examples
- **opcode_reference.md**: All 70+ opcodes with descriptions and examples
- **architecture.md**: System design and state machine
- **developer_guide.md**: Adding new opcodes and extending the emulator

## Testing Strategy

### Unit Tests
- State transitions (DeviceState)
- Each opcode handler in isolation
- Configuration parsing and validation

### Integration Tests
- LabVIEW QUERY → YES handshake
- Guide open/close command sequences
- Camera trigger and frame capture
- Multi-command sequences with state persistence

### Manual Tests
- LabVIEW application validation (documented in test_plan.md)
- Long-running stability tests
- Edge cases (timeouts, invalid commands, rapid sequences)

## Phase 2 Roadmap

- **Trigger Simulation**: ISR-driven sensor triggers, debounce logic
- **Motor Movement**: Guide motor ramping, position tracking, limit switch logic
- **Reeler Motor**: Speed-based stepping with encoder feedback
- **2D Visualizer**: Real-time device state visualization (not debugging interface)
- **Advanced Sequences**: Complex light-camera timing with multiple racks
- **Bottom Rack Support**: Independent simulation for second gauge

## Contributing

When adding new opcodes:
1. Add entry to Machine Interface Parameters.json
2. Create handler in `src/opcode_handlers.py`
3. Add unit test in `tests/test_opcode_handlers.py`
4. Document in `docs/opcode_reference.md`
5. Update `developer_guide.md` with examples

## License

Proprietary - Zentron Projects

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in `logs/` directory
3. Contact the development team

---

**Version**: 1.0-Phase1
**Last Updated**: March 2026
**Status**: Stable - Ready for LabVIEW Integration
