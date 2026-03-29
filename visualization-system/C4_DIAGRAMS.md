# C4 Architecture Diagrams - Vision System Visualizer

## C4 Model Overview

The C4 model (Context, Container, Component, Code) provides a hierarchical view of the system architecture.

---

## C4 Level 1: System Context Diagram

Shows the Vision System in its broader environment, with external systems it interacts with.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Vision System Context                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│                    ┌──────────────────────────────────────┐                │
│                    │        LabVIEW Application           │                │
│                    │     (Manufacturing Control)          │                │
│                    └────────────────┬─────────────────────┘                │
│                                     │                                      │
│                    ┌────────────────▼─────────────────────┐                │
│                    │  5-byte ASCII Serial Protocol         │                │
│                    │  (COM4 ↔ COM3 via com0com)          │                │
│                    └────────────────┬─────────────────────┘                │
│                                     │                                      │
│  ┌──────────────────────────────────▼──────────────────────────────────┐  │
│  │             Firmware Emulator (Backend)                             │  │
│  │             • Serial communication (COM3)                           │  │
│  │             • Opcode processing                                     │  │
│  │             • Device state management                               │  │
│  │             • HTTP API server (Port 5000)  [NEW]                   │  │
│  └──────────────────────────────────┬───────────────────────────────┬──┘  │
│                                      │                               │     │
│                    ┌─────────────────▼────────────────┐             │     │
│                    │    HTTP REST API                 │             │     │
│                    │ GET /api/state                   │             │     │
│                    │ GET /api/state/summary           │             │     │
│                    │ GET /health                      │             │     │
│                    └─────────────────┬────────────────┘             │     │
│                                      │                               │     │
│     ┌────────────────────────────────▼─────────────────────┐        │     │
│     │                                                       │        │     │
│     │    ┌──────────────────────────────────────────────┐  │        │     │
│     │    │    Visualization Systems [NEW]               │  │        │     │
│     │    │                                              │  │        │     │
│     │    │ Option 1: 2D Machine Diagram (Browser)      │  │        │     │
│     │    │ Option 2: Dashboard (Plotly Dash)           │  │        │     │
│     │    │ Option 3: Timeline Viewer                   │  │        │     │
│     │    │ Option 4: 3D Visualizer (Unity/Godot)       │  │        │     │
│     │    │ Option 5: Custom Implementation             │  │        │     │
│     │    │                                              │  │        │     │
│     │    │ All consume same HTTP API                    │  │        │     │
│     │    └──────────────────────────────────────────────┘  │        │     │
│     │                                                       │        │     │
│     │  (Separate repository/project - independent)         │        │     │
│     │                                                       │        │     │
│     └───────────────────────────────────────────────────────┘        │     │
│                                                                       │     │
│  ┌───────────────────────────────────────────────────────────────┐  │     │
│  │                    Logging System                              │  │     │
│  │  • logs/emulator_*.log (main events)                          │  │     │
│  │  • logs/serial_*.log (serial I/O)                            │  │     │
│  │  • logs/commands_*.log (all commands)                        │  │     │
│  │  • logs/debug_*.log (debug details)                          │  │     │
│  └───────────────────────────────────────────────────────────────┘  │     │
│                                                                       │     │
│  ┌───────────────────────────────────────────────────────────────┐  │     │
│  │              Virtual Camera Module                             │  │     │
│  │  • camera_images/top/ (12+ images)                           │  │     │
│  │  • camera_images/side/ (12+ images)                          │  │     │
│  │  • camera_images/front/ (12+ images)                         │  │     │
│  └───────────────────────────────────────────────────────────────┘  │     │
│                                                                       │     │
└─────────────────────────────────────┬───────────────────────────────┘     │
                                      │                                      │
                                      │                                      │
                                      ▼                                      │
                         (External systems)                                  │
                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘

