# Quick Start: Vision System Monitor

## 🚀 Run Visualizer (MOCK Mode - No Dependencies)

The easiest way to see the visualizer in action:

```bash
cd /mnt/d/TDD/Emulator
./run_visualizer_server.sh
```

Then open your browser:
```
http://localhost:8000/index.html
```

**In the visualizer:**
1. Mode dropdown (top right) → Select **MOCK**
2. Watch dashboard cycle through 10 state scenarios
3. All panels update in real-time

✅ **No emulator needed** - MOCK mode is fully self-contained

---

## 🎯 Full Integration (MOCK + API + Visualizer)

If you want to test with the API server running:

### Terminal 1: Start API Server
```bash
cd /mnt/d/TDD/Emulator
./run_api_server.sh
```

Output:
```
📊 Vision System Monitor API
Server: http://localhost:5000
Endpoints:
  /health              Health check
  /api/state           Full device state
  /api/state/summary   Compact state
```

### Terminal 2: Start Visualizer Server
```bash
cd /mnt/d/TDD/Emulator
./run_visualizer_server.sh
```

### Terminal 3: Open Browser
```
http://localhost:8000/index.html
```

Then select **LIVE mode** to connect to the API.

---

## 📡 Test API Endpoints

While servers are running, test the API:

```bash
# Health check
curl http://localhost:5000/health | python3 -m json.tool

# Full state
curl http://localhost:5000/api/state | python3 -m json.tool

# Compact summary (faster)
curl http://localhost:5000/api/state/summary | python3 -m json.tool
```

---

## 📊 What You'll See

### Visualizer Dashboard

**6 Monitoring Panels:**
1. **Guide Motors** - Position of top/bottom racks
2. **Reeler Motors** - Speed of top/bottom reelers
3. **Sag Sensors** - Trigger states for all 4 sensors
4. **Tower Lamp** - Red/Yellow/Green lights + Buzzer
5. **Cameras** - 7 camera flag indicators
6. **System Status** - Door lock, E-stop, Power, Last command

**Operating Modes:**
- **MOCK**: Offline simulation with synthetic states (10-state cycle)
- **LIVE**: Real-time data from API (100ms polling)

**Real-Time Updates:**
- Command log (last 20 commands)
- Status indicators
- Auto-reconnect on disconnect

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill it and try again
kill -9 <PID>
```

### API Server Not Responding
```bash
# Check if it's running
curl http://localhost:5000/health

# Check what's using port 5000
lsof -i :5000
```

### Visualizer Shows "Disconnected"
1. Verify API server is running: `curl http://localhost:5000/health`
2. Switch to MOCK mode to verify visualizer UI works
3. Check browser console (F12 → Console) for JavaScript errors

---

## 📁 Files

```
/mnt/d/TDD/Emulator/
├── run_visualizer_server.sh      # Start HTTP server
├── run_api_server.sh             # Start API server
├── RUN_VISUALIZER.md             # Detailed guide
├── visualizer/
│   ├── index.html                # Dashboard HTML
│   ├── app.js                    # JavaScript (MOCK & LIVE modes)
│   ├── styles.css                # Dark theme styling
│   └── mock_states.json          # 10 synthetic state cycles
└── firmware_emulator/src/
    ├── api_server.py             # Flask API
    ├── state_export.py           # JSON conversion
    └── device_state.py           # State machine
```

---

## 📚 For More Information

- **Implementation Details**: See `PHASE2_COMPLETION_SUMMARY.md`
- **API Reference**: See `README.md` (API section)
- **Setup Instructions**: See `QUICKSTART.md`
- **Security Notes**: See `docs/API_SECURITY.md`

---

## ✨ Key Features

✅ **No External Dependencies** (MOCK mode works offline)
✅ **Real-Time Updates** (100ms polling)
✅ **Dark Theme UI** (responsive, works on desktop/tablet)
✅ **Easy Debugging** (curl commands for API testing)
✅ **Auto-Reconnect** (handles API disconnections gracefully)
✅ **Comprehensive Monitoring** (6 panels covering all device state)

---

**Next Steps:**
1. Run `./run_visualizer_server.sh`
2. Open `http://localhost:8000/index.html`
3. Select MOCK mode
4. Watch the dashboard in action!
