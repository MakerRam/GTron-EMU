## 1. Text Renames

- [x] 1.1 Change page `<title>` from "Vision System Monitor" to "Gtron System Emulator" in index.html
- [x] 1.2 Change header `<h1>` text from "Vision System Monitor" to "Gtron System Emulator" in index.html
- [x] 1.3 Rename "Emulator Control" panel heading to "Front Panel" in index.html
- [x] 1.4 Update CSS file header comment from "Vision System Monitor" to "Gtron System Emulator" in styles.css

## 2. HTML Panel Reorder

- [x] 2.1 Reorder `<section>` elements in index.html to match visual reading order: Front Panel, Tower Lamp, Cameras, System Status, Sag Sensors, Guide Motors, Reeler Motors

## 3. CSS Grid Restructure

- [x] 3.1 Change `.dashboard-grid` from `grid-template-columns: 1fr 1fr 1fr` to 4-column explicit grid with 3 row definitions
- [x] 3.2 Add `grid-column` / `grid-row` rules for each panel: #panel-control (cols 1-3, row 1), #panel-lamps (col 4, rows 1-2), #panel-cameras (cols 1-3, row 2), #panel-system (col 4, rows 2-3), #panel-sag (col 1, row 3), #panel-guides (col 2, row 3), #panel-reelers (col 3, row 3)

## 4. Responsive Breakpoints

- [x] 4.1 Update 960px breakpoint to collapse to 2-column grid with no row-spanning (reset all grid-column/grid-row)
- [x] 4.2 Update 640px breakpoint to single-column layout (reset all grid placement)

## 5. Verification

- [x] 5.1 Visual verification that layout matches reference image (UI Card Sample.png) and all panels render correctly
