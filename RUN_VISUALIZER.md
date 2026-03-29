# Running the Vision System Monitor Visualizer

This guide shows how to run the complete Phase 2 system: Emulator API + Browser Visualizer.

## Prerequisites

- Python 3.12+
- pip installed
- Flask, Flask-CORS, pytest, pyserial installed (see Environment Setup)

## Quick Start (Option A: MOCK Mode - No Emulator Needed)

The visualizer includes a **MOCK mode** that simulates device state without needing the real emulator. This is perfect for testing the UI.

### Step 1: Start HTTP Server

```bash
cd /mnt/d/TDD/Emulator/visualizer
python3 -m http.server 8000
```

Output:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### Step 2: Open in Browser

**On the same machine:**
```
http://localhost:8000/index.html
```

**On another machine (replace YOUR_IP with server IP):**
```
http://YOUR_IP:8000/index.html
```

### Step 3: Select MOCK Mode in Browser

Once the page loads:
1. Look for the **Mode toggle** in the header (top right)
2. Select **MOCK mode**
3. Watch the dashboard cycle through 10 synthetic state scenarios
4. All 6 panels update in real-time:
   - Guide Motors (Top/Bottom position)
   - Reeler Motors (speeds)
   - Sag Sensors
   - Tower Lamp (red/yellow/green/buzzer)
   - Cameras (7 flag indicators)
   - System Status (door, e-stop, power)

## Full Integration (Option B: LIVE Mode with Emulator API)

For full integration with the firmware emulator:

### Terminal 1: Start API Server

```bash
cd /mnt/d/TDD/Emulator
export PATH=/home/ramkumar/.local/bin:$PATH
export PYTHONPATH=/mnt/d/TDD/Emulator:$PYTHONPATH

python3 << 'EOF'
import sys
sys.path.insert(0, '/mnt/d/TDD/Emulator')

from firmware_emulator.src.device_state import DeviceState
from firmware_emulator.src.state_export import StateExporter
from firmware_emulator.src.api_server import APIServer

device_state = DeviceState()
state_exporter = StateExporter(device_state)
api_server = APIServer(state_exporter, port=5000)

print("API Server running on http://localhost:5000")
print("Endpoints:")
print("  GET /health")
print("  GET /api/state")
print("  GET /api/state/summary")
api_server.start()
EOF
```

Output:
```
API Server running on http://localhost:5000
...
Running on http://127.0.0.1:5000
```

### Terminal 2: Start Visualizer HTTP Server

```bash
cd /mnt/d/TDD/Emulator/visualizer
python3 -m http.server 8000
```

Output:
```
Serving HTTP on 0.0.0.0 port 8000 (http://0.0.0.0:8000/) ...
```

### Terminal 3: Open in Browser

Open:
```
http://localhost:8000/index.html
```

Then:
1. Select **LIVE mode** from the mode toggle
2. Verify it says "Connected" in the status area
3. The dashboard polls the API every 100ms
4. Make API requests to update state:
   ```bash
   curl http://localhost:5000/api/state | python3 -m json.tool
   ```

## API Endpoints

While the visualizer is running, you can test the API:

### Health Check
```bash
curl http://localhost:5000/health | python3 -m json.tool
```

Response:
```json
{
  "status": "ok",
  "api_version": "1.0"
}
```

### Full State
```bash
curl http://localhost:5000/api/state | python3 -m json.tool
```

Returns complete device state with metadata, timestamps, etc.

### Compact Summary (Faster)
```bash
curl http://localhost:5000/api/state/summary | python3 -m json.tool
```

Returns only essential fields optimized for real-time polling.

## Visualizer Features

### 6 Monitoring Panels

1. **Guide Motors**
   - Top: Position (closed/open/moving/unknown)
   - Bottom: Position (closed/open/moving/unknown)

2. **Reeler Motors**
   - Top speed (steps/sec)
   - Bottom speed (steps/sec)

3. **Sag Sensors**
   - Top Upper
   - Top Lower
   - Bottom Upper
   - Bottom Lower

4. **Tower Lamp**
   - Red light
   - Yellow light
   - Green light
   - Buzzer

5. **Cameras**
   - 7 camera flags (0-6)
   - Active sequence

6. **System Status**
   - Door locked
   - E-stop pressed
   - Power on
   - Last command received

### Operating Modes

**MOCK Mode:**
- No external dependencies
- Cycles through 10 synthetic state scenarios
- Perfect for UI testing
- 100ms update interval

**LIVE Mode:**
- Connects to API server on port 5000
- Polls `/api/state/summary` every 100ms
- Shows real device state
- Auto-reconnects on disconnect
- Requires API server running

### Real-Time Command Log

- Shows last 20 commands received
- Updates with each state change
- Timestamp and opcode visible

## Troubleshooting

### HTTP Server Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill the process (replace PID)
kill -9 PID

# Or use a different port
python3 -m http.server 8001
# Then access: http://localhost:8001/index.html
```

### API Server Not Responding
- Check that API is running: `curl http://localhost:5000/health`
- Verify port 5000 is not in use: `lsof -i :5000`
- Check API server logs in terminal

### Visualizer Shows "Disconnected"
- Verify API is running on port 5000
- Check browser console for errors (F12 → Console)
- Try switching to MOCK mode first to verify UI works

### CORS Errors in Browser Console
- API includes CORS headers (`Access-Control-Allow-Origin: *`)
- If still failing, check API server logs

## Performance Characteristics

- **API Response Time**: < 100ms for `/api/state/summary`
- **Full State Size**: ~3-5 KB JSON
- **Summary Size**: ~150 bytes JSON
- **Update Frequency**: 100ms (10 Hz)
- **CPU Usage**: < 5% (idle), < 2% (API polling)
- **Memory**: ~50-100 MB (Python process)

## File Structure

```
/mnt/d/TDD/Emulator/
├── visualizer/
│   ├── index.html        # Dashboard HTML (265 lines, 14 KB)
│   ├── app.js            # JavaScript logic (300+ lines, 13 KB)
│   ├── styles.css        # Dark theme styling (17 KB)
│   └── mock_states.json  # 10 synthetic state cycles (15 KB)
├── firmware_emulator/src/
│   ├── api_server.py     # Flask API server
│   ├── state_export.py   # Device state JSON conversion
│   ├── device_state.py   # Core state machine
│   └── main.py           # Emulator CLI
└── RUN_VISUALIZER.md     # This file
```

## Next Steps

1. **Try MOCK mode first** to verify the UI works
2. **Start the API server** to test LIVE mode
3. **Run the full system** with emulator + API + visualizer
4. **Test API endpoints** with curl commands
5. **Check browser console** (F12) for any errors

For Phase 2 implementation details, see `PHASE2_COMPLETION_SUMMARY.md`.
