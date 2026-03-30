## ADDED Requirements

### Requirement: Expose virtual COM port to LabVIEW
The emulator SHALL create a virtual serial port that LabVIEW can connect to using standard Windows COM port APIs.

#### Scenario: LabVIEW discovers virtual port
- **WHEN** com0com driver is installed and emulator is running
- **THEN** Windows Device Manager lists a virtual COM port (e.g., COM99 pair) available for connection

#### Scenario: LabVIEW establishes serial connection
- **WHEN** LabVIEW opens COM port at 9600 baud, 8 data bits, no parity, 1 stop bit
- **THEN** connection succeeds and LabVIEW can send/receive bytes

### Requirement: Route commands from virtual port to emulator
The emulator SHALL read commands from the virtual COM port and dispatch them to the firmware API handlers.

#### Scenario: Command received and parsed
- **WHEN** LabVIEW writes 5 bytes to the virtual COM port
- **THEN** emulator reads those bytes, parses the opcode, and dispatches to the handler

#### Scenario: Response written back to port
- **WHEN** handler completes and generates a response
- **THEN** emulator writes the response bytes back to the virtual COM port where LabVIEW reads them

### Requirement: Support 9600 baud serial communication
The emulator SHALL maintain serial communication at 9600 baud to match firmware specification.

#### Scenario: Correct baud rate
- **WHEN** connection is established at 9600 baud
- **THEN** communication is stable with no transmission errors

#### Scenario: Baud rate mismatch detection
- **WHEN** LabVIEW connects at incorrect baud rate (e.g., 115200)
- **THEN** communication fails or becomes garbled (expected behavior—user misconfiguration)

### Requirement: Handle serial timeouts gracefully
The emulator SHALL handle cases where LabVIEW doesn't respond or command isn't completed within reasonable time.

#### Scenario: Command timeout
- **WHEN** partial command received and no new bytes for > 5 seconds
- **THEN** emulator discards the partial buffer and waits for new command

### Requirement: Buffer management
The emulator SHALL properly manage serial read/write buffers to prevent overflow or data loss.

#### Scenario: Multiple commands in sequence
- **WHEN** LabVIEW sends 10 consecutive 5-byte commands
- **THEN** all commands are parsed correctly and all responses are sent back in order
