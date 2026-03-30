## Why

The Vision System Monitor dashboard currently displays device state as a read-only visualization. Operators need interactive control buttons (Run, Pause, Stop, Buzzer Off) to command the emulator directly from the browser, a Query Status indicator in the title bar for at-a-glance health monitoring, and 6 dedicated light indicators near the camera panel to represent physical illumination channels. These additions transform the dashboard from a passive monitor into an active control and status panel, matching the physical HMI workflow used on real GTRON vision systems.

## What Changes

- **Control buttons panel**: Add Run, Pause, Stop, and Buzzer Off buttons to the dashboard with status light indicators (green/yellow/red) showing current state (running, paused, stopped, buzzer active/silenced)
- **Query Status indicator**: Add a query status light indicator in the title bar (header), positioned before the existing Connected/Disconnected status, showing whether the emulator is responsive to queries
- **Camera light indicators**: Add 6 light indicators next to or below the existing Cameras panel, representing physical illumination channels (lights 1-6) with on/off state
- **Backend API endpoints**: Add POST endpoints for Run, Pause, Stop, and Buzzer Off commands; add GET endpoint for query status; expose light states in existing state API
- **Device state extensions**: Add emulator run/pause/stop state, buzzer-off override, query health status, and 6 light channel states to DeviceState

## Capabilities

### New Capabilities
- `emulator-control-buttons`: Run, Pause, Stop, and Buzzer Off buttons with backend command flow and status light indicators
- `query-status-indicator`: Query status light in the title bar showing emulator responsiveness
- `camera-light-indicators`: 6 light indicators near the camera panel representing physical illumination channels

### Modified Capabilities
- `system-visualizer-ui`: Adding new interactive control buttons panel, query status indicator in header, and 6 light indicators near cameras
- `rest-api-server`: Adding POST /api/command endpoints for control actions and exposing new state fields (run state, light channels, query health)
- `real-time-visualization`: Dashboard now renders control buttons with status lights, query indicator, and camera light indicators in real-time

## Impact

- **Frontend** (`visualizer/index.html`, `app.js`, `styles.css`): New HTML sections for control buttons, query indicator, and light indicators; new JS render functions and click handlers; new CSS for button styles and light animations
- **Backend** (`firmware_emulator/src/`): Extended `DeviceState` with run_state, buzzer_override, query_status, light_channels fields; new/updated opcode handlers; extended `state_export.py` and `api_server.py`
- **Mock data** (`visualizer/mock_states.json`): Updated to include new state fields for offline testing
- **No breaking changes**: All existing functionality preserved; new features are additive
