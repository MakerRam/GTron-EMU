## ADDED Requirements

### Requirement: HTTP API exports full device state

The system SHALL expose complete device state as JSON via GET /api/state endpoint, returning all device components with metadata.

#### Scenario: Client requests full device state
- **WHEN** client sends `GET http://localhost:5000/api/state`
- **THEN** server responds with HTTP 200 + JSON object
- **AND** response contains _metadata with timestamp and api_version
- **AND** response includes all device state fields (guides, reelers, sensors, encoders, lamps, cameras, system status)
- **AND** enums are converted to string values (e.g., "closed", "open", "moving")
- **AND** response time is <100ms

#### Scenario: Client requests compact summary state
- **WHEN** client sends `GET http://localhost:5000/api/state/summary`
- **THEN** server responds with HTTP 200 + JSON object
- **AND** response contains only essential fields: guide positions, reeler speeds, sag sensors, lamps, camera flags, door/E-stop/power status, last command
- **AND** response payload is <150 bytes (vs ~400 for full state)
- **AND** response time is <20ms
- **AND** suitable for 50Hz polling without network overhead

#### Scenario: Client performs health check
- **WHEN** client sends `GET http://localhost:5000/api/health`
- **THEN** server responds with HTTP 200 + JSON `{status: "ok", api_version: "1.0"}`
- **AND** response time is <5ms

### Requirement: StateExporter converts DeviceState to JSON

The system SHALL provide a StateExporter class that converts immutable DeviceState objects to dictionaries and JSON without modifying emulator behavior.

#### Scenario: Export full state as dictionary
- **WHEN** StateExporter.get_state_dict() is called
- **THEN** returns Dict[str, Any] with all DeviceState fields
- **AND** enum values are converted to lowercase strings
- **AND** dataclass objects are converted to nested dictionaries
- **AND** timestamp and API version are added as _metadata
- **AND** original DeviceState object remains unchanged

#### Scenario: Export state as JSON string
- **WHEN** StateExporter.get_state_json() is called
- **THEN** returns valid JSON string (UTF-8 encoded)
- **AND** JSON is indented for human readability
- **AND** can be parsed by standard JSON parsers
- **AND** includes all fields from get_state_dict()

#### Scenario: Export compact summary
- **WHEN** StateExporter.export_summary() is called
- **THEN** returns Dict with essential fields only
- **AND** payload includes: guide positions, reeler speeds, sag sensors, lamps, cameras, system status
- **AND** payload is <150 bytes
- **AND** suitable for high-frequency polling (50Hz+)

### Requirement: API server runs in background thread

The system SHALL run HTTP API in a daemon thread that does not block serial communication.

#### Scenario: API server starts with emulator
- **WHEN** EmulatorEngine is initialized with enable_api=True
- **THEN** APIServer is created and started in a background daemon thread
- **AND** Flask app is created with CORS headers enabled
- **AND** routes are registered: /api/state, /api/state/summary, /health
- **AND** main serial event loop is not blocked
- **AND** API server is ready to accept requests

#### Scenario: API serves requests while emulator processes commands
- **WHEN** visualization polls /api/state every 100ms
- **AND** simultaneously LabVIEW sends serial commands
- **THEN** both operations proceed without latency interference
- **AND** serial commands are processed with same timing as before
- **AND** API requests are queued by Flask thread pool
- **AND** state reads are atomic (Python GIL protection)

#### Scenario: API port is configurable
- **WHEN** APIServer is instantiated with port=5001
- **THEN** server binds to 0.0.0.0:5001 instead of default 5000
- **AND** main.py --api-port 5001 overrides default
- **AND** multiple emulators can run on different ports simultaneously

### Requirement: API enables browser client access

The system SHALL include CORS headers and error handling to support visualization clients running in web browsers.

#### Scenario: Browser client fetches API
- **WHEN** HTML/JS visualization sends fetch('/api/state') from browser
- **THEN** Flask includes CORS headers in response
- **AND** browser receives JSON response without CORS errors
- **AND** visualization can parse and display data

#### Scenario: Browser handles preflight requests
- **WHEN** browser sends OPTIONS request to /api/state (CORS preflight)
- **THEN** Flask responds with HTTP 200 + CORS headers
- **AND** actual GET request is allowed

#### Scenario: API handles errors gracefully
- **WHEN** StateExporter encounters an error (e.g., corrupted state)
- **THEN** APIServer returns HTTP 500 + JSON {error: "description"}
- **AND** error is logged to emulator logs
- **AND** visualization shows "Connection Error" message

### Requirement: API has zero impact on existing emulator functionality

The system SHALL add HTTP API without modifying serial communication, opcode handling, or state mutation logic.

#### Scenario: All existing tests pass unchanged
- **WHEN** pytest firmware_emulator/tests/ is run
- **THEN** all 40+ existing tests pass without modification
- **AND** no changes are required to test code
- **AND** no new test failures are introduced

#### Scenario: Serial communication timing is unaffected
- **WHEN** LabVIEW sends commands to serial port
- **THEN** emulator responds with same latency as Phase 1
- **AND** no commands are dropped or delayed
- **AND** API polling does not cause serial hiccups

#### Scenario: Emulator works without API
- **WHEN** EmulatorEngine is created with enable_api=False
- **THEN** emulator functions normally without HTTP server
- **AND** no errors or warnings are logged
- **AND** useful for testing without Flask dependency
