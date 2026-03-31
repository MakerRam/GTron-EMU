# C4 Level 3: Component Diagram - API & Visualizer

## HTTP API Layer and Browser Dashboard Architecture

> **Purpose**: Shows how device state flows from the emulator core through the REST API to the browser-based visualization dashboard.

---

## Component Diagram

```mermaid
C4Component
    title Component Diagram - API Server & Visualizer Dashboard

    Container_Boundary(api_layer, "Flask API Server (Daemon Thread, Port 5000)") {

        Component(exporter, "StateExporter", "state_export.py", "Converts DeviceState to JSON dict. Serializes enums to strings, adds metadata timestamp and version")

        Component(flask_app, "Flask Application", "api_server.py", "Flask WSGI app with 3 registered routes. CORS middleware enabled. Runs in daemon thread")

        Component(health, "GET /health", "Route handler", "Returns {status: ok, api_version: 1.0}. Latency <5ms")

        Component(state_full, "GET /api/state", "Route handler", "Returns full device state with metadata. ~300-400 bytes. Latency <100ms")

        Component(state_summary, "GET /api/state/summary", "Route handler", "Returns compact state for high-frequency polling. ~150 bytes. Latency <20ms")
    }

    Container_Boundary(viz_layer, "Visualizer Dashboard (Browser, Port 8000)") {

        Component(html, "index.html", "265 lines", "Dashboard layout with 6 panel containers, mode toggle, API URL input, command log area")

        Component(appjs, "app.js", "300+ lines", "Polling engine, state parsing, panel update logic, MOCK/LIVE mode switching, auto-reconnect")

        Component(css, "styles.css", "17KB", "Dark theme, responsive grid, panel styling, status indicators, animations")

        Component(mock, "mock_states.json", "15KB", "Synthetic device states for offline MOCK mode testing without running emulator")

        Component(panels, "6 Monitoring Panels", "DOM elements", "Guide Motors | Reeler Motors | Sag Sensors | Tower Lamp | Cameras | System Status")
    }

    Component_Ext(device_state, "DeviceState", "Shared reference from emulator main thread")

    Rel(device_state, exporter, "Read-only reference", "Thread-safe via GIL")
    Rel(exporter, flask_app, "Provides JSON data")
    Rel(flask_app, health, "Routes /health")
    Rel(flask_app, state_full, "Routes /api/state")
    Rel(flask_app, state_summary, "Routes /api/state/summary")

    Rel(appjs, flask_app, "HTTP GET every 100ms", "JSON over HTTP, CORS")
    Rel(appjs, mock, "Reads in MOCK mode", "Local file")
    Rel(appjs, panels, "Updates DOM elements", "JavaScript")
    Rel(html, panels, "Contains panel containers")
    Rel(css, html, "Styles all elements")
```

---

## API Server Internals

### StateExporter - State to JSON Bridge

```
DeviceState (Python)              JSON Output
┌──────────────────┐    export    ┌────────────────────────┐
│ guide_top:       │───────────>│ "guide_top": "open"     │
│  GuidePosition   │             │ "guide_bottom":"closed" │
│  .OPEN (enum)    │             │ "reeler_top_speed": 500 │
│                  │             │ "sag_top_upper": false  │
│ reeler_top:      │             │ "lamps": {"red": false} │
│  ReelerState     │             │ "camera_flags": {...}   │
│  .speed = 500    │             │ "door_locked": true     │
│                  │             │ "last_command":"QUERY"  │
│ lamps:           │             │ "_metadata": {          │
│  LampState       │             │   "timestamp": 17...,  │
│  .red = False    │             │   "version": "1.0"     │
└──────────────────┘             │ }                       │
                                 └────────────────────────┘
```

### REST Endpoints

| Endpoint | Method | Response Size | Latency | Use Case |
|----------|--------|--------------|---------|----------|
| `/health` | GET | ~40 bytes | <5ms | Connection check |
| `/api/state` | GET | ~300-400 bytes | <100ms | Full state inspection |
| `/api/state/summary` | GET | ~150 bytes | <20ms | Dashboard polling (10Hz) |

---

## Visualizer Dashboard Panels

```
┌─────────────────────────────────────────────────────────────┐
│  VISION SYSTEM EMULATOR DASHBOARD          [MOCK] [LIVE]   │
│  API: http://localhost:5000  [Connected]                    │
├──────────────────────┬──────────────────────────────────────┤
│  GUIDE MOTORS        │  REELER MOTORS                      │
│  Top:  ████████ OPEN │  Top:  ▓▓▓▓░░░░ 500 RPM            │
│  Bot:  ░░░░░░ CLOSED │  Bot:  ▓░░░░░░░  50 RPM            │
├──────────────────────┼──────────────────────────────────────┤
│  SAG SENSORS         │  TOWER LAMP                         │
│  Top Upper:  🟢 OK   │  ┌────┐                             │
│  Top Lower:  🔴 ALERT│  │ 🔴 │ Red: OFF                    │
│  Bot Upper:  🟢 OK   │  │ 🟡 │ Yellow: OFF                 │
│  Bot Lower:  🟢 OK   │  │ 🟢 │ Green: ON                   │
│                      │  └────┘ Buzzer: OFF                  │
├──────────────────────┼──────────────────────────────────────┤
│  CAMERAS             │  SYSTEM STATUS                      │
│  Top:   ● Active     │  Door:    LOCKED                    │
│  Side:  ○ Idle       │  E-Stop:  OFF                       │
│  Front: ○ Idle       │  Power:   ON                        │
│  BotL:  ○ Idle       │  Last:    QUERY                     │
│  BotC:  ○ Idle       │  Time:    07:53:25                  │
│  BotR:  ○ Idle       │                                     │
├──────────────────────┴──────────────────────────────────────┤
│  COMMAND LOG                                                │
│  [07:53:25] QUERY → YES                                    │
│  [07:53:26] tpGOP → tpGOR (2000ms delay)                   │
│  [07:53:28] LCS01 → CAMERA TRIGGER                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Polling Architecture (app.js)

```mermaid
flowchart TD
    A[Page Load] --> B{Mode?}
    B -->|MOCK| C[Load mock_states.json]
    B -->|LIVE| D[Start Polling Loop]

    C --> E[Cycle through synthetic states]
    E --> F[Update 6 Panels]

    D --> G[GET /api/state/summary]
    G --> H{Response OK?}
    H -->|200 OK| I[Parse JSON]
    H -->|Error| J[Show Disconnected]
    J --> K[Retry with backoff]
    K --> G

    I --> F
    F --> L[Wait 100ms]
    L --> G
```

---

## MOCK vs LIVE Mode

| Feature | MOCK Mode | LIVE Mode |
|---------|-----------|-----------|
| Data Source | `mock_states.json` (local) | `/api/state/summary` (HTTP) |
| Requires Emulator | No | Yes |
| Update Rate | Synthetic cycling | 100ms polling |
| Use Case | UI development, demos | Real-time monitoring |
| Connection Status | Always "Connected" | Auto-detect, reconnect |
| State Changes | Pre-defined sequence | Driven by LabVIEW commands |

---

*C4 Level 3 - API & Visualizer | Vision System Firmware Emulator | Zentron Projects*
