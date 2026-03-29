## Requirement: Export device state via HTTP REST API

The system SHALL expose complete and summary device state through HTTP endpoints that visualization clients can query.

### Scenario: Client requests full device state
- **WHEN** visualization client sends `GET http://localhost:5000/api/state`
- **THEN** emulator returns HTTP 200 + JSON containing all device state fields
- **AND** response time is <100ms
- **AND** response includes timestamp and API version

### Scenario: Client requests compact state
- **WHEN** visualization client sends `GET http://localhost:5000/api/state/summary`
- **THEN** emulator returns HTTP 200 + JSON with essential fields only (motor positions, sensor status, lamp state)
- **AND** response is <50% size of full state
- **AND** suitable for 10Hz polling without network overhead

### Scenario: Health check
- **WHEN** visualization client sends `GET http://localhost:5000/api/health`
- **THEN** emulator returns HTTP 200 + `{status: "ok", api_version: "1.0"}`
- **AND** response time is <10ms

---

## Requirement: StateExporter class converts DeviceState to JSON

The system SHALL provide a StateExporter class that converts the immutable DeviceState object to dictionary and JSON formats without modifying emulator behavior.

### Scenario: Export full state as dictionary
- **WHEN** StateExporter.get_state_dict() is called
- **THEN** returns Dict[str, Any] with all DeviceState fields
- **AND** enums are converted to string values (e.g., GuidePosition.OPEN → "open")
- **AND** nested dataclasses are converted to nested dicts
- **AND** timestamp is added as _metadata.timestamp
- **AND** original DeviceState is not modified

### Scenario: Export state as JSON string
- **WHEN** StateExporter.get_state_json() is called
- **THEN** returns valid JSON string (utf-8 encoded)
- **AND** can be parsed by any JSON parser
- **AND** includes all fields from get_state_dict()
- **AND** is human-readable (indented)

### Scenario: Export summary (compact) state
- **WHEN** StateExporter.export_summary() is called
- **THEN** returns Dict with only essential fields:
  - Guide positions (top, bottom)
  - Reeler speeds (top, bottom)
  - Sag sensor states (4 sensors)
  - Lamp states (red, yellow, green)
  - Camera flags (0-6)
  - Door locked, E-stop, power, last command
- **AND** payload is <150 bytes (vs ~400 for full state)
- **AND** visualization can update UI at 10Hz without network congestion

---

## Requirement: Flask API server runs in background without blocking

The system SHALL run HTTP API server in a background thread that does not interfere with serial communication loop.

### Scenario: API server starts with emulator
- **WHEN** EmulatorEngine is initialized
- **THEN** APIServer is instantiated with StateExporter
- **AND** Flask app is created with CORS headers enabled
- **AND** Three routes are registered: /api/state, /api/state/summary, /health
- **AND** API server is started in a daemon thread
- **AND** main event loop (serial communication) is not blocked

### Scenario: API serves requests while emulator processes commands
- **WHEN** visualization polls GET /api/state (100ms intervals)
- **AND** simultaneously LabVIEW sends serial commands (variable timing)
- **THEN** serial loop reads/processes/responds without latency from API calls
- **AND** API requests are queued by Flask's thread pool
- **AND** state reads are thread-safe (Python GIL protects dict reads)

### Scenario: API port can be configured
- **WHEN** EmulatorEngine is created with `api_port=5001`
- **THEN** APIServer binds to 0.0.0.0:5001 instead of default 5000
- **AND** Can run multiple emulators on different ports

---

## Requirement: State format is valid JSON with complete schema

The system SHALL export state in valid JSON format following a defined schema that visualization clients can rely on.

### Scenario: Exported JSON validates against schema
- **WHEN** StateExporter.get_state_dict() is serialized to JSON
- **THEN** JSON is valid (can be parsed by json.loads)
- **AND** all required fields are present
- **AND** all enums are converted to string values:
  - GuidePosition.CLOSED → "closed"
  - GuidePosition.OPEN → "open"
  - GuidePosition.MOVING → "moving"
  - GuidePosition.UNKNOWN → "unknown"
