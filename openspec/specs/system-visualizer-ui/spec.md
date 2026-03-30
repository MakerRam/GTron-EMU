## ADDED Requirements

### Requirement: Display current device state
The visualizer SHALL show a real-time view of all device state (motor positions, sensor status, lamp states). The Cameras panel SHALL display 6 camera indicators (1-6) in a single horizontal row. The Front Panel SHALL display 6 control buttons in a single horizontal row in this order: Power On, Run, Pause, Stop, Buzzer Off, Emergency Exit.

#### Scenario: Guide position display
- **WHEN** visualizer is running
- **THEN** a 2D representation shows guide position (open/closed) for top and bottom racks

#### Scenario: Reeler status display
- **WHEN** reeler is running
- **THEN** visualizer shows reeler spinning indicator and speed value

#### Scenario: Sensor attachment status
- **WHEN** sensor is attached/detached
- **THEN** visualizer highlights sensor as active/inactive

#### Scenario: Camera activity indicator
- **WHEN** camera is triggered
- **THEN** visualizer highlights the corresponding camera momentarily to show capture event
- **AND** the Cameras panel shows exactly 6 camera indicators numbered 1 through 6
- **AND** indicators are displayed in a single horizontal row
- **AND** each indicator uses a dot + label format matching the light channel indicators

#### Scenario: Front Panel buttons display
- **WHEN** visualizer is running
- **THEN** the Front Panel shows 6 buttons in a single horizontal row
- **AND** button order is: PWR ON, RUN, PAUSE, STOP, BZR OFF, E-EXIT
- **AND** each button has a status light indicator and label

#### Scenario: Grid panels do not overlap
- **WHEN** dashboard is viewed on desktop
- **THEN** Tower Lamp panel occupies column 4 row 1 only
- **AND** System Status panel occupies column 4 rows 2-3
- **AND** no panels overlap or hide each other

### Requirement: Show 2D workspace representation
The visualizer SHALL represent the machine workspace showing part positioning and guide width.

#### Scenario: Part position visualization
- **WHEN** part is at a specific guide width
- **THEN** visualizer shows a 2D diagram with part outline and guide gap width

#### Scenario: Guide width adjustment
- **WHEN** guide moves to different position
- **THEN** visualizer updates to show new gap width

### Requirement: Display lamp states
The visualizer SHALL show tower lamp colors and buzzer state.

#### Scenario: Tower lamp colors
- **WHEN** lamps change state
- **THEN** visualizer displays red/yellow/green colors correctly (on = bright, off = dim)

#### Scenario: Buzzer indication
- **WHEN** buzzer is enabled
- **THEN** visualizer shows buzzer active indicator

### Requirement: Display sensor trigger events
The visualizer SHALL log and display sensor trigger events with timestamps.

#### Scenario: Sensor trigger logged
- **WHEN** sensor trigger occurs
- **WHEN** visualizer logs event with timestamp and sensor ID

### Requirement: Display encoder events
The visualizer SHALL show encoder position and trigger count.

#### Scenario: Encoder position tracking
- **WHEN** encoder is enabled and counting
- **THEN** visualizer displays current tooth count and position

### Requirement: Command log
The visualizer SHALL display a log of recent commands sent by LabVIEW.

#### Scenario: Command history
- **WHEN** LabVIEW sends commands
- **THEN** visualizer displays last 20 commands in a scrollable log

#### Scenario: Command responses
- **WHEN** firmware responds to a command
- **THEN** response is displayed next to command in log

### Requirement: Phase 2: Interactive pause/resume
The visualizer SHALL allow pausing and resuming the simulation.

#### Scenario: Pause simulation
- **WHEN** user clicks "Pause"
- **THEN** emulator stops processing commands and state doesn't change

#### Scenario: Resume simulation
- **WHEN** user clicks "Resume"
- **THEN** emulator resumes processing commands

### Requirement: Phase 2: Record/playback controls
The visualizer SHALL provide controls for recording and replaying simulation sessions.

#### Scenario: Record session
- **WHEN** user clicks "Record"
- **THEN** emulator logs all commands, state changes, and timing for later replay

#### Scenario: Playback session
- **WHEN** user selects a recorded session and clicks "Playback"
- **THEN** emulator replays the session with identical behavior
