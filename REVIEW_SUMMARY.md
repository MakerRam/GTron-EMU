# Review Summary: Clarifications Addressed

## Your Questions & Our Responses

### 1. LabVIEW Launch & Emulator Startup Model

**Your Question:**
> When LabVIEW application launches, it will check for COM port and camera interface. How does the firmware emulation layer start? Will there be any UI or will it run in backend always?

**Our Solution: Backend Daemon Model**

**Architecture:**
```
Terminal 1 (Always running):
  $ python3 src/main.py --port COM3 --verbose
  [Emulator process - Backend daemon]
  [No GUI, no blocking dialogs]
  [Logs visible in console + files]

Terminal 2 (Independent):
  $ labview &
  [LabVIEW IDE or application]
  [Connects to COM4 (paired with COM3)]
  [Unaware of emulator - just sees COM port]

Result:
  - LabVIEW checks COM4 → Found ✓
  - LabVIEW checks camera interface → Response ✓
  - Communication begins automatically
```

**Why This Design:**
1. **No UI overhead** - Pure backend daemon
2. **Explicit control** - User manually starts emulator before LabVIEW
3. **Decoupled** - LabVIEW doesn't need to know about emulator
4. **Scalable** - Can run on headless/embedded systems later
5. **Future-proof** - Phase 2 can add auto-launcher if needed

**Documentation:** See `docs/EXECUTION_AND_MONITORING.md` Section 1

---

### 2. Serial Monitor for Command Visibility

**Your Question:**
> Require serial monitor for look at what command is in progress

**Our Solution: Real-Time Serial Monitor (Group 0.5)**

**Three-Level Approach:**

#### Level 1: Human-Readable (Default)
```bash
$ python3 src/main.py --port COM3 --verbose

[2026-03-28 07:53:25.123] RECV: QUERY         → SEND: YES
[2026-03-28 07:53:26.045] RECV: tpGOP         → SEND: tpGOR [2000ms]
[2026-03-28 07:53:28.067] RECV: tpGCL         → SEND: tpGCR
[2026-03-28 07:53:28.234] RECV: LCS01         → SEND: (camera trigger)
[2026-03-28 07:53:28.235] RECV: TSENB         → SEND: (timestamp enabled)
```

#### Level 2: Protocol Dump (Hex)
```bash
$ python3 src/main.py --port COM3 --hex

[2026-03-28 07:53:25.123] RECV: [51 55 45 52 59] "QUERY"
[2026-03-28 07:53:25.123] SEND: [89 69 83] "YES"
[2026-03-28 07:53:26.045] RECV: [116 112 71 79 80] "tpGOP"
[2026-03-28 07:53:26.045] SEND: [116 112 71 79 82] "tpGOR"
```

#### Level 3: Detailed Command Log (Auto)
```
logs/commands_20260328_075325.log

[COMMAND_001]
  Time: 2026-03-28 07:53:25.123
  Opcode: QUERY
  Response: YES
  State Before: {power_on: True, estop_pressed: False, ...}
  State After: {power_on: True, estop_pressed: False, ...}
  Duration: 0.45ms

[COMMAND_002]
  Time: 2026-03-28 07:53:26.045
  Opcode: tpGOP
  Response: tpGOR
  State Before: {guide_top.position: UNKNOWN, moving: False}
  State After: {guide_top.position: OPEN, moving: False}
  Duration: 2000.45ms
```

**Implementation:**
- **New Class**: `SerialMonitor` (Task 0.5.1)
- **Human-readable format** (Task 0.5.2)
- **Hex dump option** (Task 0.5.3)
- **Command tracking** (Task 0.5.4) - logs state before/after

**Documentation:** See `docs/EXECUTION_AND_MONITORING.md` Section 2

---

### 3. Logging & Debugging Capabilities

**Your Question:**
> Is it possible to log and debug?

**Our Solution: Layered Logging & Debug Infrastructure**

#### Layer 1: Automatic Baseline Logging (Always On)

Four log files per session:
```
logs/
├── emulator_20260328_075325.log
│   └─ Main events: startup, shutdown, errors
│   └─ Example: "Configuration loaded: 75 opcodes"
│   └─ Example: "Serial port COM3 opened @ 9600 baud"
│   └─ Example: "ERROR: Unknown opcode FLS01 → FLS"
│
├── serial_20260328_075325.log
│   └─ Serial I/O events only
│   └─ Example: "Port opened: COM3"
│   └─ Example: "Timeout: no data for 5000ms"
│   └─ Example: "Wrote 5 bytes to COM3"
│
├── commands_20260328_075325.log
│   └─ Every command with context
│   └─ Opcode → Response mapping
│   └─ State delta (before/after)
│   └─ Duration in milliseconds
│
└── debug_20260328_075325.log
    └─ Verbose DEBUG-level messages
    └─ Handler execution flow
    └─ State transition details
```

