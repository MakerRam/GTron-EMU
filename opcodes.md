# Opcode Implementation Checklist

> Generated from `opcodes.toml` — TIME MACHINE V4.2 Complete Opcode Reference
> 
> Legend:
> - [x] = Implemented in emulator
> - [ ] = Not yet implemented
> - [?] = Uncertain about behavior — needs manual review
> - **Direction**: `command` = PC sends to controller, `response` = controller sends to PC, `internal` = internal signal
> - Only `command` opcodes need handler implementations. `response` opcodes are return values produced by handlers.

---

## Segment 1: Communication / System

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `QUERY` | Ping health check | command | Responds `YES` |
| [x] | `TSENB` | Enable timestamp output | command | Sets `timestamp_enabled = True` |
| [ ] | `YES` | Ping response | response | _(return value, no handler needed)_ |
| [ ] | `MIRSP` | Machine Interface response | response | _(return value, sets insync=true)_ |
| [ ] | `FLS` | Incorrect opcode response | response | _(returned for unknown opcodes)_ |
| [ ] | `D` | Trigger signal | internal | _(ISR context, not over serial)_ |

---

## Segment 2: Emergency Stop / Machine Power

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `EMSTP` | Check E-Stop / machine power | command | Responds `MP1` (power on) or `MP0` (power off) based on `estop_pressed` |
| [ ] | `MP1` | Machine power ON | response | _(return value)_ |
| [ ] | `MP0` | Machine power OFF | response | _(return value)_ |
| [ ] | `ES1` | E-Stop pressed event | response | _(return value)_ |
| [ ] | `ES0` | E-Stop released event | response | _(return value)_ |

---

## Segment 3: Push Button Attach / Detach

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `ATRUN` | Attach RUN button polling | command | Sets `button_flags.run = True` |
| [x] | `DTRUN` | Detach RUN button polling | command | Sets `button_flags.run = False` |
| [x] | `ATPAU` | Attach PAUSE button polling | command | Sets `button_flags.pause = True` |
| [x] | `DTPAU` | Detach PAUSE button polling | command | Sets `button_flags.pause = False` |
| [x] | `ATSTP` | Attach STOP button polling | command | Sets `button_flags.stop = True` |
| [x] | `DTSTP` | Detach STOP button polling | command | Sets `button_flags.stop = False` |
| [x] | `ATBOF` | Attach BUZZER OFF button polling | command | Sets `button_flags.buzzeroff = True` |
| [x] | `DTBOF` | Detach BUZZER OFF button polling | command | Sets `button_flags.buzzeroff = False` |
| [x] | `ATDRL` | Attach door lock switch polling | command | Sets `button_flags.doorlock = True` |
| [x] | `DTDRL` | Detach door lock switch polling | command | Sets `button_flags.doorlock = False` |

---

## Segment 4: Push Button Press Responses

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [ ] | `RUN` | RUN button pressed | response | _(event from controller, no handler)_ |
| [ ] | `PAU` | PAUSE button pressed | response | _(event from controller, no handler)_ |
| [ ] | `STP` | STOP button pressed | response | _(event from controller, no handler)_ |
| [ ] | `BOF` | BUZZER OFF button pressed | response | _(event from controller, no handler)_ |
| [ ] | `DUL` | Door unlocked event | response | _(event from controller, no handler)_ |

---

## Segment 5: Push Button Indicator Lamps

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `RUNON` | RUN lamp ON | command | Sets `button_lamps.run = True` |
| [x] | `RUNOF` | RUN lamp OFF | command | Sets `button_lamps.run = False` |
| [x] | `PAUON` | PAUSE lamp ON | command | Sets `button_lamps.pause = True` |
| [x] | `PAUOF` | PAUSE lamp OFF | command | Sets `button_lamps.pause = False` |
| [x] | `STPON` | STOP lamp ON | command | Sets `button_lamps.stop = True` |
| [x] | `STPOF` | STOP lamp OFF | command | Sets `button_lamps.stop = False` |
| [x] | `BZRON` | BUZZER lamp ON | command | Sets `button_lamps.buzzer = True` |
| [x] | `BZROF` | BUZZER lamp OFF | command | Sets `button_lamps.buzzer = False` |

