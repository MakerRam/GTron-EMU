## ADDED Requirements

### Requirement: Device state is exported in structured JSON format

The system SHALL export device state as JSON following a defined schema that all clients can rely on.

#### Scenario: Full state JSON includes all device components
- **WHEN** /api/state endpoint is called
- **THEN** response includes all device state fields:
  - _metadata: {timestamp, version}
  - guide_top, guide_bottom: {position, moving, reached_limit}
  - reeler_top, reeler_bottom: {speed, teeth, running, position}
  - sensor_top, sensor_bottom: {attached, powered, triggered}
  - encoder_top, encoder_bottom: {initialized, enabled, position, initial_angle, teeth_count}
  - lamps: {red, yellow, green, buzzer}
  - cameras: {flags: {0-6}, active_sequence, timestamp_enabled}
  - sag_top_upper, sag_top_lower, sag_bottom_upper, sag_bottom_lower: bool
  - door_locked, estop_pressed, power_on: bool
  - last_command, last_command_time: string/float
- **AND** no required fields are missing
- **AND** no unexpected fields are added

#### Scenario: Enum values are converted to strings
- **WHEN** state contains GuidePosition.CLOSED enum
- **THEN** JSON representation is "closed" (string)
- **AND** GuidePosition.OPEN → "open"
- **AND** GuidePosition.MOVING → "moving"
- **AND** GuidePosition.UNKNOWN → "unknown"

#### Scenario: Nested objects are converted to nested dicts
- **WHEN** state contains dataclass objects (GuideState, ReelerState, etc)
- **THEN** each becomes a nested dictionary
- **AND** guide_top is {position: "closed", moving: false, reached_limit: false}
- **AND** reeler_top is {speed: 0, teeth: 48, running: false, position: 0}
- **AND** all nesting levels are flattened correctly

#### Scenario: Numeric values have correct types
- **WHEN** state contains numeric fields
- **THEN** integers are JSON numbers (not strings)
- **AND** reeler_top.speed is a number, not "800"
- **AND** encoder_top.position is a number, not "123"

#### Scenario: Boolean values are correct
- **WHEN** state contains boolean fields
- **THEN** JSON represents as true/false (not "true"/"false" strings)
- **AND** door_locked is true or false
- **AND** moving is true or false

### Requirement: Summary state is a compact subset for high-frequency polling

The system SHALL provide /api/state/summary endpoint with essential fields only.

#### Scenario: Summary state includes essential fields
- **WHEN** /api/state/summary is called
- **THEN** response includes only:
  - guide_top, guide_bottom (position only)
  - reeler_top_speed, reeler_bottom_speed
  - sag_top_upper, sag_top_lower, sag_bottom_upper, sag_bottom_lower
  - lamps (full object)
  - camera_flags (dict of 0-6: bool)
  - door_locked, estop_pressed, power_on
  - last_command
- **AND** does not include: reached_limit, teeth, running, position, timestamps, coordinates, etc.

#### Scenario: Summary state is compact
- **WHEN** /api/state/summary response is measured
- **THEN** payload is <150 bytes (vs ~400 for full state)
- **AND** suitable for 50Hz polling without network overhead

#### Scenario: Summary state has correct JSON structure
- **WHEN** summary JSON is parsed
- **THEN** all values are JSON-native types (number, bool, string, object, array)
- **AND** no circular references
- **AND** no undefined values

### Requirement: Metadata is included with every response

The system SHALL include _metadata with timestamp and API version in all state exports.

#### Scenario: Metadata includes version
- **WHEN** state is exported
- **THEN** _metadata.version equals "1.0"
- **AND** client can check version for compatibility

#### Scenario: Metadata includes timestamp
- **WHEN** state is exported
- **THEN** _metadata.timestamp is Unix timestamp (float, seconds since epoch)
- **AND** timestamp is set at export time (not state creation time)
- **AND** timestamp changes with each call

#### Scenario: Metadata is present in both full and summary states
- **WHEN** /api/state or /api/state/summary is called
- **THEN** both responses include _metadata
- **AND** both have timestamp and version

### Requirement: JSON schema is backward compatible

The system SHALL support evolving state without breaking existing clients.

#### Scenario: New fields can be added without breaking clients
- **WHEN** Phase 3 adds new fields (e.g., stepper_position)
- **THEN** clients built for Phase 2 still work
- **AND** they ignore unknown fields (standard JSON behavior)
- **AND** no changes required to existing client code

#### Scenario: Field removal is prevented
- **WHEN** Phase 2 defines field set
- **THEN** no fields from Phase 2 are removed in Phase 3/4
- **AND** deprecated fields are marked as such, not removed
- **AND** clients relying on field always get it

#### Scenario: Required fields are stable
- **WHEN** Phase 2 lists required fields in spec
- **THEN** all required fields are always present in responses
- **AND** never become optional
- **AND** never change data type

### Requirement: JSON is human-readable and debuggable

The system SHALL format JSON for easy inspection by developers and operators.

#### Scenario: JSON is indented for readability
- **WHEN** /api/state response is viewed
- **THEN** JSON is pretty-printed with 2-space indentation
- **AND** each field is on its own line
- **AND** structure is visually clear

#### Scenario: JSON can be logged to files
- **WHEN** operator captures API response for debugging
- **THEN** JSON can be saved to .json file and viewed in editor
- **AND** JSON validators accept the file (valid syntax)
- **AND** can be pretty-printed for inspection

#### Scenario: Large numbers are precise
- **WHEN** timestamp or position values are exported
- **THEN** floating-point numbers maintain precision
- **AND** not rounded or truncated
- **AND** can be round-tripped without loss

### Requirement: NULL/missing values are handled correctly

The system SHALL represent absent values consistently.

#### Scenario: Uninitialized command is null
- **WHEN** last_command has not been set
- **THEN** last_command is null (JSON null value)
- **AND** not empty string, 0, or false
- **AND** client can check "if last_command !== null"

#### Scenario: Initialized fields are always present
- **WHEN** field is initialized (e.g., guide_top.position)
- **THEN** field is always in JSON
- **AND** never omitted
- **AND** has non-null value

#### Scenario: Optional fields that haven't changed have default values
- **WHEN** state is exported for first time
- **THEN** all numeric fields default to 0
- **AND** all boolean fields default to false
- **AND** all enum fields default to first value (e.g., "unknown")