Key Relationships:
• LabVIEW ↔ Emulator: Serial communication (COM3/COM4)
• Visualization ← Emulator: HTTP polling (GET /api/state every 100ms)
• Emulator writes: Logs to files, Camera images loaded from disk
```

---

## C4 Level 2: Container Diagram

Shows major containers and how they communicate.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                         Vision System Containers                            │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────┐                  │
│  │  Windows/WSL2 Machine (Single Process)              │                  │
│  ├──────────────────────────────────────────────────────┤                  │
│  │                                                      │                  │
│  │  ┌────────────────────────────────────────────────┐ │                  │
│  │  │  Emulator Container (Python Process)           │ │                  │
│  │  │  firmware_emulator/src/main.py                 │ │                  │
│  │  ├────────────────────────────────────────────────┤ │                  │
│  │  │                                                │ │                  │
│  │  │  Main Thread (Event Loop)                      │ │                  │
│  │  │  ┌──────────────────────────────────────────┐ │ │                  │
│  │  │  │ EmulatorEngine                           │ │ │                  │
│  │  │  │ • read_command() [blocking 1s timeout]   │ │ │                  │
│  │  │  │ • _process_command()                     │ │ │                  │
│  │  │  │ • write_response()                       │ │ │                  │
│  │  │  │ • _log_transaction()                     │ │ │                  │
│  │  │  │                                          │ │ │                  │
│  │  │  │ while running:                           │ │ │                  │
│  │  │  │   cmd = serial.read()                    │ │ │                  │
│  │  │  │   resp = dispatcher.dispatch(parse(cmd)) │ │ │                  │
│  │  │  │   serial.write(resp)                     │ │ │                  │
│  │  │  └──────────────────────────────────────────┘ │ │                  │
│  │  │           ▲                                   │ │                  │
│  │  │           │ references                       │ │                  │
│  │  │  ┌────────┴──────────────────────────────┐  │ │                  │
│  │  │  │ SerialBridge (COM3)                   │  │ │                  │
│  │  │  │ • read_command() → bytes              │  │ │                  │
│  │  │  │ • write_response(bytes) → bool        │  │ │                  │
│  │  │  │ • close()                             │  │ │                  │
│  │  │  └────────────────────────────────────────┘  │ │                  │
│  │  │                                                │ │                  │
│  │  │  ┌────────────────────────────────────────┐  │ │                  │
│  │  │  │ CommandParser                          │  │ │                  │
│  │  │  │ • parse(bytes) → str                  │  │ │                  │
│  │  │  │ • is_valid_command(bytes) → bool      │  │ │                  │
│  │  │  └────────────────────────────────────────┘  │ │                  │
│  │  │                                                │ │                  │
│  │  │  ┌────────────────────────────────────────┐  │ │                  │
│  │  │  │ OpcodeDispatcher                       │  │ │                  │
│  │  │  │ • dispatch(str) → bytes                │  │ │                  │
│  │  │  │ • device_state (reference)             │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  │ Router:                                │  │ │                  │
│  │  │  │  QUERY → HandshakeHandler → "YES"     │  │ │                  │
│  │  │  │  LCS01-03 → CameraHandlers → images   │  │ │                  │
│  │  │  │  Others → Placeholder handlers        │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  └────────┬───────────────────────────────┘  │ │                  │
│  │  │           │                                  │ │                  │
│  │  │           ▼                                  │ │                  │
│  │  │  ┌────────────────────────────────────────┐  │ │                  │
│  │  │  │ DeviceState (Immutable)                │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  │ Motors:                                │  │ │                  │
│  │  │  │ • guide_top, guide_bottom              │  │ │                  │
│  │  │  │ • reeler_top, reeler_bottom            │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  │ Sensors:                               │  │ │                  │
│  │  │  │ • sag_top_upper/lower                  │  │ │                  │
│  │  │  │ • sag_bottom_upper/lower               │  │ │                  │
│  │  │  │ • encoder_top, encoder_bottom          │  │ │                  │
│  │  │  │ • sensor_top, sensor_bottom            │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  │ Lamps/Status:                          │  │ │                  │
│  │  │  │ • lamps (red, yellow, green, buzzer)   │  │ │                  │
│  │  │  │ • cameras (7 flags)                    │  │ │                  │
│  │  │  │ • door_locked, estop_pressed           │  │ │                  │
│  │  │  │ • power_on                             │  │ │                  │
│  │  │  │ • last_command, last_command_time      │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  │ Methods:                               │  │ │                  │
│  │  │  │ • to_dict() → Dict[str, Any]           │  │ │                  │
│  │  │  │ • to_json() → str                      │  │ │                  │
│  │  │  │ • reset()                              │  │ │                  │
│  │  │  │ • log_command(str)                     │  │ │                  │
│  │  │  └────────┬───────────────────────────────┘  │ │                  │
│  │  │           │                                  │ │                  │
│  │  │           │ (NEW) reads state                │ │                  │
│  │  │           ▼                                  │ │                  │
│  │  │  ┌────────────────────────────────────────┐  │ │                  │
│  │  │  │ StateExporter (NEW)                    │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  │ __init__(device_state)                 │  │ │                  │
│  │  │  │ get_state_dict() → Dict                │  │ │                  │
│  │  │  │ get_state_json() → str                 │  │ │                  │
│  │  │  │ export_summary() → Dict (compact)      │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  └────────┬───────────────────────────────┘  │ │                  │
│  │  │           │                                  │ │                  │
│  │  │           │ (NEW) provides state              │ │                  │
│  │  │           ▼                                  │ │                  │
│  │  │  ┌────────────────────────────────────────┐  │ │                  │
│  │  │  │ APIServer (NEW) - Flask HTTP Server    │  │ │                  │
│  │  │  │ Port: 5000 (configurable)              │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  │ Routes:                                │  │ │                  │
│  │  │  │ ├─ GET /api/state                      │  │ │                  │
│  │  │  │ │  └─ returns exporter.get_state_dict()│  │ │                  │
│  │  │  │ ├─ GET /api/state/summary              │  │ │                  │
│  │  │  │ │  └─ returns exporter.export_summary()│  │ │                  │
│  │  │  │ └─ GET /health                         │  │ │                  │
│  │  │  │    └─ returns {status, api_version}    │  │ │                  │
│  │  │  │                                        │  │ │                  │
│  │  │  │ Features:                              │  │ │                  │
│  │  │  │ • CORS headers enabled                 │  │ │                  │
│  │  │  │ • JSON responses                       │  │ │                  │
│  │  │  │ • Error handling (HTTP 500)            │  │ │                  │
│  │  │  │ • Runs in daemon thread                │  │ │                  │
│  │  │  └────────┬───────────────────────────────┘  │ │                  │
│  │  │           │                                  │ │                  │
│  │  │           │ (HTTP Port 5000)                 │ │                  │
│  │  │           │                                  │ │                  │
│  │  │  Background Thread (HTTP):                  │ │                  │
│  │  │  ┌────────▼──────────────────────────────┐ │ │                  │
│  │  │  │ Flask WSGI Server                     │ │ │                  │
│  │  │  │ • Thread pool (default 4 threads)     │ │ │                  │
│  │  │  │ • Handles HTTP requests               │ │ │                  │
│  │  │  │ • Thread-safe reads from DeviceState  │ │ │                  │
│  │  │  │ • Does NOT block serial loop          │ │ │                  │
│  │  │  └────────────────────────────────────────┘ │ │                  │
│  │  │                                                │ │                  │
│  │  └────────────────────────────────────────────────┘ │                  │
│  │                                                      │                  │
│  │  File System (Disk I/O)                             │                  │
│  │  ┌────────────────────────────────────────────────┐ │                  │
│  │  │ logs/                                          │ │                  │
│  │  │ ├─ emulator_TIMESTAMP.log                     │ │                  │
│  │  │ ├─ serial_TIMESTAMP.log                       │ │                  │
│  │  │ ├─ commands_TIMESTAMP.log                     │ │                  │
│  │  │ └─ debug_TIMESTAMP.log                        │ │                  │
│  │  │                                                │ │                  │
│  │  │ firmware_emulator/camera_images/               │ │                  │
│  │  │ ├─ top/ (12 pre-loaded PNG images)            │ │                  │
│  │  │ ├─ side/ (12 pre-loaded PNG images)           │ │                  │
│  │  │ └─ front/ (12 pre-loaded PNG images)          │ │                  │
│  │  │                                                │ │                  │
│  │  │ Machine Interface Parameters.json              │ │                  │
│  │  └────────────────────────────────────────────────┘ │                  │
│  │                                                      │                  │
│  └──────────────────────────────────────────────────────┘                  │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘

Data Flow (Concurrent):
1. Main Thread: Serial I/O loop (continuous)
2. HTTP Thread: Handles API requests (on demand, 100ms intervals typically)
3. Both access shared DeviceState (thread-safe via Python GIL)
```

