# Firmware Emulator: Execution & Monitoring Strategy

## 1. Launch Model: Backend Daemon (Manual Start)

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     DEVELOPER MACHINE                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Terminal 1                      Terminal 2                  │
│  ┌──────────────────┐           ┌──────────────────┐        │
│  │ $ python3 main.py│           │ LabVIEW IDE      │        │
│  │ [Emulator]       │◄──COM3───►│ (running app)    │        │
│  │ ↓                │           │                  │        │
│  │ QUERY → YES      │           │ Opens serial...  │        │
│  │ tpGOP → tpGOR    │           │ Sends: QUERY     │        │
│  │ tpGCL → tpGCR    │           │ Receives: YES    │        │
│  │ ...              │           │                  │        │
│  └──────────────────┘           └──────────────────┘        │
│       (logs/)                                                 │
│       ├── emulator_20260328_075325.log                       │
│       ├── serial_20260328_075325.log                         │
│       ├── commands_20260328_075325.log                       │
│       └── debug_20260328_075325.log                          │
│                                                               │
│  Virtual COM Port Pair (com0com):                            │
│  ┌─────────────────┐          ┌──────────────────┐          │
│  │ COM3            │◄────────►│ COM4             │          │
│  │ (Emulator side) │ (virtual) │ (LabVIEW side)   │          │
│  └─────────────────┘          └──────────────────┘          │
│                                                               │
│  Camera Interface (Phase 2):                                 │
│  Shared memory / named pipes for image frames                │
│  (stub in Phase 1)                                           │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Startup Sequence

**Phase 1 (Current)**
```bash
# Terminal 1: Start emulator (blocks, runs forever)
$ python3 firmware_emulator/src/main.py --port COM3 --verbose

# Terminal 2: Launch LabVIEW
$ labview &  # or click IDE icon

# LabVIEW connects to COM4 (paired with COM3)
# Communication begins automatically
```

**Phase 2 (Auto-start helper)**
```bash
# Single command launcher (optional convenience)
$ python3 launch_emulator_and_labview.py

# Spawns:
# - Emulator in background (daemon)
# - LabVIEW in foreground
# - Emulator console in separate window (Windows: cmd.exe)
```