---

## Segment 6: Tower Lamp

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `TRED1` | Red tower lamp ON | command | Sets `lamps.red = True` |
| [x] | `TRED0` | Red tower lamp OFF | command | Sets `lamps.red = False` |
| [x] | `TYEL1` | Yellow tower lamp ON | command | Sets `lamps.yellow = True` |
| [x] | `TYEL0` | Yellow tower lamp OFF | command | Sets `lamps.yellow = False` |
| [x] | `TGRN1` | Green tower lamp ON | command | Sets `lamps.green = True` |
| [x] | `TGRN0` | Green tower lamp OFF | command | Sets `lamps.green = False` |
| [x] | `TBZR1` | Tower buzzer ON | command | Sets `lamps.buzzer = True` |
| [x] | `TBZR0` | Tower buzzer OFF | command | Sets `lamps.buzzer = False` |

---

## Segment 7: Stamping, Winding & Solenoid

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `STMP1` | Stamping relay ON | command | Sets `stamping_relay = True` |
| [x] | `STMP0` | Stamping relay OFF | command | Sets `stamping_relay = False` |
| [x] | `WIND1` | Winding relay ON | command | Sets `winding_relay = True` |
| [x] | `WIND0` | Winding relay OFF | command | Sets `winding_relay = False` |
| [x] | `SOLON` | Solenoid valve ON | command | Sets `solenoid_top = True` |
| [x] | `SOLOF` | Solenoid valve OFF | command | Sets `solenoid_top = False` |

---

## Segment 8: Door Lock / Pressure Switch

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `DOORC` | Check door lock | command | Responds `DL1` (locked) or `DL0` (unlocked) |
| [x] | `PSWEN` | Enable pressure switch polling | command | Sets `pressure_switch_enabled = True` |
| [x] | `PSWDB` | Disable pressure switch polling | command | Sets `pressure_switch_enabled = False` |
| [x] | `PSWCK` | Check pressure switch state | command | Responds `PSWON` or `PSWOF` based on state |
| [ ] | `DL1` | Door locked response | response | _(return value)_ |
| [ ] | `DL0` | Door unlocked response | response | _(return value)_ |
| [ ] | `PSWON` | Pressure switch ON response | response | _(return value)_ |
| [ ] | `PSWOF` | Pressure switch OFF response | response | _(return value)_ |

---

## Segment 9: Sag Sensor

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `TPSAG` | Check top sag sensors | command | Dual response: `TU1`/`TU0` then `TL1`/`TL0` |
| [x] | `BMSAG` | Check bottom sag sensors | command | Dual response: `BU1`/`BU0` then `BL1`/`BL0` |
| [ ] | `TU1` | Top upper sag pass | response | _(return value)_ |
| [ ] | `TU0` | Top upper sag fail | response | _(return value)_ |
| [ ] | `TL1` | Top lower sag pass | response | _(return value)_ |
| [ ] | `TL0` | Top lower sag fail | response | _(return value)_ |
| [ ] | `BU1` | Bottom upper sag pass | response | _(return value)_ |
| [ ] | `BU0` | Bottom upper sag fail | response | _(return value)_ |
| [ ] | `BL1` | Bottom lower sag pass | response | _(return value)_ |
| [ ] | `BL0` | Bottom lower sag fail | response | _(return value)_ |

---

