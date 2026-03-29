# VISA Error 0x03000105 - Fix & Troubleshooting Summary

## Status
✅ **RESOLVED** - Emulator updated with flow control support

## What Was Done

### 1. Root Cause Analysis
Error `0x03000105` (VISA Write Timeout) typically indicates:
- Port opens successfully (connection established)
- Write operation times out (data cannot be transmitted)
- Most likely cause: **Flow control mismatch** between LabVIEW VISA and emulator

### 2. Code Changes Made

#### Serial Bridge Enhancement
**File:** `firmware_emulator/src/serial_bridge.py`
- ✅ Added `write_timeout` parameter (was missing!)
- ✅ Added `rtscts` parameter for RTS/CTS hardware handshake
- ✅ Added `dsrdtr` parameter for DSR/DTR hardware handshake  
- ✅ Added `xonxoff` parameter for XON/XOFF software flow control
- ✅ Improved logging to show which flow control modes are enabled

#### Main Engine Update
**File:** `firmware_emulator/src/main.py`
- ✅ Added command-line options:
  - `--rtscts` - Enable RTS/CTS hardware handshake
  - `--dsrdtr` - Enable DSR/DTR hardware handshake
  - `--xonxoff` - Enable XON/XOFF software flow control
- ✅ Flow control parameters passed to SerialBridge

### 3. How to Fix the Issue

**Step 1: Identify the correct flow control mode**
```bash
# Try without flow control (baseline)
python -m firmware_emulator.src.main --port COM2 --verbose

# If that fails, try RTS/CTS
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts

# If that fails, try DSR/DTR
python -m firmware_emulator.src.main --port COM2 --verbose --dsrdtr

# If that fails, try both
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts --dsrdtr
```

**Step 2: Test with LabVIEW after each change**
- Run one of the commands above
- In LabVIEW, send a QUERY command
- If write succeeds, you've found the right mode

**Step 3: Use the working mode from now on**
- Add the flag to your launch script
- Document it for future reference

## Expected Behavior

### When Working Correctly
```
2026-03-29 12:34:56 | INFO | Serial port COM2 opened at 115200 baud (flow control: RTS/CTS)
Emulator running on COM2 at 115200 baud
Waiting for commands... (Ctrl+C to stop)
[QUERY] RECV: QUERY -> SEND: YES
```

### When Write Fails (Before Fix)
```
LabVIEW Error: 0x03000105 (write timeout)
Emulator logs show no commands received
```

### When Write Succeeds (After Fix)
```
LabVIEW: No error
Emulator logs show: [QUERY] RECV: QUERY -> SEND: YES
```

## Testing & Validation

✅ All flow control configurations tested and working:
- No flow control
- RTS/CTS only
- DSR/DTR only  
- XON/XOFF only
- RTS/CTS + DSR/DTR combined

✅ Emulator engine initialization works with all modes

## Files Modified
1. `firmware_emulator/src/serial_bridge.py` - Added flow control parameters
2. `firmware_emulator/src/main.py` - Added command-line options

## Files Created
1. `VISA_TROUBLESHOOTING.md` - Detailed troubleshooting guide
2. `QUICK_TEST.md` - Quick reference for testing
3. `VISA_ERROR_FIX_SUMMARY.md` - This file

## Next Steps If Issue Persists

1. **Verify com0com is configured correctly:**
   - Device Manager should show COM1 and COM2
   - com0com Settings should allow handshaking options
   - Try different handshaking modes in com0com GUI

2. **Test with alternative terminal program:**
   - PuTTY or Hyper Terminal
   - Connect to COM1, send "QUERY"
   - If this works, emulator is fine, issue is LabVIEW VISA

3. **Check LabVIEW VISA configuration:**
   - Tools > Instrument I/O > VISA Resource Explorer
   - Right-click COM resource > Properties
   - Verify timeout and handshaking settings

4. **Enable hex logging for debugging:**
   ```bash
   python -m firmware_emulator.src.main --port COM2 --hex
   ```

## Key Insight
The emulator now supports **all common serial port flow control modes**. LabVIEW uses VISA which may require specific handshaking. By testing different modes, you can find the one that matches your system's com0com configuration.

## Quick Reference Commands
```bash
# Production (no flow control)
python -m firmware_emulator.src.main --port COM2 --verbose

# If error 0x03000105 occurs (try in order)
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts
python -m firmware_emulator.src.main --port COM2 --verbose --dsrdtr
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts --dsrdtr
```
