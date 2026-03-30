## ADDED Requirements

### Requirement: Browser dashboard displays real-time device state

The system SHALL provide an HTML/JS dashboard that polls the API and displays device state with <100ms latency.

#### Scenario: Dashboard opens in browser
- **WHEN** user opens visualizer/index.html in a web browser
- **THEN** page loads with header, 6 monitoring panels, and command log
- **AND** initial connection status shows "Connecting..." or "Connected"
- **AND** all UI elements are visible and responsive

#### Scenario: Dashboard polls API for state updates
- **WHEN** dashboard is displayed in Live mode
- **THEN** JavaScript sends GET /api/state/summary every 100ms
- **AND** response is parsed and UI components update
- **AND** if poll fails, "Disconnected" message appears
- **AND** auto-retry with exponential backoff

#### Scenario: Guide motor positions display in real-time
- **WHEN** API state shows guide_top.position="open"
- **THEN** dashboard displays "OPEN" text and bar at 100% width
- **AND** updates within 100ms of state change
- **AND** moving state shows animated transition

#### Scenario: Reeler motor speeds display
- **WHEN** API state shows reeler_top.speed=800
- **THEN** dashboard displays "800 steps/s" + visual gauge
- **AND** updates within 100ms of state change

#### Scenario: Sag sensors display color-coded status
- **WHEN** API state shows sag_top_upper=false
- **THEN** dashboard displays green "PASS" indicator
- **AND** when sag_top_upper=true, displays red "TRIGGERED"
- **AND** all 4 sag sensors update independently

#### Scenario: Tower lamp state displays
- **WHEN** API state shows lamps={red:false, yellow:true, green:false, buzzer:false}
- **THEN** dashboard displays yellow lamp glowing, others dim
- **AND** updates within 100ms

#### Scenario: Camera activity displays
- **WHEN** API state shows cameras.flags={"1":true, "2":false, "3":true, "4":false, "5":false, "6":false}
- **THEN** dashboard displays 6 camera indicators (1-6) with active flags highlighted
- **AND** active_sequence shows which camera is currently active
- **AND** camera 0 does not exist in the UI

#### Scenario: Power On button sends command
- **WHEN** user clicks "PWR ON" button in live mode
- **THEN** system sends POST /api/command with {"command": "PWRON"}
- **AND** button is debounced for 500ms

#### Scenario: Emergency Exit button sends command
- **WHEN** user clicks "E-EXIT" button in live mode
- **THEN** system sends POST /api/command with {"command": "EMEXI"}
- **AND** button is debounced for 500ms

#### Scenario: System status panel displays
- **WHEN** API state shows door_locked=true, estop_pressed=false, power_on=true
- **THEN** dashboard displays door status, E-stop status, power status
- **AND** all 3 update independently and in real-time

#### Scenario: Command log accumulates history
- **WHEN** API state shows last_command="QUERY"
- **THEN** dashboard appends to command log display
- **AND** log shows last 20 commands with timestamps
- **AND** scrolls to show newest commands
- **AND** updates when last_command changes

### Requirement: Dashboard supports Mock and Live modes

The system SHALL allow offline testing with mock state cycling, and switching to live API when emulator is running.

#### Scenario: Dashboard starts in Mock mode
- **WHEN** page loads and Live mode is not selected
- **THEN** visualizer uses mock_states.json (10-state cycle)
- **AND** dashboard cycles through mock states every 500ms
- **AND** all UI components update as if polling API
- **AND** no network connection required

#### Scenario: User toggles to Live mode
- **WHEN** user clicks "LIVE" button
- **THEN** visualizer switches to polling http://localhost:5000/api/state/summary
- **AND** dashboard shows "Connecting..." during first request
- **AND** transitions to "Connected" when successful
- **AND** shows "Disconnected" if API is unreachable

#### Scenario: User toggles back to Mock mode
- **WHEN** user clicks "MOCK" button from Live mode
- **THEN** visualizer stops polling API
- **AND** returns to mock state cycling
- **AND** dashboard continues updating normally

