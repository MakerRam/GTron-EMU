# Fix: WSL Stale .pyc Cache Breaks UI Live Mode Updates

**Date:** 2026-03-29  
**Symptom:** Browser UI not reflecting serial commands; command log always empty  
**Environment:** Windows 11 + WSL2, Python 3.11 (Windows), Python 3.12 (WSL)

---

## Symptom

After sending a command from the Arduino serial monitor (e.g. `TYEL1`, `tpGCL`):

- Launcher showed `RECV: tpGCL -> SEND: TPGCR` ✓
- `[DBG-SERIAL]` prints confirmed `exporter synced: last_command='TPGCL'` ✓
- Browser UI command log did not update ✗
- Browser console showed `last_command=QUERY` (stale) ✗

---

## Root Causes (two separate bugs)

### Bug 1 — Stale `.pyc` bytecode (Windows Python 3.11)

**What happened:**  
All source edits were made from WSL (`/mnt/d/TDD/Emulator/`), which maps to `D:\TDD\Emulator\` on Windows. WSL and Windows track file modification times differently on the shared NTFS filesystem. Windows Python 3.11 compiled `.pyc` files at an earlier point and never invalidated them — even after the source `.py` files were updated in WSL — because the mtime it stored in the `.pyc` header still matched what Windows reported for the source file.

**Effect:**  
The launcher subprocess (Windows Python 3.11) was silently running old bytecode for `main.py` and `api_server.py`. Fixes like `log_command()` and `state_exporter._state` sync were present in source but never executed.

**Fix:**  
Delete all `.pyc` files and `__pycache__` directories, forcing a fresh recompile:

```bash
find /mnt/d/TDD/Emulator/firmware_emulator -name "*.pyc" -delete
find /mnt/d/TDD/Emulator/firmware_emulator -name "__pycache__" -type d -empty -delete
```

Then restart the launcher. Windows Python recompiles from the current source on next import.

---

### Bug 2 — Stale WSL Flask process on port 5000

**What happened:**  
During debugging, a Flask server was started inside WSL on port 5000 (via `curl` and `python3` test runs). This process was never killed. When the Windows launcher later started its own Flask server on port 5000, both were bound simultaneously. The browser (`localhost:5000`) hit the **WSL process first** (via WSL2 localhost forwarding), receiving stale state with `last_command=QUERY` instead of the Windows launcher's live state.

**Effect:**  
The browser always polled the wrong server. Every command sent via serial was invisible to the browser because it was reading from a dead process.

**Fix:**  
Kill the stale WSL Flask process:

```bash
# Find the process
lsof -i :5000

# Kill it (replace PID with actual)
kill <PID>
```

Verify port is free:
```bash
lsof -i :5000 || echo "port 5000 is free"
```

---

## How to Avoid This in Future

### Stale `.pyc` issue
- Always delete `__pycache__` after editing Python files from WSL that will be run by Windows Python:
  ```bash
  find /mnt/d/TDD/Emulator -name "*.pyc" -delete
  ```
- Or add `-B` flag to Python invocation to skip `.pyc` writing entirely (set `PYTHONDONTWRITEBYTECODE=1` in the launcher environment).

### Stale port 5000 issue
- Before starting the launcher, always check if port 5000 is in use in WSL:
  ```bash
  lsof -i :5000
  ```
- Never leave long-running Flask servers running in WSL during development.
- The launcher could be enhanced to print a warning if `http://localhost:5000/health` already responds before it starts.

---

## Files Changed During This Investigation

| File | Change |
|---|---|
| `firmware_emulator/src/main.py` | Added `log_command()` + `state_exporter._state` sync after serial dispatch; wired `command_handler` to `APIServer` |
| `firmware_emulator/src/api_server.py` | Fixed `/api/command` to call `log_command()` before updating exporter |
| `visualizer/app.js` | Changed default mode from `mock` to `live` |
| `visualizer/index.html` | Made LIVE button the active default |

---

## Debugging Technique That Found It

Added `[DBG-*]` print instrumentation at all four component boundaries simultaneously:

```
[DBG-SERIAL]  main.py _process_command()       — serial path
[DBG-API]     api_server.py send_command()      — HTTP command injection
[DBG-STATE]   api_server.py get_state()         — every poll response
[DBG-UI]      app.js fetchLiveState()           — browser fetch result
              app.js updateCommandLog()          — command log decision
```

Running one test command then reading all four outputs pinpointed exactly which boundary was broken, without guessing.
