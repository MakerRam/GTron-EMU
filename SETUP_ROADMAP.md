# 🚀 Complete Setup & Testing Roadmap

**Your Vision System Firmware Emulator is ready!**

This document shows you exactly what to do, step-by-step, to get everything working.

---

## 📋 Pre-Flight Checklist

- [x] Emulator code: ✅ Written & tested
- [x] Virtual cameras: ✅ Loaded with 12 images
- [x] Serial communication: ✅ Ready
- [x] IMAQDX interface: ✅ Ready
- [ ] com0com: ⏳ You need to install this

---

## 🎯 Your Setup

```
Your Windows Machine
│
├─ WSL2 (Linux terminal - where you are now)
│   └─ Emulator (runs on COM3)
│
└─ Windows
    └─ LabVIEW (will run on COM4)
```

**They communicate through virtual COM ports (COM3 ↔ COM4)**

---

## 📖 Installation Steps

### PART 1: Install com0com (One-Time Setup)

**Time:** 3 minutes

1. Go to: https://sourceforge.net/projects/com0com/files/
2. Download: `com0com-3.0.0.0-i386-and-x64-signed.zip`
3. Extract the ZIP file
4. Run `setup.exe` as Administrator
5. Follow the wizard (accept defaults)
6. **IMPORTANT:** Make sure "Install port pair" is checked (COM3 ↔ COM4)
7. Click Install
8. Restart your computer (if prompted)
9. Verify: Open Device Manager → Ports (COM & LPT) → Should see COM3 and COM4

**Detailed guide:** See `COM0COM_INSTALLATION_GUIDE.md`

---

### PART 2: Start the Emulator (Every Time You Test)

**Time:** 10 seconds

#### Terminal 1 (WSL2):
```bash
cd /mnt/d/TDD/Emulator
python3 firmware_emulator/src/main.py --port COM3 --verbose
```

**You should see:**
```
Emulator running on COM3 at 9600 baud
Waiting for commands... (Ctrl+C to stop)
```

**Keep this terminal open.** It's now listening for LabVIEW commands.

---

### PART 3: Launch LabVIEW & Connect

**Time:** 1 minute

#### Terminal 2 (Windows or WSL2):
```bash
labview &
```

**In LabVIEW Application:**

1. Open your LabVIEW project/application
2. Find serial port configuration (usually in "Initialize Hardware" or "Settings")
3. Set:
   - **Port:** COM4
   - **Baud Rate:** 9600
   - **Data Bits:** 8
   - **Parity:** None
   - **Stop Bits:** 1
4. Click **"Connect"** or **"Initialize Hardware"**

---

### PART 4: Verify Connection

**Watch Terminal 1:**

When LabVIEW connects, you should see:
```
[QUERY] RECV: QUERY → SEND: YES
```

**In LabVIEW:**
- Should show "Connected" or "Device Ready"
- Should detect cameras (top, side, front)

**Success!** 🎉 The emulator is communicating with LabVIEW

---

## 📊 Testing the Cameras

### What LabVIEW Can Do:

1. **Query camera status:**
   - "Are cameras ready?" → YES ✅

2. **Trigger top camera (LCS01):**
   - Terminal shows: `[LCS01] RECV: LCS01 → SEND: LCS1`
   - LabVIEW receives: top/1.png

3. **Trigger again:**
   - Terminal shows: `[LCS01] RECV: LCS01 → SEND: LCS1`
   - LabVIEW receives: top/2.png

4. **Trigger side camera (LCS02):**
   - Terminal shows: `[LCS02] RECV: LCS02 → SEND: LCS1`
   - LabVIEW receives: side/1.png

5. **Trigger front camera (LCS03):**
   - Terminal shows: `[LCS03] RECV: LCS03 → SEND: LCS1`
   - LabVIEW receives: front/1.png

### Frame Cycling:

Each camera cycles through 4 images:
```
Trigger 1 → Image 1
Trigger 2 → Image 2
Trigger 3 → Image 3
Trigger 4 → Image 4
Trigger 5 → Image 1 (wraps)
```

---

## 📂 Your Project Structure

```
/mnt/d/TDD/Emulator/
│
├── firmware_emulator/
│   ├── src/
│   │   ├── main.py              (← Run this)
│   │   ├── serial_bridge.py     (handles COM port)
│   │   ├── command_parser.py    (parses commands)
│   │   ├── virtual_camera.py    (serves images)
│   │   ├── imaqdx_interface.py  (LabVIEW format)
│   │   └── opcode_handlers.py   (processes commands)
│   │
│   ├── camera_images/           (← Your images are here)
│   │   ├── top/      (4 images)
│   │   ├── side/     (4 images)
│   │   └── front/    (4 images)
│   │
│   └── tests/
│       └── test_*.py (40+ tests - all passing)
│
├── logs/                (← Auto-created after first run)
│   ├── emulator_*.log
│   ├── serial_*.log
│   ├── commands_*.log
│   └── debug_*.log
│
└── README.md, etc.
```

---

## 🎬 Complete Testing Scenario

### Before You Start:
- ✅ com0com installed
- ✅ COM3 and COM4 visible in Device Manager
- ✅ Images in camera_images/top/, side/, front/
- ✅ LabVIEW installed and ready

### Step-by-Step:

