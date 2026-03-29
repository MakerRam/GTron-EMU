# Quick Start Guide - Get Visualization Running in 5 Minutes

## Prerequisites

- Python 3.8+
- Git
- A web browser (Chrome, Firefox, Safari)
- Virtual COM port (Windows) or pty pair (Linux/macOS) for serial communication

## Step 1: Install Dependencies (1 minute)

```bash
cd /path/to/GTron-EMU
pip install -r firmware_emulator/requirements.txt
```

Expected output:
```
Successfully installed pyserial flask flask-cors pytest
```

## Step 2: Start the Emulator (1 minute)

```bash
python3 firmware_emulator/src/main.py --port COM3
```

Expected output:
```
Emulator running on COM3 at 115200 baud
API server started on http://localhost:5000
Waiting for commands...
```

> **Windows users**: Replace `COM3` with your virtual COM port  
> **Linux/macOS users**: Use `/dev/ttyS0` or equivalent

## Step 3: Open the Visualizer (1 minute)

Open `visualizer/index.html` in your web browser:

```bash
# macOS
open visualizer/index.html

# Linux
xdg-open visualizer/index.html

# Windows
start visualizer/index.html
```

Or navigate manually:
1. Open your browser
2. Press `Ctrl+O` (or `Cmd+O` on macOS)
3. Select: `visualizer/index.html`

## Step 4: Test in Mock Mode (1 minute)

The visualizer launches in **MOCK mode** by default:

- **MOCK mode**: Displays synthetic cycling data (no emulator needed)
- Observe the dashboard updating every 500ms
- Verify all panels render correctly:
  - Guide Motors (position bars)
  - Reeler Motors (speed gauges)
  - Sag Sensors (color indicators)
  - Tower Lamp (RGB colors)
  - Cameras (flag states)
  - System Status (door, E-stop, power)
  - Command Log (scrolling history)

## Step 5: Switch to Live Mode (1 minute)

Click the **LIVE** button in the top-right corner:

1. Dashboard connects to `http://localhost:5000`
2. Status dot changes to **green** when connected
3. Real-time updates begin (100ms polling)

**Test a command:**

Open a second terminal and send a serial command:

```bash
# Using a Python serial monitor or LabVIEW
# Send: "TPGOP" (open top guide)
```

Watch the visualizer update in real-time!

## Troubleshooting

### Browser shows "Disconnected" (red dot)

**Solution**: Ensure emulator is running and API is accessible:

```bash
# Test the API endpoint
curl http://localhost:5000/health
# Expected: {"status": "ok", "api_version": "1.0"}
```

### API port already in use

**Solution**: Use a different port:

```bash
python3 firmware_emulator/src/main.py --port COM3 --api-port 8080
# Then in visualizer, change API URL to: http://localhost:8080
```

### Can't open visualizer file

**Solution**: Serve it via HTTP instead:

```bash
cd visualizer
python3 -m http.server 8000
# Open: http://localhost:8000
```

### Serial port errors

**Solution**: Verify the port exists:

```bash
# Windows: Check Device Manager for "COM3"
# Linux: ls /dev/tty*
# macOS: ls /dev/tty*
```

## Next Steps

- Explore the **OPCODES_REFERENCE.md** to understand all 75 firmware commands
- Review **README.md** for complete API documentation
- Run the test suite: `pytest firmware_emulator/tests/ -v`
- Integrate with your LabVIEW application

## API Reference (Quick)

| Endpoint | Response | Use Case |
|----------|----------|----------|
| `/health` | Health status | Verify API is running |
| `/api/state` | Full device state (300 bytes) | Complete state snapshot |
| `/api/state/summary` | Essential fields only (150 bytes) | High-frequency polling |

## Dashboard Features

| Feature | Purpose |
|---------|---------|
| **MOCK/LIVE Toggle** | Switch between offline and real-time modes |
| **API URL Input** | Connect to emulator on different machine (IP:port) |
| **6 Monitoring Panels** | Real-time visualization of device state |
| **Command Log** | History of last 20 executed commands |
| **Connection Status** | Green = connected, Red = disconnected |

---

**Done!** You now have a real-time vision system monitor. Send commands via LabVIEW or serial monitor and watch the visualizer update in real-time.
