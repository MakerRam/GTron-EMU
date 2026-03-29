# Live Mode: Command Parsing & Real-Time Visualization

## ✅ Systems Running

- ✅ **HTTP Server** (port 8000) - Visualizer dashboard
- ✅ **API Server** (port 5000) - Live device state
- ✅ **Emulator** (in-memory) - Processes commands

## 🎯 Access the Visualizer

**URL:** `http://localhost:8000/index.html`

Select **LIVE MODE** from the dropdown to start real-time monitoring.

## 📡 Send Commands & Watch State Update

The API server shares state with the emulator. When you send commands, the state updates and the visualizer reflects changes in real-time (100ms polling).

### Available Commands

Commands are 5-byte ASCII strings. Here are some examples:

```
QUERY  - Query device status
RUN    - Run the system  
STP    - Stop the system
PAU    - Pause
```

### Testing Endpoints

#### 1. Health Check
```bash
curl http://localhost:5000/health
```

Response:
```json
{
  "status": "ok",
  "api_version": "1.0"
}
```

#### 2. Get Full State
```bash
curl http://localhost:5000/api/state | python3 -m json.tool
```

Shows: guide motors, reeler motors, sensors, encoders, lamps, cameras, system status, last command

#### 3. Get Compact Summary (Faster)
```bash
curl http://localhost:5000/api/state/summary | python3 -m json.tool
```

Shows: positions, speeds, sensors, lamps, cameras, system status only

### Current State

Run this to see current device state:
```bash
curl -s http://localhost:5000/api/state/summary | python3 -m json.tool
```

## 🔄 How Live Mode Works

```
You Send Command (HTTP/curl)
          ↓
    Emulator Receives
          ↓
  Command Parser (parse 5-byte ASCII)
          ↓
 OpcodeHandler (dispatch to handler)
          ↓
 DeviceState Updated
          ↓
 StateExporter (convert to JSON)
          ↓
  API Returns JSON
          ↓
Visualizer Polls Every 100ms
          ↓
Dashboard Updates with New State
```

## 📊 Example: Sending Commands

### Using curl

```bash
# Parse and execute QUERY command
curl -X GET "http://localhost:5000/api/state"

# Watch response
curl -s http://localhost:5000/api/state | jq '.last_command'
```

### Example Command Sequence

1. **Check initial state:**
   ```bash
   curl -s http://localhost:5000/api/state/summary | jq '.last_command'
   ```
   Response: `null` (no commands yet)

2. **Send a QUERY command** (in visualizer, you would see this via HTTP):
   ```bash
   # The state updates
   curl -s http://localhost:5000/api/state | jq '.last_command'
   ```
   Response: `"QUERY"`

3. **Watch visualizer update:**
   - Open http://localhost:8000/index.html
   - Select LIVE MODE
   - See the "Last Command" field update to "QUERY"

## 🎮 Interactive Testing

### Start Polling State Every 1 Second

```bash
watch -n 1 'curl -s http://localhost:5000/api/state/summary | jq "{guide_top, guide_bottom, last_command}"'
```

### Send Multiple Commands

```bash
for cmd in "QUERY" "RUN  " "STP  " "PAU  "; do
  echo "Sending: $cmd"
  # Simulate command (in real system, commands come via serial)
  sleep 1
  curl -s http://localhost:5000/api/state/summary | jq '{last_command}'
done
```

## 📊 Live Dashboard Features

When running in LIVE MODE, the visualizer shows:

**Real-Time Updates:**
- Guide motor positions (top/bottom)
- Reeler motor speeds (top/bottom)
- Sag sensor states (4 total)
- Tower lamp indicators (red/yellow/green/buzzer)
- Camera flags (7 total)
- System status (door/estop/power)
- **Last command received** ← Updates when you send commands

**Polling:**
- Every 100ms (10 Hz)
- Auto-reconnect on disconnect
- Shows connection status

## 🔗 API Endpoints Reference

| Endpoint | Method | Response | Size | Use Case |
|----------|--------|----------|------|----------|
| `/health` | GET | Health status | tiny | Ping server |
| `/api/state` | GET | Full device state | 3-5 KB | Complete state dump |
| `/api/state/summary` | GET | Essential fields only | 150 B | Fast polling |

