# Architecture & Data Flow Diagram

## Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEVELOPER MACHINE (Windows)                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                               │
│  ┌──────────────────────────────────────────┐  ┌──────────────────────────┐ │
│  │      TERMINAL 1: Firmware Emulator       │  │   TERMINAL 2: LabVIEW    │ │
│  │                                          │  │                          │ │
│  │  $ python3 src/main.py                   │  │  $ labview &             │ │
│  │  --port COM3 --verbose                   │  │                          │ │
│  │                                          │  │  [LabVIEW IDE]           │ │
│  │  ┌────────────────────────────────────┐  │  │    Opens COM4            │ │
│  │  │   Emulator Process (Python)        │  │  │    Sends: QUERY          │ │
│  │  │                                    │  │  │    Recv: YES ✓           │ │
│  │  │  main.py                           │  │  │                          │ │
│  │  │  ├─ EmulatorEngine                 │  │  │ [Guide Control Panel]    │ │
│  │  │  │  ├─ event loop                  │  │  │ [Guide Open] → tpGOP     │ │
│  │  │  │  ├─ SerialBridge (COM3)         │◄─┼──┼─ → RESPONSE: tpGOR      │ │
│  │  │  │  └─ OpcodeHandler               │  │  │ [Guide Close] → tpGCL    │ │
│  │  │  │     └─ 75 opcodes               │  │  │                          │ │
│  │  │  ├─ DeviceState                    │  │  │ [Camera Controls]        │ │
│  │  │  │  ├─ guide_top/bottom            │  │  │ [Trigger Top] → LCS01    │ │
│  │  │  │  ├─ sensor_top/bottom           │  │  │ [Trigger Side] → LCS02   │ │
│  │  │  │  ├─ reeler_top/bottom           │  │  │ [Trigger Front] → LCS03  │ │
│  │  │  │  ├─ encoder_top/bottom          │  │  │                          │ │
│  │  │  │  ├─ cameras                     │  │  │ [Status]                 │ │
│  │  │  │  └─ lamps                       │  │  │  Power: ON               │ │
│  │  │  ├─ VirtualCamera                  │  │  │  E-Stop: OFF             │ │
│  │  │  │  └─ frame_queue                 │  │  │  Limit: OPEN             │ │
│  │  │  ├─ SerialMonitor                  │  │  │                          │ │
│  │  │  │  ├─ --verbose output            │  │  │ [Real-time Graph]        │ │
│  │  │  │  ├─ --hex dump                  │  │  │ Sensor: ████            │ │
│  │  │  │  ├─ --debug breakpoints         │  │  │ Motor: ╰─────╯          │ │
│  │  │  │  └─ --interactive REPL          │  │  │                          │ │
│  │  │  └─ MachineConfig                  │  │  │                          │ │
│  │  │     ├─ 75 opcodes                  │  │  │                          │ │
│  │  │     ├─ timing values               │  │  │                          │ │
│  │  │     └─ camera mappings             │  │  │                          │ │
│  │  │                                    │  │  │                          │ │
│  │  │  [Console Output]                  │  │  │                          │ │
│  │  │  [2026-03-28 07:53:25.123]         │  │  │                          │ │
│  │  │  RECV: QUERY → SEND: YES           │  │  │                          │ │
│  │  │  [2026-03-28 07:53:26.045]         │  │  │                          │ │
│  │  │  RECV: tpGOP → SEND: tpGOR [2s]    │  │  │                          │ │
│  │  │  [2026-03-28 07:53:28.234]         │  │  │                          │ │
│  │  │  RECV: LCS01 → CAMERA TRIGGER      │  │  │                          │ │
│  │  └────────────────────────────────────┘  │  └──────────────────────────┘ │
│  │                                          │                               │
│  │  COM Port Pairing (com0com):             │                               │
│  │  ┌────────────┐         ┌────────────┐   │                               │
│  │  │   COM3     │◄───────►│   COM4     │   │                               │
│  │  │ (Emulator) │(virtual)│ (LabVIEW)  │   │                               │
│  │  └────────────┘         └────────────┘   │                               │
│  │                                          │                               │
│  │  Log Files (Auto-created):               │                               │
│  │  logs/                                   │                               │
│  │  ├─ emulator_20260328_075325.log         │                               │
│  │  │  └─ Main events, startup, errors     │                               │
│  │  ├─ serial_20260328_075325.log           │                               │
│  │  │  └─ Port open/close, timeouts        │                               │
│  │  ├─ commands_20260328_075325.log         │                               │
│  │  │  └─ Every opcode: before/after state │                               │
│  │  └─ debug_20260328_075325.log            │                               │
│  │     └─ Detailed DEBUG level messages     │                               │
│  │                                          │                               │
│  └──────────────────────────────────────────┘                               │
│                                                                               │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow: Single Command Cycle

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │                     COMMAND PROCESSING CYCLE                         │
  └─────────────────────────────────────────────────────────────────────┘

