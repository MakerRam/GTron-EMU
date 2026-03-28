# Group 3: Opcode Parser Framework Implementation Plan

> **For agentic workers:** REQUIRED: Use @subagent-driven-development (with parallel worktrees) to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking. Three independent tasks can execute in parallel via separate worktrees.

**Goal:** Implement a flexible opcode parsing and dispatch framework that routes 5-byte ASCII commands to appropriate handlers, with full command logging and state tracking.

**Architecture:** 
- OpcodeParser class validates and parses 5-byte ASCII commands into opcode + optional parameters
- OpcodeHandler class manages a registry of 75+ opcode handlers and dispatches parsed commands
- Each handler is a simple function that receives DeviceState and returns (response, new_state)
- Integration with SerialMonitor for command/response logging
- Full error handling for invalid opcodes and malformed commands

**Tech Stack:** Python 3.12.3, pyserial 3.5, logging module, MachineConfig (existing)

---

## File Structure & Responsibilities

```
firmware_emulator/
├── src/
│   ├── opcode_parser.py           [NEW] Parse 5-byte ASCII commands into opcode + params
│   │   └─ OpcodeParser class: parse(), validate(), extract_params()
│   │
│   ├── opcode_handler.py          [MODIFY] Dispatch parsed commands to handlers
│   │   └─ OpcodeHandler class: register(), dispatch(), get_handler()
│   │   └─ Handler registry: dict mapping opcode -> handler function
│   │   └─ Built-in handlers for basic opcodes (QUERY, STATUS, etc.)
│   │
│   ├── __init__.py                [MODIFY] Export new classes
│   │
│   └── main.py                    [EXISTING] Entry point (already complete)
│
└── tests/
    ├── test_opcode_parser.py      [NEW] Unit tests for OpcodeParser
    │   └─ 12+ test cases: valid parsing, invalid opcodes, edge cases
    │
    ├── test_opcode_handler.py     [NEW] Unit tests for OpcodeHandler
    │   └─ 15+ test cases: registration, dispatch, error handling
    │
    └── test_opcode_integration.py [NEW] Integration tests
        └─ 8+ test cases: parser + handler together with real handlers
```

---

## Chunk 1: OpcodeParser Class & Tests (2 tasks)

### Task 1: Create test file for OpcodeParser

**Files:**
- Create: `firmware_emulator/tests/test_opcode_parser.py`
- Reference: `firmware_emulator/src/config_parser.py` (understand MachineConfig)
- Reference: `docs/superpowers/plans/2026-03-28-group-0.5-serial-monitor.md` (understand protocol)

- [ ] **Step 1: Write failing tests for OpcodeParser class**

```python
"""Tests for OpcodeParser class - 5-byte ASCII command parsing."""
import pytest
from unittest.mock import MagicMock

# Will import after implementation
# from firmware_emulator import OpcodeParser


def test_parser_init():
    """Test OpcodeParser initialization with MachineConfig."""
    pass


def test_parser_valid_command_5_bytes():
    """Test parsing valid 5-byte ASCII command (e.g., 'QUERY' -> opcode='QUERY', params=None)."""
    pass


def test_parser_command_with_numeric_params():
    """Test parsing command with numeric parameters (e.g., 'tpGOP' might have encoded params)."""
    pass


def test_parser_invalid_command_too_short():
    """Test parsing fails for commands less than 5 bytes."""
    pass


def test_parser_invalid_command_too_long():
    """Test parsing fails for commands more than 5 bytes."""
    pass


def test_parser_invalid_opcode_not_registered():
    """Test parsing fails for opcode not in MachineConfig.opcodes."""
    pass


def test_parser_nonprintable_bytes():
    """Test parsing handles non-printable ASCII bytes gracefully."""
    pass


def test_parser_case_sensitivity():
    """Test parsing is case-sensitive (QUERY != query)."""
    pass


def test_parser_extract_params_no_params():
    """Test extracting params when command has no parameters."""
    pass


def test_parser_extract_params_with_encoding():
    """Test extracting params from encoded command format."""
    pass


def test_parser_validate_opcode():
    """Test validate_opcode() returns True for registered opcodes."""
    pass


def test_parser_validate_opcode_invalid():
    """Test validate_opcode() returns False for unregistered opcodes."""
    pass
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /mnt/d/TDD/Emulator
python3 -m pytest firmware_emulator/tests/test_opcode_parser.py -v
```