### Key Points
- **Manual start = predictable**: User has explicit control
- **Always running**: Emulator doesn't exit until Ctrl+C
- **No UI bloat**: Keeps emulator lean for embedded/headless future
- **Clear separation**: LabVIEW is independent (doesn't know about emulator)

---

## 2. Serial Monitor: Real-Time Command/Response Visibility

### Current Output (Will Implement)

**Default (--verbose flag)**
```
[2026-03-28 07:53:25.123] RECV: QUERY         → SEND: YES
[2026-03-28 07:53:26.045] RECV: tpGOP         → SEND: tpGOR [2000ms delay]
[2026-03-28 07:53:28.067] RECV: tpLSC         → ERROR: tpOL0 (limit not pressed)
[2026-03-28 07:53:28.234] RECV: LCS01         → CAMERA TRIGGER [camera_id=0]
[2026-03-28 07:53:28.235] RECV: TSENB         → TIMESTAMP ENABLED
```

**With --hex flag (full protocol dump)**
```
[2026-03-28 07:53:25.123] RECV: [51 55 45 52 59] "QUERY" → SEND: [89 69 83] "YES"
[2026-03-28 07:53:26.045] RECV: [116 112 71 79 80] "tpGOP" → SEND: [116 112 71 79 82] "tpGOR"
```

**With --interactive flag (live breakpoint mode - Phase 2)**
```
[2026-03-28 07:53:25.123] RECV: QUERY
→ Press Enter to respond, or 'skip' to ignore, or 'inject <opcode>' to test:
> [ENTER]
SEND: YES

[2026-03-28 07:53:26.045] RECV: tpGOP
→ Break [opcode=tpGOP, state_before={guide_top.position=UNKNOWN}]
> state.guide_top.position = OPEN  # inject Python command
> continue
SEND: tpGOR [with modified state]
```

### Serial Monitor in logs/

Each session creates dedicated command log:

**logs/commands_20260328_075325.log**
```
[COMMAND_001] T=07:53:25.123  OPCODE=QUERY       STATE_BEFORE={...}  RESPONSE=YES         STATE_AFTER={...}
[COMMAND_002] T=07:53:26.045  OPCODE=tpGOP       STATE_BEFORE={...}  RESPONSE=tpGOR       STATE_AFTER={guide_top.position=MOVING}
[COMMAND_003] T=07:53:28.067  OPCODE=tpGCL       STATE_BEFORE={...}  RESPONSE=tpGCR       STATE_AFTER={guide_top.position=CLOSED}
[COMMAND_004] T=07:53:28.234  OPCODE=LCS01       STATE_BEFORE={...}  RESPONSE=CAMERA_TRIG STATE_AFTER={cameras.flags[0]=True}
```

### Implementation Details

```python
# In SerialBridge (Group 9)
def read_and_log(self):
    """Read 5 bytes, log as human-readable command"""
    buffer = self.port.read(5)
    opcode_str = buffer.decode('ascii', errors='ignore')
    
    if self.verbose:
        print(f"[{timestamp}] RECV: {opcode_str:10s}", end="")
    
    return opcode_str

def write_and_log(self, response):
    """Write response, log as human-readable"""
    self.port.write(response.encode('ascii'))
    
    if self.verbose:
        print(f" → SEND: {response}")
    
    logger.info(f"COMMAND: {opcode_str} -> {response}")
```

---

## 3. Logging & Debugging: Layered Approach

### Level 1: Baseline Logging (Always On)

**Files created per session:**
```
logs/
├── emulator_20260328_075325.log        # Main events: startup, shutdown, errors
├── serial_20260328_075325.log          # Serial port events: open, close, timeouts
├── commands_20260328_075325.log        # Every command: opcode, response, state delta
└── debug_20260328_075325.log           # State changes, handler details (DEBUG level)
```

**Example: emulator_20260328_075325.log**
```
2026-03-28 07:53:25.001 | INFO     | main                | Emulator starting on COM3 @ 9600 baud
2026-03-28 07:53:25.012 | INFO     | config_parser       | Loaded 75 opcodes from MI JSON
2026-03-28 07:53:25.015 | DEBUG    | serial_bridge       | Serial port opened: COM3
2026-03-28 07:53:25.123 | INFO     | opcode_handler      | QUERY → YES
2026-03-28 07:53:26.045 | INFO     | opcode_handler      | tpGOP → tpGOR [delayed 2000ms]
2026-03-28 07:53:28.067 | ERROR    | opcode_handler      | Unknown opcode: FLS01 → FLS
2026-03-28 07:53:29.234 | INFO     | event_simulator     | Sensor trigger [top, debounce=30ms]
```

### Level 2: Debug Mode (--debug flag)

**Activates conditional breakpoints:**
```bash
$ python3 src/main.py --port COM3 --debug "tpGOP,LCS01"
```

Pauses execution before sending response, allows inspection:
```
[2026-03-28 07:53:26.045] RECV: tpGOP
DEBUG BREAKPOINT: Handler=guide_open
  state_before = {guide_top: {position: UNKNOWN, moving: False}}
  handler_args = {}
  
  (emulator) > state.guide_top.position
  'GuidePosition.UNKNOWN'
  
  (emulator) > state.guide_top.position = GuidePosition.OPEN
  
  (emulator) > continue
  
Response: tpGOR
  state_after = {guide_top: {position: OPEN, moving: False}}
```

### Level 3: Interactive Monitor (--interactive flag, Phase 2)

**Live command injection & inspection:**
```bash
$ python3 src/main.py --port COM3 --interactive
```

Console mode:
```
(emulator) > help
  Commands:
    state              - Print current device state
    set <attr> <val>   - Modify state (e.g., "set guide_top.position OPEN")
    inject <opcode>    - Send opcode to handler (e.g., "inject QUERY")
    pause              - Pause on next command
    resume             - Resume if paused
    snapshot           - Save current state to JSON file
    help               - This message

(emulator) > state
DeviceState:
  guide_top: {position: UNKNOWN, moving: False, reached_limit: False}
  guide_bottom: {position: UNKNOWN, moving: False, reached_limit: False}
  sensor_top: {attached: False, powered: False}
  sensor_bottom: {attached: False, powered: False}
  lamps: {red: False, yellow: False, green: False, buzzer: False}
  cameras: {flags: {0: False, 1: False, ...}, timestamp_enabled: False}
  ... (24 keys total)

(emulator) > inject QUERY
QUERY → YES

(emulator) > set guide_top.position OPEN
Updated: guide_top.position = GuidePosition.OPEN

(emulator) > continue
```

---

## 4. Integration with Camera Interface (Phase 1 Stub)

### Phase 1 Design

**No real camera; image placeholder system:**
```python
class VirtualCamera:
    def trigger(self, camera_id: int, sequence_name: str):
        """Generate synthetic image (test pattern)"""
        # Create simple test pattern: gradient, circles, etc.
        image_data = generate_test_pattern(camera_id, width=1024, height=768)
        
        # Create metadata
        metadata = {
            'timestamp': time.time(),
            'trigger_count': self.trigger_count,
            'camera_id': camera_id,
            'sequence_name': sequence_name,
        }
        
        # Store in queue for LabVIEW
        self.frame_queue.put((image_data, metadata))
        
        logger.info(f"Camera {camera_id} triggered: {sequence_name}")
```

### Phase 2: IMAQDX Integration

LabVIEW connects via IMAQDX driver:
```
LabVIEW
  ↓
IMAQDX (IMAQdx.dll)
  ↓
Emulator: VirtualCamera module
  ├── Read from: shared memory / named pipe
  ├── Image format: raw bytes (RGB/BGR)
  └── Metadata: JSON-encoded alongside image
```

**Phase 1 stub implementation:**
```python
# In VirtualCamera (Group 11)
def get_frame_blocking(self, timeout_ms: int = 1000) -> Tuple[np.ndarray, Dict]:
    """
    Get next frame from queue (stub for IMAQDX integration).
    
    Args:
        timeout_ms: Max time to wait for frame
    
    Returns:
        (image_array, metadata_dict) or None if timeout
    """
    try:
        image, metadata = self.frame_queue.get(timeout=timeout_ms/1000.0)
        return image, metadata
    except queue.Empty:
        return None

# LabVIEW will call this via shared memory (Phase 2)
# Phase 1: just verify frames are generated when LCS opcodes trigger
```

---

## 5. Updated main.py Skeleton

```python
#!/usr/bin/env python3
"""
Firmware Emulator Entry Point
Handles CLI flags: --port, --verbose, --debug, --interactive
"""

import argparse
import sys
from src.logging_config import setup_root_logger, MAIN_LOGGER
from src.config_parser import MachineConfig
from src.emulator_engine import EmulatorEngine
from src.serial_bridge import SerialBridge

def main():
    parser = argparse.ArgumentParser(
        description="GTRON Vision System Firmware Emulator"
    )
    parser.add_argument("--port", default="COM3", help="Serial port (default: COM3)")
    parser.add_argument("--config", default="Machine Interface Parameters.json")
    parser.add_argument("--verbose", action="store_true", help="Show command/response")
    parser.add_argument("--hex", action="store_true", help="Show hex dump of protocol")
    parser.add_argument("--debug", nargs="*", help="Breakpoint on opcodes (e.g., --debug tpGOP LCS01)")
    parser.add_argument("--interactive", action="store_true", help="Interactive monitor mode")
    
    args = parser.parse_args()
    
    # Setup logging
    setup_root_logger()
    logger = MAIN_LOGGER
    
    try:
        logger.info("=" * 70)
        logger.info("GTRON Vision System Firmware Emulator v1.0")
        logger.info(f"COM Port: {args.port} @ 9600 baud")
        logger.info(f"Config: {args.config}")
        if args.verbose:
            logger.info("Verbose mode: ON (command/response visible)")
        if args.debug:
            logger.info(f"Debug mode: ON (breakpoints on {args.debug})")
        if args.interactive:
            logger.info("Interactive mode: ON")
        logger.info("=" * 70)
        
        # Load config
        config = MachineConfig(args.config)
        
        # Create serial bridge
        serial = SerialBridge(
            port=args.port,
            verbose=args.verbose,
            hex_dump=args.hex
        )
        
        # Create emulator engine
        engine = EmulatorEngine(
            serial=serial,
            config=config,
            debug_opcodes=args.debug or [],
            interactive=args.interactive
        )
        
        # Run event loop
        logger.info("Starting event loop... (Press Ctrl+C to stop)")
        engine.run()
        
    except KeyboardInterrupt:
        logger.info("Shutdown requested (Ctrl+C)")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()
```

---

## 6. New Group: Monitoring & Debugging Infrastructure

### New Tasks to Add

**Group 0.5: Serial Monitor & Debugging (6 tasks)**
- [ ] 0.5.1 Create SerialMonitor class with human-readable formatting
- [ ] 0.5.2 Implement --verbose flag (command/response logging to console)
- [ ] 0.5.3 Implement --hex flag (byte-level protocol dump)
- [ ] 0.5.4 Create enhanced logging: opcode tracking with state before/after
- [ ] 0.5.5 Implement --debug flag with breakpoint system (Phase 2)
- [ ] 0.5.6 Implement --interactive flag with REPL mode (Phase 2)

**Updated Groups**
- **Group 9**: Add SerialMonitor integration to SerialBridge
- **Group 10**: Add monitoring support to EmulatorEngine

---

## Summary: How LabVIEW Discovers Camera & COM Port

### COM Port Discovery
1. **com0com creates paired ports** (e.g., COM3 ↔ COM4)
2. **Emulator connects to COM3** with `SerialBridge(port="COM3")`
3. **LabVIEW configures to COM4** (user manual step in docs)
4. **When LabVIEW sends QUERY**, emulator responds with YES → connection verified

### Camera Discovery (Phase 1 Stub)
1. **Phase 1**: Emulator provides fake camera frames via `VirtualCamera.get_frame_blocking()`
2. **Phase 2**: IMAQDX driver integration (shared memory or named pipes)
3. **LabVIEW detects**: Emulated camera in IMAQdx enumeration (via registration key)

---

## Recommendation

1. **Implement Group 0.5** (Serial Monitor) before Groups 3+
2. **Keep backend model**: No UI, user controls via CLI flags
3. **Logging becomes the UI**: Real-time visibility via console + logs
4. **Phase 2 adds interactivity**: Interactive mode for advanced debugging

Ready to revise task plan?