## Segment 10: Guide Motor

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `tpGOP` | Open top guide | command | Sets guide_top OPEN, responds `tpGOR` (with delay) |
| [x] | `tpGCL` | Close top guide | command | Sets guide_top CLOSED, responds `tpGCR` (with delay) |
| [x] | `bmGOP` | Open bottom guide | command | Sets guide_bottom OPEN, responds `bmGOR` (with delay) |
| [x] | `bmGCL` | Close bottom guide | command | Sets guide_bottom CLOSED, responds `bmGCR` (with delay) |
| [x] | `tpGDI` | Top guide insert (move to steps) | command | Param opcode: reads step count (5000) from 2nd frame → sets guide_top CLOSED, no response |
| [x] | `bmGDI` | Bottom guide insert (move to steps) | command | Param opcode: reads step count (5000) from 2nd frame → sets guide_bottom CLOSED, no response |
| [x] | `tpGTS` | Top guide test (open then close) | command | Runs open+close sequence, no serial response |
| [x] | `bmGTS` | Bottom guide test (open then close) | command | Runs open+close sequence, no serial response |
| [ ] | `tpGOR` | Top guide open response | response | _(return value)_ |
| [ ] | `tpGCR` | Top guide close response | response | _(return value)_ |
| [ ] | `bmGOR` | Bottom guide open response | response | _(return value)_ |
| [ ] | `bmGCR` | Bottom guide close response | response | _(return value)_ |
| [ ] | `GRD` | Guide reached target | response | _(return value)_ |

---

## Segment 11: Limit Switch Check

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `tpLSC` | Check top limit switch | command | Responds `tpOL1` (pressed) or `tpOL0` (not pressed) |
| [x] | `bmLSC` | Check bottom limit switch | command | Responds `bmOL1` (pressed) or `bmOL0` (not pressed) |
| [ ] | `tpOL1` | Top limit pressed | response | _(return value)_ |
| [ ] | `tpOL0` | Top limit not pressed | response | _(return value)_ |
| [ ] | `bmOL1` | Bottom limit pressed | response | _(return value)_ |
| [ ] | `bmOL0` | Bottom limit not pressed | response | _(return value)_ |

---

## Segment 12: Stepper / Reeler Motor Initialization

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `SMINI` | Initialize stepper drivers | command | Sets `stepper_initialized = True` |
| [x] | `RMINI` | Initialize reeler motors | command | Sets `reeler_initialized = True` |

---

## Segment 13: Reeler Motor Control

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `tpSTR` | Start top reeler | command | Sets `reeler_top.running = True` |
| [x] | `tpSTP` | Stop top reeler | command | Sets `reeler_top.running = False` |
| [x] | `bmSTR` | Start bottom reeler | command | Sets `reeler_bottom.running = True` |
| [x] | `bmSTP` | Stop bottom reeler | command | Sets `reeler_bottom.running = False` |
| [x] | `tpRSP` | Set top reeler speed | command | Param opcode: reads RPM (200) from 2nd frame → stores in reeler_top.speed, no response |
| [x] | `bmRSP` | Set bottom reeler speed | command | Param opcode: reads RPM (200) from 2nd frame → stores in reeler_bottom.speed, no response |
| [x] | `tpRTR` | Rotate top reeler (diagnostic) | command | Sets reeler running, responds `RHD` when done |
| [x] | `bmRTR` | Rotate bottom reeler (diagnostic) | command | Sets reeler running, responds `RHD` when done |
| [x] | `RMSMF` | Set reeler speed multiplication factor | command | Param opcode: reads value from 2nd frame → ignored (no-op), no response |
| [ ] | `RHD` | Reeler operation complete | response | _(return value)_ |

---

## Segment 14: Encoder

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `tpENI` | Initialize top encoder | command | Sets `encoder_top.initialized = True` |
| [x] | `bmENI` | Initialize bottom encoder | command | Sets `encoder_bottom.initialized = True` |
| [x] | `tpINA` | Set top encoder initial angle | command | Param opcode: reads angle from 2nd frame → ignored (no-op), no response |
| [x] | `bmINA` | Set bottom encoder initial angle | command | Param opcode: reads angle from 2nd frame → ignored (no-op), no response |
| [x] | `tpEEN` | Enable top encoder trigger | command | Sets `encoder_top.enabled = True` |
| [x] | `tpEDB` | Disable top encoder trigger | command | Sets `encoder_top.enabled = False` |
| [x] | `bmEEN` | Enable bottom encoder trigger | command | Sets `encoder_bottom.enabled = True` |
| [x] | `bmEDB` | Disable bottom encoder trigger | command | Sets `encoder_bottom.enabled = False` |
| [x] | `tpRTH` | Set top reeler teeth count | command | Param opcode: reads teeth count from 2nd frame → ignored (no-op), no response |
| [x] | `bmRTH` | Set bottom reeler teeth count | command | Param opcode: reads teeth count from 2nd frame → ignored (no-op), no response |
| [x] | `SKTRG` | Set skip trigger count | command | Param opcode: reads count from 2nd frame → ignored (no-op), no response |