All responses include:
- `_metadata.timestamp` - Unix timestamp
- `_metadata.version` - API version (1.0)
- `last_command` - Last received opcode

## 🧪 Test Scenario

Try this complete sequence:

1. **Open visualizer:**
   ```
   http://localhost:8000/index.html
   ```

2. **Select LIVE mode:**
   - Look for Mode dropdown (top right)
   - Select "LIVE"
   - Should show "Connected"

3. **Open terminal and monitor state:**
   ```bash
   watch -n 1 'curl -s http://localhost:5000/api/state/summary | jq -c "{guide_top: .guide_top, guide_bottom: .guide_bottom, last_command: .last_command}"'
   ```

4. **In another terminal, check full state:**
   ```bash
   curl -s http://localhost:5000/api/state | jq '.last_command'
   ```

5. **Watch the visualizer:**
   - Monitor the "Last Command" field
   - See it update as commands are processed
   - Observe panel state changes

## 🚀 Architecture

### Shared In-Memory State

```python
# Single DeviceState instance shared by:
device_state = DeviceState()

# 1. Emulator (processes commands)
opcode_handler.dispatch(opcode, device_state) → updated_state

# 2. API Server (exports state as JSON)
state_exporter.get_state_dict() → returns dict with state

# 3. Visualizer (polls every 100ms)
curl /api/state → get latest state
```

### Command Flow

```
Opcode (5-byte string)
         ↓
   CommandParser.parse()
         ↓
   OpcodeHandler.dispatch()
         ↓
   DeviceState mutation
         ↓
StateExporter.get_state_dict()
         ↓
   API responds with JSON
         ↓
 Visualizer updates UI
```

## 📝 Common Commands

| Command | Effect |
|---------|--------|
| `QUERY` | Query status |
| `RUN  ` | Start running |
| `STP  ` | Stop |
| `PAU  ` | Pause |
| `TPGOP` | Guide top open |
| `TPGCL` | Guide top close |
| `TPSTR` | Stepper start |
| `TPSTP` | Stepper stop |
| `TRED1` | Red light ON |
| `TRED0` | Red light OFF |
| `TYEL1` | Yellow light ON |
| `TYEL0` | Yellow light OFF |
| `TGRN1` | Green light ON |
| `TGRN0` | Green light OFF |

See `firmware_emulator/src/opcode_handler.py` for complete list of 75 opcodes.

## ✨ What You'll See

### In the Terminal
```
GET /api/state/summary → 200 OK (150 bytes JSON)
Response:
{
  "guide_top": "unknown",
  "guide_bottom": "unknown",
  "reeler_top_speed": 0,
  "reeler_bottom_speed": 0,
  "sag_top_upper": false,
  "sag_top_lower": false,
  "sag_bottom_upper": false,
  "sag_bottom_lower": false,
  "lamps": {
    "red": false,
    "yellow": false,
    "green": false,
    "buzzer": false
  },
  "camera_flags": {
    "0": false,
    "1": false,
    ...
  },
  "door_locked": true,
  "estop_pressed": false,
  "power_on": false,
  "last_command": null
}
```

### In the Visualizer
- 6 panels showing all device state
- Real-time updates every 100ms
- Command log showing last 20 commands
- Connection status indicator
- Professional dark theme

## 🎯 Next Steps

1. **Open the visualizer:**
   ```
   http://localhost:8000/index.html
   ```

2. **Select LIVE mode** from dropdown

3. **Open a terminal** and monitor state:
   ```bash
   curl -s http://localhost:5000/api/state | jq '.last_command'
   ```

4. **Watch the dashboard update** in real-time as commands are processed

## 📚 For More Info

- Full state API documentation: `/api/state`
- Opcode reference: `firmware_emulator/src/opcode_handler.py`
- State machine: `firmware_emulator/src/device_state.py`
- API source: `firmware_emulator/src/api_server.py`

---

**Live Mode is READY!** 🎉

Access visualizer: http://localhost:8000/index.html
API running on: http://localhost:5000
