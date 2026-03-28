# How to Add Camera Images & Launch the Emulator

## 📁 Where to Add Camera Images

Your emulator has **three camera folders** ready for images:

```
/mnt/d/TDD/Emulator/firmware_emulator/camera_images/
├── top/           ← Add TOP camera images here
├── side/          ← Add SIDE camera images here
└── front/         ← Add FRONT camera images here
```

### Full Paths for Reference

- **Top camera:** `/mnt/d/TDD/Emulator/firmware_emulator/camera_images/top/`
- **Side camera:** `/mnt/d/TDD/Emulator/firmware_emulator/camera_images/side/`
- **Front camera:** `/mnt/d/TDD/Emulator/firmware_emulator/camera_images/front/`

---

## 🖼️ Image Requirements

### Supported Formats
- PNG (.png)
- BMP (.bmp)
- JPEG (.jpg, .jpeg)

### File Naming Convention

Name your images **sequentially** so they load in order:

```
top_001.png
top_002.png
top_003.png
...
top_010.png
```

**Or use any alphabetical naming:**
```
img_001.png
image_a.png
camera_frame_001.png
```

The emulator will load them **alphabetically** and cycle through them.

### Image Size Recommendations

- **Width:** 640-800 pixels (typical)
- **Height:** 480-600 pixels (typical)
- **Color:** RGB or Grayscale (both work)
- **File size:** Doesn't matter (from bytes to MB)

---

## 📝 Step-by-Step: Add Camera Images

### Option 1: Using Windows File Explorer

**For Top Camera:**
1. Open File Explorer
2. Navigate to: `C:\mnt\d\TDD\Emulator\firmware_emulator\camera_images\top\`
3. Drag & drop your PNG/BMP/JPG files into this folder
4. Files will be loaded in alphabetical order

**For Side Camera:**
1. Navigate to: `C:\mnt\d\TDD\Emulator\firmware_emulator\camera_images\side\`
2. Add your images

**For Front Camera:**
1. Navigate to: `C:\mnt\d\TDD\Emulator\firmware_emulator\camera_images\front\`
2. Add your images

### Option 2: Using Command Line (Windows PowerShell)

```powershell
# Copy top camera images
Copy-Item "C:\path\to\your\images\top_*.png" `
  -Destination "C:\mnt\d\TDD\Emulator\firmware_emulator\camera_images\top\"

# Copy side camera images
Copy-Item "C:\path\to\your\images\side_*.png" `
  -Destination "C:\mnt\d\TDD\Emulator\firmware_emulator\camera_images\side\"

# Copy front camera images
Copy-Item "C:\path\to\your\images\front_*.png" `
  -Destination "C:\mnt\d\TDD\Emulator\firmware_emulator\camera_images\front\"
```

### Option 3: Using Linux/WSL Command Line

```bash
# Copy top camera images
cp /path/to/your/images/top_*.png \
  /mnt/d/TDD/Emulator/firmware_emulator/camera_images/top/

# Copy side camera images
cp /path/to/your/images/side_*.png \
  /mnt/d/TDD/Emulator/firmware_emulator/camera_images/side/

# Copy front camera images
cp /path/to/your/images/front_*.png \
  /mnt/d/TDD/Emulator/firmware_emulator/camera_images/front/
```

### Verify Images Are In Place

**Check top camera folder:**
```bash
ls -la /mnt/d/TDD/Emulator/firmware_emulator/camera_images/top/
```

Expected output:
```
top_001.png
top_002.png
top_003.png
...
```

---

## 🚀 How to Launch the Emulator

### Prerequisites (One-Time Setup)

**On Windows, you need virtual COM ports (com0com):**

1. Download com0com from: https://sourceforge.net/projects/com0com/
2. Install it (default location is fine)
3. Run `DevCon.exe` to create port pair:
   - Navigate to com0com installation folder
   - Open Command Prompt
   - Run: `DevCon.exe install comport.inf COM3,COM4`
   - This creates a paired virtual COM port: COM3 ↔ COM4
4. Verify in Windows Device Manager (should see COM3 and COM4)

*Note: This is one-time setup. You only do this once.*

---

## 💻 Launch Steps (Every Time You Run)

### Terminal 1: Start the Emulator

**Using PowerShell (Windows):**
```powershell
cd C:\mnt\d\TDD\Emulator
python3 firmware_emulator/src/main.py --port COM3 --verbose
```

**Using CMD (Windows):**
```cmd
cd C:\mnt\d\TDD\Emulator
python3 firmware_emulator/src/main.py --port COM3 --verbose
```

**Using Bash/Linux/WSL:**
```bash
cd /mnt/d/TDD/Emulator
python3 firmware_emulator/src/main.py --port COM3 --verbose
```

### What to Expect

You should see output like:
```
Emulator running on COM3 at 9600 baud
Waiting for commands... (Ctrl+C to stop)
[READY]
```

**Keep this terminal open.** It stays running until you press Ctrl+C.

---

## 🏃 Terminal 2: Launch LabVIEW

**Open a NEW command prompt/terminal window** and launch LabVIEW:

**Using PowerShell (Windows):**
```powershell
labview &
```

**Using CMD (Windows):**
```cmd
labview.exe
```

**Using Linux/WSL:**
```bash
labview &
```

### In LabVIEW