---

## Segment 15: Trigger Sensor Power

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `POS01` | Power ON sensor 1 (top rack) | command | Sets `sensor_power[1] = True` |
| [x] | `PFS01` | Power OFF sensor 1 | command | Sets `sensor_power[1] = False` |
| [x] | `POS02` | Power ON sensor 2 | command | Sets `sensor_power[2] = True` |
| [x] | `PFS02` | Power OFF sensor 2 | command | Sets `sensor_power[2] = False` |
| [x] | `POS03` | Power ON sensor 3 | command | Sets `sensor_power[3] = True` |
| [x] | `PFS03` | Power OFF sensor 3 | command | Sets `sensor_power[3] = False` |
| [x] | `POS04` | Power ON sensor 4 | command | Sets `sensor_power[4] = True` |
| [x] | `PFS04` | Power OFF sensor 4 | command | Sets `sensor_power[4] = False` |
| [x] | `POS05` | Power ON sensor 5 (bottom rack) | command | Sets `sensor_power[5] = True` |
| [x] | `PFS05` | Power OFF sensor 5 | command | Sets `sensor_power[5] = False` |
| [x] | `POS06` | Power ON sensor 6 | command | Sets `sensor_power[6] = True` |
| [x] | `PFS06` | Power OFF sensor 6 | command | Sets `sensor_power[6] = False` |
| [x] | `POS07` | Power ON sensor 7 | command | Sets `sensor_power[7] = True` |
| [x] | `PFS07` | Power OFF sensor 7 | command | Sets `sensor_power[7] = False` |
| [x] | `POS08` | Power ON sensor 8 | command | Sets `sensor_power[8] = True` |
| [x] | `PFS08` | Power OFF sensor 8 | command | Sets `sensor_power[8] = False` |

---

## Segment 16: Trigger Sensor Attach / Detach & Check

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `tpATS` | Attach top sensor interrupt | command | Sets `sensor_top.attached = True` |
| [x] | `tpDTS` | Detach top sensor interrupt | command | Sets `sensor_top.attached = False` |
| [x] | `bmATS` | Attach bottom sensor interrupt | command | Sets `sensor_bottom.attached = True` |
| [x] | `bmDTS` | Detach bottom sensor interrupt | command | Sets `sensor_bottom.attached = False` |
| [x] | `TPSCK` | Check top trigger sensor | command | Responds `TS1` (on) or `TS0` (off) |
| [x] | `BPSCK` | Check bottom trigger sensor | command | Responds `BS1` (on) or `BS0` (off) |
| [ ] | `TS1` | Top sensor ON response | response | _(return value)_ |
| [ ] | `TS0` | Top sensor OFF response | response | _(return value)_ |
| [ ] | `BS1` | Bottom sensor ON response | response | _(return value)_ |
| [ ] | `BS0` | Bottom sensor OFF response | response | _(return value)_ |

---

## Segment 17: Light / Camera Sequences (Individual Diagnostics)

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `LCS01` | Rack 1 Top Cam sequence | command | Activates camera 1 sequence |
| [x] | `LCS02` | Rack 1 Side Cam sequence | command | Activates camera 2 sequence |
| [x] | `LCS03` | Rack 1 Front Cam sequence | command | Activates camera 3 sequence |
| [x] | `LCS04` | Rack 1 Top Light Cam (solenoid) | command | Activates camera 4 (backlight via solenoid) |
| [x] | `LCS05` | Rack 2 Top Cam sequence | command | Activates camera 5 sequence |
| [x] | `LCS06` | Rack 2 Side Cam sequence | command | Activates camera 6 sequence |
| [x] | `LCS07` | Rack 2 Front Cam sequence | command | Activates camera 7 sequence |
| [x] | `LCStp` | Full top rack sequence | command | Activates all top cameras via Timer1 |
| [x] | `LCSbm` | Full bottom rack sequence | command | Activates all bottom cameras via Timer2 |

