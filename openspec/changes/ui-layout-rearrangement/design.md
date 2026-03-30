## Context

The visualizer dashboard (`visualizer/index.html`, `styles.css`) currently uses a simple 3-column CSS grid (`.dashboard-grid { grid-template-columns: 1fr 1fr 1fr }`) where panels flow in source order. The current panel order (Guide Motors, Reeler Motors, System Status, Sag Sensors, Tower Lamp, Cameras, Emulator Control) does not match the physical machine topology shown in the reference image (UI Card Sample.png).

The reference image specifies:
- Row 1: Front Panel (wide, 3 cols) | Tower Lamp (narrow, 1 col, spans 2 rows vertically)
- Row 2: Cameras (wide, 3 cols) | System Status (1 col, spans 2 rows vertically)
- Row 3: Sag Sensors | Guide Motors | Reeler Motors | (System Status continues)

All rendering logic in `app.js` uses element IDs (e.g., `getElementById('guide-top-bar')`) so panel reordering has zero impact on JavaScript functionality.

## Goals / Non-Goals

**Goals:**
- Match dashboard panel layout to the reference image (UI Card Sample.png)
- Rename page title and header to "Gtron System Emulator"
- Rename "Emulator Control" panel to "Front Panel"
- Maintain responsive behavior at narrower viewports
- Zero changes to JavaScript logic or backend

**Non-Goals:**
- Resizing panel content or changing panel internals
- Adding new panels or removing existing ones
- Changing the polling mechanism, data flow, or mock data
- Changing the header bar layout (title, query status, connection status, mode toggle)

## Decisions

### 1. Explicit CSS Grid placement (over source-order flow)

**Decision**: Use `grid-column` / `grid-row` on each panel ID selector rather than relying on auto-flow.

**Rationale**: The reference layout has panels spanning multiple rows (Tower Lamp: rows 1-2, System Status: rows 2-3) which cannot be achieved with auto-flow. Explicit placement using panel IDs (`#panel-control`, `#panel-lamps`, etc.) ensures each panel lands exactly where specified regardless of HTML source order.

**Alternative considered**: CSS `order` property -- rejected because it cannot achieve row-spanning in grid.

### 2. 4-column grid with fractional units (3fr + 1fr)

**Decision**: Change grid to `grid-template-columns: 1fr 1fr 1fr 0.8fr` with 3 explicit rows.

**Rationale**: The reference image shows Tower Lamp and System Status as narrower right-side panels. Using `0.8fr` for the 4th column gives them a slightly narrower width while keeping the layout proportional.

### 3. HTML source order follows visual reading order

**Decision**: Reorder HTML `<section>` elements to match visual top-to-bottom, left-to-right reading order: Front Panel, Tower Lamp, Cameras, System Status, Sag Sensors, Guide Motors, Reeler Motors.

**Rationale**: Even though CSS grid placement controls visual position, matching source order to visual order improves accessibility (screen readers, tab order) and code readability.

### 4. Responsive fallback to 2-column then 1-column

**Decision**: At 960px, collapse to 2-column grid with all panels spanning full width (no multi-row spans). At 640px, collapse to single column.

**Rationale**: Multi-row spanning panels look broken on narrow viewports. Collapsing to simple stacking is the safest responsive approach.

## Risks / Trade-offs

- [Grid placement fragility] Explicit `grid-column`/`grid-row` is more rigid than auto-flow -- adding a new panel later requires updating placement rules. → Mitigation: Panel IDs are stable and well-documented; a comment block in CSS will document the grid map.
- [Responsive breakpoint change] Existing 960px/640px breakpoints need new rules. → Mitigation: Reset all grid-column/grid-row overrides at breakpoints to restore auto-flow.
- [Browser cache] Users may see stale layout after deploy. → Mitigation: Document that `Ctrl+Shift+R` hard refresh is needed (existing known issue).
