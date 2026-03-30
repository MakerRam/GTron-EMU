## ADDED Requirements

### Requirement: Dashboard includes control buttons panel
The visualizer SHALL display a new "Emulator Control" panel with Run, Pause, Stop, and Buzzer Off buttons and their status light indicators.

#### Scenario: Control panel is positioned in dashboard grid
- **WHEN** visualizer is running
- **THEN** a new "Emulator Control" panel appears in the dashboard grid
- **AND** the panel contains 4 buttons arranged horizontally or in a 2x2 grid
- **AND** each button has a colored status light indicator dot

#### Scenario: Control panel uses consistent HMI styling
- **WHEN** user views the control panel
- **THEN** buttons use the dark industrial theme with clear labels
- **AND** Run button has a green accent, Pause has yellow, Stop has red, Buzzer Off has blue
- **AND** status lights use the same indicator dot style as system status panel

### Requirement: Dashboard header includes Query Status indicator
The visualizer SHALL display a query status light in the header bar showing emulator query responsiveness.

#### Scenario: Query status is visible in header
- **WHEN** visualizer is running
- **THEN** a "QRY" status indicator appears in the header between cycle label and connection status
- **AND** the indicator shows a dot + text label

### Requirement: Dashboard displays camera light indicators
The visualizer SHALL show 6 light channel indicators within the Cameras panel.

#### Scenario: Lights section appears below camera grid
- **WHEN** visualizer is running
- **THEN** a "Lights" sub-section appears below the camera flags grid
- **AND** 6 light indicators (L1-L6) are displayed in a row or grid

### Requirement: Phase 2: Interactive pause/resume
The visualizer SHALL allow pausing and resuming the simulation.

#### Scenario: Pause simulation
- **WHEN** user clicks "Pause"
- **THEN** emulator stops processing commands and state does not change
- **AND** the Pause button status light turns yellow

#### Scenario: Resume simulation
- **WHEN** user clicks "Run" (resume)
- **THEN** emulator resumes processing commands
- **AND** the Run button status light turns green
