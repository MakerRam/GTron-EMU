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


def test_handler_handler_signature():
    """Test handler function signature: (state) -> (response, state)."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    query_handler = handler.get_handler("QUERY")
    result = query_handler(state)
    
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], DeviceState)


def test_handler_state_immutability():
    """Test handlers return new state, don't mutate original."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    original_state = state
    response, new_state = handler.dispatch("QUERY", state)
    
    assert new_state is original_state  # Same object (immutable in Phase 1)


def test_handler_error_handling():
    """Test error handling when handler raises exception."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    def error_handler(s):
        raise RuntimeError("Handler error")
    
    handler.register("ERROR", error_handler)
    
    with pytest.raises(RuntimeError):
        handler.dispatch("ERROR", state)


def test_handler_multiple_dispatch():
    """Test dispatching multiple different opcodes."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    response1, _ = handler.dispatch("QUERY", state)
    response2, _ = handler.dispatch("STATUS", state)
    
    assert response1 == "YES"
    assert response2 == "OK"
