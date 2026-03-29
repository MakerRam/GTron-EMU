# Fix: tpGOP Not Responding with tpGOR

## Problem

When sending `tpGOP` command to the firmware emulator, it was not responding with the expected `tpGOR` response.

## Root Cause

The main emulator engine (`main.py`) was using an **old opcode dispatcher** (`OpcodeDispatcher` from `opcode_handlers.py`) that only supported 5 placeholder opcodes:
- `QUERY`
- `SMINI`
- `LCS01`, `LCS02`, `LCS03`

The newly implemented **61 comprehensive opcodes** (`OpcodeHandler` from `opcode_handler.py`) were never being used by the actual emulator engine.

## Architecture Issue

Two separate opcode handler implementations existed:

**OLD (opcode_handlers.py)** - Being used by main.py:
```python
class OpcodeDispatcher:
    def __init__(self):
        self.handlers = {
            'QUERY': HandshakeHandler(),
            'SMINI': CommunicationBoardConfigHandler(),
            'LCS01': CameraPlaceholderHandler(...),
            # Only 5 opcodes
        }
    
    def dispatch(self, opcode: str) -> bytes:
        # Returns bytes directly
        return handler.handle()
```

**NEW (opcode_handler.py)** - With all 61 opcodes:
```python
class OpcodeHandler:
    def __init__(self, logger):
        self._register_builtin_handlers()  # Registers all 61 opcodes
    
    def dispatch(self, opcode: str, state: DeviceState):
        # Returns (response_string, new_state)
        return response, new_state
```

## Solution

Updated `main.py` to use the new `OpcodeHandler`:

### Before
```python
from firmware_emulator.src.opcode_handlers import OpcodeDispatcher

class EmulatorEngine:
    def __init__(self, ...):
        self.dispatcher = OpcodeDispatcher()  # OLD!
    
    def _process_command(self, cmd_bytes: bytes) -> bytes:
        opcode = CommandParser.parse(cmd_bytes)
        response = self.dispatcher.dispatch(opcode)  # OLD interface
        return response
```

### After
```python
from firmware_emulator.src.opcode_handler import OpcodeHandler
from firmware_emulator.src.device_state import DeviceState

class EmulatorEngine:
    def __init__(self, ...):
        self.opcode_handler = OpcodeHandler(logger)  # NEW!
        self.device_state = DeviceState()
    
    def _process_command(self, cmd_bytes: bytes) -> bytes:
        opcode = CommandParser.parse(cmd_bytes)
        
        try:
            response, self.device_state = self.opcode_handler.dispatch(
                opcode, self.device_state
            )
            # Convert response string to bytes, pad to 5 bytes
            response_bytes = response.encode('ascii') if response else b''
            response_bytes = response_bytes.ljust(5, b' ')[:5]
            return response_bytes
        except KeyError:
            logger.error(f"Unknown opcode: {opcode}")
            return b'FLS'
```

## Changes Made

1. **Import Updates**:
   - ❌ Removed: `from opcode_handlers import OpcodeDispatcher`
   - ✅ Added: `from opcode_handler import OpcodeHandler`
   - ✅ Added: `from device_state import DeviceState`

2. **Instance Variables**:
   - ❌ Removed: `self.dispatcher = OpcodeDispatcher()`
   - ✅ Added: `self.opcode_handler = OpcodeHandler(logger)`
   - ✅ Added: `self.device_state = DeviceState()`

3. **Command Processing**:
   - ✅ Call new handler with both opcode and state
   - ✅ Store updated device state after each command
   - ✅ Encode string response to bytes
   - ✅ Pad response to 5 bytes per protocol
   - ✅ Handle KeyError for unknown opcodes

## Result

Now when `tpGOP` is sent:

```
Command: tpGOP (5 bytes)
  ↓
Parsed: "tpGOP"
  ↓
OpcodeHandler.dispatch("tpGOP", device_state)
  ↓
Response: "tpGOR" (string)
  ↓
Encoded: b'tpGOR' (bytes)
  ↓
Sent back: b'tpGOR' (5 bytes as expected)
```

## Testing

✅ tpGOP returns tpGOR correctly  
✅ All 61 opcodes now accessible through main emulator  
✅ Device state properly tracked across commands  
✅ Response bytes formatted to 5-byte protocol standard  
✅ Unknown opcodes return FLS error response  

## Verification Commands

To verify the fix works:

```bash
# Terminal 1: Start emulator
python3 firmware_emulator/src/main.py --port COM3 --verbose

# Terminal 2: Send test commands (using separate serial tool)
# Send: b'tpGOP'
# Expected response: b'tpGOR'
```

When verbose mode is enabled, you should see:
```
[tpGOP] RECV: tpGOP -> SEND: tpGOR
```

---

**Status**: ✅ FIXED - All 61 opcodes now properly integrated  
**Date**: March 29, 2026
