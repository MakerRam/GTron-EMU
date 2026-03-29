## Why

Phase 1 (complete) delivers a fully functional firmware emulator with 75 opcodes and 100% specification compliance. However, developers and operators lack real-time visibility into device state. The HTTP API and visualization dashboard enable real-time monitoring, state inspection, and system debugging without LabVIEW, unlocking faster development and easier troubleshooting.

## What Changes

- **Add HTTP REST API Layer**: StateExporter + Flask APIServer expose device state as JSON via three endpoints (/api/state, /api/state/summary, /health). Runs in background thread, non-blocking to serial communication.
- **Add Browser Visualization Dashboard**: HTML/JS dark-themed interface with 6 monitoring panels (guides, reelers, sensors, lamps, cameras, system status) + command log. Polls API at 100ms intervals for real-time updates.
- **Add Python Dependencies**: flask, flask-cors for HTTP API. Already using pyserial for serial communication.
- **Modify main.py**: Optional API server initialization (can be disabled with --no-api flag). No changes to serial loop or opcode handling.
- **No Breaking Changes**: All Phase 1 code unchanged. API and visualization are pure additions.

## Capabilities

### New Capabilities

- `rest-api-server`: HTTP endpoints expose full and compact device state, health checks. StateExporter converts immutable DeviceState to JSON. APIServer provides Flask routes with CORS support. Runs in daemon thread without blocking serial communication.
- `real-time-visualization`: Browser-based dashboard with HTML/JS + CSS. Displays guide positions, reeler speeds, sensor status, lamp states, camera activity, system status, and command history. Polling-based (100ms) for <100ms latency. Mock mode for offline testing with 10-state simulation cycle.
- `state-json-schema`: Structured JSON format for device state export. Includes metadata (timestamp, version), all device components (guides, reelers, sensors, encoders, lamps, cameras), system status (door, E-stop, power), and last command tracking.

### Modified Capabilities

- `device-state-management`: Existing DeviceState class gains read-only API access via StateExporter. No functional changes to state mutation or command handling. New `to_dict()` method (already exists) used for JSON serialization.

## Impact

**Code**:
- Add 2 new files: firmware_emulator/src/state_export.py (78 lines), firmware_emulator/src/api_server.py (115 lines)
- Add 1 new directory: visualizer/ with HTML/JS/CSS dashboard
- Modify firmware_emulator/src/main.py: 5-10 lines for API initialization
- Add requirements.txt: flask, flask-cors, pytest, pyserial

**APIs**:
- New HTTP endpoints: GET /api/state, GET /api/state/summary, GET /health
- New JSON schema for state export (defined in specs)

**Dependencies**:
- Flask 2.3.0+ (new)
- flask-cors 4.0.0+ (new)
- pyserial 3.5+ (existing)
- pytest 7.4.0+ (existing, for API tests)

**Systems**:
- Emulator: Background thread runs Flask without impacting serial loop
- Visualization: Browser-based, pure client-side (no server required), can run on same machine or network
- Testing: API enables UI-independent testing, mock state support for development

**Deployment**:
- Same machine: Windows emulator → localhost:5000 → browser visualizer
- Network: Windows emulator → 192.168.x.x:5000 → Linux/Mac visualizer
- Both modes supported immediately after integration
