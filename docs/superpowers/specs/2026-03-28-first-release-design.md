# First Release Design: Serial Communication & Virtual Camera Module

**Date:** March 28, 2026  
**Status:** Design Approved  
**Target Completion:** ~4-5 hours

---

## Executive Summary

This first release delivers a working Vision System Firmware Emulator capable of:
1. **Serial Communication** - COM3 listener with 5-byte ASCII protocol
2. **Handshake Protocol** - QUERY → YES exchange to verify emulator is ready
3. **Virtual Camera Module** - Reads images from local folders, serves to LabVIEW via IMAQDX-compatible interface
4. **End-to-End Validation** - Unit tests + manual LabVIEW verification

**Success Criteria:**
- ✅ Emulator launches and listens on COM3
- ✅ LabVIEW connects to COM4 and sends QUERY
- ✅ Emulator responds YES
- ✅ Camera module ready for IMAQDX queries
- ✅ All unit tests pass
- ✅ Logs show complete transaction history

---

## Design Details

### 1. Serial Communication Layer

**File:** `firmware_emulator/src/serial_bridge.py`

**Responsibilities:**
- Open COM port (default 9600 baud, 8 data bits, 1 stop bit, no parity)
- Non-blocking read with timeout (1 second)
- Write 5-byte commands and 3-5 byte responses
- Handle port errors gracefully
- Log all I/O with timestamps

**Interface:**
```python
class SerialBridge:
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0)
    def is_open(self) -> bool
    def read_command(self) -> Optional[bytes]        # Returns 5-byte command or None
    def write_response(self, response: bytes) -> bool
    def close(self)
    def __enter__, __exit__  # Context manager support
```

**Error Handling:**
- Port not found → Log error + exit
- Timeout → Return None (normal condition)
- Write error → Log + raise SerialException

---

### 2. Command Parser

**File:** `firmware_emulator/src/command_parser.py`

**Responsibilities:**
- Validate 5-byte ASCII format
- Parse opcode (first 5 bytes → string)
- Route to appropriate handler
- Return default "FLS" for unknown opcodes

**Interface:**
```python
class CommandParser:
    @staticmethod
    def parse(command_bytes: bytes) -> str
        """Parse 5 bytes to opcode string"""
    
    @staticmethod
    def is_valid_command(command_bytes: bytes) -> bool
        """Validate format"""
```

**Examples:**
- Input: `[0x51, 0x55, 0x45, 0x52, 0x59]` → Output: `"QUERY"`
- Input: `[0x4C, 0x43, 0x53, 0x30, 0x31]` → Output: `"LCS01"` (camera trigger)
- Input: `[0x58, 0x58, 0x58, 0x58, 0x58]` → Output: `"XXXXX"` (unknown → respond "FLS")

---

### 3. Handshake Handler

**File:** `firmware_emulator/src/opcode_handlers.py` (QUERY handler)

**Responsibilities:**
- Handle QUERY opcode
- Respond with "YES" (3 bytes: 0x59, 0x45, 0x53)
- Update device state: `device_ready = True`
- Log handshake event

**Behavior:**
```
RECV: QUERY [0x51 0x55 0x45 0x52 0x59]
  → Device State: power_on=True
  → Response: YES [0x59 0x45 0x53]
  → Log: "[2026-03-28 10:30:45] HANDSHAKE COMPLETE: device_ready=True"
```

---

### 4. Virtual Camera Module

**File:** `firmware_emulator/src/virtual_camera.py`

**Responsibilities:**
- Load images from local folder structure
- Manage frame buffer (current frame + metadata)
- Trigger on camera command (e.g., LCS01)
- Serve metadata to LabVIEW

**Folder Structure:**
```
camera_images/
├── top/
│   ├── top_001.png
│   ├── top_002.png
│   └── ...
├── side/
│   ├── side_001.png
│   ├── side_002.png
│   └── ...
└── front/
    ├── front_001.png
    ├── front_002.png
    └── ...
```

**Frame Metadata Structure:**
```python
@dataclass
class CameraFrame:
    camera_id: str          # "top", "side", "front"
    image_bytes: bytes      # PNG/BMP raw data
    timestamp: float        # Unix timestamp (when triggered)
    trigger_count: int      # How many times this camera triggered
    frame_index: int        # Which frame in the sequence
```

**Interface:**
```python
class VirtualCamera:
    def __init__(self, camera_id: str, images_folder: str)
    
    def trigger(self) -> CameraFrame
        """Advance to next frame, return metadata + image bytes"""
    
    def get_current_frame(self) -> Optional[CameraFrame]
        """Get current frame without advancing"""
    
    def is_ready(self) -> bool
        """Check if folder has images loaded"""
```

