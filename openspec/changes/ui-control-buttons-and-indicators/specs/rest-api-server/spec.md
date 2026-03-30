## ADDED Requirements

### Requirement: API state includes emulator control fields
The REST API state response SHALL include `run_state`, `buzzer_override`, `query_responsive`, and `light_channels` fields.

#### Scenario: Full state includes new control fields
- **WHEN** client sends `GET /api/state`
- **THEN** response JSON includes `run_state` (string: "running", "paused", or "stopped")
- **AND** response includes `buzzer_override` (boolean)
- **AND** response includes `query_responsive` (boolean)
- **AND** response includes `light_channels` (object with keys "1"-"6", boolean values)

#### Scenario: Summary state includes new control fields
- **WHEN** client sends `GET /api/state/summary`
- **THEN** response includes `run_state`, `buzzer_override`, `query_responsive`, and `light_channels`
- **AND** response payload remains compact (under 300 bytes total with new fields)

### Requirement: POST /api/command handles emulator control opcodes
The existing `POST /api/command` endpoint SHALL accept EMRUN, EMPAU, EMSTP, and BZZOF opcodes for emulator control.

#### Scenario: Control command is processed via existing endpoint
- **WHEN** client sends `POST /api/command` with `{"command": "EMRUN"}`
- **THEN** the command is dispatched to the opcode handler
- **AND** response includes `{"command": "EMRUN", "response": "EMROK", "status": "ok"}`
- **AND** device state is updated with new run_state

#### Scenario: Invalid control command returns error
- **WHEN** client sends `POST /api/command` with `{"command": "EMXYZ"}`
- **THEN** the opcode handler returns an unknown command response
- **AND** device state is unchanged