#### 1. Open Terminal 1 (WSL2)
```bash
cd /mnt/d/TDD/Emulator
python3 firmware_emulator/src/main.py --port COM3 --verbose
```
**Result:** Emulator is running and listening

#### 2. Open Terminal 2
```bash
labview &
```
**Result:** LabVIEW opens

#### 3. In LabVIEW
- Configure to COM4, 9600 baud
- Click Connect
**Result:** Terminal 1 shows: `[QUERY] RECV: QUERY → SEND: YES`

#### 4. In LabVIEW, trigger top camera
- Send command to trigger camera
**Result:** Terminal 1 shows: `[LCS01] RECV: LCS01 → SEND: LCS1`
**Result:** LabVIEW displays top/1.png

#### 5. Trigger again
**Result:** LabVIEW displays top/2.png

#### 6. Trigger side camera
**Result:** LabVIEW displays side/1.png

#### 7. Stop emulator
In Terminal 1, press: **Ctrl+C**
**Result:** Emulator stops cleanly

#### 8. Check logs
```bash
ls -lh /mnt/d/TDD/Emulator/logs/
cat /mnt/d/TDD/Emulator/logs/commands_*.log
```
**Result:** See all commands exchanged

---

## 🔍 What You'll See in Terminal 1

### Normal Operation:
```
Emulator running on COM3 at 9600 baud
Waiting for commands... (Ctrl+C to stop)
[QUERY] RECV: QUERY → SEND: YES
[LCS01] RECV: LCS01 → SEND: LCS1
[LCS01] RECV: LCS01 → SEND: LCS1
[LCS02] RECV: LCS02 → SEND: LCS1
[LCS03] RECV: LCS03 → SEND: LCS1
^C
Shutting down...
=== Emulator Stopped ===
```

### If Something's Wrong:
```
Failed to open serial port COM3: [Errno 2] could not open port 'COM3'
```
**Fix:** Make sure com0com is installed and COM3 exists

---

## 📈 Image Information

Each camera serves 4 images:

```
TOP Camera:
  Images: 1.png, 2.png, 3.png, 4.png
  Size: ~440 KB each
  Resolution: 800 × 1024

SIDE Camera:
  Images: 1.png, 2.png, 3.png, 4.png
  Size: ~179 KB each
  Resolution: 752 × 600

FRONT Camera:
  Images: 1.png, 2.png, 3.png, 4.png
  Size: ~239 KB each
  Resolution: 704 × 600
```

---

## ❓ FAQ

### Q: Do I have to install com0com?
**A:** Yes, if LabVIEW is on Windows and emulator is in WSL2. (One-time setup)

### Q: Where should I run the emulator?
**A:** In WSL2 terminal: `python3 firmware_emulator/src/main.py --port COM3 --verbose`

### Q: Where should I run LabVIEW?
**A:** On Windows: `labview &` (or click LabVIEW icon)

### Q: What if I don't have images?
**A:** Images are already in the folders! Check:
```bash
ls /mnt/d/TDD/Emulator/firmware_emulator/camera_images/top/
```

### Q: What if COM3/COM4 don't appear?
**A:** Restart your computer after installing com0com

### Q: Can I use different COM ports?
**A:** Yes, but change the number in: `python3 ... --port COM5`

### Q: Do I have to see console output?
**A:** Add `--verbose` flag: `python3 ... --port COM3 --verbose`

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| "Port not found" | Install com0com, create COM3/COM4 pair, restart |
| LabVIEW won't connect | Start emulator FIRST, then LabVIEW |
| No console output | Use `--verbose` flag |
| Images won't display | Check images exist: `ls firmware_emulator/camera_images/top/` |
| com0com install fails | Run setup.exe as Administrator, restart Windows |

---

## 📚 Documentation Files

Quick reference:
- `QUICK_START.md` - 2-minute overview
- `SETUP_AND_LAUNCH_GUIDE.md` - Detailed setup & launch
- `COM0COM_REQUIREMENT.md` - Why you need com0com
- `COM0COM_INSTALLATION_GUIDE.md` - Step-by-step install
- `VIRTUAL_CAMERA_STATUS.md` - Camera module verification
- `FIRST_RELEASE_COMPLETE.md` - Full release summary

---

## ✅ Final Checklist Before Testing

- [ ] com0com installed
- [ ] COM3 & COM4 visible in Device Manager
- [ ] Images in camera_images/ folders
- [ ] Emulator code ready: `firmware_emulator/src/main.py`
- [ ] LabVIEW configured for COM4, 9600 baud
- [ ] Two terminals ready to use

---

## 🎉 You're Ready!

1. **Install com0com** (3 minutes, one-time)
2. **Terminal 1:** Start emulator
3. **Terminal 2:** Launch LabVIEW
4. **In LabVIEW:** Configure COM4 and connect
5. **Watch Terminal 1:** See QUERY → YES handshake
6. **Test cameras:** Trigger and see images
7. **Check logs:** Review transaction history

---

## 📞 Next Steps

1. Install com0com (see `COM0COM_INSTALLATION_GUIDE.md`)
2. Verify COM3/COM4 in Device Manager
3. Start emulator in Terminal 1
4. Launch LabVIEW in Terminal 2
5. Configure and test

**Questions?** All documentation is in `/mnt/d/TDD/Emulator/`

---

**Good luck! You've got everything you need!** 🚀
