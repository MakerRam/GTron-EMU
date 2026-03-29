# Firmware Opcodes Reference

Complete reference of all 75 firmware opcodes implemented in the emulator.

**Last Updated**: March 29, 2026  
**Total Opcodes**: 75 (30 specification required + 45 phase 1 enhancements)  
**Specification Compliance**: 100% ✓

## Table of Contents

### Specification Required (30 opcodes)
1. [Communication & Control](#communication--control) - 9 opcodes
2. [Door & Lock Control](#door--lock-control) - 4 opcodes
3. [Machine Control](#machine-control) - 5 opcodes
4. [Hardware Button Control](#hardware-button-control) - 8 opcodes
5. [Interrupt Trigger Events](#interrupt-trigger-events) - 5 opcodes

### Phase 1 Enhancements (45 opcodes)
6. [Guide Motor Control (Top)](#guide-motor-control-top) - 4 opcodes
7. [Guide Motor Control (Bottom)](#guide-motor-control-bottom) - 4 opcodes
8. [Limit Switch Status](#limit-switch-status) - 2 opcodes
9. [Sensor Control](#sensor-control) - 4 opcodes
10. [Encoder Control (Top)](#encoder-control-top) - 6 opcodes
11. [Encoder Control (Bottom)](#encoder-control-bottom) - 6 opcodes
12. [Light & Camera Sequences](#light--camera-sequences) - 5 opcodes
13. [Sensor Power Control](#sensor-power-control) - 3 opcodes
14. [Tower Lamps](#tower-lamps) - 8 opcodes
15. [System Control](#system-control) - 3 opcodes

---

## SPECIFICATION REQUIRED OPCODES

### Communication & Control

#### QUERY
**Type**: Specification Required  
**Purpose**: Ping/handshake command to verify device is alive  
**Response**: `YES`  
**State Changes**: None  
**Usage**: Initial communication check, device availability verification  
**Protocol**: 5-byte ASCII

#### SMINI
**Type**: Specification Required  
**Purpose**: Initialize communication board  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Board setup and initialization  
**Protocol**: 5-byte ASCII

#### RUN
**Type**: Specification Required  
**Purpose**: Run/Start machine command  
**Response**: (empty)  
**State Changes**: None (in Phase 1; Phase 2 will track run state)  
**Usage**: Start machine operation  
**Protocol**: 5-byte ASCII

#### STP
**Type**: Specification Required  
**Purpose**: Stop machine command  
**Response**: (empty)  
**State Changes**: None (in Phase 1; Phase 2 will stop all motors)  
**Usage**: Stop all machine operations  
**Protocol**: 5-byte ASCII

#### PAU
**Type**: Specification Required  
**Purpose**: Pause machine command  
**Response**: (empty)  
**State Changes**: None (in Phase 1; Phase 2 will pause motors)  
**Usage**: Pause current machine operation  
**Protocol**: 5-byte ASCII

#### MIRSP
**Type**: Specification Required  
**Purpose**: Machine interface response  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Acknowledge machine interface communication  
**Protocol**: 5-byte ASCII

#### GRD
**Type**: Specification Required  
**Purpose**: Ground/Reference command  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Reset to ground state  
**Protocol**: 5-byte ASCII

#### FLS
**Type**: Specification Required  
**Purpose**: Error/failure response (standard failure response)  
**Response**: `FLS`  
**State Changes**: None  
**Usage**: Indicates operation failed or opcode unknown  
**Protocol**: 5-byte ASCII

#### HWBDB
**Type**: Specification Required  
**Purpose**: Hardware button debug  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Debug hardware button status  
**Protocol**: 5-byte ASCII

### Door & Lock Control

#### DOORC
**Type**: Specification Required  
**Purpose**: Check door lock status  
**Response**: 
- `DL1` - Door is locked
- `DL0` - Door is unlocked
**State Changes**: None  
**Usage**: Query current door lock status  
**Protocol**: 5-byte ASCII

#### ATDRL
**Type**: Specification Required  
**Purpose**: Attach/Enable door lock  
**Response**: (empty)  
**State Changes**: Sets `door_locked = True`  
**Usage**: Lock the door  
**Protocol**: 5-byte ASCII

#### DTDRL
**Type**: Specification Required  
**Purpose**: Detach/Disable door lock  
**Response**: (empty)  
**State Changes**: Sets `door_locked = False`  
**Usage**: Unlock the door  
**Protocol**: 5-byte ASCII

#### DUL
**Type**: Specification Required  
**Purpose**: Door unlock  
**Response**: (empty)  
**State Changes**: Sets `door_locked = False`  
**Usage**: Unlock door (alternative to DTDRL)  
**Protocol**: 5-byte ASCII

### Machine Control

#### DHBLS
**Type**: Specification Required  
**Purpose**: Disable all hardware buttons and sensors  
**Response**: (empty)  
**State Changes**: Disables all sensors and encoders  
**Usage**: Emergency disable of inputs  
**Protocol**: 5-byte ASCII

#### RFS01
**Type**: Specification Required  
**Purpose**: Reference search command  
**Response**: `TRD01` (Done)  
**State Changes**: None  
**Usage**: Initiate reference search sequence  
**Protocol**: 5-byte ASCII

#### BOF
**Type**: Specification Required  
**Purpose**: Buzzer off  
**Response**: (empty)  
**State Changes**: Sets `lamps.buzzer = False`  
**Usage**: Turn off buzzer  
**Protocol**: 5-byte ASCII

#### BOFDR
**Type**: Specification Required  
**Purpose**: Buzzer off debug response  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Debug response for buzzer control  
**Protocol**: 5-byte ASCII

#### BOFER
**Type**: Specification Required  
**Purpose**: Buzzer off error response  
**Response**: `FLS` (error)  
**State Changes**: None  
**Usage**: Error response for buzzer operations  
**Protocol**: 5-byte ASCII

### Hardware Button Control

#### ATRUN
**Type**: Specification Required  
**Purpose**: Attach/Enable RUN button interrupt  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Enable RUN button for interrupt handling  
**Protocol**: 5-byte ASCII

#### DTRUN
**Type**: Specification Required  
**Purpose**: Detach/Disable RUN button interrupt  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Disable RUN button interrupt  
**Protocol**: 5-byte ASCII

#### ATPAU
**Type**: Specification Required  
**Purpose**: Attach/Enable PAUSE button interrupt  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Enable PAUSE button for interrupt handling  
**Protocol**: 5-byte ASCII

#### DTPAU
**Type**: Specification Required  
**Purpose**: Detach/Disable PAUSE button interrupt  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Disable PAUSE button interrupt  
**Protocol**: 5-byte ASCII

#### ATSTP
**Type**: Specification Required  
**Purpose**: Attach/Enable STOP button interrupt  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Enable STOP button for interrupt handling  
**Protocol**: 5-byte ASCII

#### DTSTP
**Type**: Specification Required  
**Purpose**: Detach/Disable STOP button interrupt  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Disable STOP button interrupt  
**Protocol**: 5-byte ASCII

#### ATBOF
**Type**: Specification Required  
**Purpose**: Attach/Enable BUZZER OFF button interrupt  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Enable BUZZER OFF button for interrupt handling  
**Protocol**: 5-byte ASCII

#### DTBOF
**Type**: Specification Required  
**Purpose**: Detach/Disable BUZZER OFF button interrupt  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Disable BUZZER OFF button interrupt  
**Protocol**: 5-byte ASCII

### Interrupt Trigger Events

#### IESEL
**Type**: Specification Required  
**Purpose**: Select button pressed - interrupt trigger  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Hardware button notification from machine  
**Note**: These are interrupt triggers FROM the machine, not commands TO it  
**Protocol**: 5-byte ASCII

#### IERUN
**Type**: Specification Required  
**Purpose**: Run button pressed - interrupt trigger  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Hardware button notification from machine  
**Protocol**: 5-byte ASCII

#### IEPAU
**Type**: Specification Required  
**Purpose**: Pause button pressed - interrupt trigger  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Hardware button notification from machine  
**Protocol**: 5-byte ASCII

#### IEPAS
**Type**: Specification Required  
**Purpose**: Pass/Success event - interrupt trigger  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Machine event notification (operation succeeded)  
**Protocol**: 5-byte ASCII

#### IEFAI
**Type**: Specification Required  
**Purpose**: Fail/Error event - interrupt trigger  
**Response**: (empty)  
**State Changes**: None  
**Usage**: Machine event notification (operation failed)  
**Protocol**: 5-byte ASCII

---

## PHASE 1 ENHANCEMENT OPCODES

### Guide Motor Control (Top)

#### TPGOP
**Type**: Phase 1 Enhancement  
**Purpose**: Open top guide motor  
**Response**: `TPGOR` (Guide Open Response)  
**State Changes**: Sets `guide_top.position = GuidePosition.OPEN`  
**Usage**: Open the top guide  
**Future Enhancement**: Parameter parsing for position control  
**Protocol**: 5-byte ASCII

#### TPGCL
**Type**: Phase 1 Enhancement  
**Purpose**: Close top guide motor  
**Response**: `TPGCR` (Guide Close Response)  
**State Changes**: Sets `guide_top.position = GuidePosition.CLOSED`  
**Usage**: Close the top guide  
**Future Enhancement**: Parameter parsing for position control  
**Protocol**: 5-byte ASCII

#### TPRTR
**Type**: Phase 1 Enhancement  
**Purpose**: Rotate top reeler motor  
**Response**: (empty)  
**State Changes**: Sets `reeler_top.running = True`  
**Usage**: Start rotating top reeler  
**Future Enhancement**: Timing simulation, step tracking  
**Protocol**: 5-byte ASCII

#### TPGDI
**Type**: Phase 1 Enhancement  
**Purpose**: Set guide distance index (motor steps for ready positions)  
**Response**: (empty)  
**State Changes**: None (Phase 1)  
**Usage**: Configure guide motor step distances  
**Future Enhancement**: Parameter parsing for distance values  
**Protocol**: 5-byte ASCII

### Guide Motor Control (Bottom)

#### BMGOP
**Type**: Phase 1 Enhancement  
**Purpose**: Open bottom guide motor  
**Response**: `BMGOR` (Guide Open Response)  
**State Changes**: Sets `guide_bottom.position = GuidePosition.OPEN`  
**Usage**: Open the bottom guide  
**Future Enhancement**: Parameter parsing for position control  
**Protocol**: 5-byte ASCII

#### BMGCL
**Type**: Phase 1 Enhancement  
**Purpose**: Close bottom guide motor  
**Response**: `BMGCR` (Guide Close Response)  
**State Changes**: Sets `guide_bottom.position = GuidePosition.CLOSED`  
**Usage**: Close the bottom guide  
**Future Enhancement**: Parameter parsing for position control  
**Protocol**: 5-byte ASCII

#### BMRTR
**Type**: Phase 1 Enhancement  
**Purpose**: Rotate bottom reeler motor  
**Response**: (empty)  
**State Changes**: Sets `reeler_bottom.running = True`  
**Usage**: Start rotating bottom reeler  
**Future Enhancement**: Timing simulation, step tracking  
**Protocol**: 5-byte ASCII

#### BMGDI
**Type**: Phase 1 Enhancement  
**Purpose**: Set bottom guide distance index  
**Response**: (empty)  
**State Changes**: None (Phase 1)  
**Usage**: Configure guide motor step distances  
**Future Enhancement**: Parameter parsing for distance values  
**Protocol**: 5-byte ASCII

### Limit Switch Status

#### TPLSC
**Type**: Phase 1 Enhancement  
**Purpose**: Check top limit switch status  
**Response**: 
- `TPOL1` - Limit switch pressed
- `TPOL0` - Limit switch not pressed
**State Changes**: None  
**Usage**: Query limit switch status  
**Protocol**: 5-byte ASCII

#### BMLSC
**Type**: Phase 1 Enhancement  
**Purpose**: Check bottom limit switch status  
**Response**: 
- `BMOL1` - Limit switch pressed
- `BMOL0` - Limit switch not pressed
**State Changes**: None  
**Usage**: Query limit switch status  
**Protocol**: 5-byte ASCII

### Sensor Control

#### TPATS
**Type**: Phase 1 Enhancement  
**Purpose**: Attach/Enable top sensor  
**Response**: (empty)  
**State Changes**: Sets `sensor_top.attached = True`, `sensor_top.powered = True`  
**Usage**: Activate top sensor  
**Protocol**: 5-byte ASCII

#### TPDTS
**Type**: Phase 1 Enhancement  
**Purpose**: Detach/Disable top sensor  
**Response**: (empty)  
**State Changes**: Sets `sensor_top.attached = False`, `sensor_top.powered = False`  
**Usage**: Deactivate top sensor  
**Protocol**: 5-byte ASCII

#### BMATS
**Type**: Phase 1 Enhancement  
**Purpose**: Attach/Enable bottom sensor  
**Response**: (empty)  
**State Changes**: Sets `sensor_bottom.attached = True`, `sensor_bottom.powered = True`  
**Usage**: Activate bottom sensor  
**Protocol**: 5-byte ASCII

#### BMDTS
**Type**: Phase 1 Enhancement  
**Purpose**: Detach/Disable bottom sensor  
**Response**: (empty)  
**State Changes**: Sets `sensor_bottom.attached = False`, `sensor_bottom.powered = False`  
**Usage**: Deactivate bottom sensor  
**Protocol**: 5-byte ASCII

### Encoder Control (Top)

#### TPENI
**Type**: Phase 1 Enhancement  
**Purpose**: Initialize top encoder  
**Response**: (empty)  
**State Changes**: Sets `encoder_top.initialized = True`  
**Usage**: Prepare top encoder for operation  
**Protocol**: 5-byte ASCII

#### TPEEN
**Type**: Phase 1 Enhancement  
**Purpose**: Enable top encoder  
**Response**: (empty)  
**State Changes**: Sets `encoder_top.enabled = True`  
**Usage**: Activate top encoder  
**Protocol**: 5-byte ASCII

#### TPEDB
**Type**: Phase 1 Enhancement  
**Purpose**: Disable top encoder  
**Response**: (empty)  
**State Changes**: Sets `encoder_top.enabled = False`  
**Usage**: Deactivate top encoder  
**Protocol**: 5-byte ASCII

#### TPRSP
**Type**: Phase 1 Enhancement  
**Purpose**: Set encoder starting position  
**Response**: (empty)  
**State Changes**: Sets `encoder_top.position = 0`  
**Usage**: Reset encoder position counter  
**Protocol**: 5-byte ASCII

#### TPRTH
**Type**: Phase 1 Enhancement  
**Purpose**: Set encoder teeth/resolution  
**Response**: (empty)  
**State Changes**: None (Phase 1)  
**Usage**: Configure encoder resolution  
**Future Enhancement**: Parameter parsing for teeth count  
**Protocol**: 5-byte ASCII

#### TPINA
**Type**: Phase 1 Enhancement  
**Purpose**: Set encoder index  
**Response**: (empty)  
**State Changes**: Sets `encoder_top.initial_angle = 0`  
**Usage**: Set encoder initial angle  
**Protocol**: 5-byte ASCII

### Encoder Control (Bottom)

#### BMENI
**Type**: Phase 1 Enhancement  
**Purpose**: Initialize bottom encoder  
**Response**: (empty)  
**State Changes**: Sets `encoder_bottom.initialized = True`  
**Usage**: Prepare bottom encoder for operation  
**Protocol**: 5-byte ASCII

#### BMEEN
**Type**: Phase 1 Enhancement  
**Purpose**: Enable bottom encoder  
**Response**: (empty)  
**State Changes**: Sets `encoder_bottom.enabled = True`  
**Usage**: Activate bottom encoder  
**Protocol**: 5-byte ASCII

#### BMEDB
**Type**: Phase 1 Enhancement  
**Purpose**: Disable bottom encoder  
**Response**: (empty)  
**State Changes**: Sets `encoder_bottom.enabled = False`  
**Usage**: Deactivate bottom encoder  
**Protocol**: 5-byte ASCII

#### BMRSP
**Type**: Phase 1 Enhancement  
**Purpose**: Set bottom encoder starting position  
**Response**: (empty)  
**State Changes**: Sets `encoder_bottom.position = 0`  
**Usage**: Reset encoder position counter  
**Protocol**: 5-byte ASCII

#### BMRTH
**Type**: Phase 1 Enhancement  
**Purpose**: Set bottom encoder teeth/resolution  
**Response**: (empty)  
**State Changes**: None (Phase 1)  
**Usage**: Configure encoder resolution  
**Future Enhancement**: Parameter parsing for teeth count  
**Protocol**: 5-byte ASCII

#### BMINA
**Type**: Phase 1 Enhancement  
**Purpose**: Set bottom encoder index  
**Response**: (empty)  
**State Changes**: Sets `encoder_bottom.initial_angle = 0`  
**Usage**: Set encoder initial angle  
**Protocol**: 5-byte ASCII

### Light & Camera Sequences

#### LCS01
**Type**: Phase 1 Enhancement  
**Purpose**: Trigger light-camera sequence 1  
**Response**: (empty)  
**State Changes**: Sets `cameras.flags[0] = True`, `cameras.active_sequence = 1`  
**Usage**: Activate camera/light sequence 1  
**Future Enhancement**: Timing simulation, frame generation  
**Protocol**: 5-byte ASCII

#### LCS02
**Type**: Phase 1 Enhancement  
**Purpose**: Trigger light-camera sequence 2  
**Response**: (empty)  
**State Changes**: Sets `cameras.flags[1] = True`, `cameras.active_sequence = 2`  
**Usage**: Activate camera/light sequence 2  
**Protocol**: 5-byte ASCII

#### LCS03
**Type**: Phase 1 Enhancement  
**Purpose**: Trigger light-camera sequence 3  
**Response**: (empty)  
**State Changes**: Sets `cameras.flags[2] = True`, `cameras.active_sequence = 3`  
**Usage**: Activate camera/light sequence 3  
**Protocol**: 5-byte ASCII

#### LCSTP
**Type**: Phase 1 Enhancement  
**Purpose**: Trigger all light-camera sequences  
**Response**: (empty)  
**State Changes**: Sets all camera flags, `cameras.active_sequence = -1` (all)  
**Usage**: Activate all camera/light sequences  
**Protocol**: 5-byte ASCII

#### LCSBM
**Type**: Phase 1 Enhancement  
**Purpose**: Trigger bottom light-camera sequences  
**Response**: (empty)  
**State Changes**: Sets bottom camera flags, `cameras.active_sequence = 2` (bottom)  
**Usage**: Activate bottom camera/light sequences  
**Protocol**: 5-byte ASCII

### Sensor Power Control

#### POS01
**Type**: Phase 1 Enhancement  
**Purpose**: Power on sensor 1  
**Response**: (empty)  
**State Changes**: Sets `sensor_top.powered = True`  
**Usage**: Enable power to sensor 1  
**Protocol**: 5-byte ASCII

#### POS02
**Type**: Phase 1 Enhancement  
**Purpose**: Power on sensor 2  
**Response**: (empty)  
**State Changes**: Sets `sensor_bottom.powered = True`  
**Usage**: Enable power to sensor 2  
**Protocol**: 5-byte ASCII

#### POS03
**Type**: Phase 1 Enhancement  
**Purpose**: Power on sensor 3  
**Response**: (empty)  
**State Changes**: None (Phase 1)  
**Usage**: Enable power to sensor 3 (reserved)  
**Protocol**: 5-byte ASCII

### Tower Lamps

#### TRED1
**Type**: Phase 1 Enhancement  
**Purpose**: Turn red tower lamp ON  
**Response**: (empty)  
**State Changes**: Sets `lamps.red = True`  
**Usage**: Activate red indicator lamp  
**Protocol**: 5-byte ASCII

#### TRED0
**Type**: Phase 1 Enhancement  
**Purpose**: Turn red tower lamp OFF  
**Response**: (empty)  
**State Changes**: Sets `lamps.red = False`  
**Usage**: Deactivate red indicator lamp  
**Protocol**: 5-byte ASCII

#### TYEL1
**Type**: Phase 1 Enhancement  
**Purpose**: Turn yellow tower lamp ON  
**Response**: (empty)  
**State Changes**: Sets `lamps.yellow = True`  
**Usage**: Activate yellow indicator lamp  
**Protocol**: 5-byte ASCII

#### TYEL0
**Type**: Phase 1 Enhancement  
**Purpose**: Turn yellow tower lamp OFF  
**Response**: (empty)  
**State Changes**: Sets `lamps.yellow = False`  
**Usage**: Deactivate yellow indicator lamp  
**Protocol**: 5-byte ASCII

#### TGRN1
**Type**: Phase 1 Enhancement  
**Purpose**: Turn green tower lamp ON  
**Response**: (empty)  
**State Changes**: Sets `lamps.green = True`  
**Usage**: Activate green indicator lamp  
**Protocol**: 5-byte ASCII

#### TGRN0
**Type**: Phase 1 Enhancement  
**Purpose**: Turn green tower lamp OFF  
**Response**: (empty)  
**State Changes**: Sets `lamps.green = False`  
**Usage**: Deactivate green indicator lamp  
**Protocol**: 5-byte ASCII

#### TBZR1
**Type**: Phase 1 Enhancement  
**Purpose**: Turn buzzer ON  
**Response**: (empty)  
**State Changes**: Sets `lamps.buzzer = True`  
**Usage**: Activate buzzer  
**Protocol**: 5-byte ASCII

#### TBZR0
**Type**: Phase 1 Enhancement  
**Purpose**: Turn buzzer OFF  
**Response**: (empty)  
**State Changes**: Sets `lamps.buzzer = False`  
**Usage**: Deactivate buzzer  
**Protocol**: 5-byte ASCII

### System Control

#### TPSTP
**Type**: Phase 1 Enhancement  
**Purpose**: Shutdown/Stop command  
**Response**: (empty)  
**State Changes**: None  
**Usage**: System shutdown  
**Protocol**: 5-byte ASCII

#### TPSTR
**Type**: Phase 1 Enhancement  
**Purpose**: Status/State response  
**Response**: `TPSTR`  
**State Changes**: None  
**Usage**: Query system status  
**Protocol**: 5-byte ASCII

---

## Summary by Category

| Category | Count | Status |
|----------|-------|--------|
| Communication & Control | 9 | ✓ Spec Required |
| Door & Lock Control | 4 | ✓ Spec Required |
| Machine Control | 5 | ✓ Spec Required |
| Hardware Button Control | 8 | ✓ Spec Required |
| Interrupt Trigger Events | 5 | ✓ Spec Required |
| Guide Motors (Top) | 4 | Phase 1 Enhancement |
| Guide Motors (Bottom) | 4 | Phase 1 Enhancement |
| Limit Switch Status | 2 | Phase 1 Enhancement |
| Sensor Control | 4 | Phase 1 Enhancement |
| Encoder Control (Top) | 6 | Phase 1 Enhancement |
| Encoder Control (Bottom) | 6 | Phase 1 Enhancement |
| Light & Camera Sequences | 5 | Phase 1 Enhancement |
| Sensor Power Control | 3 | Phase 1 Enhancement |
| Tower Lamps | 8 | Phase 1 Enhancement |
| System Control | 3 | Phase 1 Enhancement |
| **TOTAL** | **75** | **Complete** |

---

## Response Protocol

All opcodes follow the 5-byte ASCII protocol:

**Request Format:**
```
[5 bytes ASCII] → Opcode name (e.g., "TPGOP")
```

**Response Format:**
```
[Response string] → Padded/truncated to 5 bytes ASCII
Example: "TPGOR" → "TPGOR" (exactly 5 bytes)
Example: "YES" → "YES  " (padded with spaces to 5 bytes)
Example: "" → "     " (empty response = 5 spaces)
```

---

## State Management

All opcodes follow an immutable state pattern:

```python
handler(state: DeviceState) → (response: str, new_state: DeviceState)
```

Key principles:
- ✓ Original state is never mutated
- ✓ Each handler returns a new state copy
- ✓ State transitions are isolated and traceable
- ✓ No side effects or global state changes

---

## Error Handling

**Unknown Opcodes:**
- Return: `FLS` (standard failure response)
- State: Unchanged

**Invalid Command Format:**
- Must be exactly 5 bytes
- Return: `FLS`
- State: Unchanged

---

## Future Enhancements (Phase 2+)

### Parameter Parsing
- TPGDI, BMGDI: Distance parameters for guide motors
- TPRTH, BMRTH: Tooth count for encoder resolution
- Motor control with actual step counts and timing

### Event Simulation
- Motor movement with realistic timing
- Sensor trigger simulation
- Encoder position tracking
- Camera frame generation

### Device Diagnostics
- Hardware status reporting
- Error condition simulation
- Performance metrics

---

**Document Version**: 2.0  
**Last Updated**: March 29, 2026  
**Status**: Complete - 75 opcodes, 100% specification compliant
