# Quick Test Guide for VISA Error 0x03000105

## The Problem
LabVIEW can CONNECT to COM1 but WRITE fails with error 0x03000105 (write timeout)

## Most Likely Cause
**Flow Control Mismatch** - LabVIEW VISA expects hardware handshake (RTS/CTS or DSR/DTR) that emulator doesn't provide

## Quick Fix (Try in This Order)

### Test 1: Check com0com Configuration
Before running emulator, verify virtual COM ports exist:
```bash
# On Windows, in Device Manager:
# Look for "COM1" and "COM2" under Ports (COM & LPT)
# If using different ports, note the exact numbers
```

### Test 2: Run Emulator WITHOUT Flow Control (Baseline)
```bash
python -m firmware_emulator.src.main --port COM2 --verbose
```
- Try LabVIEW write
- **If it works:** Your emulator is fine, issue is elsewhere
- **If it fails:** Continue to Test 3

### Test 3: Run Emulator WITH RTS/CTS Flow Control
```bash
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts
```
- Try LabVIEW write again
- **If it works NOW:** Use `--rtscts` for all future runs ✓
- **If it still fails:** Continue to Test 4

### Test 4: Run Emulator WITH DSR/DTR Flow Control
```bash
python -m firmware_emulator.src.main --port COM2 --verbose --dsrdtr
```
- Try LabVIEW write
- **If it works NOW:** Use `--dsrdtr` for all future runs ✓
- **If it still fails:** Continue to Test 5

### Test 5: Run Emulator WITH BOTH RTS/CTS + DSR/DTR
```bash
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts --dsrdtr
```
- Try LabVIEW write
- **If it works NOW:** Use both flags for all future runs ✓
- **If it still fails:** See "If Nothing Works" below

## Expected Output When Working
```
Emulator running on COM2 at 115200 baud
Waiting for commands... (Ctrl+C to stop)
[QUERY] RECV: QUERY -> SEND: YES
[QUERY] RECV: QUERY -> SEND: YES
```

## If Nothing Works

### Check 1: Verify COM Ports Actually Exist
```bash
# Windows: Device Manager > Ports (COM & LPT)
# Check that COM1 and COM2 are listed
# If not, reinstall com0com
```

### Check 2: Verify com0com Configuration
1. Open com0com from Windows control panel
2. Ensure the pair COM1 ↔ COM2 exists
3. Click "Edit" and check:
   - "Enable All States" should be checked
   - Handshaking options visible
4. Try different handshaking modes in com0com itself

### Check 3: Test com0com with Simple Terminal
1. Open PuTTY or similar terminal program
2. Connect to COM1 at 115200 baud
3. Type "QUERY" and press Enter
4. You should see "YES" response from emulator
5. **If this works:** com0com is fine, issue is LabVIEW VISA config
6. **If this fails:** com0com setup issue, reinstall/reconfigure

## Production Command
Once you find which flag works, use it every time:

```bash
# Example if --rtscts works:
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts

# You can also add to a batch file (Windows):
@echo off
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts
pause
```

## Logs Location
Check `firmware_emulator/logs/` for detailed debug information if issues persist.

## Related Documentation
See `VISA_TROUBLESHOOTING.md` for more detailed explanations
