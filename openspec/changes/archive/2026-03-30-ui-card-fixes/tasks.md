## 1. Fix CSS Grid Overlap

- [x] 1.1 Change Tower Lamp grid placement from `grid-row: 1 / 3` to `grid-row: 1` in styles.css
- [x] 1.2 Verify System Status stays at `grid-row: 2 / 4` (no change needed)

## 2. Fix Camera Indicators

- [x] 2.1 Remove cam-0 element from index.html, keep cam-1 through cam-6
- [x] 2.2 Change `.camera-grid` CSS from `repeat(4, 1fr)` to `repeat(6, 1fr)` for single-row layout
- [x] 2.3 Update renderCameras() in app.js to iterate 1-6 instead of 0-6
- [x] 2.4 Update all 10 mock states in mock_states.json: camera flags keys from "0"-"6" to "1"-"6"

## 3. Fix Front Panel Buttons

- [x] 3.1 Add "Power On" button (id=btn-power, opcode=PWRON) as first button in index.html
- [x] 3.2 Add "Emergency Exit" button (id=btn-estop, opcode=EMEXI) as last button in index.html
- [x] 3.3 Change `.control-buttons-grid` CSS from `1fr 1fr` to `repeat(6, 1fr)` for single-row layout
- [x] 3.4 Add CSS styles for new button colors (power=cyan, emergency=red)
- [x] 3.5 Update onControlClick() in app.js to map PWRON and EMEXI opcodes
- [x] 3.6 Update updateControlButtonsDisabled() in app.js to include new button IDs
- [x] 3.7 Add renderControlButtons() logic for power_on and estop_pressed light states

## 4. Verification

- [x] 4.1 Visual verification: no panel overlap, cameras in single row, buttons in single row
