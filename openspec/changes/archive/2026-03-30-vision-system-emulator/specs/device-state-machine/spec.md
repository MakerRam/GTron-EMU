## ADDED Requirements

### Requirement: Track guide motor state
The device state machine SHALL track the position and movement status of guide motors (top and bottom racks).

#### Scenario: Guide position after open command
- **WHEN** "tpGOP" command completes
- **THEN** state.guide_top.position = OPEN

#### Scenario: Guide position after close command
- **WHEN** "tpGCL" command completes
- **THEN** state.guide_top.position = CLOSED

### Requirement: Track reeler motor state
The device state machine SHALL track reeler speed, teeth count, and running status.

#### Scenario: Reeler speed set
- **WHEN** "tpRSP" + <speed_value> is received
- **THEN** state.reeler_top.speed = <speed_value>

#### Scenario: Reeler teeth configured
- **WHEN** "tpRTH" + <teeth_value> is received
- **THEN** state.reeler_top.teeth = <teeth_value>

#### Scenario: Reeler started
- **WHEN** "tpSTR" is received
- **THEN** state.reeler_top.running = true

#### Scenario: Reeler stopped
- **WHEN** "tpSTP" is received
- **THEN** state.reeler_top.running = false

### Requirement: Track sensor attachment state
The device state machine SHALL track which sensors are attached/detached and powered on/off.

#### Scenario: Sensor attached
- **WHEN** "tpATS" (attach sensor top) is received
- **THEN** state.sensor_top.attached = true

#### Scenario: Sensor detached
- **WHEN** "tpDTS" (detach sensor top) is received
- **THEN** state.sensor_top.attached = false

#### Scenario: Sensor powered on
- **WHEN** "POS01" (power on sensor 1) is received
- **THEN** state.sensor_top.powered = true

#### Scenario: Sensor powered off
- **WHEN** "PFS01" (power off sensor 1) is received
- **THEN** state.sensor_top.powered = false

### Requirement: Track encoder state
The device state machine SHALL track encoder initialization, enable/disable status, and configuration.

#### Scenario: Encoder initialized
- **WHEN** "tpENI" (encoder init top) is received
- **THEN** state.encoder_top.initialized = true

#### Scenario: Encoder enabled
- **WHEN** "tpEEN" (encoder enable top) is received
- **THEN** state.encoder_top.enabled = true

#### Scenario: Encoder disabled
- **WHEN** "tpEDB" (encoder disable top) is received
- **THEN** state.encoder_top.enabled = false

### Requirement: Track camera sequence state
The device state machine SHALL track which light-camera sequences are active and whether timestamp logging is enabled.

#### Scenario: Camera sequence flag set
- **WHEN** "LCSI0" is received
- **THEN** state.cameras.flags[0] = true (camera sequence 0 enabled)

#### Scenario: Timestamp enabled
- **WHEN** "TSENB" is received
- **THEN** state.cameras.timestamp_enabled = true

### Requirement: Track lamp state
The device state machine SHALL track the on/off state of all tower lamps and buzzer.

#### Scenario: Red lamp on
- **WHEN** "TRED1" is received
- **THEN** state.lamps.red = true

#### Scenario: Yellow lamp off
- **WHEN** "TYEL0" is received
- **THEN** state.lamps.yellow = false

### Requirement: Track machine-level state
The device state machine SHALL track emergency stop, machine power, door lock, and solenoid states.

#### Scenario: E-stop pressed (simulated)
- **WHEN** state.estop_pressed is set to true
- **THEN** "EMSTP" query returns "MP0" (machine powered off)

#### Scenario: Door locked
- **WHEN** door lock is engaged
- **THEN** "DOORC" query returns "DL1" (door limit switch pressed)

### Requirement: Persistent state across commands
The device state machine SHALL maintain state across multiple commands, creating proper state transitions.

#### Scenario: State persistence
- **WHEN** "tpGOP" is sent, then later "tpLSC" (limit switch check) is sent
- **THEN** limit switch state reflects the previous guide open command result
