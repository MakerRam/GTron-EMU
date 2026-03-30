## MODIFIED Requirements

### Requirement: Browser dashboard displays real-time device state

The system SHALL provide an HTML/JS dashboard that polls the API and displays device state with <100ms latency. The page title and header SHALL read "Gtron System Emulator".

#### Scenario: Dashboard opens in browser
- **WHEN** user opens visualizer/index.html in a web browser
- **THEN** page title reads "Gtron System Emulator"
- **AND** header h1 reads "Gtron System Emulator"
- **AND** page loads with header, 7 monitoring panels, and command log
- **AND** initial connection status shows "Connecting..." or "Connected"
- **AND** all UI elements are visible and responsive

#### Scenario: Dashboard polls API for state updates
- **WHEN** dashboard is displayed in Live mode
- **THEN** JavaScript sends GET /api/state/summary every 100ms
- **AND** response is parsed and UI components update
- **AND** if poll fails, "Disconnected" message appears
- **AND** auto-retry with exponential backoff

### Requirement: Dashboard is responsive and performant

The system SHALL render properly on desktop and support smooth real-time updates.

#### Scenario: Dashboard renders on desktop (1920x1080+)
- **WHEN** page loads in Chrome/Firefox/Safari on desktop
- **THEN** all 7 panels are visible in 4-column grid with explicit placement
- **AND** fonts are readable, colors are distinct
- **AND** dark theme is applied

#### Scenario: Dashboard renders on tablet (iPad)
- **WHEN** page loads on iPad in landscape mode
- **THEN** layout adapts to 2-column grid with no row-spanning panels
- **AND** all content is visible and usable
