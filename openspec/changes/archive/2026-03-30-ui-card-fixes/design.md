## Context

The dashboard was recently rearranged to a 4-column explicit CSS grid layout. Live testing revealed several issues: Tower Lamp (col 4, rows 1-2) overlaps with System Status (col 4, rows 2-3) because they both claim row 2 in column 4. Cameras show 7 indicators (0-6) but real hardware has 6 cameras (1-6). Front Panel buttons are in a 2x2 grid but need to be a single horizontal row with 6 buttons total.

## Goals / Non-Goals

**Goals:**
- Fix grid overlap between Tower Lamp and System Status panels
- Correct camera count from 7 (0-6) to 6 (1-6)
- Display cameras in a single horizontal row matching the light indicators style
- Display Front Panel buttons in a single horizontal row (6 buttons)
- Add Power On and Emergency Exit buttons to Front Panel

**Non-Goals:**
- Implementing backend opcode handlers for PWRON/EMEXI (UI-only for now)
- Changing any other panel layouts or content
- Modifying the header bar

## Decisions

### 1. Grid fix: Tower Lamp row 1 only, System Status rows 2-3

**Decision**: Change Tower Lamp from `grid-row: 1 / 3` to `grid-row: 1` (single row). System Status stays at `grid-row: 2 / 4` (rows 2-3). This eliminates the overlap in column 4 row 2.

**Rationale**: The Tower Lamp panel is short (4 indicators) and fits in a single row. System Status has 8 rows of data and benefits from the extra height of spanning 2 rows.

### 2. Camera indicators: 6-column horizontal row (same as lights)

**Decision**: Change `.camera-grid` from `grid-template-columns: repeat(4, 1fr)` to `repeat(6, 1fr)` and use the same compact indicator style as `.light-channel-grid`.

**Rationale**: The reference image shows cameras and lights as parallel rows. Using the same style creates visual consistency.

### 3. Front Panel: 6-column single row

**Decision**: Change `.control-buttons-grid` from `grid-template-columns: 1fr 1fr` (2x2) to `repeat(6, 1fr)` (single row of 6).

**Rationale**: With 6 buttons (PWR ON, RUN, PAUSE, STOP, BZR OFF, E-EXIT), a single row keeps everything visible at a glance. The Front Panel spans 3 grid columns so there is ample width.

### 4. New button opcodes: PWRON and EMEXI

**Decision**: Add these as UI-only buttons. They call sendControlCommand() like existing buttons but the backend handlers are not implemented yet (will fail gracefully with HTTP error logged to console).

**Rationale**: The UI should match the physical machine front panel. Backend handlers can be added in a follow-up change.

## Risks / Trade-offs

- [PWRON/EMEXI no backend handler] Clicking these buttons in live mode will produce a console error since the backend doesn't handle these opcodes yet. -> Mitigation: The error is caught and logged, UI remains functional.
- [Mock data key change] Camera flags change from "0"-"6" to "1"-"6" in mock_states.json. -> Mitigation: All 10 mock states will be updated consistently.
