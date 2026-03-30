## Why

Currently, running the full system requires three separate steps: opening the Tkinter GUI launcher to start the emulator, running `run_api_server.sh` to start the API server, and running `run_visualizer_server.sh` to serve the dashboard — all in separate terminals. This friction makes it slow to start during testing and confusing for new users. A single entry point that brings everything up automatically eliminates this overhead.

## What Changes

- Replace the multi-step startup (GUI launcher + 2 shell scripts) with a single command: `python start.py` (or double-click `start.py`)
- The new entry point starts the firmware emulator, the Flask API server, and the visualizer HTTP server all in background threads/subprocesses automatically
- The Tkinter GUI launcher (`emulator_launcher.py`) is retired as the primary entry point; it may be kept as an optional advanced UI but is no longer required
- All three services print their status to a single unified console output
- A single Ctrl+C shuts down all three services cleanly
- The visualizer URL is printed on startup so the user can open it directly in a browser

## Capabilities

### New Capabilities
- `unified-entrypoint`: Single `start.py` script that orchestrates startup and shutdown of all three services (emulator, API server, visualizer HTTP server) with a unified console log

### Modified Capabilities
- `emulator-launcher`: The existing `emulator_launcher.py` GUI is demoted from primary entry point; the new `start.py` supersedes it for standard use

## Impact

- New file: `start.py` at project root
- `emulator_launcher.py`: no code changes required; it remains as-is but is no longer documented as the primary way to start
- `firmware_emulator/src/main.py`: no changes required; invoked as subprocess or module
- `run_api_server.sh` and `run_visualizer_server.sh`: superseded but kept for reference
- `README.md`: update Quick Start section to point to `start.py`
- No changes to emulator logic, opcode handling, API endpoints, or visualizer files