Expected: All tests FAIL with "OpcodeParser not defined"

---

### Task 2: Implement OpcodeParser class

**Files:**
- Create: `firmware_emulator/src/opcode_parser.py`
- Modify: `firmware_emulator/src/__init__.py` (export OpcodeParser)
- Reference: `firmware_emulator/src/config_parser.py` (understand MachineConfig structure)
- Reference: `firmware_emulator/src/device_state.py` (understand DeviceState)

- [ ] **Step 1: Write OpcodeParser class stub**

```python
"""5-byte ASCII opcode parsing and validation."""
import logging
from typing import Optional, Tuple, Any
from firmware_emulator.src.config_parser import MachineConfig


class OpcodeParser:
    """Parse 5-byte ASCII commands into opcode and optional parameters."""
    
    def __init__(self, config: MachineConfig, logger: logging.Logger):
        """
        Initialize OpcodeParser.
        
        Args:
            config: MachineConfig instance with registered opcodes
            logger: logging.Logger instance
        """
        self.config = config
        self.logger = logger
    
    def parse(self, data: bytes) -> Tuple[str, Optional[Any]]:
        """
        Parse 5-byte ASCII command into opcode and optional parameters.
        
        Format: 5 bytes total
        - Bytes 0-4: Opcode (5-char ASCII string, e.g., 'QUERY', 'tpGOP')
        - If opcode has parameters, they may be encoded in bytes 0-4
        
        Args:
            data: Raw 5 bytes from serial port
        
        Returns:
            Tuple (opcode, params) where params is None if no parameters
        
        Raises:
            ValueError: If command is not 5 bytes, not ASCII, or opcode not registered
        """
        # Validate data
        if len(data) != 5:
            raise ValueError(f"Command must be 5 bytes, got {len(data)}")
        
        # Convert to ASCII string
        try:
            command_str = data.decode('ascii')
        except UnicodeDecodeError as e:
            raise ValueError(f"Command contains non-ASCII bytes: {data.hex()}") from e
        
        # Extract opcode (first 5 chars, or validate against registered opcodes)
        opcode = command_str.strip()  # Remove any trailing spaces
        
        # Validate opcode is registered
        if not self.validate_opcode(opcode):
            raise ValueError(f"Unregistered opcode: {opcode}")
        
        # Extract parameters (if any)
        params = self.extract_params(command_str)
        
        return opcode, params
    
    def validate_opcode(self, opcode: str) -> bool:
        """
        Validate that opcode is registered in MachineConfig.
        
        Args:
            opcode: Opcode string (e.g., 'QUERY', 'tpGOP')
        
        Returns:
            True if opcode is registered, False otherwise
        """
        return self.config.is_valid_opcode(opcode)
    
    @staticmethod
    def extract_params(command_str: str) -> Optional[Any]:
        """
        Extract parameters from command string.
        
        Phase 1: No parameters (return None for all commands)
        Phase 2: Support parameter encoding in specific opcodes
        
        Args:
            command_str: 5-character command string
        
        Returns:
            None (Phase 1 stub)
        """
        # Phase 1: No parameter parsing
        # Phase 2: Add support for encoded parameters in specific opcodes
        return None
```

- [ ] **Step 2: Implement actual test logic**

