## Context

The Vision System Firmware Emulator (completed in Phase 1) maintains comprehensive device state but provides no real-time visualization. Developers and operators cannot see:
- Real-time motor positions and speeds
- Sensor triggering events
- Camera activity sequences
- System diagnostic information

The system is designed as a two-tier application:
1. **Emulator (Backend)**: Python, runs on Windows (WSL2), controls serial communication, maintains device state
2. **Visualizer (Frontend)**: Independent, any technology, consumes state via HTTP API

This decoupling allows visualization specialists to build UIs without understanding emulator internals, using their preferred tech stack.

## Goals / Non-Goals

**Goals (MVP):**
- Expose device state via clean HTTP REST API
- Display real-time guide motor positions (top/bottom)
- Show reeler motor speeds with gauges
- Visualize sag sensor status (color-coded)
- Track camera activity and image counts
- Display tower lamp states (RGB)
- Show door lock, E-stop, power status
- Provide command history display
- Error handling for API timeouts/disconnects
- Works on desktop browsers (1920x1080 minimum)

**Non-Goals (MVP):**
- 3D visualization (Phase 2+)
- Historical data logging/replay (Phase 2+)
- Mobile app (Phase 2+)
- Complex analytics/reporting
- Machine learning predictions
- Hardware integration beyond HTTP API

## Architectural Decisions

### Decision 1: HTTP REST API over WebSocket (Phase 1)
**Decision**: Use HTTP polling (50-100ms intervals) instead of WebSocket for Phase 1.

**Rationale**:
- Simpler to implement in Flask
- Decouples timing concerns
- Easier for visualization to implement (no persistent connection needed)
- Lower overhead for MVP
- Can upgrade to WebSocket in Phase 2 without changing architecture

**Trade-off**: ~100ms latency vs. instant updates (acceptable for non-safety-critical monitoring)

### Decision 2: Stateless API Endpoints
**Decision**: Each API call returns complete device state, no incremental updates.

**Rationale**:
- Visualization never needs to maintain state consistency with emulator
- No syncing issues
- Can start/stop visualization anytime
- Simpler debugging
- Visualization can snapshot for replay

**Implementation**:
```
GET /api/state          → Full DeviceState (300+ bytes)
GET /api/state/summary  → Compact subset (100 bytes)
GET /health            → Health check
```

### Decision 3: JSON as Data Format
**Decision**: Export state as JSON only (no MessagePack, Protobuf, etc.)

**Rationale**:
- Language-agnostic (works with any platform)
- Human-readable (debugging)
- Native support in JavaScript, Python, C#, Go, etc.
- Small payload (~200-400 bytes per request)
- No serialization complexity

### Decision 4: Visualization as Standalone Project
**Decision**: Keep visualization in completely separate Git repository / project.

**Rationale**:
- Independent release cycle
- Different team can own it
- Can use different tech stack
- Easy to replace/upgrade later
- Emulator never needs to know about UI

**Contract**: Single HTTP API endpoint (`/api/state`)

### Decision 5: Mock Data Support for Visualization Dev
**Decision**: Visualization should work with mock/recorded state JSON for testing.

**Rationale**:
- UI devs can work without running emulator
- Can write UI tests without emulator
- Can design UI in isolation
- Can replay recorded sessions

**Implementation**: Visualization accepts state from API or local JSON file (toggleable)

### Decision 6: Minimal Emulator Changes
**Decision**: Add API as optional module, don't modify core emulator logic.

**Rationale**:
- Existing tests continue to pass
- Emulator behavior unchanged
- Can run with or without API server
- Clean separation of concerns

**Implementation**:
- New file: `state_export.py` (StateExporter class)
- New file: `api_server.py` (APIServer/Flask app)
- Modify: `main.py` (instantiate and start API server)

## Architecture

### System Context Diagram (C4 Level 1)