- **AND** all numeric values are present (0 for uninitialized)
- **AND** all boolean values are present (false for unset)
- **AND** nested structures match expected schema

### Scenario: JSON includes comprehensive motor state
- **WHEN** state is exported
- **THEN** includes:
  - guide_top: {position, moving, reached_limit}
  - guide_bottom: {position, moving, reached_limit}
  - reeler_top: {speed, teeth, running, position}
  - reeler_bottom: {speed, teeth, running, position}
- **AND** all fields are always present (no conditional fields)

### Scenario: JSON includes complete sensor state
- **WHEN** state is exported
- **THEN** includes:
  - sag_top_upper, sag_top_lower (bool)
  - sag_bottom_upper, sag_bottom_lower (bool)
  - sensor_top: {attached, powered, triggered}
  - sensor_bottom: {attached, powered, triggered}
  - encoder_top: {initialized, enabled, position, initial_angle, teeth_count}
  - encoder_bottom: {same structure}

### Scenario: JSON includes complete camera/lamp state
- **WHEN** state is exported
- **THEN** includes:
  - cameras: {flags: {0-6: bool}, active_sequence: int, timestamp_enabled: bool}
  - lamps: {red, yellow, green, buzzer: bool}
  - last_command: str (opcode name)
  - last_command_time: float (timestamp)

---

## Requirement: CORS headers enable browser-based visualization

The system SHALL include proper CORS headers so visualization running in browser can access API.

### Scenario: Browser visualization can fetch API
- **WHEN** HTML/JS visualization running on different origin calls fetch('/api/state')
- **THEN** Flask includes CORS headers:
  - `Access-Control-Allow-Origin: *`
  - `Access-Control-Allow-Methods: GET, OPTIONS`
  - `Access-Control-Allow-Headers: Content-Type`
- **AND** browser allows the cross-origin request
- **AND** visualization receives JSON response

### Scenario: Preflight requests are handled
- **WHEN** browser sends OPTIONS request to /api/state
- **THEN** Flask responds with 200 + CORS headers
- **AND** no error response

---

## Requirement: API handles errors gracefully

The system SHALL handle errors and timeouts gracefully, returning appropriate HTTP status codes.

### Scenario: State export error
- **WHEN** StateExporter encounters an error (e.g., corrupt state)
- **THEN** APIServer returns HTTP 500 + `{error: "description"}`
- **AND** original error is logged to emulator logs
- **AND** visualization receives error response and can display "Connection Error"

