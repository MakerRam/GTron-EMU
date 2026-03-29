## Why

The Vision System Firmware Emulator (Phase 1) provides comprehensive real-time device state tracking but lacks visualization capabilities. Currently, state is only logged to files. Operators and developers cannot visualize machine behavior, diagnose issues, or demonstrate system functionality without:

- Real-time monitoring of motor positions, reeler speeds, sensor states
- Visual feedback of camera triggers and lamp status
- Tracking of command sequences and state transitions
- Ability to replay recorded sessions for debugging

Building a standalone visualization system decouples the emulator from UI concerns, enabling:
1. **Independent development** by visualization specialists using preferred tech stack
2. **Multi-faceted visualization** - multiple UIs consuming same API
3. **Future flexibility** - swap, upgrade, or replace visualization without touching emulator
4. **Clean architecture** - HTTP-based coupling is minimal and language-agnostic

## What Changes

**Emulator Side (Minimal):**
- Add `StateExporter` class to convert DeviceState → JSON (50 lines)
- Add `APIServer` (Flask) to expose state via HTTP REST (100 lines)
- Start API server in background thread (5 lines)
- No changes to existing logic or interfaces

**New Standalone System:**
- Create independent "Vision System Visualizer" project
- Consumes state from emulator's HTTP API (`/api/state`, `/api/state/summary`)
- Renders real-time UI showing:
  - Guide motor positions (top/bottom racks)
  - Reeler motor speeds
  - Sag sensor status (green=pass, red=triggered)
  - Camera activity indicators
  - Tower lamp state
  - Door lock and E-stop status
  - Command history/logging

## Capabilities

### New Capabilities (Visualization System)

- `real-time-state-monitoring`: Poll emulator state API and update UI every 100ms
- `2d-machine-diagram`: SVG-based schematic showing machine layout with real-time status overlays
- `motor-visualization`: Animated guide bars showing position (0-100%) and reeler speed gauges
- `sensor-status-display`: Color-coded indicators for all 4 sag sensors
- `camera-activity-tracking`: Show which cameras (top/side/front) triggered and image counts
- `lamp-status-indicators`: RGB visualization of tower lamp states
- `device-status-panel`: Door lock, E-stop, power, last command display
- `http-api-consumer`: Robust polling with error handling, retry logic, connection status
- `state-json-visualization`: Interactive JSON tree viewer for advanced debugging
- `responsive-ui`: Works on desktop (1920x1080+), tablet (iPad), and displays

### Emulator Modifications (Minimal)

- `state-export-layer`: StateExporter class for DeviceState → JSON conversion
- `http-rest-api`: Flask-based REST API for state queries
- `background-api-server`: Thread-safe async API server that doesn't block serial loop

## Impact

**Development Workflow:**
- Visualization team can start immediately without emulator changes
- Uses live, running emulator as data source
- Fast iteration: change UI, reload browser, see results instantly

**Testing:**
- Can build UI tests consuming mock API responses
- Can replay recorded state sequences
- No dependency on actual hardware or COM ports

**Deployment:**
- Visualization runs independently (different machine possible)
- Works over network (emulator on Windows, UI on Linux/Mac)
- Can run multiple visualizations simultaneously on same state API

**Future Extensibility:**
- As Phase 2 adds motors, encoders, triggers → state grows automatically
- Visualization just adds new panels/indicators
- No architectural changes needed

## Scope

**Included (MVP):**
- HTTP API in emulator (StateExporter + Flask)
- One primary visualization (2D machine diagram OR dashboard - TBD with team)
- Real-time state polling
- Motor/sensor/lamp/camera status display
- Error handling and connection status

**Deferred (Phase 2+):**
- 3D visualization (Unity/Godot)
- Command timeline/replay viewer
- Historical state logging and playback
- Multiple simultaneous visualizations
- Advanced analytics/diagnostics
- Mobile app version

## Dependencies

**Emulator Side:**
- Flask (HTTP server)
- flask-cors (cross-origin support)
- Python 3.8+

**Visualization Side (TBD, examples):**
- Option A: Python + Plotly Dash (full-stack Python)
- Option B: React + D3/Chart.js (modern JavaScript)
- Option C: Vue.js + Fabric.js (lightweight JavaScript)
- Option D: C# WPF (Windows native desktop)
- Option E: Custom (team choice)

## Success Criteria

- ✅ Emulator exports state via HTTP API without breaking existing functionality
- ✅ Visualization displays all emulator state (guide, reeler, sensors, lamps, cameras)
- ✅ Real-time updates (≤100ms polling latency)
- ✅ Responsive UI that works on common screen sizes
- ✅ Error handling for disconnected/slow emulator
- ✅ Can be developed in parallel by different team
- ✅ Zero coupling between visualization and emulator internals

---

**Effort:** ~1.5 weeks
- Emulator API: 2-3 days
- Visualization MVP: 5-7 days (varies by tech choice)
- Testing/refinement: 2-3 days

**Team:** 1-2 people (visualization specialist preferred)
