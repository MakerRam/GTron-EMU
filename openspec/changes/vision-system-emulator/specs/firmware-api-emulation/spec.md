## ADDED Requirements

### Requirement: Parse all firmware opcodes
The emulator SHALL parse incoming 5-byte ASCII opcodes from LabVIEW and dispatch them to appropriate handlers.

#### Scenario: Valid opcode received
- **WHEN** LabVIEW sends "QUERY\0" (ping) via serial
- **THEN** firmware emulator receives 5 bytes, identifies QUERY opcode, invokes ping handler

#### Scenario: Unknown opcode handling
- **WHEN** LabVIEW sends an unrecognized 5-byte sequence
- **THEN** firmware emulator returns "FLS" (false/error) response

### Requirement: Execute device commands with state transitions
The emulator SHALL maintain device state and transition it based on received opcodes.

#### Scenario: Guide open command
- **WHEN** LabVIEW sends "tpGOP" (guide open)
- **THEN** firmware emulator sets guide_top.target_position = OPEN and returns "tpGOR" after simulating movement delay

#### Scenario: Guide close command
- **WHEN** LabVIEW sends "tpGCL" (guide close)
- **THEN** firmware emulator sets guide_top.target_position = CLOSED and returns "tpGCR" after simulating movement delay

#### Scenario: Sensor attachment
- **WHEN** LabVIEW sends "tpATS" (attach sensor top)
- **THEN** firmware emulator sets sensor_top.attached = true (no immediate response sent)

#### Scenario: Sensor detachment
- **WHEN** LabVIEW sends "tpDTS" (detach sensor top)
- **THEN** firmware emulator sets sensor_top.attached = false

### Requirement: Implement 70+ opcodes
The emulator SHALL support all opcodes defined in Machine Interface Parameters.json, including:
- Device readiness (QUERY)
- Guide motors (tpGOP, tpGCL, bmGOP, bmGCL, tpGDI, bmGDI)
- Reeler motors (tpRTR, bmRTR, tpRSP, bmRSP, tpRTH, bmRTH, tpSTR, tpSTP, bmSTR, bmSTP)
- Sensors (tpATS, tpDTS, bmATS, bmDTS, POS01-08, TPSCK, BPSCK)
- Encoders (tpENI, bmENI, tpEEN, bmEEN, tpEDB, bmEDB, tpINA, bmINA, tpRTH, bmRTH)
- Light-camera sequences (LCS01-07, LCStp, LCSbm, LCSI0-6, TSENB)
- Tower lamps (TRED1/0, TYEL1/0, TGRN1/0, TBZR1/0)
- Door lock (DOORC, ATDRL, DTDRL)
- E-stop (EMSTP)
- Sag sensors (TPSAG, BMSAG)
- And others as defined in MI JSON

#### Scenario: All opcodes return appropriate responses
- **WHEN** each opcode in the 70+ set is sent
- **THEN** firmware emulator returns the correct response defined in MI JSON (or state change without response where applicable)

### Requirement: Respond with correct timing
The emulator SHALL simulate movement delays based on configuration in Machine Interface Parameters.json.

#### Scenario: Guide open with delay
- **WHEN** "tpGOP" is received
- **THEN** firmware emulator waits DelayValuesInms.TimingUnitSetup (2000ms) before responding "tpGOR"

#### Scenario: Sensor debounce
- **WHEN** sensor trigger fires rapidly (false triggers)
- **THEN** firmware emulator applies debounce delay (30ms for top, 50ms for bottom) and ignores spurious re-triggers

### Requirement: Return proper response format
The emulator SHALL return responses in the exact format expected by LabVIEW (5-byte ASCII strings).

#### Scenario: Standard response
- **WHEN** "tpGOP" command is executed successfully
- **THEN** response is exactly "tpGOR\0" (5 bytes including null terminator)

#### Scenario: Yes/no response
- **WHEN** "QUERY" command is executed
- **THEN** response is exactly "YES\0\0" (padded to 5 bytes)