---

## Segment 18: Light / Camera Sequence Flags (Inspection Enable)

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `LCSI0` | Enable Rack 1 Top Cam flag | command | Sets `camera_flags[0] = True` |
| [x] | `LCSI1` | Enable Rack 1 Side Cam flag | command | Sets `camera_flags[1] = True` |
| [x] | `LCSI2` | Enable Rack 1 Front Cam flag | command | Sets `camera_flags[2] = True` |
| [x] | `LCSI3` | Enable Rack 1 Top Light Cam flag | command | Sets `camera_flags[3] = True` |
| [x] | `LCSI4` | Enable Rack 2 Top Cam flag | command | Sets `camera_flags[4] = True` |
| [x] | `LCSI5` | Enable Rack 2 Side Cam flag | command | Sets `camera_flags[5] = True` |
| [x] | `LCSI6` | Enable Rack 2 Front Cam flag | command | Sets `camera_flags[6] = True` |

---

## Segment 19: Light / Camera Timing Config (COMMENTED OUT in firmware)

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `LONDT` | Set light ON delay | command | Param opcode: commented out in firmware → ignored (no-op), no response |
| [x] | `CONDT` | Set camera ON delay | command | Param opcode: commented out in firmware → ignored (no-op), no response |
| [x] | `COFDT` | Set camera OFF delay | command | Param opcode: commented out in firmware → ignored (no-op), no response |
| [x] | `LOFDT` | Set light OFF delay | command | Param opcode: commented out in firmware → ignored (no-op), no response |
| [x] | `TLOND` | Set top-light ON delay | command | Param opcode: commented out in firmware → ignored (no-op), no response |
| [x] | `TCOND` | Set top-camera ON delay | command | Param opcode: commented out in firmware → ignored (no-op), no response |
| [x] | `TCOFD` | Set top-camera OFF delay | command | Param opcode: commented out in firmware → ignored (no-op), no response |
| [x] | `TLOFD` | Set top-light OFF delay | command | Param opcode: commented out in firmware → ignored (no-op), no response |

---

## Segment 20: IET (Inspection Event Transitions)

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `IESEL` | Select state | command | Enable RUN, disable others, reset trig counts, RUN lamp ON |
| [x] | `IERUN` | Run state | command | Enable PAUSE+STOP, green tower lamp ON, enable solenoid |
| [x] | `IEPAS` | Pass state | command | Same as IERUN (enable PAUSE+STOP, green lamp) |
| [x] | `IEPAU` | Pause state | command | Enable RUN+STOP, yellow tower lamp, close stamping+solenoid |
| [x] | `IEFAI` | Fail state | command | Enable BUZZEROFF only, red lamp + buzzer ON, close stamping+solenoid |
| [x] | `BOFDR` | Buzzer off (during run) | command | Disable RUN, enable STOP, turn off buzzer |
| [x] | `BOFER` | Buzzer off (error recovery) | command | Enable RUN+STOP, turn off buzzer |
| [x] | `IEDRL` | Door lock poka-yoke | command | Accept silently (not handled in firmware either) |
| [x] | `DHBLS` | Full hardware reset | command | Stop timers, disable all buttons/motors/interrupts/sensors, reset all flags |
| [x] | `HWBDB` | Disable all hardware buttons | command | Disable all buttons, turn off all indicator lamps |

---