**Camera IDs and Trigger Opcodes:**
- `"top"` → triggered by `LCS01`
- `"side"` → triggered by `LCS02`
- `"front"` → triggered by `LCS03`

---

### 5. IMAQDX Interface Compatibility

**File:** `firmware_emulator/src/imaqdx_interface.py`

**Responsibilities:**
- Format CameraFrame data for LabVIEW IMAQDX compatibility
- Provide image handle/reference for LabVIEW
- Expose frame metadata in expected structure
- Support repeated reads (same frame until new trigger)

**Metadata Format (LabVIEW-compatible struct):**
```python
@dataclass
class IMAQdxImageInfo:
    image_id: int           # Unique ID per frame
    timestamp: int          # Milliseconds since epoch
    camera_id: str          # "top", "side", "front"
    trigger_count: int      # Total triggers
    frame_number: int       # Sequential frame index
    width: int              # Image width (from file)
    height: int             # Image height (from file)
    bytes_per_pixel: int    # 1 (grayscale) or 3 (RGB)
    image_data_ptr: int     # Pointer to raw image bytes
```

**Interface:**
```python
class IMAQdxInterface:
    def __init__(self, virtual_camera: VirtualCamera)
    
    def get_image_info(self) -> IMAQdxImageInfo
        """Return metadata of current frame"""
    
    def get_image_data(self) -> bytes
        """Return raw image bytes (PNG/BMP)"""
    
    def is_ready(self) -> bool
```

---

### 6. Main Event Loop

**File:** `firmware_emulator/src/main.py`

**Flow:**
```
1. Parse CLI arguments (--port, --verbose, --debug, --interactive)
2. Load configuration (Machine Interface Parameters.json)
3. Initialize serial bridge
4. Initialize virtual camera module
5. Start event loop:
   a. Read command from COM port (timeout = 1 second)
   b. If command received:
      - Parse opcode
      - Route to handler
      - Execute handler
      - Update device state
      - Write response
   c. Log transaction (time, opcode, response, state delta)
   d. Continue loop
6. On Ctrl+C: Close serial port, exit gracefully
```

**Entry Point Interface:**
```bash
python3 firmware_emulator/src/main.py --port COM3 [--verbose] [--hex] [--debug opcode1 opcode2...]
```

**Flags:**
- `--port COM3` - Serial port (required)
- `--verbose` - Print human-readable commands to console
- `--hex` - Print hex bytes instead of ASCII
- `--debug opcode1 opcode2...` - Log warnings for specific opcodes (Phase 1)

---

### 7. Unit Tests

**Test Files:**
1. `tests/test_serial_bridge.py` - Serial I/O validation
2. `tests/test_command_parser.py` - Opcode parsing
3. `tests/test_handshake.py` - QUERY/YES exchange
4. `tests/test_virtual_camera.py` - Image loading and triggering
5. `tests/test_imaqdx_interface.py` - Metadata format
6. `tests/test_integration.py` - End-to-end flow

**Test Coverage:**
- ✅ SerialBridge opens port
- ✅ SerialBridge reads 5-byte commands
- ✅ SerialBridge writes 3-5 byte responses
- ✅ CommandParser validates ASCII
- ✅ CommandParser handles unknown opcodes
- ✅ Handshake: QUERY → YES response
- ✅ Device state updated on handshake
- ✅ Virtual camera loads images from folder
- ✅ Virtual camera cycles through images
- ✅ IMAQdx metadata format correct
- ✅ End-to-end: Open port → QUERY → YES → Camera ready

---

### 8. Logging Strategy

**Log Levels:**
- **INFO** - Startup, configuration, handshake complete
- **DEBUG** - Every command/response, state transitions
- **ERROR** - Port errors, invalid commands, exceptions

**Log Format:**
```
[2026-03-28 10:30:45.123] [HANDSHAKE] RECV: QUERY → SEND: YES | State: device_ready=True
[2026-03-28 10:30:46.045] [CAMERA   ] RECV: LCS01 → SEND: LCS1 | Camera: top, Frame: 1/10
```

**Auto-Created Log Files:**
```
logs/
├── emulator_20260328_103045.log       # Main events
├── serial_20260328_103045.log         # Serial I/O
├── commands_20260328_103045.log       # All commands with state delta
└── debug_20260328_103045.log          # DEBUG level details
```

---

## Folder Structure

