## ADDED Requirements

### Requirement: Dashboard renders control button status lights in real-time
The dashboard SHALL update control button status lights based on polled state every 100ms.

#### Scenario: Run state is reflected in control lights
- **WHEN** API state shows `run_state: "running"`
- **THEN** dashboard displays Run button light as green (active)
- **AND** Pause and Stop button lights are grey (inactive)
- **AND** updates within 100ms of state change

#### Scenario: Paused state is reflected in control lights
- **WHEN** API state shows `run_state: "paused"`
- **THEN** dashboard displays Pause button light as yellow (active)
- **AND** Run and Stop button lights are grey (inactive)

#### Scenario: Stopped state is reflected in control lights
- **WHEN** API state shows `run_state: "stopped"`
- **THEN** dashboard displays Stop button light as red (active)
- **AND** Run and Pause button lights are grey (inactive)

### Requirement: Dashboard renders query status indicator in real-time
The dashboard SHALL update the header query status indicator based on polled state.

#### Scenario: Query responsive state updates in real-time
- **WHEN** API state shows `query_responsive: true`
- **THEN** header query dot is green with "QRY OK" text
- **AND** updates within 100ms of state change

#### Scenario: Query unresponsive state updates in real-time
- **WHEN** API state shows `query_responsive: false`
- **THEN** header query dot is red with "QRY FAIL" text

### Requirement: Dashboard renders camera light indicators in real-time
The dashboard SHALL update 6 light channel indicators based on polled state.

#### Scenario: Light channels update in real-time
- **WHEN** API state shows `light_channels: {"1": true, "2": false, ...}`
- **THEN** dashboard updates L1-L6 indicators (green=on, grey=off)
- **AND** each indicator updates independently within 100ms

### Requirement: Dashboard sends control commands via button clicks
The dashboard SHALL send control commands to the emulator when users click control buttons.

#### Scenario: Button click sends POST request
- **WHEN** user clicks "Run" button in the control panel
- **THEN** dashboard sends `POST /api/command` with `{"command": "EMRUN"}`
- **AND** the button is briefly disabled until next state poll
- **AND** if the request fails, an error is logged to console

#### Scenario: Button click in mock mode is no-op
- **WHEN** dashboard is in mock mode and user clicks a control button
- **THEN** no HTTP request is sent
- **AND** the button click is ignored (buttons are visually disabled or greyed out in mock mode)