## Segment 21: Reference Search

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `RFS01` | Top camera reference search | command | Responds `TRD01` (with delay) |
| [x] | `RFS02` | Bottom camera reference search | command | Responds `TRD02` (with delay) |
| [x] | `SPM01` | Set top SPM delay | command | Param opcode: reads microseconds (3000) from 2nd frame → stores in spm_delay_top, no response |
| [x] | `SPM02` | Set bottom SPM delay | command | Param opcode: reads microseconds (3000) from 2nd frame → stores in spm_delay_bottom, no response |
| [ ] | `TRD01` | Top reference search done | response | _(return value)_ |
| [ ] | `TRD02` | Bottom reference search done | response | _(return value)_ |

---

## Segment 22: Rejection Logic

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `RJENB` | Enable rejection logic | command | Sets `rejection_enabled = True`, powers sensor |
| [ ] | `RJDNE` | Rejection detection complete | response | _(return value)_ |

---

## Segment 23: I2C Expander Initialization

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `I2C1` | Re-initialize I2C expander 1 (input) | command | Sets `i2c_initialized[1] = True` |
| [x] | `I2C2` | Re-initialize I2C expander 2 (output) | command | Sets `i2c_initialized[2] = True` |
| [x] | `I2C3` | Re-initialize I2C expander 3 (output) | command | Sets `i2c_initialized[3] = True` |

---

## Emulator-Only Opcodes (UI Control Buttons)

These opcodes are NOT part of the real hardware protocol. They exist only for the dashboard UI.

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | `EMRUN` | Set emulator to RUNNING | command | Sets `run_state = RUNNING`, responds `EMROK` |
| [x] | `EMPAU` | Set emulator to PAUSED | command | Sets `run_state = PAUSED`, responds `EMPOK` |
| [x] | `EMSTP` | Set emulator to STOPPED | command | Sets `run_state = STOPPED`, responds `EMSOK` |
| [x] | `BZZOF` | Buzzer override (silence) | command | Sets `buzzer_override = True`, responds `BZZOK` |

> **Note**: The real hardware `EMSTP` opcode (Emergency Stop check) conflicts with the emulator-only `EMSTP` (set emulator to STOPPED). The emulator-only version has been renamed to `EMEST` to avoid the collision. The real `EMSTP` handler now correctly checks e-stop state.

---

## Unknown Opcode Handling

| Status | Opcode | Name | Direction | Emulator Behavior |
|--------|--------|------|-----------|-------------------|
| [x] | _(any)_ | Unrecognized opcode fallback | — | Responds `FLS` (as per real hardware) |

---

## Summary

| Category | Total | Implemented | Uncertain | Notes |
|----------|-------|-------------|-----------|-------|
| Command opcodes | ~80 | ~65 | ~12 | [?] items need param support (Phase 2) |
| Response opcodes | ~35 | N/A | N/A | Return values only, no handler needed |
| Internal opcodes | 1 | N/A | N/A | ISR context only |
| Emulator-only | 4 | 4 | 0 | UI control buttons |

### Uncertain Items ([?]) — Need Manual Review

All `[?]` items are opcodes that **read additional data from serial** after the 5-byte opcode. The current protocol is fixed 5-byte frames with no parameter passing. These opcodes are accepted silently (no error) but do not parse parameters yet.

Opcodes needing Phase 2 parameter support:
- `tpGDI` / `bmGDI` — guide motor step count  - step count constant: 5000 //step count comes anlong with opcode. No response required, upadte in UI close guide condition.
- `tpRSP` / `bmRSP` — reeler RPM -  constant: 200 //count comes anlong with opcode. No response required.
- `RMSMF` — reeler multiplication factor //ignore, no response required.
- `tpINA` / `bmINA` — encoder initial angle //ignore, no response required.
- `tpRTH` / `bmRTH` — encoder teeth count //ignore, no response required.
- `SKTRG` — skip trigger count ignore, no response required.
- `SPM01` / `SPM02` — SPM delay microseconds //3000ms
- `LONDT` / `CONDT` / `COFDT` / `LOFDT` / `TLOND` / `TCOND` / `TCOFD` / `TLOFD` — timing configs (commented out in firmware)  //ignore, no response required.