```
┌─────────────────────────────────────────────────────────────┐
│                   Vision System                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────┐                  ┌──────────────────┐ │
│  │   LabVIEW App    │◄──serial(COM4)──►│   Emulator       │ │
│  │   (Control)      │                  │   (Backend)      │ │
│  └──────────────────┘                  └────────┬─────────┘ │
│                                                  │           │
│                                    HTTP /api/state(port 5000)│
│                                                  │           │
│                                        ┌─────────▼─────────┐ │
│                                        │  Visualizer       │ │
│                                        │  (Frontend)       │ │
│                                        │  (Browser/UI)     │ │
│                                        └───────────────────┘ │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Container Diagram (C4 Level 2)

```
┌──────────────────────────────────────────────────────────────────┐
│  Windows/WSL2 Machine                                            │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  Emulator Container (Python)                              │ │
│  ├────────────────────────────────────────────────────────────┤ │
│  │                                                            │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │ │
│  │  │ SerialBridge │  │ CommandParser│  │OpcodeDspatch│    │ │
│  │  │ (COM3/COM4)  │  │ (5-byte ASCII)  │  (Handlers) │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘    │ │
│  │                           ▲                              │ │
│  │                           │                              │ │
│  │  ┌──────────────────────────────────────┐               │ │
│  │  │      DeviceState (immutable)         │               │ │
│  │  │ • Guide motors (top/bottom)          │               │ │
│  │  │ • Reeler motors                      │               │ │
│  │  │ • Sensors (4 sag sensors)            │               │ │
│  │  │ • Cameras (7 flags)                  │               │ │
│  │  │ • Lamps (red/yellow/green/buzzer)   │               │ │
│  │  │ • Door/E-stop/Power status           │               │ │
│  │  └──────────────────────────────────────┘               │ │
│  │           ▲                                             │ │
│  │           │ to_dict()                                   │ │
│  │  ┌────────┴─────────┐                                   │ │
│  │  │ StateExporter    │                                   │ │
│  │  │ • get_state_dict()                                   │ │
│  │  │ • export_summary()                                   │ │
│  │  └────────┬─────────┘                                   │ │
│  │           │                                             │ │
│  │  ┌────────▼──────────────────┐                          │ │
│  │  │ APIServer (Flask)          │                          │ │
│  │  │ Port: 5000                 │                          │ │
│  │  │ • GET /api/state           │                          │ │
│  │  │ • GET /api/state/summary   │                          │ │
│  │  │ • GET /health              │                          │ │
│  │  └────────┬──────────────────┘                          │ │
│  │           │                                             │ │
│  └───────────┼─────────────────────────────────────────────┘ │
│              │                                                │
│              │ HTTP GET (port 5000)                          │
│              │                                                │
└──────────────┼────────────────────────────────────────────────┘
               │
        ┌──────▼──────┐
        │  Browser    │
        │  or         │
        │  Desktop UI │
        │ (External)  │
        └─────────────┘
```

### Component Diagram (C4 Level 3 - Emulator Side)

```
┌──────────────────────────────────────────────────────────────┐
│  Emulator Container                                          │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  EmulatorEngine (main.py)                                    │
│  ┌──────────────────────────────────────────────────────────┤
│  │                                                          │
│  │  ┌────────────────────────────────────────────────────┐ │
│  │  │  SerialBridge                      (existing)      │ │
│  │  │  • read_command() → bytes                          │ │
│  │  │  • write_response(bytes) → bool                    │ │
│  │  │  • close()                                         │ │
│  │  └────────────────────────────────────────────────────┘ │
│  │                                                          │
│  │  ┌────────────────────────────────────────────────────┐ │
│  │  │  CommandParser                      (existing)      │ │
│  │  │  • parse(bytes) → str (opcode)                     │ │
│  │  │  • is_valid_command(bytes) → bool                  │ │
│  │  └────────────────────────────────────────────────────┘ │
│  │                                                          │
│  │  ┌────────────────────────────────────────────────────┐ │
│  │  │  OpcodeDispatcher                  (existing)      │ │
│  │  │  • dispatch(opcode) → bytes                        │ │
│  │  │  • device_state (reference)                        │ │
│  │  └────────────────────────────────────────────────────┘ │
│  │           ▲                                             │
│  │           │                                             │
│  │  ┌────────┴────────────────────────────────────────────┐ │
│  │  │  DeviceState                       (existing)      │ │
│  │  │  • guide_top, guide_bottom                         │ │
│  │  │  • reeler_top, reeler_bottom                       │ │
│  │  │  • sensor_top, sensor_bottom                       │ │
│  │  │  • encoder_top, encoder_bottom                     │ │
│  │  │  • lamps                                           │ │
│  │  │  • cameras (flags, active_sequence, ts_enabled)  │ │
│  │  │  • sag_top_upper/lower, sag_bottom_upper/lower   │ │
│  │  │  • door_locked, estop_pressed, power_on           │ │
│  │  │  • last_command, last_command_time                │ │
│  │  │                                                    │ │
│  │  │  Methods:                                          │ │
│  │  │  • to_dict() → Dict                              │ │
│  │  │  • to_json() → str                               │ │
│  │  │  • reset()                                        │ │
│  │  └────────┬─────────────────────────────────────────┘ │
│  │           │ (NEW) to_dict()                            │
│  │  ┌────────▼─────────────────────────────────────────┐  │
│  │  │  StateExporter                        (NEW)       │  │
│  │  │                                                   │  │
│  │  │  __init__(device_state: DeviceState)             │  │
│  │  │  get_state_dict() → Dict[str, Any]              │  │
│  │  │  get_state_json() → str                         │  │
│  │  │  export_summary() → Dict[str, Any] (compact)    │  │
│  │  └────────┬─────────────────────────────────────────┘  │
│  │           │                                             │
│  │  ┌────────▼─────────────────────────────────────────┐  │
│  │  │  APIServer (Flask)                   (NEW)        │  │
│  │  │                                                   │  │
│  │  │  __init__(state_exporter, port=5000)            │  │
│  │  │  run() → starts Flask on 0.0.0.0:5000           │  │
│  │  │                                                   │  │
│  │  │  Routes:                                         │  │
│  │  │  ├─ GET /api/state                              │  │
│  │  │  │  └─ returns exporter.get_state_dict()        │  │
│  │  │  ├─ GET /api/state/summary                      │  │
│  │  │  │  └─ returns exporter.export_summary()        │  │
│  │  │  ├─ GET /health                                 │  │
│  │  │  │  └─ returns {status: ok, api_version: 1.0}  │  │
│  │  │  └─ Includes CORS headers for browser access    │  │
│  │  │                                                   │  │
│  │  │  Runs in background thread (daemon)              │  │
│  │  │  Does not block serial communication loop        │  │
│  │  └─────────────────────────────────────────────────┘  │
│  │                                                        │
│  └──────────────────────────────────────────────────────────┘
│
│  Main Event Loop (simplified):
│
│  while running:
│      cmd_bytes = serial_bridge.read_command()
│      if valid:
│          response = dispatcher.dispatch(parse(cmd_bytes))
│          serial_bridge.write_response(response)
│
│  (Meanwhile, in background thread:)
│      api_server runs Flask WSGI app
│      handles HTTP GET requests to /api/state
│      reads device_state, returns JSON
│
└──────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
Sequential Flow (Emulator):
1. LabVIEW sends: "QUERY" (5 bytes via COM4)
2. SerialBridge reads 5 bytes → "QUERY\0"
3. CommandParser parses → opcode="QUERY"
4. OpcodeDispatcher.dispatch(QUERY)
5. HandshakeHandler.handle() → b"YES"
6. SerialBridge writes 3 bytes → "YES"
7. OpcodeHandler updates DeviceState
8. DeviceState immutable, command-driven

