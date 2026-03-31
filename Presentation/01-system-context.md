# C4 Level 1: System Context Diagram

## Vision System Firmware Emulator - Who Uses It and What It Connects To

> **Purpose**: Shows the entire system as a single box, surrounded by the people and external systems that interact with it.

---

## Context Diagram

```mermaid
C4Context
    title System Context - Vision System Firmware Emulator

    Person(developer, "Developer", "Builds and tests LabVIEW integration without physical hardware")
    Person(operator, "Machine Operator", "Monitors emulated device state via browser dashboard")
    Person(qa, "QA Engineer", "Validates firmware protocol compliance using emulator logs")

    System(emulator, "Vision System Firmware Emulator", "Emulates GTRON vision system firmware: 75 opcodes, virtual COM port, HTTP API, real-time dashboard")

    System_Ext(labview, "LabVIEW Application", "Manufacturing control software. Sends 5-byte ASCII opcodes over serial port")
    System_Ext(com0com, "com0com Virtual Port Driver", "Creates paired virtual COM ports (COM3 <-> COM4) on Windows")
    System_Ext(physical_hw, "Physical GTRON Hardware", "Real machine with guides, reelers, sensors, cameras, lamps - REPLACED by emulator")
    System_Ext(browser, "Web Browser", "Chrome/Edge/Firefox renders the visualizer dashboard")
    System_Ext(config, "Machine Interface Parameters.json", "Zentron configuration file defining all 75 opcodes, timing values, and camera mappings")

    Rel(developer, emulator, "Starts emulator, reviews logs, debugs protocol")
    Rel(operator, emulator, "Views real-time dashboard in browser")
    Rel(qa, emulator, "Reviews command logs, validates opcode responses")

    Rel(labview, emulator, "Sends/receives 5-byte ASCII commands", "Serial over COM4 at 115200 baud")
    Rel(emulator, com0com, "Listens on COM3", "Virtual serial port pair")
    Rel(emulator, browser, "Serves REST API + static dashboard", "HTTP on ports 5000 and 8000")
    Rel(emulator, config, "Reads opcode definitions and timing", "File I/O at startup")

    Rel(physical_hw, labview, "REPLACED - no longer needed for development", "Was: RS-232 serial")
```

---

## Key Relationships

| From | To | Protocol | Purpose |
|------|----|----------|---------|
| LabVIEW | Emulator | Serial (COM4 -> COM3) | Send opcodes, receive responses |
| Emulator | com0com | Virtual COM port | Provides serial endpoint |
| Emulator | Browser | HTTP REST (port 5000) | Serves device state as JSON |
| Emulator | Browser | HTTP Static (port 8000) | Serves visualizer HTML/JS/CSS |
| Emulator | File System | File I/O | Reads config, writes logs |
| Developer | Emulator | CLI + Logs | Starts process, monitors output |
| Operator | Browser | HTTP | Views real-time dashboard |

---

## What This System Replaces

```
BEFORE (Physical Setup):                    AFTER (Emulated Setup):
┌──────────┐  RS-232  ┌──────────────┐     ┌──────────┐  Virtual  ┌──────────────┐
│ LabVIEW  │────────>│ GTRON HW     │     │ LabVIEW  │────────>│ Firmware     │
│          │<────────│ (Physical)   │     │          │<────────│ Emulator     │
└──────────┘         │ - 3 Cameras  │     └──────────┘  COM    │ (Python)     │
                     │ - 2 Guides   │                   Port   │ + REST API   │
                     │ - 2 Reelers  │                          │ + Dashboard  │
                     │ - 4 Sag Sens │                          │ + Logs       │
                     │ - Tower Lamp │                          └──────────────┘
                     │ - Encoders   │
                     └──────────────┘
```

---

## Benefits of Emulation

- **No physical hardware required** - develop and test anywhere
- **Deterministic behavior** - same command sequence = same state
- **Full visibility** - every command logged with before/after state
- **Real-time monitoring** - browser dashboard shows live device state
- **Fast iteration** - no hardware setup/teardown between tests

---

*C4 Level 1 - System Context | Vision System Firmware Emulator | Zentron Projects*
