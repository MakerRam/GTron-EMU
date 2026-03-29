# VISA Error 0x03000105 Troubleshooting Guide

## Error Description
**0x03000105** = VISA Serial Write Timeout
- Connection established but write operation fails
- Typically caused by flow control mismatch or port configuration issues

## Root Causes & Solutions

### 1. Flow Control Mismatch (Most Likely)
LabVIEW VISA might be expecting hardware handshake signals (RTS/CTS or DSR/DTR) that the emulator isn't providing.

**Solution A: Test with RTS/CTS**
```bash
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts
```

**Solution B: Test with DSR/DTR**
```bash
python -m firmware_emulator.src.main --port COM2 --verbose --dsrdtr
```

**Solution C: Test with XON/XOFF (software flow control)**
```bash
python -m firmware_emulator.src.main --port COM2 --verbose --xonxoff
```

### 2. com0com Port Configuration Issue
The virtual COM port pair might not be properly configured for handshaking.

**Check com0com settings:**
1. Open com0com configuration utility
2. Check the COM port pair (COM1 ↔ COM2)
3. Ensure "Enable All States" or equivalent is checked
4. Try different handshaking modes:
   - None
   - RTS/CTS
   - DTR/DSR
   - Both

**Note:** The emulator and LabVIEW must use MATCHING flow control modes.

### 3. LabVIEW VISA Configuration
Check your LabVIEW VISA resource configuration:

**Steps:**
1. Open LabVIEW
2. Go to **Tools** > **Instrument I/O** > **VISA Resource Explorer**
3. Find your serial resource (e.g., **ASRL1::INSTR**)
4. Right-click > **Properties**
5. Check the **Handshaking** tab:
   - Note the current setting (None, RTS/CTS, DTR/DSR, XON/XOFF)
6. Check the **Advanced** tab:
   - Verify timeout settings
   - Check flow control options

### 4. Timeout Issues
If port opens but write times out, the emulator might be too slow to respond.

**Try increasing timeout:**
```bash
# Emulator logs will show if it's receiving commands
python -m firmware_emulator.src.main --port COM2 --verbose
```

**In LabVIEW:**
- Increase VISA write timeout to 5000+ ms
- Increase read timeout as well

### 5. Test Sequence

1. **Without flow control (baseline):**
   ```bash
   python -m firmware_emulator.src.main --port COM2 --verbose
   ```
   Check LabVIEW write - note if it fails

2. **With RTS/CTS:**
   ```bash
   python -m firmware_emulator.src.main --port COM2 --verbose --rtscts
   ```
   Check LabVIEW write - note if it works

3. **With DSR/DTR:**
   ```bash
   python -m firmware_emulator.src.main --port COM2 --verbose --dsrdtr
   ```
   Check LabVIEW write - note if it works

4. **Note which mode works** and use that for production

### 6. Diagnostic Output
The emulator now logs its configuration. Look for lines like:
```
Serial port COM2 opened at 115200 baud (flow control: RTS/CTS)
```

### 7. Alternative: Check Emulator is Receiving
Before/After each test, verify the emulator is actually receiving commands:

**Terminal output should show:**
```
[QUERY] RECV: QUERY -> SEND: YES
```

If this doesn't appear, the write is failing at the OS/hardware level.

## Quick Reference: Command Examples

```bash
# No flow control (baseline)
python -m firmware_emulator.src.main --port COM2 --verbose

# RTS/CTS hardware handshake
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts

# DTR/DSR hardware handshake  
python -m firmware_emulator.src.main --port COM2 --verbose --dsrdtr

# XON/XOFF software flow control
python -m firmware_emulator.src.main --port COM2 --verbose --xonxoff

# Combination: RTS/CTS + DSR/DTR (both hardware handshakes)
python -m firmware_emulator.src.main --port COM2 --verbose --rtscts --dsrdtr
```

## Next Steps If Still Failing

1. **Verify com0com is working:** Use Putty or another terminal to COM1/COM2
2. **Check Windows Device Manager:** Ensure virtual COM ports show no errors
3. **Try different com0com settings:** Some configurations work better than others
4. **Enable emulator hex logging:** `--hex` flag to see exact bytes
5. **Contact NI support:** If VISA itself is misconfigured

## Related Files
- `firmware_emulator/src/serial_bridge.py` - Serial configuration
- `firmware_emulator/src/main.py` - Flow control command-line options
