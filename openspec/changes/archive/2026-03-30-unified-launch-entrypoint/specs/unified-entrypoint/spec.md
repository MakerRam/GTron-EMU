## ADDED Requirements

### Requirement: Single command startup
The system SHALL provide a `start.py` script at the project root that starts the firmware emulator (serial + API server on port 5000) and the visualizer HTTP server (port 8000) with a single command: `python start.py --port <COM_PORT>`.

#### Scenario: Successful startup
- **WHEN** the user runs `python start.py --port COM2`
- **THEN** the emulator process starts on COM2 at 115200 baud
- **THEN** the Flask API server starts on port 5000
- **THEN** the visualizer HTTP server starts on port 8000
- **THEN** the console prints `Visualizer: http://localhost:8000/index.html`
- **THEN** all three services are reachable within 3 seconds

#### Scenario: Unified shutdown
- **WHEN** the user presses Ctrl+C in the terminal running `start.py`
- **THEN** the emulator subprocess is terminated
- **THEN** the visualizer HTTP server thread is stopped
- **THEN** the process exits cleanly with no hanging threads

### Requirement: Port conflict detection
`start.py` SHALL check whether ports 5000 and 8000 are already in use before starting any service, and SHALL exit with an actionable error message if either port is occupied.

#### Scenario: API port in use
- **WHEN** port 5000 is already bound by another process
- **WHEN** the user runs `python start.py --port COM2`
- **THEN** `start.py` prints an error identifying port 5000 as occupied
- **THEN** `start.py` exits without starting any services

#### Scenario: Visualizer port in use
- **WHEN** port 8000 is already bound by another process
- **WHEN** the user runs `python start.py --port COM2`
- **THEN** `start.py` prints an error identifying port 8000 as occupied
- **THEN** `start.py` exits without starting any services

### Requirement: Serial port is a required argument
`start.py` SHALL require `--port` as a mandatory CLI argument. It SHALL NOT hardcode any COM port value.

#### Scenario: Missing port argument
- **WHEN** the user runs `python start.py` without `--port`
- **THEN** `start.py` prints a usage error indicating `--port` is required
- **THEN** `start.py` exits with a non-zero exit code

#### Scenario: Valid port argument
- **WHEN** the user runs `python start.py --port COM3`
- **THEN** the emulator is started with `--port COM3`

### Requirement: Emulator subprocess failure detection
If the emulator subprocess exits unexpectedly within 3 seconds of launch, `start.py` SHALL detect this and print an error, then stop the visualizer server and exit.

#### Scenario: Bad COM port causes immediate exit
- **WHEN** the user specifies a non-existent COM port (e.g., `--port COM99`)
- **THEN** the emulator subprocess exits with an error
- **THEN** `start.py` detects the exit within 3 seconds
- **THEN** `start.py` prints the error output from the emulator
- **THEN** `start.py` stops all other services and exits

### Requirement: Optional configuration flags
`start.py` SHALL expose optional CLI flags for baud rate (`--baudrate`, default 115200), API port (`--api-port`, default 5000), visualizer port (`--visualizer-port`, default 8000), and flow control (`--rtscts`, `--dsrdtr`).

#### Scenario: Custom ports
- **WHEN** the user runs `python start.py --port COM2 --api-port 5001 --visualizer-port 8001`
- **THEN** the API server starts on port 5001
- **THEN** the visualizer HTTP server starts on port 8001
- **THEN** the console prints `Visualizer: http://localhost:8001/index.html`