```python
"""Tests for OpcodeParser class - 5-byte ASCII command parsing."""
import pytest
from unittest.mock import MagicMock

from firmware_emulator.src.opcode_parser import OpcodeParser
from firmware_emulator.src.config_parser import MachineConfig


def test_parser_init():
    """Test OpcodeParser initialization with MachineConfig."""
    config = MagicMock(spec=MachineConfig)
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    assert parser.config is config
    assert parser.logger is logger


def test_parser_valid_command_5_bytes():
    """Test parsing valid 5-byte ASCII command."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    data = b"QUERY"
    opcode, params = parser.parse(data)
    
    assert opcode == "QUERY"
    assert params is None


def test_parser_invalid_command_too_short():
    """Test parsing fails for commands less than 5 bytes."""
    config = MagicMock(spec=MachineConfig)
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    with pytest.raises(ValueError, match="must be 5 bytes"):
        parser.parse(b"QUIT")


def test_parser_invalid_command_too_long():
    """Test parsing fails for commands more than 5 bytes."""
    config = MagicMock(spec=MachineConfig)
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    with pytest.raises(ValueError, match="must be 5 bytes"):
        parser.parse(b"QUERIES")


def test_parser_invalid_opcode_not_registered():
    """Test parsing fails for opcode not in MachineConfig."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = False
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    with pytest.raises(ValueError, match="Unregistered opcode"):
        parser.parse(b"XXXXX")


def test_parser_nonprintable_bytes():
    """Test parsing handles non-printable ASCII bytes gracefully."""
    config = MagicMock(spec=MachineConfig)
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    data = bytes([0x00, 0x51, 0xFF, 0x45, 0x52])  # Non-ASCII bytes
    
    with pytest.raises(ValueError, match="non-ASCII"):
        parser.parse(data)


def test_parser_case_sensitivity():
    """Test parsing is case-sensitive."""
    config = MagicMock(spec=MachineConfig)
    
    def is_valid(opcode):
        return opcode == "QUERY"  # Only uppercase QUERY
    
    config.is_valid_opcode.side_effect = is_valid
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    # Lowercase should fail
    with pytest.raises(ValueError, match="Unregistered opcode"):
        parser.parse(b"query")


def test_parser_validate_opcode():
    """Test validate_opcode() returns True for registered opcodes."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    assert parser.validate_opcode("QUERY") is True


def test_parser_validate_opcode_invalid():
    """Test validate_opcode() returns False for unregistered opcodes."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = False
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    assert parser.validate_opcode("XXXXX") is False


def test_parser_extract_params_no_params():
    """Test extracting params when command has no parameters."""
    command_str = "QUERY"
    params = OpcodeParser.extract_params(command_str)
    
    assert params is None
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
cd /mnt/d/TDD/Emulator
python3 -m pytest firmware_emulator/tests/test_opcode_parser.py -v
```

Expected: All tests PASS ✓

- [ ] **Step 4: Update __init__.py to export OpcodeParser**

```python
# In firmware_emulator/src/__init__.py, add:
from .opcode_parser import OpcodeParser

__all__ = [
    'OpcodeParser',
    'SerialMonitor',
    'DebugBreakpoint',
    'InteractiveMonitor',
    'MachineConfig',
    'DeviceState',
    'get_logger',
    # ... existing exports
]
```

- [ ] **Step 5: Commit Task 1-2**

```bash
cd /mnt/d/TDD/Emulator
git add firmware_emulator/src/opcode_parser.py \
        firmware_emulator/src/__init__.py \
        firmware_emulator/tests/test_opcode_parser.py
git commit -m "feat(3.1-3.2): implement OpcodeParser with 5-byte ASCII parsing and validation"
```

---

## Chunk 2: OpcodeHandler Class & Tests (2 tasks)

### Task 3: Create test file for OpcodeHandler

**Files:**
- Create: `firmware_emulator/tests/test_opcode_handler.py`

- [ ] **Step 1: Write failing tests for OpcodeHandler class**

