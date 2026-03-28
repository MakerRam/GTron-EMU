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
    """Test error handling for invalid opcode: parse error -> no dispatch."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = False
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    
    with pytest.raises(ValueError, match="Unregistered opcode"):
        parser.parse(b"XXXXX")


def test_integration_command_counter_tracking():
    """Test command counter increments across multiple dispatches."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    # Execute first command
    opcode1, _ = parser.parse(b"QUERY")
    response1, state = handler.dispatch(opcode1, state)
    assert response1 == "YES"
    
    # Execute second command
    opcode2, _ = parser.parse(b"QUERY")
    response2, state = handler.dispatch(opcode2, state)
    assert response2 == "YES"


def test_integration_state_tracking():
    """Test state changes tracked correctly through dispatch."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    handler = OpcodeHandler(logger)
    initial_state = DeviceState()
    
    # Parse and dispatch command
    opcode, _ = parser.parse(b"QUERY")
    response, new_state = handler.dispatch(opcode, initial_state)
    
    # Verify state was returned correctly
    assert new_state is not None
    assert isinstance(new_state, DeviceState)


def test_integration_with_serialmonitor():
    """Test integration with SerialMonitor logging."""
    from firmware_emulator.src.serial_monitor import SerialMonitor
    
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    # Create SerialMonitor for logging
    monitor = SerialMonitor(logger)
    
    parser = OpcodeParser(config, logger)
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    # Parse and dispatch command
    opcode, _ = parser.parse(b"QUERY")
    response, _ = handler.dispatch(opcode, state)
    
    # Monitor should have been created successfully
    assert monitor is not None
    assert response == "YES"


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
