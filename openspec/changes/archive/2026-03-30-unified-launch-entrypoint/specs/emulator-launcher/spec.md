## MODIFIED Requirements

### Requirement: Primary entry point
The emulator-launcher (`emulator_launcher.py`) SHALL be retained as an optional advanced GUI entry point. It SHALL NOT be the primary documented method for starting the system. The Quick Start section of `README.md` SHALL reference `start.py` as the primary entry point.

#### Scenario: Launcher still functional
- **WHEN** the user runs `python emulator_launcher.py`
- **THEN** the GUI launches and all existing functionality works unchanged

#### Scenario: README updated
- **WHEN** a user reads the README Quick Start section
- **THEN** the first instruction is `python start.py --port <COM_PORT>`
- **THEN** `emulator_launcher.py` is mentioned under an "Advanced / GUI" section
