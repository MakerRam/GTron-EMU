# Quick Reference Card: Camera Images & Launch

## 🖼️ Camera Image Locations

Add your images to these three folders:

| Camera | Full Path |
|--------|-----------|
| **TOP** | `/mnt/d/TDD/Emulator/firmware_emulator/camera_images/top/` |
| **SIDE** | `/mnt/d/TDD/Emulator/firmware_emulator/camera_images/side/` |
| **FRONT** | `/mnt/d/TDD/Emulator/firmware_emulator/camera_images/front/` |

### Using Windows File Explorer:
1. Open: `C:\mnt\d\TDD\Emulator\firmware_emulator\camera_images\`
2. Drag images into `top\`, `side\`, and `front\` folders
3. Done!

---

## 📋 Image Requirements

- **Format:** PNG, BMP, or JPG
- **Naming:** Any alphabetical order (e.g., `top_001.png`, `image_a.png`)
- **Quantity:** At least 1 image per camera (more = longer sequence)
- **Size:** Any resolution (640x480 recommended)

---

## 🚀 Launch Emulator (2 Steps)

### Step 1: Terminal 1 - Start Emulator

```bash
cd /mnt/d/TDD/Emulator
python3 firmware_emulator/src/main.py --port COM3 --verbose
```

**Expected Output:**
```
Emulator running on COM3 at 9600 baud
Waiting for commands... (Ctrl+C to stop)
```

### Step 2: Terminal 2 - Launch LabVIEW

```bash
labview &
```

**In LabVIEW:**
1. Configure serial: **COM4** (baud: 9600)
2. Click Connect
3. LabVIEW sends QUERY
4. Emulator responds YES ✓

---

## 📊 Verify It Works

### In Terminal 1, you should see:
```
[QUERY] RECV: QUERY → SEND: YES
```

### Check logs:
```bash
ls -lh /mnt/d/TDD/Emulator/logs/
cat /mnt/d/TDD/Emulator/logs/commands_*.log
```

---

## ⚙️ One-Time Setup (Windows)

1. Download & install **com0com**
2. Run `DevCon.exe install comport.inf COM3,COM4`
3. Verify in Device Manager (COM3 & COM4 should exist)
4. Done! (only needs to be done once)

---

## 🎯 Common Commands

```bash
# Basic launch with console output
python3 firmware_emulator/src/main.py --port COM3 --verbose

# With hex debugging
python3 firmware_emulator/src/main.py --port COM3 --hex

# Different baud rate
python3 firmware_emulator/src/main.py --port COM3 --baudrate 115200 --verbose

# Stop emulator
Ctrl+C in Terminal 1
```

---

## 🐛 Quick Fixes

| Problem | Solution |
|---------|----------|
| "Port not found" | Install com0com, create COM3/COM4 pair |
| "No images found" | Add PNG/BMP/JPG files to `camera_images/{top,side,front}/` |
| LabVIEW won't connect | Start emulator FIRST, then LabVIEW. Check COM4 baud rate |
| No console output | Add `--verbose` flag |

---

**Ready?** Add images → Start emulator → Launch LabVIEW → Test handshake! 🎉
