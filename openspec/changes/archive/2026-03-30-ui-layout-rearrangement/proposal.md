## Why

The current dashboard panel layout does not match the physical arrangement of the real GTRON hardware. The reference layout (UI Card Sample.png) shows how panels should be spatially organized to mirror the actual machine topology -- control panel at top, cameras in the middle, motors and sensors at the bottom, with tower lamp and system status as tall side panels. Additionally, the page title still reads "Vision System Monitor" and needs to be updated to "Gtron System Emulator", and the "Emulator Control" panel should be renamed to "Front Panel" to match hardware terminology.

## What Changes

- Rearrange the CSS grid layout from a simple 3-column flow to an explicit 4-column placement grid that matches the reference image
- Move "Front Panel" (currently "Emulator Control") to span the top row (columns 1-3)
- Position "Tower Lamp" as a narrow panel at top-right (column 4, spanning rows 1-2)
- Position "Cameras" panel spanning columns 1-3 in the second row
- Position "System Status" as a tall panel at bottom-right (column 4, spanning rows 2-3)
- Arrange "Sag Sensors", "Guide Motors", "Reeler Motors" across columns 1-3 in the bottom row
- Rename page title from "Vision System Monitor" to "Gtron System Emulator"
- Rename header h1 from "Vision System Monitor" to "Gtron System Emulator"
- Rename "Emulator Control" panel heading to "Front Panel"
- Update CSS file header comment to reflect new name

## Capabilities

### New Capabilities

- `dashboard-grid-layout`: Explicit CSS grid placement rules mapping each panel to a specific row/column position matching the physical machine topology

### Modified Capabilities

- `system-visualizer-ui`: Panel ordering and naming changes to match physical hardware layout
- `real-time-visualization`: Dashboard title and panel heading text updates

## Impact

- `visualizer/index.html` -- panel order in HTML, page title, header h1 text, panel heading text
- `visualizer/styles.css` -- `.dashboard-grid` CSS rules, per-panel grid placement, responsive breakpoints
- `visualizer/app.js` -- no changes expected (rendering uses element IDs, not position)
- No backend changes required
- No JavaScript logic changes required
- Responsive breakpoints (960px, 640px) need updating to degrade gracefully from the new 4-column layout
