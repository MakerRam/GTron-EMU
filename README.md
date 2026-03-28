# Vision System Firmware Emulator

A comprehensive emulator for the GTRON vision system firmware that allows LabVIEW applications to validate against virtualized hardware without requiring physical equipment.

## Overview

This emulator implements the complete firmware API (70+ opcodes) over a virtual COM port, enabling:
- Full communication protocol compliance (5-byte ASCII at 9600 baud)
- Device state machine with realistic command handling
- Virtual camera simulation with frame capture
- Sensor and encoder simulation
- Light-camera sequence timing
- Integration with LabVIEW via IMAQDX-compatible interface

## Phase 1 Scope

- **Firmware API**: All opcode handlers (device readiness, sensors, light-camera, lamps, motors, encoders)
- **Serial Communication**: Virtual COM port via com0com, pyserial transport
- **Virtual Camera**: Synthetic image generation with metadata (timestamp, trigger count, camera ID)
- **Device State**: Immutable state machine with command-driven transitions
- **Configuration**: Machine Interface Parameters.json parsing
- **Top Rack Only**: 3 cameras (Top, Side, Front); Bottom Rack deferred to Phase 2

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Virtual COM Port (Windows)

Download and install **com0com**:
1. Go to https://sourceforge.net/projects/com0com/
2. Install the latest stable release
3. Run `DevCon.exe` to create a virtual port pair (e.g., COM1 ↔ COM2)
4. Configure LabVIEW to connect to one port; the emulator will connect to the other

### 3. Verify Setup

```bash
python src/main.py --help
```

## Usage

### Starting the Emulator

```bash
python src/main.py --port COM3 --config Machine\ Interface\ Parameters.json
```

### Running Tests

```bash
# Unit tests
pytest tests/

# Integration test (emulator must be running)
python tests/integration_test.py
```

### LabVIEW Integration

1. Connect LabVIEW serial port to the virtual COM port (paired with emulator port)
2. Send `QUERY` → emulator responds `YES`
3. All subsequent commands follow the protocol defined in Machine Interface Parameters.json

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