Parallel Flow (Visualization):
1. Visualizer: GET http://localhost:5000/api/state
2. APIServer (Flask) handles request in thread pool
3. StateExporter.get_state_dict() reads DeviceState
4. DeviceState.to_dict() converts → Python dict
5. Flask jsonify() converts → JSON
6. HTTP response 200 + JSON payload
7. Visualizer receives JSON
8. Visualizer updates UI components
9. Sleep 100ms, repeat

These flows are completely independent!
```

### State Export Format (JSON Schema)

```json
{
  "_metadata": {
    "timestamp": "<float: Unix timestamp>",
    "version": "<str: API version>"
  },
  
  "guide_top": {
    "position": "<enum: closed|open|moving|unknown>",
    "moving": "<bool: currently moving>",
    "reached_limit": "<bool: hit limit switch>"
  },
  
  "guide_bottom": {
    "position": "<enum: closed|open|moving|unknown>",
    "moving": "<bool>",
    "reached_limit": "<bool>"
  },
  
  "reeler_top": {
    "speed": "<int: steps/sec>",
    "teeth": "<int: number of teeth>",
    "running": "<bool>",
    "position": "<int: current position>"
  },
  
  "reeler_bottom": {
    "speed": "<int>",
    "teeth": "<int>",
    "running": "<bool>",
    "position": "<int>"
  },
  
  "sensor_top": {
    "attached": "<bool>",
    "powered": "<bool>",
    "triggered": "<bool>"
  },
  
  "sensor_bottom": {
    "attached": "<bool>",
    "powered": "<bool>",
    "triggered": "<bool>"
  },
  
  "encoder_top": {
    "initialized": "<bool>",
    "enabled": "<bool>",
    "position": "<int>",
    "initial_angle": "<int>",
    "teeth_count": "<int>"
  },
  
  "encoder_bottom": {
    "initialized": "<bool>",
    "enabled": "<bool>",
    "position": "<int>",
    "initial_angle": "<int>",
    "teeth_count": "<int>"
  },
  
  "lamps": {
    "red": "<bool>",
    "yellow": "<bool>",
    "green": "<bool>",
    "buzzer": "<bool>"
  },
  
  "cameras": {
    "flags": "<dict: {0:bool, 1:bool, ..., 6:bool}>",
    "active_sequence": "<int: -1=none, 0-6=camera id>",
    "timestamp_enabled": "<bool>"
  },
  
  "door_locked": "<bool>",
  "estop_pressed": "<bool>",
  "power_on": "<bool>",
  
  "sag_top_upper": "<bool: false=pass, true=triggered>",
  "sag_top_lower": "<bool>",
  "sag_bottom_upper": "<bool>",
  "sag_bottom_lower": "<bool>",
  
  "solenoid_top": "<bool>",
  "solenoid_bottom": "<bool>",
  
  "stamping_relay": "<bool>",
  
  "stepper_initialized": "<bool>",
  "reeler_initialized": "<bool>",
  
  "last_command": "<str: opcode name or null>",
  "last_command_time": "<float: Unix timestamp or null>"
}
```

## Implementation Plan

### Phase 1: Emulator API Layer (2-3 days)

**Tasks:**
1. Create `firmware_emulator/src/state_export.py`
   - StateExporter class
   - get_state_dict(), get_state_json(), export_summary()
   - Type hints and docstrings

2. Create `firmware_emulator/src/api_server.py`
   - APIServer class wrapping Flask
   - Three endpoints: /api/state, /api/state/summary, /health
   - CORS support
   - Error handling

3. Modify `firmware_emulator/src/main.py`
   - Import StateExporter and APIServer
   - In EmulatorEngine.__init__:
     - Create StateExporter instance
     - Create APIServer instance
     - Start API server in daemon thread
   - Add command-line arg: --api-port (default 5000)
   - Update console output to show API is running

4. Testing
   - Unit tests for StateExporter
   - Integration tests for APIServer
   - Manual testing: curl http://localhost:5000/api/state

### Phase 2: Visualization (5-7 days, varies by tech)

**Option A: Python + Plotly Dash (Recommended for this team)**
- Create visualization/ directory
- Dashboard with live-updating components
- Motor gauges, sensor tables, lamp indicators
- Command log display
- Real-time polling with error handling

**Option B: React + D3/Chart.js**
- HTML/JS SPA
- SVG-based 2D machine diagram
- Real-time state binding
- Responsive design
- Browser-native

**Option C: Vue.js + Fabric.js**
- Similar to React but lighter
- Canvas-based animations
- Lower bundle size

**Decision**: TBD with team preference (Python fastest, JavaScript most flexible)

### Testing Plan

**Emulator Tests:**
- StateExporter: convert DeviceState → JSON
- APIServer: HTTP endpoints return valid JSON
- Integration: Running emulator, query API, get state

**Visualization Tests (varies by choice):**
- Component rendering tests
- State update tests (mock API responses)
- Error handling tests
- Responsive layout tests

## Risks / Trade-offs

| Risk | Impact | Mitigation |
|------|--------|-----------|
| **HTTP polling latency** | ~100ms delay in UI updates | Acceptable for monitoring; can upgrade to WebSocket Phase 2 |
| **API blocked by bad state** | Visualization shows stale data | Add error handling, timeout, retry logic |
| **Network disconnects** | Visualization loses connection | Show "Connecting..." UI, auto-retry |
| **State grows with Phase 2** | JSON payload increases | Add pagination/filtering in Phase 2 |
| **Multiple visualizations** | Port conflicts? | Run each on different port (5000, 5001, 5002) |
| **Security** | Anyone on network can query API | Phase 2: add authentication/firewalling |

## Open Questions

1. **Visualization Tech Stack?**
   - Team preference: Python, JavaScript, C#, other?
   - Browser-based or native desktop?

2. **Visualization Scope?**
   - Just 2D diagram?
   - Full dashboard with metrics?
   - Timeline viewer?
   - Multiple visualizations?

3. **Deployment Model?**
   - Single machine (Windows)?
   - Network (emulator on Windows, UI on Linux)?
   - Docker containers?

4. **Phase 2 Priorities?**
   - 3D visualization?
   - Historical replay?
   - Advanced analytics?

## Migration Path

**Phase 1 (Current):**
- Emulator exports state via HTTP API
- One MVP visualization (2D diagram or dashboard)
- Real-time polling (100ms intervals)

**Phase 2 (Future):**
- Upgrade to WebSocket for instant updates
- Add historical state logging
- Add replay/timeline viewer
- Add 3D visualization
- Build multiple visualizations from same API
- Add analytics/diagnostics

**Phase 3+ (Enterprise):**
- Real-time collaboration (multiple users)
- Cloud-based replay storage
- Advanced ML-based diagnostics
- Mobile app version
- Integration with manufacturing MES systems

