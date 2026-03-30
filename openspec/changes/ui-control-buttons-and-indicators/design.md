## Context

The Vision System Monitor is a browser-based dashboard (`visualizer/`) that provides read-only real-time visualization of a GTRON vision system firmware emulator. The frontend is vanilla HTML/CSS/JS (no framework) polling a Flask REST API at 100ms intervals. The backend (`firmware_emulator/src/`) uses an immutable state pattern where opcode handlers receive `DeviceState` and return `(response, new_state)`.

Currently, the dashboard has no interactive controls -- operators can only observe state. The existing `POST /api/command` endpoint already supports injecting 5-byte opcodes via HTTP, which provides the foundation for control buttons. The existing `system-visualizer-ui` spec already mentions Phase 2 pause/resume capabilities but none are implemented.

**Stakeholders**: Operators testing firmware, developers debugging emulator behavior.

## Goals / Non-Goals

**Goals:**
- Add Run, Pause, Stop, Buzzer Off control buttons with live status light indicators
- Add a Query Status indicator in the header bar for at-a-glance emulator health
- Add 6 light indicators near the camera panel representing physical illumination channels
- Implement phased delivery: UI first (Phase 1), then backend integration (Phase 2)
- Maintain backward compatibility with existing API consumers and mock mode

**Non-Goals:**
- WebSocket real-time push (remains deferred to future Phase 3 per existing design docs)
- Record/playback controls (separate Phase 2 feature in existing spec)
- Full HMI remote control of physical hardware (this controls the emulator only)
- Mobile/responsive layout changes

## Decisions

### Decision 1: Reuse existing POST /api/command for control actions

**Choice**: Route Run/Pause/Stop/Buzzer Off through the existing `POST /api/command` endpoint using emulator-specific opcodes rather than creating new REST endpoints.

**Rationale**: The `POST /api/command` endpoint already handles command injection with proper state mutation, logging, and response handling. Adding new opcodes (`EMRUN`, `EMPAU`, `EMSTP`, `BZZOF`) keeps the architecture consistent with the 5-byte opcode protocol. The alternative of creating `POST /api/run`, `POST /api/pause`, etc. would bypass the opcode dispatch pattern and create a parallel control path.

**Alternative considered**: Dedicated REST endpoints (`POST /api/control/run`). Rejected because it would require duplicating state mutation logic outside the opcode handler registry.

### Decision 2: Add emulator run state to DeviceState

**Choice**: Add a `run_state` enum field (RUNNING, PAUSED, STOPPED) and `buzzer_override` boolean to `DeviceState`. Add `light_channels` dict (6 boolean flags) for physical light indicators. Add `query_responsive` boolean for query health.

**Rationale**: The immutable state pattern means all observable state lives in `DeviceState`. The state export pipeline (`DeviceState` -> `StateExporter` -> JSON -> API -> UI) already handles new fields automatically via `to_dict()`. Adding fields here means the existing polling + render pipeline picks them up with no architectural changes.

### Decision 3: Phased UI-first approach

**Choice**: Implement in 3 phases:
- **Phase 1**: UI elements only (HTML/CSS/JS) with hardcoded/mock rendering -- buttons render but send no commands
- **Phase 2**: Backend state extensions + opcode handlers + API wiring
- **Phase 3**: Full integration -- buttons send commands, indicators reflect live state

**Rationale**: User requested phased, checklist-based implementation. UI-first allows visual validation before wiring up backend logic. Each phase produces a testable, committable increment.

### Decision 4: Light indicators as a separate panel section

**Choice**: Add 6 light indicators as a sub-section below the camera grid within the existing Cameras panel, rather than a new panel.

**Rationale**: Physical lights are co-located with cameras on the real machine (lights illuminate the part for camera capture). Keeping them together in the UI reflects the physical layout. Adding a 7th panel would break the 3x2 grid layout.

### Decision 5: Query Status indicator placement

**Choice**: Place the Query Status light indicator in the header bar, between the cycle label and the existing connection status dot.

**Rationale**: Query health is a system-level concern (is the emulator responding to QUERY opcodes?) and belongs in the persistent header, not in a panel. Placing it before the connection status creates a left-to-right flow: cycle state -> query health -> connection status.

## Risks / Trade-offs

- **[Risk] Button click during rapid polling could cause race conditions** -> Mitigation: Use a request queue or debounce clicks; disable button briefly after click until next state poll confirms the action took effect.

- **[Risk] New DeviceState fields break existing tests** -> Mitigation: All new fields have safe defaults (run_state=RUNNING, buzzer_override=False, light_channels all False, query_responsive=True). Existing tests that don't reference these fields are unaffected.

- **[Risk] Mock mode won't reflect new state fields** -> Mitigation: Update `mock_states.json` to include new fields in Phase 1 so mock mode demonstrates the full UI.

- **[Trade-off] Reusing POST /api/command means control actions are limited to 5-byte opcodes** -> Acceptable: The emulator protocol is fundamentally 5-byte ASCII. Custom opcodes for emulator control (EM-prefixed) are clearly distinguished from firmware opcodes.
