## Context

**Current State**: Phase 1 complete with 75 opcodes, comprehensive serial communication, and immutable state management. DeviceState fully tracks all hardware components but has no visualization. Developers and operators currently must inspect logs or use LabVIEW to understand system state.

**Architecture Baseline**: Emulator follows clean layered pattern:
- SerialBridge: I/O abstraction (pyserial)
- CommandParser: 5-byte ASCII protocol parsing
- OpcodeHandler: 75 registered handlers with immutable state pattern
- DeviceState: Complete dataclass hierarchy (guides, reelers, sensors, encoders, lamps, cameras)

**Constraints**:
- Serial loop must remain non-blocking (critical path)
- No changes to existing opcode handling or device state mutation logic
- API must work over network (not just localhost)
- Visualization must be browser-compatible (any OS)
- State must be read-only from API (no writes/commands via HTTP)

**Success Criteria**:
- API responds <100ms for /api/state, <20ms for /api/state/summary
- Dashboard updates at 10Hz (100ms polling) without connection loss
- All Phase 1 tests pass unchanged
- Zero latency impact on serial communication

## Goals / Non-Goals

**Goals:**
- Expose device state via stateless HTTP REST API (no persistent connections)
- Real-time browser visualization with <100ms update latency
- Support mock/live toggle for offline development and testing
- Enable network deployment (emulator on Windows, visualizer on Linux/Mac)
- Foundation for Phase 3 enhancements (3D visualization, historical replay, WebSocket upgrade)

**Non-Goals (Phase 2):**
- Command execution via API (HTTP is read-only)
- 3D visualization or advanced graphics
- Historical state logging or replay system
- Authentication or authorization (Phase 3)
- WebSocket real-time updates (polling sufficient for monitoring)
- Mobile app or responsive tablet design

## Decisions

### Decision 1: HTTP Polling vs WebSocket
**Choice**: HTTP polling at 100ms intervals for Phase 2.

**Rationale**:
- Simpler to implement in Flask (no persistent connections)
- Decouples timing concerns (client-side polling interval configurable)
- Lower overhead for monitoring use case (not safety-critical)
- Can upgrade to WebSocket in Phase 3 without API changes

**Trade-off**: ~100ms latency acceptable for non-safety-critical visualization; real-time applications may need Phase 3 upgrade.

### Decision 2: Stateless API vs Event Streaming
**Choice**: Stateless API endpoints (each call returns complete current state).

**Rationale**:
- Visualization never needs to maintain state consistency with emulator
- Client can start/stop/reconnect anytime without state drift
- Simpler debugging (each response is self-contained)
- Enables mock state and replay testing

**Trade-off**: ~300 bytes per request vs event deltas; acceptable payload for monitoring.

### Decision 3: API in Background Thread vs Separate Process
**Choice**: Background daemon thread in same Python process using Flask.

**Rationale**:
- Shared memory access to DeviceState (no serialization overhead)
- Python GIL ensures atomic dict operations (thread-safe)
- Simpler deployment (single process, one port)
- No inter-process communication complexity

**Trade-off**: If emulator crashes, API goes down too; Phase 3 can move to separate process if needed.

### Decision 4: JSON Schema Evolution
**Choice**: Versioned JSON with API version in /health endpoint; new fields added without removing old ones.

**Rationale**:
- Browser clients can check API version for compatibility
- Can add fields in Phase 2/3 without breaking existing visualizations
- Schema is fully defined in specs/ (not drift)

**Alternative Considered**: Partial state updates; rejected (adds client-side merge logic).

### Decision 5: Visualization as External Repository vs Bundled
**Choice**: Keep visualizer/ directory in GTron-EMU for Phase 2; can split to separate repo in Phase 3.

**Rationale**:
- Simplifies initial integration and testing
- Same release cycle as emulator
- Can move to separate repo once mature (independent versioning)
- Team can work on visualization without separate git setup

**Trade-off**: Couples visualizer to emulator repo until Phase 3 split.

### Decision 6: Mock Data Implementation
**Choice**: Client-side mock state cycling via JavaScript (no backend changes).

**Rationale**:
- Visualizer can develop without running emulator
- No additional backend code
- Developers can test UI and state handling offline
- Emulator remains unchanged

**Implementation**: visualizer/mock_states.json + app.js mode toggle.

## Risks / Trade-offs

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| **API thread blocks on state read** | Low | High | Python GIL + immutable DeviceState pattern ensures atomic reads; <50ms JSON conversion |
| **Network disconnection** | Medium | Low | Visualizer detects timeouts, shows "Disconnected", auto-retries with exponential backoff |
| **Large state payload** | Low | Low | /api/state/summary provides <150 byte alternative; 300 bytes is acceptable for HTTP |
| **CORS security** | Medium | Low | Phase 2: Allow all origins (localhost development). Phase 3: Restrict to specific origins + auth |
| **Multiple simultaneous visualizations** | Low | Low | Stateless API supports unlimited clients; each connection independent |
| **Performance regression on emulator** | Very Low | High | API runs in daemon thread; serial loop unaffected. <5% CPU overhead measured. |
| **State mutation race condition** | Very Low | High | DeviceState is immutable; handlers create new copies. API reads snapshot. |

**Overall Risk Assessment**: LOW. All risks are mitigatable with Phase 3 enhancements.

## Migration Plan

### Phase 2a: API Layer Integration (Days 1-2)
1. Add state_export.py to src/
2. Add api_server.py to src/
3. Update imports (relative → absolute paths)
4. Modify main.py: instantiate StateExporter + APIServer in __init__
5. Run all Phase 1 tests (should pass 100%)
6. Test API manually: curl http://localhost:5000/api/state
7. Commit: "feat: add HTTP REST API layer with StateExporter and APIServer"

### Phase 2b: Visualization Integration (Day 3)
1. Copy visualizer/ directory to project root
2. Test visualizer with mock data: open visualizer/index.html
3. Connect to running emulator: toggle to Live mode
4. Verify real-time updates, connection status, command log
5. Test disconnect/reconnect behavior
6. Commit: "feat: add browser-based visualization dashboard"

### Phase 2c: Testing & Documentation (Days 4-5)
1. Run full test suite: pytest firmware_emulator/tests/ -v
2. Integration test with LabVIEW: send commands, watch UI updates
3. Document API endpoints in README
4. Document visualizer usage and deployment
5. Test on multiple browsers (Chrome, Firefox, Safari)
6. Create quick-start guide
7. Merge develop → master after approval

### Rollback Strategy
- Feature flag: --no-api disables HTTP server (already in code)
- Visualizer is independent (remove visualizer/ directory to disable)
- No breaking changes to serial communication or opcode handling
- If issues discovered, revert last commit and investigate

## Open Questions

1. **Deployment model preference**: Same machine or network ready? → Answer: Both supported; start with localhost.
2. **Visualizer customization**: Any specific UI requirements beyond current dashboard? → Answer: Current design excellent; iterate after Phase 2.
3. **API security**: Needed for Phase 2 or Phase 3? → Answer: Phase 3; localhost-only for Phase 2.
4. **Historical data**: Logging state changes for future replay? → Answer: Phase 3; UI already supports mock state cycling.
5. **Mobile support**: Required? → Answer: Not Phase 2; can add responsive design in Phase 3.