---

## C4 Level 3: Component Diagram (Emulator Side)

Detailed breakdown of components within EmulatorEngine.

```
┌────────────────────────────────────────────────────────────────────────────┐
│  EmulatorEngine Container - Internal Components                           │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  SERIAL COMMUNICATION LAYER                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ SerialBridge (existing)                                              │ │
│  │                                                                      │ │
│  │ Responsibility: Low-level COM port I/O                             │ │
│  │                                                                      │ │
│  │ Interface:                                                           │ │
│  │ ├─ __init__(port: str, baudrate: int=9600, timeout: float=1.0)    │ │
│  │ ├─ read_command() → bytes | None                                   │ │
│  │ ├─ write_response(bytes: bytes) → bool                             │ │
│  │ ├─ close() → None                                                  │ │
│  │ └─ is_open() → bool                                                │ │
│  │                                                                      │ │
│  │ Internals:                                                           │ │
│  │ ├─ self.serial (pyserial Serial object)                            │ │
│  │ ├─ Timeout handling (1 second default)                             │ │
│  │ ├─ Error logging                                                   │ │
│  │ └─ Context manager support                                         │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│           ▲                                                                │
│           │ reads/writes 5-byte commands/responses                        │
│           │                                                                │
│  COMMAND PARSING LAYER                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ CommandParser (existing)                                             │ │
│  │                                                                      │ │
│  │ Responsibility: Convert 5-byte ASCII to opcode string               │ │
│  │                                                                      │ │
│  │ Interface:                                                           │ │
│  │ ├─ @staticmethod parse(cmd_bytes: bytes) → str                     │ │
│  │ │  └─ "QUERY\0" → "QUERY"                                          │ │
│  │ └─ @staticmethod is_valid_command(bytes) → bool                    │ │
│  │    └─ Must be exactly 5 bytes                                       │ │
│  │                                                                      │ │
│  │ Internals:                                                           │ │
│  │ ├─ Decode ASCII, strip nulls                                        │ │
│  │ ├─ No state (stateless)                                             │ │
│  │ └─ Simple string operations                                         │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│           ▲                                                                │
│           │ routes opcode to handler                                      │
│           │                                                                │
│  OPCODE HANDLING LAYER                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ OpcodeDispatcher (existing)                                          │ │
│  │                                                                      │ │
│  │ Responsibility: Route opcodes to appropriate handlers                │ │
│  │                                                                      │ │
│  │ Interface:                                                           │ │
│  │ ├─ __init__()                                                       │ │
│  │ ├─ dispatch(opcode: str) → bytes                                    │ │
│  │ └─ device_state (DeviceState reference)                             │ │
│  │                                                                      │ │
│  │ Internals:                                                           │ │
│  │ ├─ self.handlers (Dict[str, OpcodeHandler])                         │ │
│  │ │  ├─ "QUERY" → HandshakeHandler()                                  │ │
│  │ │  ├─ "SMINI" → CommunicationBoardConfigHandler()                  │ │
│  │ │  ├─ "LCS01" → CameraPlaceholderHandler()                          │ │
│  │ │  ├─ "LCS02" → CameraPlaceholderHandler()                          │ │
│  │ │  └─ "LCS03" → CameraPlaceholderHandler()                          │ │
│  │ │                                                                    │ │
│  │ ├─ Routing logic:                                                    │ │
│  │ │  if opcode in handlers:                                           │ │
│  │ │    handler.handle() → response bytes                              │ │
│  │ │  else:                                                             │ │
│  │ │    return b'FLS' (fail)                                           │ │
│  │ │                                                                    │ │
│  │ └─ Opcode handlers:                                                  │ │
│  │    • OpcodeHandler (abstract base)                                   │ │
│  │    • HandshakeHandler: QUERY → YES                                   │ │
│  │    • CameraPlaceholderHandler: LCS0* → LCS1                         │ │
│  │    • More handlers added in Phase 2                                  │ │
│  │                                                                      │ │
│  └────────────┬──────────────────────────────────────────────────────────┘ │
│               │                                                             │
│               │ reads/modifies device state                                │
│               ▼                                                             │
│  STATE MANAGEMENT LAYER                                                   │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ DeviceState (existing)                                               │ │
│  │                                                                      │ │
│  │ Responsibility: Track complete immutable device state                │ │
│  │                                                                      │ │
│  │ Structure:                                                           │ │
│  │ ├─ Motor States:                                                     │ │
│  │ │  ├─ guide_top: GuideState                                         │ │
│  │ │  ├─ guide_bottom: GuideState                                      │ │
│  │ │  ├─ reeler_top: ReelerState                                       │ │
│  │ │  └─ reeler_bottom: ReelerState                                    │ │
│  │ │                                                                    │ │
│  │ ├─ Sensor States:                                                    │ │
│  │ │  ├─ sensor_top, sensor_bottom: SensorState                        │ │
│  │ │  ├─ encoder_top, encoder_bottom: EncoderState                     │ │
│  │ │  ├─ sag_top_upper/lower: bool                                     │ │
│  │ │  └─ sag_bottom_upper/lower: bool                                  │ │
│  │ │                                                                    │ │
│  │ ├─ Lamp States:                                                      │ │
│  │ │  └─ lamps: LampState (red, yellow, green, buzzer: bool)          │ │
│  │ │                                                                    │ │
│  │ ├─ Camera States:                                                    │ │
│  │ │  └─ cameras: CameraState (flags[0-6], active_sequence, ts_en)    │ │
│  │ │                                                                    │ │
│  │ ├─ Status:                                                           │ │
│  │ │  ├─ door_locked: bool                                             │ │
│  │ │  ├─ estop_pressed: bool                                           │ │
│  │ │  ├─ power_on: bool                                                │ │
│  │ │  ├─ last_command: str                                             │ │
│  │ │  └─ last_command_time: float                                      │ │
│  │ │                                                                    │ │
│  │ └─ Interface:                                                        │ │
│  │    ├─ to_dict() → Dict[str, Any]                                   │ │
│  │    ├─ to_json() → str                                              │ │
│  │    ├─ reset() → None                                               │ │
│  │    ├─ log_command(str) → None                                      │ │
│  │    └─ __repr__() → str                                             │ │
│  │                                                                      │ │
│  │ Design:                                                              │ │
│  │ • Immutable (state transitions via new object creation)             │ │
│  │ • Command-driven (no polling or background threads)                 │ │
│  │ • Deterministic (same command sequence = same state)                │ │
│  │ • Thread-safe for reads (GIL protects dict operations)              │ │
│  │                                                                      │ │
│  └────────────┬──────────────────────────────────────────────────────────┘ │
│               │                                                             │
│               │ (NEW) reads current state                                   │
│               ▼                                                             │
│  STATE EXPORT LAYER (NEW)                                                 │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ StateExporter (NEW - firmware_emulator/src/state_export.py)         │ │
│  │                                                                      │ │
│  │ Responsibility: Convert DeviceState to JSON for visualization        │ │
│  │                                                                      │ │
│  │ Design:                                                              │ │
│  │ • Does NOT modify DeviceState                                        │ │
│  │ • Pure function: state_in → JSON_out                                │ │
│  │ • No caching (always reads fresh)                                    │ │
│  │ • Thread-safe (reads only, no locks needed)                          │ │
│  │                                                                      │ │
│  │ Interface:                                                           │ │
│  │ ├─ __init__(device_state: DeviceState)                              │ │
│  │ │  └─ Store reference to device state                               │ │
│  │ │                                                                    │ │
│  │ ├─ get_state_dict() → Dict[str, Any]                               │ │
│  │ │  └─ Full state as Python dict                                     │ │
│  │ │     • Enums converted to strings (e.g., GuidePosition.OPEN→"open")│ │
│  │ │     • Nested dataclasses → nested dicts                           │ │
│  │ │     • Adds _metadata with timestamp and version                   │ │
│  │ │     • ~300-400 bytes when serialized to JSON                      │ │
│  │ │                                                                    │ │
│  │ ├─ get_state_json() → str                                           │ │
│  │ │  └─ Same as get_state_dict() but serialized to JSON              │ │
│  │ │     • Valid UTF-8 JSON string                                     │ │
│  │ │     • Indented for human readability                              │ │
│  │ │     • Can be parsed by any JSON decoder                           │ │
│  │ │                                                                    │ │
│  │ └─ export_summary() → Dict[str, Any]                                │ │
│  │    └─ Compact subset of state                                       │ │
│  │       • Only essential fields                                        │ │
│  │       • ~50-100 bytes when serialized                                │ │
│  │       • Suitable for 10Hz+ polling                                   │ │
│  │       • Fields:                                                      │ │
│  │         - Guide positions (top, bottom)                              │ │
│  │         - Reeler speeds (top, bottom)                                │ │
│  │         - Sag sensor states (4 values)                               │ │
│  │         - Lamps (4 values)                                           │ │
│  │         - Camera flags (7 values)                                    │ │
│  │         - Door, E-stop, power, last_command, timestamp               │ │
│  │                                                                      │ │
│  │ Internals:                                                           │ │
│  │ • No state (stateless converter)                                     │ │
│  │ • Helper methods for enum/dataclass conversion                      │ │
│  │ • Error handling for corrupted state (unlikely)                      │ │
│  │                                                                      │ │
│  └────────────┬──────────────────────────────────────────────────────────┘ │
│               │                                                             │
│               │ (NEW) provides JSON data                                    │
│               ▼                                                             │
│  HTTP API LAYER (NEW)                                                      │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ APIServer (NEW - firmware_emulator/src/api_server.py)               │ │
│  │                                                                      │ │
│  │ Responsibility: Expose state via HTTP REST API                       │ │
│  │                                                                      │ │
│  │ Design:                                                              │ │
│  │ • Flask-based HTTP server                                            │ │
│  │ • Runs in daemon thread (non-blocking to main loop)                 │ │
│  │ • Thread-safe (multiple concurrent requests OK)                      │ │
│  │ • CORS-enabled (for browser visualization)                           │ │
│  │ • Stateless (just reads StateExporter)                               │ │
│  │                                                                      │ │
│  │ Interface:                                                           │ │
│  │ ├─ __init__(state_exporter: StateExporter, port: int = 5000)       │ │
│  │ │  └─ Create Flask app and register routes                          │ │
│  │ │                                                                    │ │
│  │ ├─ run() → None (blocking)                                          │ │
│  │ │  └─ Start Flask WSGI server on 0.0.0.0:port                      │ │
│  │ │     • Called in daemon thread from main                           │ │
│  │ │     • Does not return (blocking loop)                             │ │
│  │ │                                                                    │ │
│  │ └─ Routes:                                                           │ │
│  │    │                                                                │ │
│  │    ├─ GET /api/state                                               │ │
│  │    │  ├─ Handler: get_state()                                       │ │
│  │    │  ├─ Calls: state_exporter.get_state_dict()                    │ │
│  │    │  ├─ Returns: HTTP 200 + JSON (full state)                     │ │
│  │    │  ├─ Content-Type: application/json                             │ │
│  │    │  ├─ CORS headers: Access-Control-Allow-Origin: *               │ │
│  │    │  ├─ Size: ~300-400 bytes                                       │ │
│  │    │  └─ Latency: <50ms (network + server)                          │ │
│  │    │                                                                │ │
│  │    ├─ GET /api/state/summary                                        │ │
│  │    │  ├─ Handler: get_summary()                                     │ │
│  │    │  ├─ Calls: state_exporter.export_summary()                    │ │
│  │    │  ├─ Returns: HTTP 200 + JSON (compact state)                  │ │
│  │    │  ├─ Size: ~50-100 bytes                                        │ │
│  │    │  └─ Latency: <20ms                                             │ │
│  │    │                                                                │ │
│  │    └─ GET /health                                                  │ │
│  │       ├─ Handler: health()                                          │ │
│  │       ├─ Returns: HTTP 200 + {status: "ok", api_version: "1.0"}    │ │
│  │       └─ Latency: <5ms                                              │ │
│  │                                                                      │ │
│  │ Error Handling:                                                      │ │
│  │ • Internal error → HTTP 500 + {error: "message"}                    │ │
│  │ • Logged to emulator logs                                            │ │
│  │ • Visualization retries                                              │ │
│  │                                                                      │ │
│  │ Implementation:                                                      │ │
│  │ • from flask import Flask, jsonify                                  │ │
│  │ • from flask_cors import CORS                                        │ │
│  │ • app = Flask(__name__)                                              │ │
│  │ • CORS(app)  # Enable cross-origin                                  │ │
│  │ • @app.route('/api/state', methods=['GET'])                         │ │
│  │ • app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)   │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## C4 Level 3: Component Diagram (Visualization Side)

Shows how visualization systems consume the API.

```
┌────────────────────────────────────────────────────────────────────────────┐
│  Visualization Container - Generic Architecture (Any Tech)                 │
├────────────────────────────────────────────────────────────────────────────┤
│                                                                            │
│  HTTP CLIENT LAYER                                                         │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ StateAPIClient                                                       │ │
│  │                                                                      │ │
│  │ Responsibility: Fetch state from emulator API                        │ │
│  │                                                                      │ │
│  │ Interface:                                                           │ │
│  │ ├─ __init__(api_url: str = "http://localhost:5000")                │ │
│  │ ├─ fetch_state() → Dict | None                                     │ │
│  │ │  └─ GET /api/state, return parsed JSON or None on error          │ │
│  │ ├─ fetch_summary() → Dict | None                                   │ │
│  │ │  └─ GET /api/state/summary                                        │ │
│  │ ├─ health_check() → bool                                            │ │
│  │ │  └─ GET /health, return True if OK                                │ │
│  │ └─ set_reconnect_strategy(timeout, retry_interval, max_retries)    │ │
│  │    └─ Configure retry logic                                         │ │
│  │                                                                      │ │
│  │ Internals:                                                           │ │
│  │ • HTTP client (requests/fetch/axios depending on tech)               │ │
│  │ • Timeout handling (2 second default)                                │ │
│  │ • Retry logic (exponential backoff)                                  │ │
│  │ • Connection state tracking                                          │ │
│  │ • Error logging                                                      │ │
│  │                                                                      │ │
│  └────────────┬──────────────────────────────────────────────────────────┘ │
│               │                                                             │
│               │ parses JSON state dict                                      │
│               ▼                                                             │
│  STATE MANAGEMENT LAYER                                                    │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ UIStateStore / StateModel                                            │ │
│  │                                                                      │ │
│  │ Responsibility: Keep UI state in sync with API state                 │ │
│  │                                                                      │ │
│  │ Maintains:                                                           │ │
│  │ ├─ guide_top_position (string: closed/open/moving)                 │ │
│  │ ├─ guide_bottom_position (string)                                   │ │
│  │ ├─ reeler_top_speed (int: RPM)                                      │ │
│  │ ├─ reeler_bottom_speed (int)                                        │ │
│  │ ├─ sag sensor states (4 bools)                                      │ │
│  │ ├─ lamp states (4 bools)                                            │ │
│  │ ├─ camera flags (7 bools)                                           │ │
│  │ ├─ door_locked (bool)                                               │ │
│  │ ├─ estop_pressed (bool)                                             │ │
│  │ ├─ power_on (bool)                                                  │ │
│  │ ├─ last_command (str)                                               │ │
│  │ ├─ connection_status (enum: connected/connecting/disconnected)     │ │
│  │ └─ last_update_time (timestamp)                                     │ │
│  │                                                                      │ │
│  │ Methods:                                                             │ │
│  │ ├─ update_from_api(dict) → None                                     │ │
│  │ │  └─ Consume API response, update internal state                   │ │
│  │ ├─ set_connection_status(str) → None                                │ │
│  │ │  └─ Update connection indicator                                   │ │
│  │ ├─ reset_to_defaults() → None                                       │ │
│  │ │  └─ Clear state on disconnect                                     │ │
│  │ └─ emit_change_event(field, old_val, new_val) → None               │ │
│  │    └─ Notify UI of changes (for reactive frameworks)                │ │
│  │                                                                      │ │
│  │ Implementation depends on tech:                                      │ │
│  │ • React: useState hooks                                              │ │
│  │ • Vue: ref/reactive                                                  │ │
│  │ • Plotly Dash: dcc.Store                                             │ │
│  │ • Plain JS: event emitter pattern                                    │ │
│  │                                                                      │ │
│  └────────────┬──────────────────────────────────────────────────────────┘ │
│               │                                                             │
│               │ trigger UI updates                                          │
│               ▼                                                             │
│  VISUALIZATION LAYER                                                       │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ Components / UI Widgets                                              │ │
│  │                                                                      │ │
│  │ (Varies by tech choice, but all consume state)                      │ │
│  │                                                                      │ │
│  │ Option 1: 2D Machine Diagram (SVG)                                   │ │
│  │ ├─ GuideVisualizer                                                   │ │
│  │ │  └─ Render guides as animated bars (0-100% open)                  │ │
│  │ ├─ ReelerVisualizer                                                 │ │
│  │ │  └─ Render reels as spinning wheels + speed gauge                 │ │
│  │ ├─ SensorStatusDisplay                                              │ │
│  │ │  └─ Color-coded sensor status (green/red)                         │ │
│  │ └─ LampIndicator                                                     │ │
│  │    └─ RGB circles showing lamp colors                                │ │
│  │                                                                      │ │
│  │ Option 2: Real-Time Dashboard (Plotly/Dash)                         │ │
│  │ ├─ MotorGauges                                                       │ │
│  │ │  ├─ Gauge: Guide position (0-100%)                                │ │
│  │ │  └─ Gauge: Reeler speed (0-1000 RPM)                              │ │
│  │ ├─ SensorTable                                                       │ │
│  │ │  └─ DataTable: All sensor states                                  │ │
│  │ ├─ StatusPanel                                                       │ │
│  │ │  └─ Indicators: Door, E-stop, Power                               │ │
│  │ └─ CommandLog                                                        │ │
│  │    └─ List: Last 20 commands                                         │ │
│  │                                                                      │ │
│  │ Option 3: Timeline Viewer                                            │ │
│  │ ├─ CommandTimeline                                                   │ │
│  │ │  └─ X-axis: time, Y-axis: state values                            │ │
│  │ ├─ StateTransitionVisualization                                     │ │
│  │ │  └─ Show before/after for each command                            │ │
│  │ └─ DelayVisualization                                                │ │
│  │    └─ Bars showing command timing                                    │ │
│  │                                                                      │ │
│  │ Option 4: 3D Visualizer (Unity/Godot)                               │ │
│  │ ├─ MachineGeometry                                                   │ │
│  │ │  └─ 3D model of machine frame, guides, reels                      │ │
│  │ ├─ AnimatedComponents                                                │ │
│  │ │  ├─ Guide: animate based on position                              │ │
│  │ │  └─ Reels: rotate based on speed                                  │ │
│  │ └─ RealTimeOverlay                                                   │ │
│  │    └─ Sensor status, lamp colors, command log                       │ │
│  │                                                                      │ │
│  │ State Binding Examples:                                              │ │
│  │ • guide_top_position = "open" → GuideBar width = 100%               │ │
│  │ • reeler_top_speed = 500 → ReelGauge needle angle = 180°            │ │
│  │ • sag_bottom_upper = false → SensorIndicator color = green          │ │
│  │ • sag_bottom_upper = true → SensorIndicator color = red, animate    │ │
│  │ • connection_status = "disconnected" → Show overlay: "Disconnected" │ │
│  │                                                                      │ │
│  └────────────┬──────────────────────────────────────────────────────────┘ │
│               │                                                             │
│               │ render to screen                                            │
│               ▼                                                             │
│  DISPLAY OUTPUT                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ Browser (HTML/Canvas/SVG) OR Native Window (PyQt/WPF/Unity)         │ │
│  │                                                                      │ │
│  │ Real-time machine visualization with:                               │ │
│  │ • Motor positions animated                                           │ │
│  │ • Sensor status color-coded                                          │ │
│  │ • Lamps glowing with correct colors                                  │ │
│  │ • Command log scrolling                                              │ │
│  │ • Connection status indicator                                        │ │
│  │ • Last update timestamp                                              │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
│  POLLING LOOP                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐ │
│  │ Main Event Loop                                                      │ │
│  │                                                                      │ │
│  │ while visualization_running:                                         │ │
│  │   try:                                                                │ │
│  │     if time_since_last_poll > 100ms:  # 10Hz polling                │ │
│  │       state = client.fetch_summary()                                 │ │
│  │       if state:                                                       │ │
│  │         ui_state.update_from_api(state)                              │ │
│  │         trigger_ui_update()                                          │ │
│  │   except ConnectionError:                                             │ │
│  │     show_connection_lost()                                            │ │
│  │     retry_with_exponential_backoff()                                 │ │
│  │   except TimeoutError:                                                │ │
│  │     # Treat as transient, try again                                  │ │
│  │                                                                      │ │
│  └──────────────────────────────────────────────────────────────────────┘ │
│                                                                            │
└────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Complete Request-Response Cycle