### Scenario: API timeout
- **WHEN** StateExporter takes >5 seconds to respond (shouldn't happen)
- **THEN** Flask times out and returns HTTP 504
- **AND** visualization treats as connection loss

### Scenario: Emulator has no state
- **WHEN** APIServer starts before first command is processed
- **THEN** returns empty/default state (not error)
- **AND** visualization shows initial state (guides closed, reelers stopped, etc.)

---

## Requirement: No changes to existing emulator behavior

The system SHALL add API layer without modifying serial communication, opcode handling, or state machine logic.

### Scenario: Existing unit tests still pass
- **WHEN** running `pytest tests/` after adding StateExporter
- **THEN** 40+ existing tests pass without modification
- **AND** no changes to test files required
- **AND** no changes to command processing logic

### Scenario: Serial communication unaffected
- **WHEN** visualization polls API while LabVIEW sends commands
- **THEN** emulator responds to serial commands with same timing as before
- **AND** no latency introduced to serial loop
- **AND** no commands are dropped or delayed

### Scenario: Emulator works with or without API
- **WHEN** EmulatorEngine starts without APIServer initialization
- **THEN** emulator still functions normally
- **AND** serial communication works
- **AND** just no HTTP API available (for testing)

---

## Requirement: Visualization consumes state via HTTP polling

Visualization systems SHALL fetch state from API at regular intervals (50-100ms) without requiring persistent connections.

### Scenario: Visualization polls API every 100ms
- **WHEN** visualization client creates fetch interval
- **THEN** sends `GET /api/state/summary` every 100ms
- **AND** receives JSON response
- **AND** parses JSON and updates UI
- **AND** handles missed polls gracefully (uses last valid state)

### Scenario: Visualization handles slow network
- **WHEN** API response takes 150ms
- **THEN** visualization adjusts (polls less frequently or accepts latency)
- **AND** does not hammer the API with queued requests
- **AND** shows "Slow Connection" indicator if lag exceeds threshold

### Scenario: Visualization handles disconnection
- **WHEN** emulator is stopped/restarted
- **AND** API is unreachable
- **THEN** visualization shows "Disconnected" UI
- **AND** auto-retries with exponential backoff
- **AND** reconnects when emulator is available again

---

## Requirement: StateExporter maintains thread safety

The system SHALL ensure StateExporter can be safely called from multiple threads without data corruption.

### Scenario: Concurrent reads during state update
- **WHEN** Flask thread calls StateExporter.get_state_dict()
- **AND** simultaneously main thread updates DeviceState
- **THEN** StateExporter reads are atomic (Python GIL protects dict operations)
- **AND** either old or new state is returned (never corrupted)
- **AND** no locks needed (DeviceState is immutable between updates)

### Scenario: Multiple visualization clients
- **WHEN** multiple visualizations query API simultaneously
- **THEN** each gets consistent state (not a mix of old/new)
- **AND** no race conditions occur
- **AND** all clients see same state at same instant

---

## Requirement: API is discoverable and documented

The system SHALL provide clear documentation and discovery mechanisms.

### Scenario: Client discovers available endpoints
- **WHEN** visualization client sends `GET /health`
- **THEN** returns `{status: ok, api_version: "1.0"}`
- **AND** client knows API is alive and version is compatible

### Scenario: State schema is discoverable
- **WHEN** visualization developer reads DESIGN.md
- **THEN** finds complete JSON schema with field descriptions
- **AND** can understand mapping from state to UI (guide position → bar width, etc.)

### Scenario: API is documented with examples
- **WHEN** visualization developer reads documentation
- **THEN** finds:
  - Example curl commands
  - Example JSON responses
  - Field descriptions
  - Response times
  - Error codes

---

## Requirement: Performance is acceptable for real-time display

The system SHALL respond fast enough for smooth real-time visualization at 10Hz (100ms intervals).

### Scenario: Full state response time
- **WHEN** visualization sends `GET /api/state`
- **THEN** response arrives in <50ms (network + server)
- **AND** suitable for 20Hz polling if desired
- **AND** JSON payload is <500 bytes

### Scenario: Summary state response time
- **WHEN** visualization sends `GET /api/state/summary`
- **THEN** response arrives in <20ms
- **AND** suitable for 50Hz polling if desired
- **AND** JSON payload is <150 bytes

### Scenario: Health check response time
- **WHEN** visualization sends `GET /health`
- **THEN** response arrives in <5ms
- **AND** can be used for frequent liveness checks

---

## Requirement: Visualization can work with mock/recorded state

Visualization systems SHALL be able to test/develop without running emulator.

### Scenario: Visualization loads state from JSON file
- **WHEN** visualization developer is building UI (no emulator running)
- **THEN** visualization can load state from `mock_state.json`
- **AND** renders UI as if API provided that state
- **AND** supports toggling between API and mock mode

### Scenario: Visualization can replay recorded state sequences
- **WHEN** recorded state JSON files are provided
- **THEN** visualization can play through them sequentially
- **AND** simulates real-time state updates
- **AND** allows testing UI behavior without emulator

This enables UI testing to proceed in parallel with emulator development.

---

## Open Questions

1. **Should API support authentication in Phase 1?**
   - Current answer: No (localhost only, not exposed)
   - Phase 2: Consider API key or OAuth

2. **Should API support filtering/pagination?**
   - Current answer: No (state is small enough)
   - Phase 2: If state grows, add field selection

3. **Should API log all requests?**
   - Current answer: Yes (to emulator logs)
   - Could be toggle: `--api-verbose`

4. **Should API support historical state queries?**
   - Current answer: No (returns current only)
   - Phase 2: Add historical endpoints

5. **Should StateExporter cache state or always read fresh?**
   - Current answer: Always read fresh (consistency over speed)
   - Phase 2: Consider caching if state reads become expensive