**Log Format Example:**
```
2026-03-28 07:53:25.001 | INFO     | main                | Emulator starting on COM3 @ 9600 baud
2026-03-28 07:53:25.012 | INFO     | config_parser       | Loaded 75 opcodes from MI JSON
2026-03-28 07:53:25.015 | DEBUG    | serial_bridge       | Serial port opened: COM3
2026-03-28 07:53:25.123 | INFO     | opcode_handler      | QUERY → YES
2026-03-28 07:53:26.045 | DEBUG    | device_state        | guide_top.position: UNKNOWN → MOVING
2026-03-28 07:53:28.045 | DEBUG    | device_state        | guide_top.position: MOVING → OPEN
2026-03-28 07:53:28.067 | INFO     | opcode_handler      | tpGOP → tpGOR [duration: 2000.45ms]
```

#### Layer 2: Debug Mode (Optional --debug Flag)

```bash
$ python3 src/main.py --port COM3 --debug tpGOP LCS01

# Phase 1: Logs warning when breakpoint opcode arrives
[2026-03-28 07:53:26.045] DEBUG BREAKPOINT: tpGOP
  State before: {guide_top.position: UNKNOWN}
  Handler: guide_open()

# Phase 2: Pauses execution for inspection/modification
[2026-03-28 07:53:26.045] BREAKPOINT: tpGOP
> state.guide_top.position
'GuidePosition.UNKNOWN'
> continue
Response: tpGOR
```

#### Layer 3: Interactive Monitor (Optional --interactive Flag, Phase 2)

```bash
$ python3 src/main.py --port COM3 --interactive

(emulator) > help
  Commands:
    state              - Print current device state (24 keys)
    set <attr> <val>   - Modify state live
    inject <opcode>    - Send opcode to handler
    pause              - Pause on next command
    snapshot           - Save state to JSON
    help               - This message

(emulator) > state
DeviceState:
  guide_top: {position: UNKNOWN, moving: False}
  guide_bottom: {position: UNKNOWN, moving: False}
  sensor_top: {attached: False, powered: False}
  sensor_bottom: {attached: False, powered: False}
  cameras: {flags: {0: False, 1: False, ...}, timestamp_enabled: False}
  ... (24 keys total)

(emulator) > set guide_top.position OPEN
Updated: guide_top.position = GuidePosition.OPEN

(emulator) > inject QUERY
QUERY → YES

(emulator) > snapshot
Saved to: snapshots/state_20260328_075328.json
```

**Implementation:**
- **Baseline logging** - Always on, no overhead (Task 0.5.1-0.5.4)
- **Debug breakpoints** - Phase 1 stub, Phase 2 full (Task 0.5.5)
- **Interactive REPL** - Phase 1 stub, Phase 2 full (Task 0.5.6)

**Documentation:** See `docs/EXECUTION_AND_MONITORING.md` Section 3

---

## Updated Architecture Overview

### Execution Flow
```
User Terminal:
  $ python3 src/main.py --port COM3 --verbose --debug tpGOP
       ↓
  Emulator starts (background daemon)
       ↓
  Configuration loaded (75 opcodes, timing values)
       ↓
  Serial port opened (COM3 @ 9600 baud)
       ↓
  Event loop begins (read → parse → handle → respond)
       ↓
  Real-time console output (if --verbose)
       ↓
  Logs written to files (rotating, 5MB max)
       ↓
  User launches LabVIEW (separate terminal)
       ↓
  LabVIEW connects to COM4 (paired with COM3)
       ↓
  Communication begins automatically
       ↓
  All commands logged & visible (--verbose, logs/, --debug)
```

### Files Created
```
firmware_emulator/
├── src/
│   ├── main.py                    [NEW - CLI entry point]
│   ├── serial_monitor.py          [NEW - Group 0.5.1-0.5.3]
│   ├── debug_breakpoint.py        [NEW - Group 0.5.5]
│   ├── interactive_monitor.py     [NEW - Group 0.5.6]
│   ├── logging_config.py          [DONE - Group 1.5]
│   ├── config_parser.py           [DONE - Group 1.6]
│   └── device_state.py            [DONE - Group 2.1-2.7]
├── tests/
│   └── test_device_state.py       [DONE - Group 2.8]
└── docs/
    ├── EXECUTION_AND_MONITORING.md    [NEW - Complete startup model]
    ├── ARCHITECTURE_DIAGRAM.md        [NEW - Data flow & logging]
    ├── TASK_PLAN_UPDATED.md          [NEW - Revised task structure]
    └── [other docs...]
```

---

## Key Design Decisions Validated

