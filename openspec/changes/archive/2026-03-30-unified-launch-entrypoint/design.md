## Context

The project currently has three separate entry points that must all be started manually:

1. `emulator_launcher.py` — a Tkinter GUI that starts `firmware_emulator/src/main.py` (serial + API server) as a subprocess
2. `run_api_server.sh` — a bash script that starts a standalone Flask API server (without serial)
3. `run_visualizer_server.sh` — a bash script that starts a Python HTTP server serving `visualizer/`

In practice, the intended workflow is to run all three together. The separate scripts exist for historical reasons (they were built incrementally across Phase 1 and Phase 2) but impose unnecessary startup friction.

The emulator's `main.py` already starts the API server internally (on port 5000) when `--no-api` is not passed. So `run_api_server.sh` is actually redundant in the normal workflow. The visualizer HTTP server (port 8000) is the only missing piece that `main.py` does not start.

## Goals / Non-Goals

**Goals:**
- Single command (`python start.py`) starts all three services: emulator (serial + API on port 5000) and visualizer HTTP server (port 8000)
- Unified console output — one terminal shows the status of all services
- Single Ctrl+C stops everything cleanly
- Prints the browser URL on startup so the user can open the dashboard immediately
- Works on Windows (COM port) without requiring bash or WSL
- Port in use detection for both 5000 and 8000 before attempting to start

**Non-Goals:**
- No Tkinter GUI — `start.py` is a headless CLI script
- No changes to emulator logic, opcode handling, API endpoints, or visualizer files
- Not replacing `emulator_launcher.py` for users who prefer the GUI — it remains as-is
- Not handling multiple simultaneous emulator instances
- Not a daemon/service installer (no systemd, no Windows service)

## Decisions

### Decision 1: Single Python file at project root, not a shell script

**Choice:** `start.py` (pure Python, no bash)

**Why:** The project runs on Windows where bash scripts require WSL or Git Bash. A pure Python script works everywhere without prerequisites beyond Python itself — consistent with how `emulator_launcher.py` works.

**Alternatives considered:**
- `start.bat` (Windows batch) + `start.sh` (Linux/Mac) — two files to maintain, diverge over time
- `Makefile` — requires `make`, not universally available on Windows

---

### Decision 2: Visualizer HTTP server runs as a Python `threading.Thread`, not a subprocess

**Choice:** Start `http.server` via `socketserver.TCPServer` in a daemon thread inside `start.py`

**Why:** No subprocess management overhead, clean shutdown when the main thread exits. The visualizer is pure static files — Python's built-in HTTP server is sufficient and has no dependencies.

**Alternatives considered:**
- `subprocess.Popen(['python3', '-m', 'http.server', '8000'])` — works but requires managing a second process handle and cross-platform `python`/`python3` inconsistency

---

### Decision 3: Emulator started as a subprocess (not imported as a module)

**Choice:** `subprocess.Popen([sys.executable, '-m', 'firmware_emulator.src.main', '--port', port, ...])` — same approach as `emulator_launcher.py`

**Why:** The emulator's `main.py` blocks in a `while True` loop and is designed to run as a standalone process. Starting it as an in-process thread would require refactoring `EmulatorEngine.run()` to be non-blocking. Keeping it as a subprocess preserves existing behavior and crash isolation.

**Alternatives considered:**
- Run `EmulatorEngine` in a thread — requires non-trivial refactoring of the blocking event loop; deferred

---

### Decision 4: COM port is a required argument, not hardcoded

**Choice:** `python start.py --port COM2` (required argument, same as `main.py`)

**Why:** COM port varies per machine (COM1/COM2/COM3, or `/dev/ttyS0` on Linux). Hardcoding COM2 would break on any other configuration. The user must specify it — same contract as running `main.py` directly.

**Rationale for not defaulting:** A wrong port causes a hard error immediately; a silent wrong default would be more confusing.

---

### Decision 5: Port conflict detection before starting services

**Choice:** Check ports 5000 and 8000 before launching, print actionable error and exit if in use

**Why:** Silently failing or binding to a random port confuses users. Existing scripts (`run_api_server.sh`) already do this check; `start.py` carries the same pattern forward.

## Risks / Trade-offs

- **[Risk] Windows `python` vs `python3` command** → Mitigation: use `sys.executable` (the currently running interpreter) for subprocess launch, guaranteeing the same Python binary
- **[Risk] Serial port not available** → Mitigation: subprocess immediately prints error from `main.py` and exits; `start.py` monitors the subprocess and reports if it dies unexpectedly within 2 seconds of launch
- **[Risk] Port 5000 blocked by another process** → Mitigation: port check before launch with actionable message (`lsof -i :5000` hint on Linux, `netstat -ano` hint on Windows)
- **[Risk] emulator_launcher.py still exists and users run it instead** → Mitigation: `README.md` quick-start updated to lead with `start.py`; launcher kept but moved to "Advanced" section

## Migration Plan

1. Add `start.py` to project root
2. Update `README.md` Quick Start section
3. No other files modified
4. Rollback: delete `start.py` — nothing else changed

## Open Questions

- Should `--flow-control` options from the GUI launcher be exposed as CLI flags in `start.py`? (Proposed: yes, optional flags matching `main.py` existing flags)
- Should the visualizer port (8000) be configurable via `--visualizer-port`? (Proposed: yes, optional, default 8000)
