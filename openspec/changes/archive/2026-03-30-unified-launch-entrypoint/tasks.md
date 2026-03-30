## 1. Create start.py entry point

- [x] 1.1 Create `start.py` at project root with argument parser: `--port` (required), `--baudrate` (default 115200), `--api-port` (default 5000), `--visualizer-port` (default 8000), `--rtscts`, `--dsrdtr`
- [x] 1.2 Implement `check_port_free(port)` helper using `socket.socket` to detect if a TCP port is already bound
- [x] 1.3 Check ports 5000 and 8000 (or custom values) before starting any service; exit with actionable error if occupied
- [x] 1.4 Implement `start_visualizer_server(port, directory)` that runs Python's `http.server.HTTPServer` in a daemon thread serving `visualizer/`
- [x] 1.5 Implement `start_emulator(args)` that launches `firmware_emulator.src.main` as a subprocess using `sys.executable -m firmware_emulator.src.main --port ... --api-port ...`
- [x] 1.6 Print startup banner with service URLs: emulator port, API URL (`http://localhost:<api-port>`), visualizer URL (`http://localhost:<visualizer-port>/index.html`)
- [x] 1.7 Implement subprocess health check: monitor emulator subprocess for 3 seconds after launch; if it exits, capture stderr output, stop visualizer server, and exit with error
- [x] 1.8 Implement `shutdown()` that terminates the emulator subprocess and stops the visualizer thread on Ctrl+C (KeyboardInterrupt)
- [x] 1.9 Main event loop: after startup, wait for KeyboardInterrupt or emulator subprocess exit, then call `shutdown()`

## 2. Tests

- [x] 2.1 Write unit test `tests/test_start.py`: test `check_port_free()` returns True on a free port and False on an occupied port (bind a temp socket to occupy it)
- [x] 2.2 Write unit test: `start.py --help` exits 0 and includes `--port`, `--api-port`, `--visualizer-port` in output
- [x] 2.3 Write unit test: running `start.py` without `--port` exits with non-zero code and prints usage error
- [x] 2.4 Run `python3 -m pytest tests/test_start.py -v` and verify all pass

## 3. Manual Verification

- [ ] 3.1 Run `python start.py --port COM2` (or appropriate port) and verify console shows all three service URLs
- [ ] 3.2 Verify `curl http://localhost:5000/health` returns JSON response
- [ ] 3.3 Verify `http://localhost:8000/index.html` opens in browser and shows the visualizer
- [ ] 3.4 Press Ctrl+C and verify all services stop cleanly (no hanging processes)
- [x] 3.5 Run `python start.py --port COM99` (invalid port) and verify error is printed and process exits within 5 seconds

## 4. Documentation

- [x] 4.1 Update `README.md` Quick Start section: replace GUI launcher instructions with `python start.py --port <COM_PORT>`
- [x] 4.2 Move `emulator_launcher.py` reference in `README.md` to an "Advanced / GUI Launcher" section
- [x] 4.3 Add `--help` output example to README so users can see all flags

## 5. Commit

- [x] 5.1 `git add start.py tests/test_start.py README.md`
- [x] 5.2 Commit: `feat: add unified start.py entry point (emulator + API + visualizer in one command)`
