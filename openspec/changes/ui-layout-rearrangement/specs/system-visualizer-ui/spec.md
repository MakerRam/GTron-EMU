## MODIFIED Requirements

### Requirement: Display current device state
The visualizer SHALL show a real-time view of all device state (motor positions, sensor status, lamp states). The "Emulator Control" panel SHALL be renamed to "Front Panel" to match hardware terminology.

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

#### Scenario: Front Panel heading
- **WHEN** visualizer is running
- **THEN** the control panel heading reads "Front Panel" (not "Emulator Control")
