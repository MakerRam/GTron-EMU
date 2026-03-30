## Why

The current dashboard has several visual bugs and missing features identified from live testing:
1. Cameras panel shows 7 cameras (0-6) but the real hardware only has 6 (1-6) -- camera 0 does not exist
2. Camera indicators are displayed in a 4-column grid (card-style) but should be in a single horizontal row matching the light indicators layout
3. Tower Lamp panel is hidden/overlapped by System Status due to CSS grid row overlap (both share row 2 in column 4)
4. Front Panel buttons are in a 2x2 grid but should be in a single horizontal row (in series)
5. Front Panel is missing two buttons: "Power On" and "Emergency Exit" (order: PWR ON, RUN, PAUSE, STOP, BZR OFF, E-EXIT)

## What Changes

- Remove camera 0 from HTML and JS -- cameras are now 1-6 only
- Change camera indicators from 4-column grid to 6-column single-row layout (same style as light channel indicators)
- Fix CSS grid so Tower Lamp and System Status do not overlap -- Tower Lamp gets row 1 only, System Status gets rows 2-3
- Change Front Panel control buttons from 2-column grid to 6-column single-row layout
- Add "Power On" button (opcode PWRON) as first button in Front Panel
- Add "Emergency Exit" button (opcode EMEXI) as last button in Front Panel
- Update app.js renderCameras() to iterate 1-6 instead of 0-6
- Update app.js onControlClick/sendControlCommand to handle new opcodes
- Update mock_states.json camera flags to use keys "1"-"6" instead of "0"-"6"

## Capabilities

### New Capabilities

### Modified Capabilities

- `system-visualizer-ui`: Camera count correction (6 not 7), layout changes to cameras and front panel, two new control buttons
- `real-time-visualization`: Camera rendering loop change (1-6), new button opcode handling

## Impact

- `visualizer/index.html` -- camera flags HTML (remove cam-0, renumber), control buttons HTML (add 2, change grid)
- `visualizer/styles.css` -- grid overlap fix, camera-grid to 6-col row, control-buttons-grid to 6-col row, new button styles
- `visualizer/app.js` -- renderCameras() loop 1-6, onControlClick() new opcodes, updateControlButtonsDisabled() new button IDs
- `visualizer/mock_states.json` -- camera flags keys changed from "0"-"6" to "1"-"6"
- No backend changes in this commit (PWRON/EMEXI opcodes are UI-only for now)
