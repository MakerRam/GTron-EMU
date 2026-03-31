# C4 Level 3: Component Diagram - Emulator Core

## Firmware Emulator Internal Architecture

> **Purpose**: Breaks open the Emulator Process container to show its internal components and their interactions.

---

## Component Diagram

```mermaid
C4Component
    title Component Diagram - Emulator Core (firmware_emulator/src/)

    Container_Boundary(emulator, "Firmware Emulator Process") {

        Component(engine, "EmulatorEngine", "main.py", "Main event loop: orchestrates read-parse-dispatch-respond cycle. Entry point for the entire system")

        Component(serial, "SerialBridge", "serial_bridge.py", "Low-level COM port I/O via pyserial. Read 5-byte commands, write responses. Timeout and error handling")

        Component(parser, "CommandParser", "command_parser.py", "Stateless converter: raw bytes -> opcode string. Strips nulls, validates 5-byte format")

        Component(dispatcher, "OpcodeDispatcher", "opcode_handler.py", "Routes opcode strings to registered handlers. Unknown opcodes return FLS (fail)")

        Component(handlers, "OpcodeHandlers", "opcode_handlers.py", "75 handler functions across 8 categories: device readiness, sensors, motors, cameras, lamps, encoders, interrupts, machine control")

        Component(state, "DeviceState", "device_state.py", "Immutable state object: guides, reelers, sensors, encoders, cameras, lamps, system status. Command-driven transitions")

        Component(camera, "VirtualCamera", "virtual_camera.py", "Synthetic image generation from pre-loaded PNGs. Frame metadata: timestamp, trigger count, camera ID")

        Component(config, "ConfigParser", "config_parser.py", "Parses Machine Interface Parameters.json. Provides opcode definitions, timing delays, camera-light mappings")

        Component(logging, "LoggingConfig", "logging_config.py", "Structured logging to 4 files: emulator, serial, commands, debug. Timestamp and context for every transaction")

        Component(monitor, "SerialMonitor", "serial_monitor.py", "Console output for --verbose, --hex, --debug modes. Real-time command/response display")

        Component(exporter, "StateExporter", "state_export.py", "Converts DeviceState to JSON dicts. Enum serialization, metadata injection. Used by API layer")
    }

    Rel(engine, serial, "Reads commands, writes responses")
    Rel(engine, parser, "Passes raw bytes for parsing")
    Rel(engine, dispatcher, "Sends parsed opcode for routing")
    Rel(engine, logging, "Logs every transaction")
    Rel(engine, monitor, "Outputs to console if --verbose")

    Rel(dispatcher, handlers, "Routes to specific handler")
    Rel(handlers, state, "Reads current state, returns new state")
    Rel(handlers, camera, "Triggers frame capture on LCS opcodes")

    Rel(engine, config, "Loads at startup")
    Rel(dispatcher, config, "Reads opcode registry and timing")

    Rel(exporter, state, "Reads state for JSON conversion")
```

---

## Component Responsibilities

### EmulatorEngine (`main.py`)
```
Entry Point - Orchestrates the entire system

┌─────────────────────────────────────────┐
│  def run():                             │
│    config = ConfigParser.load(json)     │
│    serial = SerialBridge(COM3, 115200)  │
│    state = DeviceState()                │
│    dispatcher = OpcodeDispatcher(state) │
│    api = APIServer(StateExporter(state))│
│    api.start_daemon_thread()            │
│                                         │
│    while running:                       │
│      bytes = serial.read_command()      │
│      opcode = parser.parse(bytes)       │
│      response = dispatcher.dispatch()   │
│      serial.write_response(response)    │
│      logger.log(opcode, response)       │
└─────────────────────────────────────────┘
```

### OpcodeHandlers - 75 Commands in 8 Categories

| Category | Opcodes | Example | Response |
|----------|---------|---------|----------|
| Device Readiness | QUERY, SMINI, RSTSM | QUERY | YES |
| Guide Motors | tpGOP, tpGCL, btGOP, btGCL | tpGOP | tpGOR (2s delay) |
| Reeler Motors | tpRLR, tpRST, btRLR, btRST | tpRLR | tpROK |
| Cameras | LCS01, LCS02, LCS03 | LCS01 | LCS1 + frame |
| Tower Lamps | TLRED, TLGRN, TLBLU, TLOFF | TLRED | TLROK |
| Sag Sensors | tSSUP, tSSLO, bSSUP, bSSLO | tSSUP | sensor state |
| Encoders | tpENC, btENC, TSENB | tpENC | encoder value |
| Machine Control | DLCKD, ESTOP, PWRON | DLCKD | door state |

### DeviceState - Immutable State Machine

```
┌──────────────────────────────────────────────────┐
│  DeviceState (Immutable - new object per change) │
│                                                  │
│  Motors:                                         │
│  ├─ guide_top:    GuideState {position, moving}  │
│  ├─ guide_bottom: GuideState {position, moving}  │
│  ├─ reeler_top:   ReelerState {speed, direction} │
│  └─ reeler_bottom:ReelerState {speed, direction} │
│                                                  │
│  Sensors:                                        │
│  ├─ sag_top_upper/lower:    bool                 │
│  ├─ sag_bottom_upper/lower: bool                 │
│  ├─ encoder_top/bottom:     EncoderState         │
│  └─ sensor_top/bottom:      SensorState          │
│                                                  │
│  Output:                                         │
│  ├─ lamps: LampState {red, yellow, green, buzz}  │
│  └─ cameras: CameraState {flags[0-6], sequence}  │
│                                                  │
│  System:                                         │
│  ├─ door_locked, estop_pressed, power_on: bool   │
│  ├─ last_command: str                            │
│  └─ last_command_time: float (epoch)             │
│                                                  │
│  Design Pattern: Command -> new state object     │
│  Thread Safety: GIL protects dict reads          │
└──────────────────────────────────────────────────┘
```

---

## File Map

```
firmware_emulator/src/
├── main.py              → EmulatorEngine (entry point, event loop)
├── serial_bridge.py     → SerialBridge (COM port I/O)
├── command_parser.py    → CommandParser (bytes -> opcode string)
├── opcode_handler.py    → OpcodeDispatcher (routing registry)
├── opcode_handlers.py   → 75 opcode handler functions
├── device_state.py      → DeviceState (immutable state machine)
├── virtual_camera.py    → VirtualCamera (image generation)
├── config_parser.py     → ConfigParser (JSON config loader)
├── logging_config.py    → LoggingConfig (4 log files setup)
├── serial_monitor.py    → SerialMonitor (--verbose console)
├── state_export.py      → StateExporter (state -> JSON)
├── api_server.py        → APIServer (Flask REST, see diagram 04)
└── debug_breakpoint.py  → DebugBreakpoint (--debug mode)
```

---

*C4 Level 3 - Emulator Components | Vision System Firmware Emulator | Zentron Projects*