```python
"""Tests for OpcodeHandler class - opcode dispatch and handler registry."""
import pytest
from unittest.mock import MagicMock

# Will import after implementation
# from firmware_emulator import OpcodeHandler


def test_handler_init():
    """Test OpcodeHandler initialization."""
    pass


def test_handler_register_handler():
    """Test registering a handler for an opcode."""
    pass


def test_handler_get_handler():
    """Test retrieving a registered handler."""
    pass


def test_handler_get_handler_not_found():
    """Test get_handler raises KeyError for unregistered opcode."""
    pass


def test_handler_dispatch_query():
    """Test dispatching QUERY command (always returns 'YES')."""
    pass


def test_handler_dispatch_status():
    """Test dispatching STATUS command (returns device status)."""
    pass


def test_handler_dispatch_with_state_change():
    """Test handler that modifies state."""
    pass


def test_handler_dispatch_invalid_opcode():
    """Test dispatch raises error for invalid opcode."""
    pass


def test_handler_list_handlers():
    """Test listing all registered handlers."""
    pass


def test_handler_built_in_query():
    """Test built-in QUERY handler."""
    pass


def test_handler_built_in_status():
    """Test built-in STATUS handler returns device status."""
    pass


def test_handler_handler_signature():
    """Test handler function signature: (state) -> (response, state)."""
    pass


def test_handler_state_immutability():
    """Test handlers return new state, don't mutate original."""
    pass


def test_handler_error_handling():
    """Test error handling when handler raises exception."""
    pass


def test_handler_dispatch_multiple():
    """Test dispatching multiple different opcodes."""
    pass
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /mnt/d/TDD/Emulator
python3 -m pytest firmware_emulator/tests/test_opcode_handler.py -v
```

Expected: All tests FAIL with "OpcodeHandler not defined"

---

### Task 4: Implement OpcodeHandler class

**Files:**
- Create: `firmware_emulator/src/opcode_handler.py`
- Modify: `firmware_emulator/src/__init__.py` (export OpcodeHandler)
- Reference: `firmware_emulator/src/device_state.py` (understand DeviceState)

- [ ] **Step 1: Write OpcodeHandler class stub**

```python
"""Opcode handler registry and dispatch mechanism."""
import logging
from typing import Callable, Dict, Tuple, Optional, Any
from firmware_emulator.src.device_state import DeviceState


# Handler function signature: (state) -> (response, new_state)
HandlerFunc = Callable[[DeviceState], Tuple[str, DeviceState]]


class OpcodeHandler:
    """
    Registry and dispatcher for opcode handlers.
    
    Each opcode maps to a handler function with signature:
        handler(state: DeviceState) -> (response: str, new_state: DeviceState)
    
    Handlers are stateless - they receive immutable state and return new state.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize OpcodeHandler with logger.
        
        Args:
            logger: logging.Logger instance
        """
        self.logger = logger
        self.handlers: Dict[str, HandlerFunc] = {}
        
        # Register built-in handlers
        self._register_builtin_handlers()
    
    def register(self, opcode: str, handler: HandlerFunc) -> None:
        """
        Register a handler for an opcode.
        
        Args:
            opcode: Opcode string (e.g., 'QUERY', 'tpGOP')
            handler: Handler function with signature (state) -> (response, new_state)
        """
        self.handlers[opcode] = handler
        self.logger.info(f"Handler registered for opcode: {opcode}")
    
    def get_handler(self, opcode: str) -> HandlerFunc:
        """
        Retrieve a handler for an opcode.
        
        Args:
            opcode: Opcode string
        
        Returns:
            Handler function
        
        Raises:
            KeyError: If opcode has no registered handler
        """
        if opcode not in self.handlers:
            raise KeyError(f"No handler registered for opcode: {opcode}")
        return self.handlers[opcode]
    
    def dispatch(self, opcode: str, state: DeviceState) -> Tuple[str, DeviceState]:
        """
        Dispatch opcode to appropriate handler.
        
        Args:
            opcode: Opcode string
            state: Current DeviceState
        
        Returns:
            Tuple (response, new_state)
        
        Raises:
            KeyError: If opcode has no registered handler
        """
        handler = self.get_handler(opcode)
        response, new_state = handler(state)
        return response, new_state
    
    def list_handlers(self) -> list:
        """
        List all registered opcode handlers.
        
        Returns:
            List of registered opcode strings
        """
        return sorted(self.handlers.keys())
    
    def _register_builtin_handlers(self) -> None:
        """Register built-in handlers for common opcodes."""
        # QUERY: Always returns "YES"
        def handle_query(state: DeviceState) -> Tuple[str, DeviceState]:
            return "YES", state
        
        self.register("QUERY", handle_query)
        
        # STATUS: Returns device status (Phase 1: simplified version)
        def handle_status(state: DeviceState) -> Tuple[str, DeviceState]:
            # Phase 1: Return simple status
            # Phase 2: Return detailed device status based on current state
            return "OK", state
        
        self.register("STATUS", handle_status)
```