1. LabVIEW sends 5 bytes over COM4 (paired with COM3)
   ┌──────┐
   │ QUERY│  (ASCII: [Q][U][E][R][Y])
   └──────┘
        │
        │ (virtual COM port)
        ▼
2. EmulatorEngine.run() reads from SerialBridge
   ┌────────────────────┐
   │ read(5 bytes)      │
   │ → "QUERY"          │
   │ timestamp: 07:53:25│
   └────────────────────┘
        │
        ▼
3. SerialMonitor logs (if --verbose)
   ┌──────────────────────────────────┐
   │[2026-03-28 07:53:25.123]         │
   │RECV: QUERY                        │
   │(console output)                   │
   └──────────────────────────────────┘
        │
        ▼
4. OpcodeHandler dispatches
   ┌────────────────────────────────────────┐
   │ opcode_handler.handle("QUERY")         │
   │ └─ found handler: handle_query()       │
   │    ├─ state_before = {power_on: True} │
   │    └─ response = "YES"                 │
   │       state_after = {power_on: True}   │
   └────────────────────────────────────────┘
        │
        ▼
5. Enhanced logging (command tracking)
   ┌──────────────────────────────────────────┐
   │ logs/commands_*.log                      │
   │                                          │
   │ [COMMAND_001]                           │
   │ Time: 2026-03-28 07:53:25.123           │
   │ Opcode: QUERY                           │
   │ Response: YES                           │
   │ State Before: {power_on: True, ...}     │
   │ State After: {power_on: True, ...}      │
   │ Duration: 0.45ms                        │
   └──────────────────────────────────────────┘
        │
        ▼
6. SerialBridge writes response to COM3
   ┌──────┐
   │ YES  │ (ASCII: [Y][E][S])
   └──────┘
        │
        │ (virtual COM port)
        ▼
7. LabVIEW receives on COM4
   ┌──────────────────┐
   │ Receives: YES    │
   │ Connection: OK ✓ │
   └──────────────────┘
        │
        ▼
8. SerialMonitor logs response (if --verbose)
   ┌──────────────────────────────────┐
   │[2026-03-28 07:53:25.123]         │
   │RECV: QUERY → SEND: YES           │
   │(console output)                   │
   └──────────────────────────────────┘

[Total cycle time: ~2ms for QUERY/YES]
```

---

## State Transition: Guide Open Command

```
  ┌─────────────────────────────────────────────────────────────────────┐
  │              GUIDE OPEN SEQUENCE (tpGOP command)                    │
  └─────────────────────────────────────────────────────────────────────┘

