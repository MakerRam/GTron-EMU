"""Tests for OpcodeHandler class - opcode dispatch and handler registry."""
import pytest
from unittest.mock import MagicMock

from firmware_emulator.src.opcode_handler import OpcodeHandler, PARAM_OPCODES
from firmware_emulator.src.device_state import DeviceState, RunState, GuidePosition


def test_handler_init():
    """Test OpcodeHandler initialization."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    
    assert handler.handlers is not None
    assert len(handler.handlers) >= 2  # At least QUERY and many real opcodes


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


def test_handler_dispatch_doorc():
    """Test dispatching DOORC command (check door lock → responds DL1 when locked)."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    response, new_state = handler.dispatch("DOORC", state)
    
    assert response == "DL1"  # door_locked defaults to True
    assert new_state is state  # State unchanged (read-only check)


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
    """Test dispatch returns FLS for unknown opcode (matching real hardware)."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    response, new_state = handler.dispatch("XXXXX", state)
    assert response == "FLS"


def test_handler_list_handlers():
    """Test listing all registered handlers."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    
    handlers_list = handler.list_handlers()
    
    assert "QUERY" in handlers_list
    assert "DOORC" in handlers_list
    assert len(handlers_list) >= 2


def test_handler_built_in_query():
    """Test built-in QUERY handler."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    query_handler = handler.get_handler("QUERY")
    response, _ = query_handler(state)
    
    assert response == "YES"


def test_handler_built_in_doorc():
    """Test built-in DOORC handler checks door lock state."""
    logger = MagicMock()
    handler = OpcodeHandler(logger)
    state = DeviceState()
    
    doorc_handler = handler.get_handler("DOORC")
    response, new_state = doorc_handler(state)
    
    assert response == "DL1"  # door_locked defaults to True
    assert new_state is state


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
    response2, new_state = handler.dispatch("DOORC", state)
    
    assert response1 == "YES"
    assert response2 == "DL1"


# --- Push Button Press Response Handlers (Segment 4) ---

class TestPushButtonHandlers:
    """Test RUN, PAU, STP, BOF opcode handlers (Segment 4: Push Button Press Responses)."""

    def setup_method(self):
        self.logger = MagicMock()
        self.handler = OpcodeHandler(self.logger)
        self.state = DeviceState()

    def test_run_registered(self):
        """RUN handler is registered."""
        assert "RUN" in self.handler.list_handlers()

    def test_pau_registered(self):
        """PAU handler is registered."""
        assert "PAU" in self.handler.list_handlers()

    def test_stp_registered(self):
        """STP handler is registered."""
        assert "STP" in self.handler.list_handlers()

    def test_bof_registered(self):
        """BOF handler is registered."""
        assert "BOF" in self.handler.list_handlers()

    def test_run_sets_running(self):
        """RUN sets run_state to RUNNING and returns RUN."""
        response, new_state = self.handler.dispatch("RUN", self.state)
        assert response == "RUN"
        assert new_state.run_state == RunState.RUNNING

    def test_pau_sets_paused(self):
        """PAU sets run_state to PAUSED and returns PAU."""
        self.state.run_state = RunState.RUNNING
        response, new_state = self.handler.dispatch("PAU", self.state)
        assert response == "PAU"
        assert new_state.run_state == RunState.PAUSED

    def test_stp_sets_stopped(self):
        """STP sets run_state to STOPPED and returns STP."""
        self.state.run_state = RunState.RUNNING
        response, new_state = self.handler.dispatch("STP", self.state)
        assert response == "STP"
        assert new_state.run_state == RunState.STOPPED

    def test_bof_sets_buzzer_override(self):
        """BOF sets buzzer_override to True and returns BOF."""
        assert self.state.buzzer_override is False
        response, new_state = self.handler.dispatch("BOF", self.state)
        assert response == "BOF"
        assert new_state.buzzer_override is True

    def test_run_returns_new_state(self):
        """RUN returns a new state object (immutable pattern)."""
        response, new_state = self.handler.dispatch("RUN", self.state)
        assert new_state is not self.state

    def test_pau_returns_new_state(self):
        """PAU returns a new state object."""
        response, new_state = self.handler.dispatch("PAU", self.state)
        assert new_state is not self.state

    def test_stp_returns_new_state(self):
        """STP returns a new state object."""
        response, new_state = self.handler.dispatch("STP", self.state)
        assert new_state is not self.state

    def test_bof_returns_new_state(self):
        """BOF returns a new state object."""
        response, new_state = self.handler.dispatch("BOF", self.state)
        assert new_state is not self.state

    def test_run_does_not_mutate_original(self):
        """RUN does not mutate the original state."""
        original_run_state = self.state.run_state
        self.handler.dispatch("RUN", self.state)
        assert self.state.run_state == original_run_state

    def test_bof_does_not_mutate_original(self):
        """BOF does not mutate the original state."""
        assert self.state.buzzer_override is False
        self.handler.dispatch("BOF", self.state)
        assert self.state.buzzer_override is False

    def test_full_run_pause_stop_cycle(self):
        """Test full lifecycle: STOPPED -> RUNNING -> PAUSED -> STOPPED."""
        assert self.state.run_state == RunState.STOPPED

        _, state2 = self.handler.dispatch("RUN", self.state)
        assert state2.run_state == RunState.RUNNING

        _, state3 = self.handler.dispatch("PAU", state2)
        assert state3.run_state == RunState.PAUSED

        _, state4 = self.handler.dispatch("STP", state3)
        assert state4.run_state == RunState.STOPPED


# --- Parameter Opcode Handlers ---

class TestParamOpcodeHandlers:
    """Test opcodes that expect a second 5-byte parameter frame."""

    def setup_method(self):
        self.logger = MagicMock()
        self.handler = OpcodeHandler(self.logger)
        self.state = DeviceState()

    # -- PARAM_OPCODES set --

    def test_param_opcodes_contains_tpgdi(self):
        """TPGDI is listed as a parameter opcode."""
        assert "TPGDI" in PARAM_OPCODES

    def test_param_opcodes_contains_bmgdi(self):
        """BMGDI is listed as a parameter opcode."""
        assert "BMGDI" in PARAM_OPCODES

    def test_param_opcodes_contains_tprsp(self):
        """TPRSP is listed as a parameter opcode."""
        assert "TPRSP" in PARAM_OPCODES

    def test_param_opcodes_contains_spm01(self):
        """SPM01 is listed as a parameter opcode."""
        assert "SPM01" in PARAM_OPCODES

    def test_param_opcodes_contains_timing(self):
        """Timing config opcodes are all listed as parameter opcodes."""
        for op in ("LONDT", "CONDT", "COFDT", "LOFDT", "TLOND", "TCOND", "TCOFD", "TLOFD"):
            assert op in PARAM_OPCODES, f"{op} missing from PARAM_OPCODES"

    def test_is_param_opcode_true(self):
        """is_param_opcode returns True for known param opcodes."""
        assert self.handler.is_param_opcode("TPGDI") is True
        assert self.handler.is_param_opcode("tpgdi") is True  # Case insensitive

    def test_is_param_opcode_false(self):
        """is_param_opcode returns False for non-param opcodes."""
        assert self.handler.is_param_opcode("QUERY") is False
        assert self.handler.is_param_opcode("RUN") is False

    # -- TPGDI / BMGDI: Guide close --

    def test_tpgdi_no_param_sets_guide_closed(self):
        """TPGDI without param still sets guide_top to CLOSED."""
        self.state.guide_top.position = GuidePosition.OPEN
        response, new_state = self.handler.dispatch("TPGDI", self.state)
        assert response == ""
        assert new_state.guide_top.position == GuidePosition.CLOSED

    def test_tpgdi_with_param_sets_guide_closed(self):
        """TPGDI with param (step count) sets guide_top to CLOSED."""
        self.state.guide_top.position = GuidePosition.OPEN
        response, new_state = self.handler.dispatch_with_param("TPGDI", self.state, "5000")
        assert response == ""
        assert new_state.guide_top.position == GuidePosition.CLOSED

    def test_bmgdi_with_param_sets_guide_closed(self):
        """BMGDI with param (step count) sets guide_bottom to CLOSED."""
        self.state.guide_bottom.position = GuidePosition.OPEN
        response, new_state = self.handler.dispatch_with_param("BMGDI", self.state, "5000")
        assert response == ""
        assert new_state.guide_bottom.position == GuidePosition.CLOSED

    def test_tpgdi_does_not_mutate_original(self):
        """TPGDI returns a new state; original is unmodified."""
        self.state.guide_top.position = GuidePosition.OPEN
        _, new_state = self.handler.dispatch_with_param("TPGDI", self.state, "5000")
        assert self.state.guide_top.position == GuidePosition.OPEN
        assert new_state is not self.state

    # -- TPRSP / BMRSP: Reeler speed --

    def test_tprsp_with_param_sets_speed(self):
        """TPRSP with param stores RPM in reeler_top.speed."""
        response, new_state = self.handler.dispatch_with_param("TPRSP", self.state, "200")
        assert response == ""
        assert new_state.reeler_top.speed == 200

    def test_bmrsp_with_param_sets_speed(self):
        """BMRSP with param stores RPM in reeler_bottom.speed."""
        response, new_state = self.handler.dispatch_with_param("BMRSP", self.state, "200")
        assert response == ""
        assert new_state.reeler_bottom.speed == 200

    def test_tprsp_no_param_is_noop(self):
        """TPRSP without param doesn't change state."""
        original_speed = self.state.reeler_top.speed
        response, new_state = self.handler.dispatch("TPRSP", self.state)
        assert response == ""
        assert new_state.reeler_top.speed == original_speed

    def test_tprsp_malformed_param_ignored(self):
        """TPRSP with non-numeric param is handled gracefully."""
        response, new_state = self.handler.dispatch_with_param("TPRSP", self.state, "abc")
        assert response == ""
        # Speed should be unchanged
        assert new_state.reeler_top.speed == self.state.reeler_top.speed

    # -- SPM01 / SPM02: SPM delay --

    def test_spm01_with_param_sets_delay(self):
        """SPM01 with param stores microseconds in spm_delay_top."""
        response, new_state = self.handler.dispatch_with_param("SPM01", self.state, "3000")
        assert response == ""
        assert new_state.spm_delay_top == 3000

    def test_spm02_with_param_sets_delay(self):
        """SPM02 with param stores microseconds in spm_delay_bottom."""
        response, new_state = self.handler.dispatch_with_param("SPM02", self.state, "3000")
        assert response == ""
        assert new_state.spm_delay_bottom == 3000

    # -- No-op param opcodes --

    def test_rmsmf_registered(self):
        """RMSMF handler is registered."""
        assert "RMSMF" in self.handler.list_handlers()

    def test_rmsmf_no_response(self):
        """RMSMF returns empty response (no-op)."""
        response, new_state = self.handler.dispatch("RMSMF", self.state)
        assert response == ""

    def test_sktrg_no_response(self):
        """SKTRG returns empty response (no-op)."""
        response, new_state = self.handler.dispatch("SKTRG", self.state)
        assert response == ""

    def test_tpina_no_response(self):
        """TPINA returns empty response (no-op)."""
        response, new_state = self.handler.dispatch("TPINA", self.state)
        assert response == ""

    def test_tprth_no_response(self):
        """TPRTH returns empty response (no-op)."""
        response, new_state = self.handler.dispatch("TPRTH", self.state)
        assert response == ""

    # -- Timing config opcodes (Segment 19) --

    def test_timing_opcodes_registered(self):
        """All 8 timing config opcodes are registered."""
        handlers = self.handler.list_handlers()
        for op in ("LONDT", "CONDT", "COFDT", "LOFDT", "TLOND", "TCOND", "TCOFD", "TLOFD"):
            assert op in handlers, f"{op} not registered"

    def test_timing_opcodes_return_empty(self):
        """Timing config opcodes return empty string (no response)."""
        for op in ("LONDT", "CONDT", "COFDT", "LOFDT", "TLOND", "TCOND", "TCOFD", "TLOFD"):
            response, _ = self.handler.dispatch(op, self.state)
            assert response == "", f"{op} returned {response!r}, expected empty"

    # -- dispatch_with_param fallback --

    def test_dispatch_with_param_falls_back_to_dispatch(self):
        """dispatch_with_param for non-param opcode falls back to normal dispatch."""
        response, new_state = self.handler.dispatch_with_param("QUERY", self.state, "ignored")
        assert response == "YES"