| Decision | Validation |
|----------|-----------|
| **Backend daemon (no UI)** | ✅ No blocking dialogs, lean architecture, scalable |
| **Manual start before LabVIEW** | ✅ Explicit control, decoupled, predictable |
| **Virtual COM port (com0com)** | ✅ LabVIEW sees real COM port, no emulator awareness needed |
| **--verbose flag for monitoring** | ✅ Human-readable, non-intrusive, always available |
| **Rotating log files** | ✅ Auto-created, comprehensive, diagnostic-friendly |
| **Structured logging with state delta** | ✅ Enables debugging without interactive console |
| **Phased approach (Phase 1 stub, Phase 2 full)** | ✅ Core functionality works now, advanced features later |

---

## New Group 0.5: Serial Monitor & Debugging

**6 Tasks (Insert before Group 3)**

```
0.5.1 Create SerialMonitor class
  └─ Human-readable command/response formatting
  └─ File: src/serial_monitor.py

0.5.2 Implement --verbose flag
  └─ Console output: [timestamp] RECV: opcode → SEND: response
  └─ Integration: src/main.py CLI args

0.5.3 Implement --hex flag
  └─ Byte-level protocol dump: [byte1 byte2 byte3 byte4 byte5]
  └─ Integration: SerialMonitor class

0.5.4 Enhanced logging: Command tracking with state delta
  └─ Format: [COMMAND_001] opcode → response [state_before → state_after]
  └─ File: logs/commands_*.log (auto-created)

0.5.5 Implement --debug flag (Phase 1 stub, Phase 2 full)
  └─ Phase 1: Logs warning on breakpoint opcode
  └─ Phase 2: Pause execution for inspection
  └─ File: src/debug_breakpoint.py

0.5.6 Implement --interactive flag (Phase 1 stub, Phase 2 full)
  └─ Phase 1: Stub with help message
  └─ Phase 2: Full REPL (state inspection, injection, snapshots)
  └─ File: src/interactive_monitor.py
```

**Estimated Effort:** 3-4 hours

---

## Revised Task Count

```
Group 0.5:    6 new tasks (Serial Monitor - HIGH PRIORITY)
Group 1:      6 tasks (✅ DONE)
Group 2:      8 tasks (✅ DONE)
Group 3:      6 tasks (pending)
Group 4-8:   43 tasks (pending)
Group 9:      7 tasks (pending - includes monitor integration)
Group 10:     6 tasks (pending - includes monitor integration)
Group 11-15: 38 tasks (pending)
Group 16:     6 tasks (pending)
─────────────────────────
TOTAL:       110 tasks

Progress: 14/110 (12.7%)

Estimated Timeline:
- Groups 0.5-10:   76 tasks → 40-50 hours (foundation)
- Groups 11-15:    34 tasks → 15-20 hours (features + docs)
- Group 16:         6 tasks → 2-3 hours (Phase 2 planning)
─────────────────────────
Total Phase 1:     ~60-75 hours
```

---

## Documentation References

1. **`docs/EXECUTION_AND_MONITORING.md`**
   - Complete startup model (Section 1)
   - Serial monitoring details (Section 2)
   - Logging & debugging strategy (Section 3)
   - Camera interface stubs (Section 4)
   - main.py skeleton code (Section 5)
   - New Group 0.5 tasks (Section 6)

2. **`docs/ARCHITECTURE_DIAGRAM.md`**
   - Complete system architecture diagram
   - Data flow for single command cycle
   - State transition example (guide open)
   - Debug breakpoint flow
   - Logging hierarchy

3. **`docs/TASK_PLAN_UPDATED.md`**
   - Overview & revised group structure
   - Group 0.5 detailed tasks
   - How this solves your requirements
   - Updated task count

4. **`README.md`** (updated)
   - Two-terminal workflow
   - --verbose, --hex, --debug flags
   - Monitoring output example
   - Logs directory structure

---

## Summary

✅ **All Three Questions Addressed:**

1. **Emulator Launch:** Backend daemon (manual start, always running, no UI)
2. **Serial Monitor:** Three levels (human-readable, hex dump, command logging)
3. **Logging & Debug:** Baseline (auto), debug mode (breakpoints), interactive (Phase 2)

✅ **New Group 0.5:** 6 tasks for serial monitor infrastructure

✅ **Documentation Complete:** 4 comprehensive guides covering execution, monitoring, architecture

✅ **Design Validated:** Phased approach, scalable, decoupled from LabVIEW

---

## Next Steps

**Option 1: Implement Group 0.5 immediately** (3-4 hours)
- Core visibility infrastructure in place
- Then proceed to Group 3 (Opcode Parser) with high confidence

**Option 2: Review & refine first**
- Clarify any remaining questions
- Adjust group priority if needed
- Then proceed with implementation

Which approach would you prefer?
