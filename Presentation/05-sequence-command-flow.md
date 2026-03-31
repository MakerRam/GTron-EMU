# C4 Sequence Diagram: End-to-End Command Flow

## From Startup to Real-Time Visualization

> **Purpose**: Shows the complete lifecycle - system startup, LabVIEW handshake, command processing, state updates, and visualization polling as a time-sequenced flow.

---

## Phase 1: System Startup

```mermaid
sequenceDiagram
    participant Dev as Developer
    participant Start as start.py
    participant Emu as EmulatorEngine
    participant Serial as SerialBridge
    participant Config as ConfigParser
    participant API as Flask API Server
    participant Viz as Visualizer (port 8000)

    Dev->>Start: python start.py --port COM2
    Start->>Config: Load Machine Interface Parameters.json
    Config-->>Start: 75 opcodes, timing values, camera maps

    Start->>Emu: Initialize EmulatorEngine
    Emu->>Serial: Open COM2 at 115200 baud
    Serial-->>Emu: Port ready

    Start->>API: Start daemon thread (port 5000)
    API-->>Start: HTTP server listening

    Start->>Viz: Start HTTP server (port 8000)
    Viz-->>Start: Static files served

    Start-->>Dev: All services running
    Note over Dev: Open http://localhost:8000 in browser
```

---

## Phase 2: LabVIEW Handshake

```mermaid
sequenceDiagram
    participant LV as LabVIEW (COM4)
    participant COM as com0com Bridge
    participant Serial as SerialBridge (COM2)
    participant Parser as CommandParser
    participant Dispatch as OpcodeDispatcher
    participant State as DeviceState
    participant Log as Logger

    LV->>COM: Open COM4, 115200 baud
    LV->>COM: Send "QUERY" (5 bytes ASCII)
    COM->>Serial: Forward via virtual pair

    Serial->>Parser: read_command() -> b"QUERY"
    Parser-->>Serial: parse() -> "QUERY"

    Serial->>Dispatch: dispatch("QUERY")
    Dispatch->>Dispatch: Lookup handler registry
    Dispatch->>State: HandshakeHandler.handle()
    State-->>Dispatch: No state change needed
    Dispatch-->>Serial: Response: b"YES"

    Serial->>COM: Write "YES" (3 bytes)
    COM->>LV: Forward response
    LV->>LV: Connection confirmed

    Serial->>Log: Log transaction
    Note over Log: [COMMAND_001] QUERY -> YES (0.4ms)
```

---

## Phase 3: Command Processing (Guide Open Example)

```mermaid
sequenceDiagram
    participant LV as LabVIEW
    participant Serial as SerialBridge
    participant Dispatch as OpcodeDispatcher
    participant Handler as GuideOpenHandler
    participant State as DeviceState
    participant Export as StateExporter
    participant API as Flask API
    participant Viz as Browser Dashboard

    LV->>Serial: Send "tpGOP" (open top guide)

    Serial->>Dispatch: dispatch("tpGOP")
    Dispatch->>Handler: route to guide_open_handler

    Handler->>State: Read current state
    Note over State: guide_top.position = CLOSED

    Handler->>State: Set position = MOVING
    Handler->>Handler: Delay 2000ms (from config)
    Handler->>State: Set position = OPEN
    Handler-->>Dispatch: Response: "tpGOR"

    Dispatch-->>Serial: Write "tpGOR"
    Serial-->>LV: Guide open confirmed

    Note over Viz: Meanwhile, dashboard polls every 100ms...

    Viz->>API: GET /api/state/summary
    API->>Export: export_summary()
    Export->>State: Read current state
    Note over State: guide_top = "open" (updated)
    Export-->>API: JSON dict
    API-->>Viz: HTTP 200 + JSON

    Viz->>Viz: Update Guide Motors panel
    Note over Viz: Top Guide: ████████ OPEN
```

---

## Phase 4: Continuous Operation

```
Timeline: Concurrent Serial + HTTP Operations
════════════════════════════════════════════════════════════════════

Time     Main Thread (Serial)              Daemon Thread (HTTP API)
──────   ──────────────────────            ─────────────────────────
  0ms    read_command() [blocking]         [idle - waiting]
 50ms    ...waiting for serial data...     GET /api/state/summary
 51ms    ...                               → export_summary()
 52ms    ...                               → HTTP 200 + JSON
100ms    Received: "tpGOP"                 [idle]
101ms    parse("tpGOP")                    [idle]
102ms    dispatch → GuideOpenHandler       [idle]
103ms    Set state: MOVING                 [idle]
150ms    ...delay 2000ms...               GET /api/state/summary
151ms    ...                               → state shows "moving"
152ms    ...                               → HTTP 200 + JSON
250ms    ...delay continues...             GET /api/state/summary
251ms    ...                               → state still "moving"
 ...     ... (2 second delay) ...          ... (20 more polls) ...
2102ms   Set state: OPEN                   [idle]
2103ms   Write response: "tpGOR"           [idle]
2104ms   Log transaction                   [idle]
2150ms   read_command() [blocking]         GET /api/state/summary
2151ms   ...waiting...                     → state shows "open"
2152ms   ...                               → HTTP 200 + JSON

Key: Both threads access DeviceState safely (Python GIL)
     API thread NEVER blocks the serial event loop
     Dashboard sees state transitions in real-time (100ms granularity)

════════════════════════════════════════════════════════════════════
```

---

## Complete Data Flow Summary

```
┌──────────┐  5-byte   ┌───────────┐  parse   ┌──────────┐  route   ┌──────────┐
│ LabVIEW  │──ASCII──>│  Serial   │────────>│ Command  │───────>│ Opcode   │
│ (COM4)   │          │  Bridge   │          │ Parser   │        │Dispatcher│
└──────────┘          │  (COM2)   │          └──────────┘        └────┬─────┘
     ▲                └─────┬─────┘                                   │
     │                      │                                    handle│
     │                      │                                         ▼
     │               write  │                               ┌──────────────┐
     │              response│                               │   Handler    │
     │                      │                               │  (1 of 75)   │
     │                      │                               └──────┬───────┘
     │                      │                                      │
     │                ┌─────▼─────┐                          update │
     │                │  Serial   │                                │
     └───3-5 byte────│  Bridge   │                          ┌─────▼──────┐
        response      └───────────┘                          │  Device    │
                                                             │  State     │
                      ┌───────────┐   read    ┌──────────┐  │ (immutable)│
                      │  Browser  │◄──JSON───│  Flask    │◄─┤            │
                      │ Dashboard │  (HTTP)  │  API      │  └────────────┘
                      │ (6 panels)│  100ms   │ (port     │
                      └───────────┘  poll    │  5000)    │
                                              └──────────┘

                      ┌───────────┐
                      │   Logs    │◄── Every transaction logged
                      │ (4 files) │    with before/after state
                      └───────────┘
```

---

## Startup Command Reference

```bash
# Full stack (recommended)
python start.py --port COM2

# Individual components
python firmware_emulator/src/main.py --port COM2 --verbose   # Emulator only
python -m http.server 8000 --directory visualizer             # Dashboard only

# With options
python start.py --port COM2 --api-port 8080 --verbose --rtscts
```

---

*C4 Sequence Diagram - Command Flow | Vision System Firmware Emulator | Zentron Projects*