Initial State:
  guide_top = {position: UNKNOWN, moving: False, reached_limit: False}

                        ┌──────────────────────┐
                        │ LabVIEW sends tpGOP  │
                        └──────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ EmulatorEngine receives  │
                    │ opcode = "tpGOP"         │
                    └──────────────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────────────────┐
                    │ OpcodeHandler.handle_guide_open()  │
                    │                                    │
                    │ 1. state_before = {...}            │
                    │ 2. Set guide_top.moving = True     │
                    │ 3. Set guide_top.position=MOVING   │
                    │ 4. Delay 2000ms (from config)      │
                    │ 5. Set guide_top.position = OPEN   │
                    │ 6. Set guide_top.moving = False    │
                    │ 7. return "tpGOR"                  │
                    │                                    │
                    └────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    ▼                         ▼
          ┌────────────────────┐  ┌─────────────────────┐
          │ SerialMonitor      │  │ Enhanced Logging    │
          │ (--verbose)        │  │                     │
          │                    │  │ [COMMAND_002]       │
          │ RECV: tpGOP        │  │ Time: ...           │
          │ SEND: tpGOR        │  │ Opcode: tpGOP       │
          │ [2000ms delay]     │  │ Response: tpGOR     │
          │                    │  │ Duration: 2000.45ms │
          │ (console output)   │  │ State Before:       │
          │                    │  │   guide.position:   │
          │                    │  │   UNKNOWN → MOVING  │
          │                    │  │   → OPEN            │
          │                    │  │                     │
          └────────────────────┘  └─────────────────────┘
                    │                         │
                    └────────────┬────────────┘
                                 ▼
                    ┌──────────────────────────┐
                    │ SerialBridge writes tpGOR│
                    │ to COM3 (delayed 2000ms) │
                    └──────────────────────────┘
                                 │
                                 ▼
                    ┌──────────────────────────┐
                    │ LabVIEW receives tpGOR   │
                    │ Guide status: OPEN ✓     │
                    └──────────────────────────┘

Final State:
  guide_top = {position: OPEN, moving: False, reached_limit: True}

Logs:
  [emulator.log]     "tpGOP handler completed in 2000.45ms"
  [serial.log]       "Wrote 5 bytes: tpGOR"
  [commands.log]     "COMMAND_002: tpGOP → tpGOR [2000ms] {state delta}"
  [debug.log]        "guide_top.position: UNKNOWN → MOVING → OPEN"
```

---

## Debugging with --debug Flag (Phase 2)

```
Command arrives: tpGOP
  │
  ├─ Check debug breakpoints
  │
  ├─ If opcode in --debug list:
  │  │
  │  ├─ Pause execution
  │  │
  │  ├─ Enter debug console:
  │  │
  │  │ [2026-03-28 07:53:26.045] BREAKPOINT: tpGOP
  │  │ State before: {guide_top.position: UNKNOWN}
  │  │
  │  │ (emulator:debug) > state.guide_top.position
  │  │ 'GuidePosition.UNKNOWN'
  │  │
  │  │ (emulator:debug) > state.guide_top.position = GuidePosition.OPEN
  │  │
  │  │ (emulator:debug) > continue
  │  │
  │  └─ Resume with modified state
  │
  └─ Send response
```

---

## Logging Hierarchy

```
Log Level: DEBUG ────► INFO ────► WARNING ────► ERROR

File Logs (DEBUG & above):
├─ emulator_*.log       (all events)
├─ serial_*.log         (port I/O only)
├─ commands_*.log       (opcode tracking)
└─ debug_*.log          (verbose debug)

Console Output (INFO & above):
├─ Main events
├─ Errors & warnings
└─ (if --verbose) Human-readable commands

Example:
  DEBUG: "SerialBridge._read() called"            → files only
  INFO:  "QUERY received → YES sent"              → files + console
  WARN:  "Command timeout, discarding buffer"    → files + console
  ERROR: "Serial port not found"                 → files + console
```

---

## Summary

**Execution Model:**
- Emulator: Backend daemon (Terminal 1, always running)
- LabVIEW: Independent frontend (Terminal 2 or IDE)
- Communication: Virtual COM port pair (COM3 ↔ COM4)

**Visibility:**
- Real-time console: `--verbose` flag
- Detailed logs: Auto-created in `logs/` directory
- Protocol dump: `--hex` flag
- Debug breakpoints: `--debug` flag (Phase 2)
- Interactive console: `--interactive` flag (Phase 2)

**Data Flow:**
1. Read 5 bytes from serial port
2. Parse to opcode string
3. Dispatch to handler
4. Execute command (may include delays)
5. Log before/after state
6. Write response
7. Repeat

No UI, pure backend daemon. All visibility through logging and console output.
