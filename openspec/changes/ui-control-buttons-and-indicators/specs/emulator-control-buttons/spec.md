## ADDED Requirements

### Requirement: Dashboard provides Run, Pause, Stop, and Buzzer Off control buttons
The dashboard SHALL display a control buttons panel with Run, Pause, Stop, and Buzzer Off buttons, each with a status light indicator showing current state.

#### Scenario: Control buttons panel is visible on dashboard
- **WHEN** user opens the dashboard in a browser
- **THEN** a control buttons panel is displayed with 4 buttons: Run, Pause, Stop, Buzzer Off
- **AND** each button has an adjacent status light indicator (circular dot)
- **AND** the panel uses the same dark industrial styling as existing panels

#### Scenario: Run button sends run command
- **WHEN** user clicks the "Run" button
- **THEN** the dashboard sends `POST /api/command` with `{"command": "EMRUN"}`
- **AND** the Run status light turns green (active)
- **AND** the Pause and Stop status lights turn off (grey)

#### Scenario: Pause button sends pause command
- **WHEN** user clicks the "Pause" button
- **THEN** the dashboard sends `POST /api/command` with `{"command": "EMPAU"}`
- **AND** the Pause status light turns yellow (active)
- **AND** the Run status light turns off

#### Scenario: Stop button sends stop command
- **WHEN** user clicks the "Stop" button
- **THEN** the dashboard sends `POST /api/command` with `{"command": "EMSTP"}`
- **AND** the Stop status light turns red (active)
- **AND** the Run and Pause status lights turn off

#### Scenario: Buzzer Off button sends buzzer silence command
- **WHEN** user clicks the "Buzzer Off" button
- **THEN** the dashboard sends `POST /api/command` with `{"command": "BZZOF"}`
- **AND** the Buzzer Off status light turns green (buzzer silenced)

#### Scenario: Status lights reflect current emulator state from polling
- **WHEN** the dashboard polls `/api/state` and receives `run_state` field
- **THEN** the control button status lights update to match the current state
- **AND** only the active state's light is illuminated (Run=green, Pause=yellow, Stop=red)

#### Scenario: Buzzer Off light reflects buzzer override state
- **WHEN** the dashboard polls `/api/state` and `buzzer_override` is true
- **THEN** the Buzzer Off status light is green
- **AND** when `buzzer_override` is false, the light is grey

#### Scenario: Buttons are debounced to prevent rapid repeated clicks
- **WHEN** user rapidly clicks a control button multiple times within 500ms
- **THEN** only the first click is sent as a command
- **AND** subsequent clicks are ignored until the next state poll confirms the action

### Requirement: Backend handles emulator control opcodes
The emulator SHALL support EMRUN, EMPAU, EMSTP, and BZZOF opcodes for controlling emulator run state and buzzer override.

#### Scenario: EMRUN opcode sets emulator to running state
- **WHEN** emulator receives opcode "EMRUN"
- **THEN** `DeviceState.run_state` is set to RUNNING
- **AND** response "EMROK" is returned
- **AND** the emulator resumes processing serial commands normally

#### Scenario: EMPAU opcode pauses the emulator
- **WHEN** emulator receives opcode "EMPAU"
- **THEN** `DeviceState.run_state` is set to PAUSED
- **AND** response "EMPOK" is returned
- **AND** the emulator stops processing serial commands (queues them)

#### Scenario: EMSTP opcode stops the emulator
- **WHEN** emulator receives opcode "EMSTP"
- **THEN** `DeviceState.run_state` is set to STOPPED
- **AND** response "EMSOK" is returned
- **AND** the emulator stops processing and clears command queue

#### Scenario: BZZOF opcode silences the buzzer
- **WHEN** emulator receives opcode "BZZOF"
- **THEN** `DeviceState.buzzer_override` is set to True
- **AND** `DeviceState.lamps.buzzer` effective state becomes False (silenced)
- **AND** response "BZZOK" is returned

#### Scenario: DeviceState includes run_state and buzzer_override fields
- **WHEN** DeviceState is initialized
- **THEN** `run_state` defaults to RUNNING (enum: RUNNING, PAUSED, STOPPED)
- **AND** `buzzer_override` defaults to False
- **AND** both fields are serialized in `to_dict()` and exported via API
