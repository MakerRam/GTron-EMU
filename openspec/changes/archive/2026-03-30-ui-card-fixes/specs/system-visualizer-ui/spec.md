## MODIFIED Requirements

### Requirement: Display current device state
The visualizer SHALL show a real-time view of all device state. The Cameras panel SHALL display 6 camera indicators (1-6) in a single horizontal row. The Front Panel SHALL display 6 control buttons in a single horizontal row in this order: Power On, Run, Pause, Stop, Buzzer Off, Emergency Exit.

#### Scenario: Camera indicators display
- **WHEN** visualizer is running
- **THEN** the Cameras panel shows exactly 6 camera indicators numbered 1 through 6
- **AND** indicators are displayed in a single horizontal row (not a grid)
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