- [ ] **Step 2: Implement actual test logic**

```python
"""Tests for OpcodeHandler class - opcode dispatch and handler registry."""
import pytest
from unittest.mock import MagicMock

from firmware_emulator.src.opcode_handler import OpcodeHandler
from firmware_emulator.src.device_state import DeviceState


def test_handler_init():
    """Test OpcodeHandler initialization."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    
    assert handler.handlers is not None
    assert len(handler.handlers) >= 2  # At least QUERY and STATUS


def test_handler_register_handler():
    """Test registering a handler for an opcode."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    
    def dummy_handler(state):
        return "RESPONSE", state
    
    handler.register("CUSTOM", dummy_handler)
    
    assert "CUSTOM" in handler.handlers
    assert handler.handlers["CUSTOM"] is dummy_handler


def test_handler_get_handler():
    """Test retrieving a registered handler."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    
    retrieved = handler.get_handler("QUERY")
    
    assert retrieved is not None
    assert callable(retrieved)


def test_handler_get_handler_not_found():
    """Test get_handler raises KeyError for unregistered opcode."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    
    with pytest.raises(KeyError, match="No handler"):
        handler.get_handler("XXXXX")


def test_handler_dispatch_query():
    """Test dispatching QUERY command (always returns 'YES')."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    response, new_state = handler.dispatch("QUERY", state)
    
    assert response == "YES"
    assert new_state is state  # State unchanged


def test_handler_dispatch_status():
    """Test dispatching STATUS command (returns device status)."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    response, new_state = handler.dispatch("STATUS", state)
    
    assert response == "OK"
    assert new_state is state


def test_handler_dispatch_with_state_change():
    """Test handler that modifies state."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    def state_changing_handler(s):
        # Return modified state (immutable pattern)
        new_state = s
        return "CHANGED", new_state
    
    handler.register("MODIFY", state_changing_handler)
    response, new_state = handler.dispatch("MODIFY", state)
    
    assert response == "CHANGED"


def test_handler_dispatch_invalid_opcode():
    """Test dispatch raises error for invalid opcode."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    with pytest.raises(KeyError):
        handler.dispatch("XXXXX", state)


def test_handler_list_handlers():
    """Test listing all registered handlers."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    
    handlers_list = handler.list_handlers()
    
    assert "QUERY" in handlers_list
    assert "STATUS" in handlers_list
    assert len(handlers_list) >= 2


def test_handler_built_in_query():
    """Test built-in QUERY handler."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    query_handler = handler.get_handler("QUERY")
    response, _ = query_handler(state)
    
    assert response == "YES"


def test_handler_built_in_status():
    """Test built-in STATUS handler returns device status."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    status_handler = handler.get_handler("STATUS")
    response, _ = status_handler(state)
    
    assert response == "OK"


def test_handler_multiple_dispatch():
    """Test dispatching multiple different opcodes."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    response1, _ = handler.dispatch("QUERY", state)
    response2, _ = handler.dispatch("STATUS", state)
    
    assert response1 == "YES"
    assert response2 == "OK"
```

