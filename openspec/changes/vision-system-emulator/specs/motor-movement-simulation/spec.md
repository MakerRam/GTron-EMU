## ADDED Requirements

### Requirement: Simulate guide motor movement with timing
The emulator SHALL simulate guide motor movement with realistic delays based on configuration.

#### Scenario: Guide open movement delay
- **WHEN** "tpGOP" (guide open) is sent
- **THEN** emulator waits approximately 2000ms (DelayValuesInms.TimingUnitSetup from MI JSON) before marking movement complete and responding "tpGOR"

#### Scenario: Guide close movement delay
- **WHEN** "tpGCL" (guide close) is sent
- **THEN** emulator waits approximately 2000ms before marking movement complete and responding "tpGCR"

### Requirement: Detect and respond to limit switches
The emulator SHALL track when guide position reaches limits and prevent overshoot.

#### Scenario: Open limit switch reached
- **WHEN** guide is commanded to open
- **THEN** emulator sets guide_top.position = OPEN and "tpOL1" response available if "tpLSC" queried

#### Scenario: Close limit switch reached
- **WHEN** guide is commanded to close
- **THEN** emulator sets guide_top.position = CLOSED and "tpOL0" response available if "tpLSC" queried

### Requirement: Support guide discrete positioning
The emulator SHALL support moving guide to specific step positions via tpGDI/bmGDI commands.

#### Scenario: Guide move to position
- **WHEN** "tpGDI" + <steps> is received (e.g., "tpGDI164000" for ready-to-insert position)
- **THEN** emulator calculates movement time based on configured speed and steps, applies delay, then responds with completion

#### Scenario: Guide reached response
- **WHEN** guide movement completes
- **THEN** response "GRD" (guide reached) is available

### Requirement: Simulate reeler motor movement
The emulator SHALL simulate reeler motor speed control and step execution.

#### Scenario: Reeler speed configuration
- **WHEN** "tpRSP" + <speed_value> is received
- **THEN** emulator sets reeler speed and uses it for subsequent movement calculations

#### Scenario: Reeler start and run
- **WHEN** "tpSTR" (start reeler) is received
- **THEN** emulator sets reeler_top.running = true and simulates motor rotation at configured speed

#### Scenario: Reeler stop
- **WHEN** "tpSTP" (stop reeler) is received
- **THEN** emulator sets reeler_top.running = false and responds appropriately

### Requirement: Support reeler interrupt completion
The emulator SHALL track reeler movement and generate completion signals when movement is done.

#### Scenario: Reeler home done
- **WHEN** reeler completes its configured tooth count
- **THEN** response "RHD" (reeler home done) is sent via serial

### Requirement: Calculate movement timing from speed and distance
The emulator SHALL use physics-based calculations to derive realistic movement timing.

#### Scenario: Movement time calculation
- **WHEN** guide is commanded to move N steps at speed S
- **THEN** movement time = (N / S) * 1000ms (approximate, based on firmware behavior)

### Requirement: Phase 2: Simulate motor acceleration/deceleration
For realism in Phase 2, emulator SHALL support ramping speeds rather than instant acceleration.

#### Scenario: Smooth acceleration
- **WHEN** reeler is started
- **THEN** speed ramps from 0 to configured value over configured acceleration time

#### Scenario: Smooth deceleration
- **WHEN** reeler is stopped
- **THEN** speed ramps from current value to 0 over configured deceleration time