#### Scenario: User configures custom API URL
- **WHEN** user enters "http://192.168.1.100:5000" in API URL field and toggles Live
- **THEN** visualizer polls the custom URL instead of localhost
- **AND** shows "Connected" if custom URL responds
- **AND** shows "Disconnected" if custom URL is unreachable

### Requirement: Dashboard handles connection loss gracefully

The system SHALL display error states and auto-retry when API becomes unavailable.

#### Scenario: API becomes unreachable
- **WHEN** emulator stops or API port is closed
- **THEN** next poll fails with network error
- **AND** dashboard displays "Disconnected" in red
- **AND** last valid state remains displayed
- **AND** auto-retry starts with 500ms initial delay

#### Scenario: Dashboard reconnects when API returns
- **WHEN** emulator restarts and API becomes available
- **THEN** auto-retry succeeds
- **AND** dashboard shows "Connected" in green
- **AND** state updates resume at normal polling rate

#### Scenario: Slow network is handled
- **WHEN** API response takes 200ms
- **THEN** dashboard receives response but displays "Slow Connection" warning
- **AND** does not spam API with queued requests
- **AND** continues polling at normal interval

### Requirement: Dashboard is responsive and performant

The system SHALL render properly on desktop and support smooth real-time updates.

#### Scenario: Dashboard renders on desktop (1920x1080+)
- **WHEN** page loads in Chrome/Firefox/Safari on desktop
- **THEN** all 6 panels are visible in 3x2 grid
- **AND** fonts are readable, colors are distinct
- **AND** dark theme (#1a1a2e background) is applied

#### Scenario: Dashboard renders on tablet (iPad)
- **WHEN** page loads on iPad in landscape mode
- **THEN** layout adapts to 2-column grid
- **AND** all content is visible and usable

#### Scenario: UI updates do not cause flicker
- **WHEN** state updates arrive every 100ms
- **THEN** DOM updates are smooth and non-flickering
- **AND** animations (bar widths) are smooth
- **AND** no excessive repainting

#### Scenario: JavaScript performance is acceptable
- **WHEN** dashboard polls every 100ms for 10 minutes
- **THEN** memory usage remains stable (<100MB)
- **AND** CPU usage is <5%
- **AND** no memory leaks detected

### Requirement: Dashboard has intuitive UI design

The system SHALL display information clearly with visual hierarchy and proper labeling.

#### Scenario: Guide motors panel is intuitive
- **WHEN** user views Guide Motors panel
- **THEN** sees "TOP" and "BTM" labels clearly
- **AND** sees position text (CLOSED, OPEN, MOVING)
- **AND** sees visual bar showing position percentage
- **AND** understands purpose without help

#### Scenario: Status indicators use consistent colors
- **WHEN** user views all indicator elements
- **THEN** green (#00e676) means "OK" or "active"
- **AND** red (#ff1744) means "fault" or "triggered"
- **AND** yellow (#ffea00) means "warning" or "busy"
- **AND** gray (#424242) means "off"

#### Scenario: Command log is readable
- **WHEN** user views Command Log at bottom
- **THEN** sees list of recent commands with timestamps
- **AND** newest commands appear at bottom (scroll to view)
- **AND** format is: "[HH:MM:SS] COMMAND_NAME"

### Requirement: Mock data simulates realistic state sequences

The system SHALL provide 10-state cycle that represents a typical machine operation.

#### Scenario: Mock states transition smoothly
- **WHEN** mock mode is active
- **THEN** states cycle through: IDLE → HANDSHAKE → CONFIGURE → GUIDES_OPENING → GUIDES_OPEN+REELERS_START → MATERIAL_RUNNING → CAMERA_SEQUENCE → ALL_CAMERAS_DONE → GUIDES_CLOSING → CYCLE_COMPLETE → repeat
- **AND** each state represents a logical step in machine operation
- **AND** guides move from closed → opening → open → closing
- **AND** cameras activate when material is running
- **AND** reelers run during material phase

#### Scenario: Mock state JSON is valid
- **WHEN** mock_states.json is loaded
- **THEN** JSON parses without errors
- **AND** each state object includes all required fields
- **AND** field values are realistic and within valid ranges
- **AND** camera flags use keys "1" through "6" (not "0" through "6")