- [ ] **Step 3: Run tests to verify they pass**

```bash
cd /mnt/d/TDD/Emulator
python3 -m pytest firmware_emulator/tests/test_opcode_handler.py -v
```

Expected: All tests PASS ✓

- [ ] **Step 4: Update __init__.py to export OpcodeHandler**

```python
# In firmware_emulator/src/__init__.py, add:
from .opcode_handler import OpcodeHandler

__all__ = [
    'OpcodeParser',
    'OpcodeHandler',
    'SerialMonitor',
    'DebugBreakpoint',
    'InteractiveMonitor',
    'MachineConfig',
    'DeviceState',
    'get_logger',
    # ... existing exports
]
```

- [ ] **Step 5: Commit Task 3-4**

```bash
cd /mnt/d/TDD/Emulator
git add firmware_emulator/src/opcode_handler.py \
        firmware_emulator/src/__init__.py \
        firmware_emulator/tests/test_opcode_handler.py
git commit -m "feat(3.3-3.4): implement OpcodeHandler with dispatch mechanism and built-in handlers"
```

---

## Chunk 3: Integration & Testing (2 tasks)

### Task 5: Create integration test file

**Files:**
- Create: `firmware_emulator/tests/test_opcode_integration.py`

- [ ] **Step 1: Write failing integration tests**

```python
"""Integration tests for OpcodeParser + OpcodeHandler."""
import pytest
from unittest.mock import MagicMock

# Will import after implementation
# from firmware_emulator import OpcodeParser, OpcodeHandler


def test_integration_parse_and_dispatch():
    """Test parsing command then dispatching to handler."""
    pass


def test_integration_query_command():
    """Test complete QUERY command: parse -> dispatch -> response."""
    pass


def test_integration_status_command():
    """Test complete STATUS command: parse -> dispatch -> response."""
    pass


def test_integration_invalid_opcode_error():
    """Test error handling for invalid opcode: parse error -> no dispatch."""
    pass


def test_integration_command_counter_tracking():
    """Test command counter increments across multiple dispatches."""
    pass


def test_integration_state_tracking():
    """Test state changes tracked correctly through dispatch."""
    pass


def test_integration_with_serialmonitor():
    """Test integration with SerialMonitor logging."""
    pass


def test_integration_multiple_commands():
    """Test handling multiple commands in sequence."""
    pass
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /mnt/d/TDD/Emulator
python3 -m pytest firmware_emulator/tests/test_opcode_integration.py -v
```

Expected: Tests FAIL with import/missing implementation errors

---

### Task 6: Implement integration and fix any issues

**Files:**
- Modify: `firmware_emulator/tests/test_opcode_integration.py` (implement test logic)
- Reference: `firmware_emulator/src/opcode_parser.py`
- Reference: `firmware_emulator/src/opcode_handler.py`
- Reference: `firmware_emulator/src/device_state.py`

- [ ] **Step 1: Implement full test logic**

