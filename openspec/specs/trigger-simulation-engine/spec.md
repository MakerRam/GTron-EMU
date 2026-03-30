## ADDED Requirements

### Requirement: Simulate sensor trigger events
The emulator SHALL generate sensor trigger events with proper debouncing when commanded.

#### Scenario: Sensor trigger with debounce
- **WHEN** sensor is attached and powered, and a trigger event occurs
- **THEN** emulator applies debounce delay (30ms for top, 50ms for bottom) and fires the trigger only after delay elapses

#### Scenario: Rapid sensor re-triggers ignored
- **WHEN** two sensor triggers occur within debounce window
- **THEN** second trigger is ignored (debounce logic suppresses it)

### Requirement: Simulate encoder pulse counting
The emulator SHALL track encoder position and generate pulse events at configured pitch intervals.

#### Scenario: Encoder position tracking
- **WHEN** encoder is initialized with teeth count and initial angle
- **THEN** emulator tracks encoder position as it increments

#### Scenario: Encoder trigger at pitch boundary
- **WHEN** encoder position crosses a tooth boundary (based on configured teeth)
- **THEN** encoder trigger event fires and camera capture is initiated

### Requirement: Synchronize camera triggers with firmware ISR events
The emulator SHALL signal the virtual camera when ISR events (sensor or encoder) occur, ensuring frame capture is triggered properly.

#### Scenario: Sensor ISR triggers camera
- **WHEN** SetLCtp() ISR would fire in real firmware (sensor rising edge with debounce)
- **THEN** emulator signals virtual camera to capture frame

#### Scenario: Encoder ISR triggers camera
- **WHEN** ISRTrigger_Top() would fire in real firmware (encoder falling edge)
- **THEN** emulator signals virtual camera to capture frame

### Requirement: Support configurable trigger timing
The emulator SHALL allow trigger delays and debounce values to be configured from Machine Interface Parameters.json.

#### Scenario: Load trigger timing from config
- **WHEN** emulator starts
- **THEN** it reads DelayValuesInms and sensor debounce settings from MI JSON

#### Scenario: Apply configured debounce
- **WHEN** sensor trigger occurs
- **THEN** debounce delay from config is applied (not hardcoded)

### Requirement: Phase 2: Asynchronous trigger generation
For advanced scenarios, emulator SHALL support generating periodic triggers to simulate continuous conveyor operation.

#### Scenario: Periodic sensor triggers
- **WHEN** "periodic trigger mode" is enabled
- **THEN** emulator generates sensor triggers at configured intervals (e.g., every 50ms for 1200 parts/min)

#### Scenario: Deterministic trigger replay
- **WHEN** a trigger sequence is recorded
- **THEN** same sequence can be replayed with identical timing and behavior