1. Open your LabVIEW application
2. **Configure Serial Port:**
   - Find serial port settings
   - Set to **COM4** (this is paired with emulator's COM3)
   - Set baud rate to **9600**
   - Set data bits to **8**
   - Set parity to **None**
3. **Click "Connect" or "Initialize Hardware"**
4. LabVIEW will send QUERY command
5. Emulator responds with YES
6. Check **Terminal 1** for output like:
   ```
   [QUERY] RECV: QUERY → SEND: YES
   ```

---

## 📊 Real-World Example

### Your Terminal 1 (Emulator)

```
C:\mnt\d\TDD\Emulator> python3 firmware_emulator/src/main.py --port COM3 --verbose
Emulator running on COM3 at 9600 baud
Waiting for commands... (Ctrl+C to stop)
[QUERY] RECV: QUERY → SEND: YES
[LCS01] RECV: LCS01 → SEND: LCS1
[LCS02] RECV: LCS02 → SEND: LCS1
[LCS01] RECV: LCS01 → SEND: LCS1
^C
Shutting down...
```

### Your Terminal 2 (LabVIEW)

LabVIEW window opens, you configure COM4, click Connect, and:
- LabVIEW sends QUERY
- Emulator responds YES
- LabVIEW is connected
- You can now query cameras

### Check Logs

After running, check the logs folder:

```bash
ls -lh /mnt/d/TDD/Emulator/logs/
```

You should see 4 log files:
```
emulator_20260328_120530.log      # Main events
serial_20260328_120530.log        # Serial I/O
commands_20260328_120530.log      # All commands
debug_20260328_120530.log         # Debug details
```

**View the commands log:**
```bash
cat /mnt/d/TDD/Emulator/logs/commands_*.log
```

---

## 🎯 Command-Line Options (Advanced)

### Basic Launch (Recommended for Testing)
```bash
python3 firmware_emulator/src/main.py --port COM3 --verbose
```

### With Hex Debugging
```bash
python3 firmware_emulator/src/main.py --port COM3 --hex
```

### With Specific Baud Rate
```bash
python3 firmware_emulator/src/main.py --port COM3 --baudrate 9600 --verbose
```

### All Options Combined
```bash
python3 firmware_emulator/src/main.py \
  --port COM3 \
  --baudrate 9600 \
  --verbose \
  --hex \
  --debug tpGOP LCS01
```

### Option Descriptions

| Option | Value | Example | Purpose |
|--------|-------|---------|---------|
| `--port` | COM port | `COM3` | **Required:** Serial port to listen on |
| `--baudrate` | Number | `9600` | Baud rate (default: 9600) |
| `--verbose` | Flag | (no value) | Print human-readable commands to console |
| `--hex` | Flag | (no value) | Print hex bytes instead of ASCII |
| `--debug` | Opcode(s) | `tpGOP LCS01` | Log warnings for specific opcodes (Phase 2) |
| `--interactive` | Flag | (no value) | Interactive console mode (Phase 2) |

---

## ✅ Troubleshooting

### Problem: "Port not found" Error

**Error Message:**
```
Failed to open serial port COM3: [Errno 2] could not open port 'COM3'
```

**Solution:**
1. Verify com0com is installed
2. Verify COM3/COM4 pair was created (use `DevCon.exe`)
3. Check Windows Device Manager for COM3
4. Restart emulator after creating ports

### Problem: "No images found" Warning

**Error Message:**
```
[WARNING] No images found in C:\...\camera_images\top\
```

**Solution:**
1. Verify you added images to the correct folder
2. Check file format (PNG, BMP, JPG only)
3. Verify file extensions are lowercase (.png not .PNG)
4. Check file count with: `ls -la /mnt/d/TDD/Emulator/firmware_emulator/camera_images/top/`

### Problem: LabVIEW Connection Refused

**Error in LabVIEW:**
```
Connection refused: COM4
```

**Solution:**
1. Make sure emulator is running FIRST (Terminal 1)
2. Verify you see "[READY]" message in Terminal 1
3. Verify COM4 is paired with COM3
4. Check if another application is using COM4
5. Restart both emulator and LabVIEW

### Problem: No Output in Console

**No messages appearing:**
```
python3 firmware_emulator/src/main.py --port COM3
# Nothing appears
```

**Solution:**
1. Use `--verbose` flag to see output:
   ```bash
   python3 firmware_emulator/src/main.py --port COM3 --verbose
   ```
2. Check logs folder: `/mnt/d/TDD/Emulator/logs/`
3. Verify serial port is working with: `--hex` flag

---

## 📁 Directory Structure (For Reference)

```
C:\mnt\d\TDD\Emulator\
├── firmware_emulator\
│   ├── src\
│   │   ├── main.py                 (← launches this)
│   │   ├── serial_bridge.py
│   │   ├── command_parser.py
│   │   ├── opcode_handlers.py
│   │   ├── virtual_camera.py       (reads from camera_images)
│   │   └── imaqdx_interface.py
│   │
│   ├── camera_images\              (← ADD IMAGES HERE)
│   │   ├── top\                    (← TOP camera images)
│   │   ├── side\                   (← SIDE camera images)
│   │   └── front\                  (← FRONT camera images)
│   │
│   └── tests\
│       ├── test_*.py
│       └── ...
│
├── logs\                           (← AUTO-CREATED)
│   ├── emulator_*.log
│   ├── serial_*.log
│   ├── commands_*.log
│   └── debug_*.log
│
└── README.md
```

---

## 🎬 Quick Summary

### Add Images:
```
1. Put images in: C:\mnt\d\TDD\Emulator\firmware_emulator\camera_images\{top,side,front}\
2. Use PNG/BMP/JPG format
3. Name sequentially (top_001.png, top_002.png, etc.)
```

### Launch Emulator:
```
Terminal 1: python3 firmware_emulator/src/main.py --port COM3 --verbose
Terminal 2: labview &
```

### Verify:
```
See [QUERY] → YES in Terminal 1
LabVIEW shows connected
Logs created in C:\mnt\d\TDD\Emulator\logs\
```

---

**You're all set!** Add your images and launch the emulator. It will wait for LabVIEW to connect.
