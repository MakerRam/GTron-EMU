"""Tests for OpcodeHandler class - opcode dispatch and handler registry."""
import pytest
from unittest.mock import MagicMock

from firmware_emulator.src.opcode_handler import OpcodeHandler
from firmware_emulator.src.device_state import DeviceState, RunState


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


# --- Emulator Control Opcode Handlers ---

class TestEmulatorControlHandlers:
    """Test EMRUN, EMPAU, EMSTP, BZZOF opcode handlers."""

    def setup_method(self):
        self.logger = MagicMock()
        self.handler = OpcodeHandler(self.logger)
        self.state = DeviceState()

    def test_emrun_registered(self):
        """EMRUN handler is registered."""
        assert "EMRUN" in self.handler.list_handlers()

    def test_empau_registered(self):
        """EMPAU handler is registered."""
        assert "EMPAU" in self.handler.list_handlers()

    def test_emstp_registered(self):
        """EMSTP handler is registered."""
        assert "EMSTP" in self.handler.list_handlers()

    def test_bzzof_registered(self):
        """BZZOF handler is registered."""
        assert "BZZOF" in self.handler.list_handlers()

    def test_emrun_sets_running(self):
        """EMRUN sets run_state to RUNNING and returns EMROK."""
        response, new_state = self.handler.dispatch("EMRUN", self.state)
        assert response == "EMROK"
        assert new_state.run_state == RunState.RUNNING

    def test_empau_sets_paused(self):
        """EMPAU sets run_state to PAUSED and returns EMPOK."""
        self.state.run_state = RunState.RUNNING
        response, new_state = self.handler.dispatch("EMPAU", self.state)
        assert response == "EMPOK"
        assert new_state.run_state == RunState.PAUSED

    def test_emstp_sets_stopped(self):
        """EMSTP sets run_state to STOPPED and returns EMSOK."""
        self.state.run_state = RunState.RUNNING
        response, new_state = self.handler.dispatch("EMSTP", self.state)
        assert response == "EMSOK"
        assert new_state.run_state == RunState.STOPPED

    def test_bzzof_sets_buzzer_override(self):
        """BZZOF sets buzzer_override to True and returns BZZOK."""
        assert self.state.buzzer_override is False
        response, new_state = self.handler.dispatch("BZZOF", self.state)
        assert response == "BZZOK"
        assert new_state.buzzer_override is True

    def test_emrun_returns_new_state(self):
        """EMRUN returns a new state object (immutable pattern)."""
        response, new_state = self.handler.dispatch("EMRUN", self.state)
        assert new_state is not self.state

    def test_empau_returns_new_state(self):
        """EMPAU returns a new state object."""
        response, new_state = self.handler.dispatch("EMPAU", self.state)
        assert new_state is not self.state

    def test_emstp_returns_new_state(self):
        """EMSTP returns a new state object."""
        response, new_state = self.handler.dispatch("EMSTP", self.state)
        assert new_state is not self.state

    def test_bzzof_returns_new_state(self):
        """BZZOF returns a new state object."""
        response, new_state = self.handler.dispatch("BZZOF", self.state)
        assert new_state is not self.state

    def test_emrun_does_not_mutate_original(self):
        """EMRUN does not mutate the original state."""
        original_run_state = self.state.run_state
        self.handler.dispatch("EMRUN", self.state)
        assert self.state.run_state == original_run_state

    def test_bzzof_does_not_mutate_original(self):
        """BZZOF does not mutate the original state."""
        assert self.state.buzzer_override is False
        self.handler.dispatch("BZZOF", self.state)
        assert self.state.buzzer_override is False

    def test_full_run_pause_stop_cycle(self):
        """Test full lifecycle: STOPPED -> RUNNING -> PAUSED -> STOPPED."""
        assert self.state.run_state == RunState.STOPPED

        _, state2 = self.handler.dispatch("EMRUN", self.state)
        assert state2.run_state == RunState.RUNNING

        _, state3 = self.handler.dispatch("EMPAU", state2)
        assert state3.run_state == RunState.PAUSED

        _, state4 = self.handler.dispatch("EMSTP", state3)
        assert state4.run_state == RunState.STOPPED
