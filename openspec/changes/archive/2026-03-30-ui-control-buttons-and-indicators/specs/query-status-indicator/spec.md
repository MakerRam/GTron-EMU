## ADDED Requirements

### Requirement: Header displays Query Status indicator
The dashboard header SHALL display a query status light indicator showing whether the emulator is responsive to QUERY opcodes.

#### Scenario: Query status light is visible in header
- **WHEN** user opens the dashboard
- **THEN** a query status indicator (labeled "QRY") appears in the header bar
- **AND** it is positioned between the cycle label and the connection status dot
- **AND** it consists of a colored dot and a short label

#### Scenario: Query status light shows green when emulator is responsive
- **WHEN** the dashboard polls `/api/state` and `query_responsive` is true
- **THEN** the query status dot is green
- **AND** the label shows "QRY OK"

#### Scenario: Query status light shows red when emulator is unresponsive
- **WHEN** the dashboard polls `/api/state` and `query_responsive` is false
- **THEN** the query status dot is red
- **AND** the label shows "QRY FAIL"

#### Scenario: Query status light shows grey when disconnected
- **WHEN** the dashboard is in disconnected state (API unreachable)
- **THEN** the query status dot is grey
- **AND** the label shows "QRY --"

#### Scenario: Query status light updates in mock mode
- **WHEN** the dashboard is in mock mode
- **THEN** the query status dot reflects the `query_responsive` field from mock state data
- **AND** if mock state does not include `query_responsive`, it defaults to true (green)

### Requirement: DeviceState tracks query responsiveness
The DeviceState SHALL include a `query_responsive` boolean field indicating whether the emulator successfully processed the last QUERY opcode.

#### Scenario: query_responsive defaults to true
- **WHEN** DeviceState is initialized
- **THEN** `query_responsive` is True
- **AND** it is included in `to_dict()` output and API state export

#### Scenario: query_responsive is set to false on query timeout
- **WHEN** QUERY opcode processing takes longer than 1 second
- **THEN** `query_responsive` is set to False
- **AND** next successful QUERY resets it to True
