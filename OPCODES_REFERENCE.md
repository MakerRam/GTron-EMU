# Firmware Opcodes Reference

Complete reference of all 61 firmware opcodes implemented in the emulator.

## Table of Contents
1. [Communication & Handshake](#communication--handshake)
2. [Initialization](#initialization)
3. [Door Lock Control](#door-lock-control)
4. [Guide Motor Control (Top)](#guide-motor-control-top)
5. [Guide Motor Control (Bottom)](#guide-motor-control-bottom)
6. [Limit Switch Status](#limit-switch-status)
7. [Sensor Control](#sensor-control)
8. [Encoder Control](#encoder-control)
9. [Light & Camera Sequences](#light--camera-sequences)
10. [Sensor Power Control](#sensor-power-control)
11. [Tower Lamps](#tower-lamps)
12. [Hardware Button Control](#hardware-button-control)
13. [System Control](#system-control)
14. [Error Handling](#error-handling)

---

## Communication & Handshake

### QUERY
**Purpose**: Ping/handshake command to verify device is alive
**Response**: `YES`
**State Changes**: None
**Usage**: Initial communication check, device availability verification

### SMINI
**Purpose**: Initialize communication board
**Response**: (empty)
**State Changes**: None
**Usage**: Board setup and initialization

---

## Initialization

No additional initialization-only opcodes currently defined.

---

## Door Lock Control

### DOORC
**Purpose**: Check door lock status
**Response**: 
- `DL1` - Door is locked
- `DL0` - Door is unlocked
**State Changes**: None (read-only)
**Usage**: Status polling for door lock

### ATDRL
**Purpose**: Attach/Enable door lock (set locked state)
**Response**: (empty)
**State Changes**: Sets `door_locked = True`
**Usage**: Engage door lock

### DTDRL
**Purpose**: Detach/Disable door lock (set unlocked state)
**Response**: (empty)
**State Changes**: Sets `door_locked = False`
**Usage**: Release door lock

---

## Guide Motor Control (Top)

### tpGOP
**Purpose**: Open top guide motor
**Response**: `tpGOR` (Guide Open Response)
**State Changes**: `guide_top.position = OPEN`
**Usage**: Move top guide to open position

### tpGCL
**Purpose**: Close top guide motor
**Response**: `tpGCR` (Guide Close Response)
**State Changes**: `guide_top.position = CLOSED`
**Usage**: Move top guide to closed position

### tpRTR
**Purpose**: Rotate top reeler motor
**Response**: (empty)
**State Changes**: `reeler_top.running = True`
**Usage**: Start reeler motor rotation

### tpGDI
**Purpose**: Set guide distance index (motor steps for ready positions)
**Response**: (empty)
**State Changes**: None (Phase 1 - accepts command without processing parameters)
**Usage**: Configure motor movement distance
**Note**: Phase 2 will support parameter parsing for step counts

---

## Guide Motor Control (Bottom)

### bmGOP
**Purpose**: Open bottom guide motor
**Response**: `bmGOR` (Guide Open Response)
**State Changes**: `guide_bottom.position = OPEN`
**Usage**: Move bottom guide to open position

### bmGCL
**Purpose**: Close bottom guide motor
**Response**: `bmGCR` (Guide Close Response)
**State Changes**: `guide_bottom.position = CLOSED`
**Usage**: Move bottom guide to closed position

### bmRTR
**Purpose**: Rotate bottom reeler motor
**Response**: (empty)
**State Changes**: `reeler_bottom.running = True`
**Usage**: Start bottom reeler motor rotation

### bmGDI
**Purpose**: Set bottom guide distance index
**Response**: (empty)
**State Changes**: None
**Usage**: Configure bottom motor movement distance
**Note**: Phase 2 will support parameter parsing

---

## Limit Switch Status

### tpLSC
**Purpose**: Check top limit switch status
**Response**:
- `tpOL1` - Limit switch pressed (at limit)
- `tpOL0` - Limit switch not pressed (not at limit)
**State Changes**: None (read-only)
**Usage**: Monitor top limit switch position

### bmLSC
**Purpose**: Check bottom limit switch status
**Response**:
- `bmOL1` - Limit switch pressed (at limit)
- `bmOL0` - Limit switch not pressed (not at limit)
**State Changes**: None (read-only)
**Usage**: Monitor bottom limit switch position

---

## Sensor Control

### tpATS
**Purpose**: Attach/Enable top trigger sensor
**Response**: (empty)
**State Changes**: `sensor_top.attached = True`, `sensor_top.powered = True`
**Usage**: Activate top sensor

### tpDTS
**Purpose**: Detach/Disable top trigger sensor
**Response**: (empty)
**State Changes**: `sensor_top.attached = False`, `sensor_top.powered = False`
**Usage**: Deactivate top sensor

### bmATS
**Purpose**: Attach/Enable bottom trigger sensor
**Response**: (empty)
**State Changes**: `sensor_bottom.attached = True`, `sensor_bottom.powered = True`
**Usage**: Activate bottom sensor

### bmDTS
**Purpose**: Detach/Disable bottom trigger sensor
**Response**: (empty)
**State Changes**: `sensor_bottom.attached = False`, `sensor_bottom.powered = False`
**Usage**: Deactivate bottom sensor

---

## Encoder Control

### tpENI
**Purpose**: Initialize top encoder
**Response**: (empty)
**State Changes**: `encoder_top.initialized = True`
**Usage**: Set up top encoder

### tpEEN
**Purpose**: Enable top encoder
**Response**: (empty)
**State Changes**: `encoder_top.enabled = True`
**Usage**: Start top encoder operation

### tpEDB
**Purpose**: Disable top encoder
**Response**: (empty)
**State Changes**: `encoder_top.enabled = False`
**Usage**: Stop top encoder operation

### tpRSP
**Purpose**: Set top encoder starting position
**Response**: (empty)
**State Changes**: `encoder_top.position = 0`
**Usage**: Reset top encoder position

### tpRTH
**Purpose**: Set top encoder teeth/resolution
**Response**: (empty)
**State Changes**: None (Phase 1)
**Usage**: Configure top encoder resolution
**Note**: Phase 2 will parse parameter for teeth count

### tpINA
**Purpose**: Set top encoder index angle
**Response**: (empty)
**State Changes**: `encoder_top.initial_angle = 0`
**Usage**: Initialize top encoder angle reference

### bmENI
**Purpose**: Initialize bottom encoder
**Response**: (empty)
**State Changes**: `encoder_bottom.initialized = True`
**Usage**: Set up bottom encoder

### bmEEN
**Purpose**: Enable bottom encoder
**Response**: (empty)
**State Changes**: `encoder_bottom.enabled = True`
**Usage**: Start bottom encoder operation

### bmEDB
**Purpose**: Disable bottom encoder
**Response**: (empty)
**State Changes**: `encoder_bottom.enabled = False`
**Usage**: Stop bottom encoder operation

### bmRSP
**Purpose**: Set bottom encoder starting position
**Response**: (empty)
**State Changes**: `encoder_bottom.position = 0`
**Usage**: Reset bottom encoder position

### bmRTH
**Purpose**: Set bottom encoder teeth/resolution
**Response**: (empty)
**State Changes**: None (Phase 1)
**Usage**: Configure bottom encoder resolution

### bmINA
**Purpose**: Set bottom encoder index angle
**Response**: (empty)
**State Changes**: `encoder_bottom.initial_angle = 0`
**Usage**: Initialize bottom encoder angle reference

---

## Light & Camera Sequences

### LCS01
**Purpose**: Trigger light-camera sequence 1
**Response**: (empty)
**State Changes**: `cameras.flags[0] = True`, `cameras.active_sequence = 1`
**Usage**: Activate camera 1 and associated lighting

### LCS02
**Purpose**: Trigger light-camera sequence 2
**Response**: (empty)
**State Changes**: `cameras.flags[1] = True`, `cameras.active_sequence = 2`
**Usage**: Activate camera 2 and associated lighting

### LCS03
**Purpose**: Trigger light-camera sequence 3
**Response**: (empty)
**State Changes**: `cameras.flags[2] = True`, `cameras.active_sequence = 3`
**Usage**: Activate camera 3 and associated lighting

### LCStp
**Purpose**: Trigger all light-camera sequences
**Response**: (empty)
**State Changes**: Activates all 7 camera flags, `cameras.active_sequence = -1`
**Usage**: Activate all cameras and lighting simultaneously

### LCSbm
**Purpose**: Trigger bottom light-camera sequences
**Response**: (empty)
**State Changes**: `cameras.flags[3-5] = True`, `cameras.active_sequence = 2`
**Usage**: Activate bottom cameras and associated lighting

---

## Sensor Power Control

### POS01
**Purpose**: Power on sensor 1
**Response**: (empty)
**State Changes**: `sensor_top.powered = True`
**Usage**: Enable power to top sensor

### POS02
**Purpose**: Power on sensor 2
**Response**: (empty)
**State Changes**: `sensor_bottom.powered = True`
**Usage**: Enable power to bottom sensor

### POS03
**Purpose**: Power on sensor 3
**Response**: (empty)
**State Changes**: None (Phase 1 - generic placeholder)
**Usage**: Enable power to third sensor
**Note**: Phase 2 will implement specific sensor 3 power control

---

## Tower Lamps

### TRED1
**Purpose**: Turn red tower lamp ON
**Response**: (empty)
**State Changes**: `lamps.red = True`
**Usage**: Light red indicator lamp

### TRED0
**Purpose**: Turn red tower lamp OFF
**Response**: (empty)
**State Changes**: `lamps.red = False`
**Usage**: Extinguish red indicator lamp

### TYEL1
**Purpose**: Turn yellow tower lamp ON
**Response**: (empty)
**State Changes**: `lamps.yellow = True`
**Usage**: Light yellow indicator lamp

### TYEL0
**Purpose**: Turn yellow tower lamp OFF
**Response**: (empty)
**State Changes**: `lamps.yellow = False`
**Usage**: Extinguish yellow indicator lamp

### TGRN1
**Purpose**: Turn green tower lamp ON
**Response**: (empty)
**State Changes**: `lamps.green = True`
**Usage**: Light green indicator lamp

### TGRN0
**Purpose**: Turn green tower lamp OFF
**Response**: (empty)
**State Changes**: `lamps.green = False`
**Usage**: Extinguish green indicator lamp

### TBZR1
**Purpose**: Turn buzzer ON
**Response**: (empty)
**State Changes**: `lamps.buzzer = True`
**Usage**: Enable audible alert

### TBZR0
**Purpose**: Turn buzzer OFF
**Response**: (empty)
**State Changes**: `lamps.buzzer = False`
**Usage**: Disable audible alert

---

## Hardware Button Control

### ATRUN
**Purpose**: Attach/Enable RUN button interrupt
**Response**: (empty)
**State Changes**: None
**Usage**: Enable RUN button processing

### DTRUN
**Purpose**: Detach/Disable RUN button interrupt
**Response**: (empty)
**State Changes**: None
**Usage**: Disable RUN button processing

### ATPAU
**Purpose**: Attach/Enable PAUSE button interrupt
**Response**: (empty)
**State Changes**: None
**Usage**: Enable PAUSE button processing

### DTPAU
**Purpose**: Detach/Disable PAUSE button interrupt
**Response**: (empty)
**State Changes**: None
**Usage**: Disable PAUSE button processing

### ATSTP
**Purpose**: Attach/Enable STOP button interrupt
**Response**: (empty)
**State Changes**: None
**Usage**: Enable STOP button processing

### DTSTP
**Purpose**: Detach/Disable STOP button interrupt
**Response**: (empty)
**State Changes**: None
**Usage**: Disable STOP button processing

### ATBOF
**Purpose**: Attach/Enable BUZZER OFF button interrupt
**Response**: (empty)
**State Changes**: None
**Usage**: Enable BUZZER OFF button processing

### DTBOF
**Purpose**: Detach/Disable BUZZER OFF button interrupt
**Response**: (empty)
**State Changes**: None
**Usage**: Disable BUZZER OFF button processing

---

## System Control

### tpSTP
**Purpose**: Shutdown/Stop command
**Response**: (empty)
**State Changes**: None
**Usage**: Initiate system shutdown or stop operations

### tpSTR
**Purpose**: Status/State response opcode
**Response**: `tpSTR`
**State Changes**: None
**Usage**: Return current device state (response opcode)

### RFS01
**Purpose**: Reference search command
**Response**: `TRD01` (Done response)
**State Changes**: None
**Usage**: Trigger reference position search sequence

### DHBLS
**Purpose**: Disable all hardware buttons and sensors
**Response**: (empty)
**State Changes**: Disables all sensors and encoders
**Usage**: Disable all inputs for safe operation
**Details**: Sets `sensor_top/bottom.attached = False`, `encoder_top/bottom.enabled = False`

### HWBDB
**Purpose**: Hardware button debug
**Response**: (empty)
**State Changes**: None
**Usage**: Debug mode for hardware buttons

---

## Error Handling

### FLS
**Purpose**: Failed/Error response (standard failure response)
**Response**: `FLS`
**State Changes**: None
**Usage**: Generic failure response for invalid or unhandled opcodes

---

## Handler Statistics

- **Total Opcodes Implemented**: 61
- **Command Categories**: 13
  - Communication: 2
  - Door Control: 3
  - Top Guide Motors: 4
  - Bottom Guide Motors: 4
  - Limit Switches: 2
  - Sensor Control: 4
  - Encoder Control: 12
  - Light/Camera: 5
  - Sensor Power: 3
  - Tower Lamps: 8
  - Hardware Buttons: 8
  - System Control: 4
  - Error Handling: 1

## Implementation Notes

### State Immutability
All handlers follow the immutable state pattern:
```python
def handle_command(state: DeviceState) -> Tuple[str, DeviceState]:
    new_state = state.copy()  # Create immutable copy
    new_state.property = value  # Modify copy
    return response, new_state  # Return response and new state
```

### Handler Signature
All handlers implement the standard signature:
```python
(state: DeviceState) -> Tuple[str, DeviceState]
```

### Response Format
- Opcodes are 5-character ASCII strings
- Responses are ASCII strings (can be empty)
- State transitions happen atomically with response

## Testing

All 61 opcodes have been tested with:
- Basic functionality tests (response validation)
- State transition tests (property verification)
- State immutability tests (original state unchanged)
- Integration tests (multiple command sequences)

See `firmware_emulator/tests/test_opcode_handler.py` for comprehensive test suite.

## Future Enhancements (Phase 2)

- Parameter parsing for opcodes with configuration values
- Timing simulation for long-running operations
- Event simulation for sensor triggers
- More granular state tracking for motor positions
- Encoder position tracking with step counts
- Motor speed and acceleration profiles

---

*Last Updated: March 29, 2026*
*Version: 1.0 - Initial Implementation*
