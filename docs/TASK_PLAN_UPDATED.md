# Updated Task Plan: Execution & Monitoring Integration

## Overview

Based on clarifications about LabVIEW startup, serial monitoring, and debugging requirements, we've added a new **Group 0.5: Serial Monitor & Debugging Infrastructure** to be completed before the main handler implementation.

**Total Tasks: 110 (was 104 + 6 new)**

---

## Revised Group Structure

### ✅ Completed
- **Group 1**: Project Setup (6/6)
- **Group 2**: Device State Machine (8/8)

### 🔄 New: Group 0.5 (Priority)
- **Serial Monitor & Debugging** (6 tasks) - INSERT BEFORE Group 3
- Enables: Real-time command visibility, hex dump, debug breakpoints

### 📋 Remaining (Sequential)
1. **Group 3**: Opcode Parser Framework (6 tasks)
2. **Groups 4-8**: Command Handlers (43 tasks)
3. **Group 9**: Serial Communication (7 tasks) - *includes monitor integration*
4. **Group 10**: Main Emulator Loop (6 tasks)
5. **Groups 11-15**: Virtual Camera, Event Simulator, Testing, Docs (38 tasks)
6. **Group 16**: Phase 2 Planning (6 tasks)

---

## New Group 0.5: Serial Monitor & Debugging Infrastructure

### Purpose
Enable real-time visibility into command flow and state changes without external tools.

### Tasks

#### 0.5.1 Create SerialMonitor Class
**File**: `src/serial_monitor.py`

```python
class SerialMonitor:
    """Human-readable serial protocol logging"""
    
    def __init__(self, verbose: bool = False, hex_dump: bool = False):
        self.verbose = verbose
        self.hex_dump = hex_dump
        self.command_count = 0
    
    def log_command(self, opcode: str, response: str, delay_ms: int = 0):
        """Log command/response in human-readable format"""
        # [timestamp] RECV: QUERY → SEND: YES
        # [timestamp] RECV: tpGOP → SEND: tpGOR [2000ms delay]
    
    def log_hex(self, label: str, data: bytes):
        """Log raw bytes in hex format"""
        # [timestamp] RECV: [51 55 45 52 59] "QUERY"
    
    def log_error(self, opcode: str, error: str):
        """Log protocol errors"""
        # [timestamp] ERROR: Unknown opcode: FLS01 → FLS
```

#### 0.5.2 Implement --verbose Flag
**File**: `src/main.py`

Add argparse option:
```python
parser.add_argument("--verbose", action="store_true", help="Show command/response to console")
```