```python
"""Integration tests for OpcodeParser + OpcodeHandler."""
import pytest
from unittest.mock import MagicMock

from firmware_emulator.src.opcode_parser import OpcodeParser
from firmware_emulator.src.opcode_handler import OpcodeHandler
from firmware_emulator.src.device_state import DeviceState
from firmware_emulator.src.config_parser import MachineConfig


def test_integration_parse_and_dispatch():
    """Test parsing command then dispatching to handler."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    # Parse command
    opcode, params = parser.parse(b"QUERY")
    
    # Dispatch to handler
    response, new_state = handler.dispatch(opcode, state)
    
    assert opcode == "QUERY"
    assert response == "YES"
    assert new_state is state


def test_integration_query_command():
    """Test complete QUERY command workflow."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    # Simulate QUERY command
    data = b"QUERY"
    opcode, _ = parser.parse(data)
    response, _ = handler.dispatch(opcode, state)
    
    assert response == "YES"


def test_integration_status_command():
    """Test complete STATUS command workflow."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    # Simulate STATUS command
    data = b"STATU"  # 5 bytes
    opcode, _ = parser.parse(data)
    
    # Register STATUS handler
    def status_handler(s):
        return "OK", s
    
    handler.register("STATU", status_handler)
    response, _ = handler.dispatch(opcode, state)
    
    assert response == "OK"


def test_integration_invalid_opcode_error():
    """Test error handling for invalid opcode."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = False
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    with pytest.raises(ValueError, match="Unregistered opcode"):
        parser.parse(b"XXXXX")


def test_integration_multiple_commands():
    """Test handling multiple commands in sequence."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    # Send QUERY
    opcode1, _ = parser.parse(b"QUERY")
    response1, state = handler.dispatch(opcode1, state)
    assert response1 == "YES"
    
    # Send STATUS
    opcode2, _ = parser.parse(b"STATU")
    handler.register("STATU", lambda s: ("OK", s))
    response2, state = handler.dispatch(opcode2, state)
    assert response2 == "OK"
```

- [ ] **Step 2: Run tests to verify they pass**

```bash
cd /mnt/d/TDD/Emulator
python3 -m pytest firmware_emulator/tests/test_opcode_parser.py \
                   firmware_emulator/tests/test_opcode_handler.py \
                   firmware_emulator/tests/test_opcode_integration.py -v
```

Expected: ALL TESTS PASS ✓ (30+ total)

- [ ] **Step 3: Commit Task 5-6**

```bash
cd /mnt/d/TDD/Emulator
git add firmware_emulator/tests/test_opcode_integration.py
git commit -m "feat(3.5-3.6): implement integration tests for parser + handler"
```

---

## Summary

**Group 3: Opcode Parser Framework**
- **Tasks**: 6 (3 pairs of test + implementation)
- **Files Created**: 5
  - `src/opcode_parser.py` (70 lines)
  - `src/opcode_handler.py` (95 lines)
  - `tests/test_opcode_parser.py` (120 lines, 12+ tests)
  - `tests/test_opcode_handler.py` (135 lines, 15+ tests)
  - `tests/test_opcode_integration.py` (100 lines, 8+ tests)
- **Files Modified**: 1
  - `src/__init__.py` (add 2 exports)
- **Tests**: 35+
- **Commits**: 3 (one per task pair)
- **Estimated Time**: 6 hours
- **After Completion**: 26/110 tasks complete (23.6%), ready for Groups 4-8 (Command Handlers)

---

## Next: Groups 4-8 - Command Handlers (43 tasks)

Groups 4-8 implement handlers for all 75+ opcodes organized by category:
- Group 4: Device State Query Handlers (tpQUY, tpGUR, etc.) - 8 tasks
- Group 5: Guide Motor Handlers (tpGOP, tpGCL, tpGED, etc.) - 9 tasks
- Group 6: Reeler Motor Handlers (tpRTR, tpRSP, tpRTH, etc.) - 8 tasks
- Group 7: Sensor/Encoder Handlers (tpSEN, tpENC, etc.) - 9 tasks
- Group 8: Light/Camera Handlers (tpLMP, tpCAM, etc.) - 9 tasks

Each handler follows the same pattern:
1. Test file with test cases for valid inputs + edge cases
2. Implementation with state changes + response formatting
3. Integration with existing parser + handler registry
4. Single commit per handler group

---

## Phase 2 Integration Points

- **Group 3 provides**: Clean interface for routing commands to handlers
- **Groups 4-8 provide**: Actual opcode implementations with state changes
- **Phase 2 adds**: ISR-driven triggers, real sensor simulation, multi-rack support
- **No breaking changes**: All Phase 1 interfaces remain stable in Phase 2
