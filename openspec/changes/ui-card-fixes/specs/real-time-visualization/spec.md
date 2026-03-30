## MODIFIED Requirements

### Requirement: Browser dashboard displays real-time device state

The system SHALL poll the API and render camera state for cameras 1-6 (not 0-6). New control buttons (Power On, Emergency Exit) SHALL send commands via POST /api/command.

#### Scenario: Camera activity displays
- **WHEN** API state shows cameras.flags={"1":true, "2":false, "3":true, "4":false, "5":false, "6":false}
- **THEN** dashboard displays 6 camera indicators (1-6) with active flags highlighted
- **AND** camera 0 does not exist in the UI

#### Scenario: Power On button sends command
- **WHEN** user clicks "PWR ON" button in live mode
- **THEN** system sends POST /api/command with {"command": "PWRON"}
- **AND** button is debounced for 500ms

#### Scenario: Emergency Exit button sends command
- **WHEN** user clicks "E-EXIT" button in live mode
- **THEN** system sends POST /api/command with {"command": "EMEXI"}
- **AND** button is debounced for 500ms

#### Scenario: Mock data uses camera keys 1-6
- **WHEN** mock mode is active
- **THEN** mock_states.json camera flags use keys "1" through "6"
- **AND** camera rendering works identically in mock and live modes