Real-time console output (non-intrusive, doesn't block event loop):
- Format: `[timestamp] RECV: OPCODE → SEND: RESPONSE`
- Line-buffered (doesn't clutter with every byte)
- Optional delay annotation: `[2000ms]` for timed operations

#### 0.5.3 Implement --hex Flag
**File**: `src/serial_monitor.py`

Protocol-level visibility:
- Format: `[timestamp] RECV: [byte1 byte2 byte3 byte4 byte5] "ASCII"`
- Helps verify 5-byte protocol compliance
- Diagnose corrupted frames (parity, encoding errors)

#### 0.5.4 Create Enhanced Logging: Command Tracking
**File**: `src/opcode_handler.py` (Group 3 integration point)

Log template for every opcode:
```
[COMMAND_001]
  Time: 2026-03-28 07:53:25.123
  Opcode: QUERY
  Response: YES
  State Before: {power_on: True, estop_pressed: False, ...}
  State After: {power_on: True, estop_pressed: False, ...}
  Duration: 0.45ms
```

Goes to: `logs/commands_<timestamp>.log`

#### 0.5.5 Implement --debug Flag (Phase 2 Foundation)
**File**: `src/debug_breakpoint.py`

```python
parser.add_argument("--debug", nargs="*", 
    help="Breakpoint on opcodes (e.g., --debug tpGOP LCS01)")
```

Phase 1: Just warn when breakpoint opcode arrives
Phase 2: Pause execution, allow state inspection

#### 0.5.6 Implement --interactive Flag (Phase 2 Foundation)
**File**: `src/interactive_monitor.py`

Interactive console for debugging:
```
(emulator) > state
(emulator) > set guide_top.position OPEN
(emulator) > inject QUERY
```

Phase 1: Stub with help message
Phase 2: Full REPL implementation

---

## Implementation Order

### Phase 1 (This Sprint)
1. **Group 0.5.1-0.5.4**: Serial monitor + command logging ✅ Core feature
2. **Group 0.5.5-0.5.6**: Debug/interactive stubs ✅ Placeholder
3. **Group 3-10**: Main handler implementation
4. **Group 11-15**: Virtual camera, testing, docs

### Phase 2 (Future)
1. Enhance 0.5.5 with actual breakpoint logic
2. Implement 0.5.6 REPL mode
3. Interactive camera frame injection
4. Advanced state inspection

---

## Files Affected

### New Files
- `src/serial_monitor.py` (Task 0.5.1-0.5.3)
- `src/debug_breakpoint.py` (Task 0.5.5)
- `src/interactive_monitor.py` (Task 0.5.6)

### Modified Files
- `src/main.py` (CLI arguments, monitor initialization)
- `src/opcode_handler.py` (when created in Group 3, integrate monitoring)
- `src/emulator_engine.py` (when created in Group 10, use monitors)
- `README.md` ✅ (done)
- `docs/EXECUTION_AND_MONITORING.md` ✅ (created)

---

## How This Solves Your Requirements

### 1. LabVIEW Application Startup
```
User opens LabVIEW:
  ↓
LabVIEW checks COM4 → Found (paired with emulator's COM3)
  ↓
LabVIEW checks camera interface → Stub response (Phase 1)
  ↓
LabVIEW sends QUERY
  ↓
Emulator responds YES
  ↓
Full communication begins (developer watches in Terminal 1)
```

### 2. Serial Monitor for Command Inspection
**Terminal 1 output (--verbose):**
```
[2026-03-28 07:53:25.123] RECV: QUERY         → SEND: YES
[2026-03-28 07:53:26.045] RECV: tpGOP         → SEND: tpGOR [2000ms]
[2026-03-28 07:53:28.067] RECV: LCS01         → SEND: (camera trigger)
[2026-03-28 07:53:28.234] RECV: TSENB         → SEND: (timestamp enabled)
```

**Logs available anytime:**
```
$ tail -f logs/commands_*.log
[COMMAND_001] QUERY → YES
[COMMAND_002] tpGOP → tpGOR [state: guide_top.position = MOVING → OPEN]
[COMMAND_003] LCS01 → CAMERA_TRIG [state: cameras.flags[0] = False → True]
```

### 3. Logging & Debugging
**Always-on logging (baseline):**
- 4 log files per session (main, serial, commands, debug)
- Rotating file handlers (5MB max)
- Console INFO + file DEBUG

**Optional --debug flag:**
- Phase 1: Logs warning on breakpoint opcode
- Phase 2: Pauses execution for inspection

**Optional --interactive flag:**
- Phase 1: Stub with help
- Phase 2: Full REPL for state modification & injection

---

## Updated Task Count

```
Group 0.5:   6 new tasks (serial monitor)
Group 1:     6 tasks (✅ complete)
Group 2:     8 tasks (✅ complete)
Group 3:     6 tasks (pending)
Group 4-8:   43 tasks (pending)
Group 9:     7 tasks (pending, with monitor integration)
Group 10:    6 tasks (pending, with monitor integration)
Group 11-15: 38 tasks (pending)
Group 16:    6 tasks (pending)
─────────────────────────
TOTAL:       110 tasks

Progress: 14/110 (12.7%)
Estimated Groups 0.5-10: 76 tasks → ~40-50 hours
Estimated Groups 11-16: 34 tasks → ~15-20 hours
Total Phase 1: ~55-70 hours
```

---

## Recommendation

✅ **Insert Group 0.5 immediately** (estimated 3-4 hours)

Benefits:
1. **Transparency**: Developer sees every command in real-time
2. **Debugging**: Comprehensive logs for issue diagnosis
3. **Phased approach**: Phase 1 has basics, Phase 2 adds interactivity
4. **Non-intrusive**: Flags are optional, doesn't slow emulator

Then proceed with Group 3 (Opcode Parser) with confidence that monitoring is in place.

Ready to implement Group 0.5?