```
TIME SEQUENCE DIAGRAM
═════════════════════════════════════════════════════════════════════════════

  Visualizer          HTTP Network        Emulator Backend
  Browser/App         (TCP/IP)            Python Process
     │                    │                    │
     │                    │                    │
 [t=0ms] User loads visualizer UI
     │                    │                    │
     │                    │                    │
 [t=10ms] Visualization starts polling
     ├──── GET /api/state/summary ──────────►│
     │                    │                    │  [StateExporter called]
     │                    │                    │  Device state: {
     │                    │                    │    guide_top: "open",
     │                    │                    │    reeler_top: 500,
     │                    │                    │    sag_*: [...],
     │                    │                    │    ...
     │                    │                    │  }
     │                    │  ◄──── HTTP 200 + JSON ─────┤  [Flask route handler]
     │                    │                    │
     │ [t=45ms] JSON received and parsed
     │ UI updates:
     │ • Guide bar animates to full width
     │ • Reeler gauge shows 500 RPM
     │ • Sensor indicators show green
     │
     ├──── Wait 100ms ────┤                    │
     │                    │                    │
 [t=110ms] Poll again     │                    │
     ├──── GET /api/state/summary ──────────►│
     │                    │                    │  [Device state may have changed]
     │                    │  ◄──── HTTP 200 + JSON ─────┤
     │
     ├──── Wait 100ms ────┤                    │
     │                    │                    │
     ... (polling continues every 100ms) ...
     │                    │                    │
     │                    │                    │  [Meanwhile, LabVIEW sends command]
     │                    │                    │  LabVIEW: QUERY (5 bytes via serial)
     │                    │                    │  Emulator main thread: [blocked on read]
     │                    │                    │  Command received, dispatched
     │                    │                    │  Response: YES (3 bytes)
     │                    │                    │  DeviceState: last_command = "QUERY"
     │
     ├──── GET /api/state/summary ──────────►│
     │                    │                    │  [Flask thread calls StateExporter]
     │                    │                    │  Device state includes new last_command
     │                    │  ◄──── HTTP 200 + JSON ─────┤
     │                    │                    │
     │ [t=1550ms] JSON received
     │ UI updates: last_command display shows "QUERY"
     │
     ... (continues indefinitely until stop) ...

═════════════════════════════════════════════════════════════════════════════

CONCURRENT EXECUTION
═════════════════════════════════════════════════════════════════════════════

Main Thread (Serial Loop)        Background Thread (HTTP API)
─────────────────────────────────────────────────────────────────────────
1. read_command() [blocking]     1. Flask app.run()
2. parse opcode                  2. Listen on port 5000
3. dispatch to handler           3. [idle, waiting for requests]
4. update device_state           4. [idle, waiting for requests]
5. write response                5. [idle, waiting for requests]
6. log transaction               6. Request arrives: GET /api/state/summary
7. goto 1                        7. StateExporter.export_summary() called
                                 8. Read device_state (GIL protects)
                                 9. Convert to dict
                                10. JSON encode
                                11. HTTP 200 response
                                12. goto 3

KEY INSIGHT: Both threads access DeviceState concurrently!
Python GIL ensures dict reads are atomic.
StateExporter never writes, so no race conditions.

═════════════════════════════════════════════════════════════════════════════
```

---

## Architecture Constraints & Assumptions

```
Constraints:
1. Python 3.8+ required
2. Flask (HTTP server) and flask-cors (CORS support) must be installed
3. Emulator runs on single machine (Windows/WSL2)
4. Serial communication loop must not be blocked by API requests
5. DeviceState is immutable (no concurrent writes)
6. State JSON payload must be <500 bytes (for fast polling)

Assumptions:
1. Visualization polling at 10Hz (100ms) is acceptable
2. ~100ms network/processing latency is tolerable
3. Visualization clients are trusted (no authentication in Phase 1)
4. API runs on localhost (not exposed to external networks)
5. Machine has available port 5000 (configurable)
6. DeviceState structure is stable across emulator versions

Non-Functional Requirements:
• Response time: <50ms for /api/state, <20ms for /api/state/summary
• Availability: 99.9% (same as serial loop)
• Throughput: 10-100 requests/second (can handle multiple visualizations)
• Data consistency: Always returns current state (no stale data)
• Thread safety: Python GIL protects dict operations
```