```
firmware_emulator/
├── src/
│   ├── __init__.py
│   ├── main.py                       # Entry point
│   ├── serial_bridge.py              # COM port I/O
│   ├── command_parser.py             # 5-byte ASCII parser
│   ├── opcode_handlers.py            # QUERY handler (expand later)
│   ├── virtual_camera.py             # Image folder reader
│   ├── imaqdx_interface.py           # LabVIEW compatibility
│   ├── device_state.py               # (exists) State machine
│   └── logging_config.py             # (exists) Logging setup
├── camera_images/                    # USER POPULATES
│   ├── top/
│   ├── side/
│   └── front/
├── tests/
│   ├── __init__.py
│   ├── test_serial_bridge.py
│   ├── test_command_parser.py
│   ├── test_handshake.py
│   ├── test_virtual_camera.py
│   ├── test_imaqdx_interface.py
│   └── test_integration.py
├── logs/                             # Auto-created
├── Machine\ Interface\ Parameters.json
├── requirements.txt                  # (exists)
└── README.md                         # (update with quick start)
```

---

## Implementation Sequence

1. **SerialBridge** - Foundation for all communication
2. **CommandParser** - Enables opcode routing
3. **Handshake Handler** - QUERY/YES logic
4. **VirtualCamera** - Image loading and frame management
5. **IMAQdxInterface** - Metadata format for LabVIEW
6. **Main Event Loop** - Orchestrates everything
7. **Unit Tests** - Validate each component
8. **Integration Tests** - Full workflow validation

---

## Success Criteria (Detailed)

### Before LabVIEW Integration:
- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ Command-line startup works: `python3 src/main.py --port COM3`
- ✅ Logs created successfully
- ✅ No unhandled exceptions

### With LabVIEW Integration:
- ✅ LabVIEW connects to COM4 (paired with COM3)
- ✅ LabVIEW sends QUERY
- ✅ Emulator responds YES
- ✅ LabVIEW confirms device_ready = True
- ✅ LabVIEW can query camera via IMAQDX
- ✅ Camera returns image frame with metadata
- ✅ All transactions logged to files

---

## Dependencies

**Already Available:**
- `pyserial` (in requirements.txt)
- `device_state.py` (state machine)
- `logging_config.py` (logging infrastructure)
- `Machine Interface Parameters.json` (config)

**New Requirements:**
- Image files (you'll provide in `camera_images/` folders)

---

## Estimated Effort

| Component | Effort | Notes |
|-----------|--------|-------|
| SerialBridge | 45 min | Straightforward pyserial wrapper |
| CommandParser | 15 min | Simple byte parsing |
| Handshake | 20 min | Single opcode handler |
| VirtualCamera | 1 hour | Folder scanning, image loading |
| IMAQdxInterface | 30 min | Metadata struct + formatting |
| Main Loop | 45 min | Event loop orchestration |
| Unit Tests | 1.5 hours | 6 test files, ~40 test cases |
| Integration Tests | 30 min | Full workflow validation |
| **Total** | **~5 hours** | Conservative estimate |

---

## Acceptance Criteria

**Phase 1 - Unit Tests (Automated):**
```bash
pytest tests/ -v
# Expected: All tests pass (GREEN)
```

**Phase 2 - Manual LabVIEW Verification:**
1. Start emulator: `python3 firmware_emulator/src/main.py --port COM3 --verbose`
2. Launch LabVIEW application
3. LabVIEW connects to COM4
4. Observe console output:
   ```
   [2026-03-28 10:30:45.123] HANDSHAKE: RECV QUERY → SEND YES
   [2026-03-28 10:30:46.045] CAMERA: LCS01 triggered, serving frame 1/10
   ```
5. Check logs: `cat logs/commands_*.log | grep QUERY`
6. Expected: Transaction history with timestamps, opcodes, responses

**Go/No-Go Decision:**
- ✅ All tests pass → GO to next release
- ❌ Any test fails → Fix and re-test before proceeding

---

## Next Steps After Release 1

**Release 2 (Motor & Guide):**
- Add guide motor open/close handlers
- Implement position tracking
- Add limit switch simulation

**Release 3 (Advanced Features):**
- Encoder feedback
- Sensor triggers
- Light sequencing

---

## Appendix: IMAQDX Protocol Notes

LabVIEW's IMAQDX (Image Acquisition) interface expects:
1. **Image Handle** - Unique reference per frame
2. **Metadata Struct** - Timestamp, dimensions, camera ID
3. **Image Data** - Raw bytes (PNG, BMP, or raw pixel data)
4. **State Persistence** - Same image returned until new trigger

Our implementation handles all four requirements via:
- `CameraFrame.image_id` → Image handle
- `IMAQdxImageInfo` → Metadata struct
- `CameraFrame.image_bytes` → Image data
- `VirtualCamera.get_current_frame()` → State persistence

---

**Design Approved:** ✅  
**Ready for Implementation:** ✅  
**Ready for Testing:** ✅
