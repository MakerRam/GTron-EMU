# ELTIMA Virtual Serial Port Driver Setup Guide

## Step 1: Download and Install ELTIMA

1. Go to: https://www.eltima.com/products/vspdxp/
2. Download the installer
3. Run installer and follow setup wizard
4. Accept license agreement
5. Finish installation

---

## Step 2: Create Virtual COM Port Pair

1. **Open ELTIMA Virtual Serial Port Driver**
   - Right-click Start → Search "Virtual Serial Port"
   - Or find in Programs menu

2. **Create a new pair:**
   - Click "Add Pair" button
   - You'll see options to create two linked ports

3. **Configure Port A (for LabVIEW):**
   - Name: `Arduino`
   - Keep other settings as default
   - Click OK

4. **Configure Port B (for Emulator):**
   - Name: `Arduino_Emulator` (or any name)
   - Keep other settings as default
   - Click OK

5. **Verify ports created:**
   - Open Device Manager (Win + R → `devmgmt.msc`)
   - Expand "Ports (COM & LPT)"
   - Should see your new ports listed

---

## Step 3: Note the COM Port Numbers

After creation, ELTIMA will assign COM numbers. For example:
- **Port A (LabVIEW):** COM5
- **Port B (Emulator):** COM6

**Write these down!** You'll need them in the next step.

---

## Step 4: Update Emulator Launcher

Update the launcher to use the correct COM port:

**Edit:** `D:\TDD\Emulator\emulator_launcher.py`

Find this line (around line 198):
```python
port = "CNCA2"
```

Replace with your Port B COM number (e.g., COM6):
```python
port = "COM6"
```

Save the file.

---

## Step 5: Launch Emulator

1. Run launcher:
   ```cmd
   cd /d D:\TDD\Emulator
   python emulator_launcher.py
   ```

2. Click **"START EMULATOR"** button

3. You should see in logs:
   ```
   [INFO] Using port: COM6
   [SUCCESS] Emulator started successfully!
   [INFO] Listening for commands on COM6 port...
   ```

---

## Step 6: Launch LabVIEW

1. Open your old LabVIEW app
2. Configure serial port to **Arduino** (Port A COM number, e.g., COM5)
3. Set baud rate: **9600**
4. Click **Connect**

---

## Step 7: Verify Handshake

In the launcher window, you should see:
```
[QUERY] RECV: QUERY → SEND: YES
```

If you see this → ✅ **Success! Connected!**

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| ELTIMA won't open | Restart computer after installation |
| Ports not appearing in Device Manager | Close Device Manager and reopen it |
| LabVIEW can't find "Arduino" | Make sure port name is exactly "Arduino" in ELTIMA |
| Emulator says port not found | Check COM number matches what ELTIMA assigned |
| Handshake not appearing | Check baud rate is 9600 in LabVIEW |

---

## Next Steps After Handshake Works

Once handshake succeeds:
1. Add camera images to `firmware_emulator/camera_images/{top,side,front}/`
2. Test camera trigger commands (LCS01, LCS02, LCS03)
3. Verify full communication

---

**Let me know once you've installed ELTIMA and created the port pair!**
