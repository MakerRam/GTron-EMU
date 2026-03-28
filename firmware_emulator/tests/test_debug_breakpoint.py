"""Tests for debug breakpoint infrastructure."""
import logging
from unittest.mock import MagicMock

from firmware_emulator.src.debug_breakpoint import DebugBreakpoint


def test_breakpoint_register():
    """Test registering a breakpoint on an opcode."""
    logger = MagicMock(spec=logging.Logger)
    bp = DebugBreakpoint(logger)
    
    bp.register("QUERY", "Test breakpoint")
    
    assert "QUERY" in bp.breakpoints
    assert bp.breakpoints["QUERY"]["description"] == "Test breakpoint"
    assert bp.breakpoints["QUERY"]["hit_count"] == 0


def test_breakpoint_check_triggers():
    """Test breakpoint triggers when opcode matches."""
    logger = MagicMock(spec=logging.Logger)
    bp = DebugBreakpoint(logger)
    
    bp.register("QUERY", "Test")
    result = bp.check("QUERY")
    
    # Phase 1: Returns False (no pause), but logs warning
    assert result is False
    logger.warning.assert_called_once()
    assert bp.breakpoints["QUERY"]["hit_count"] == 1


def test_breakpoint_check_doesnt_trigger():
    """Test breakpoint doesn't trigger when opcode doesn't match."""
    logger = MagicMock(spec=logging.Logger)
    bp = DebugBreakpoint(logger)
    
    bp.register("QUERY", "Test")
    result = bp.check("OTHER")
    
    assert result is False
    logger.warning.assert_not_called()


def test_breakpoint_hit_count_increments():
    """Test hit count increments on each trigger."""
    logger = MagicMock(spec=logging.Logger)
    bp = DebugBreakpoint(logger)
    
    bp.register("QUERY", "Test")
    
    bp.check("QUERY")
    assert bp.breakpoints["QUERY"]["hit_count"] == 1
    
    bp.check("QUERY")
    assert bp.breakpoints["QUERY"]["hit_count"] == 2


def test_multiple_breakpoints():
    """Test registering multiple breakpoints."""
    logger = MagicMock(spec=logging.Logger)
    bp = DebugBreakpoint(logger)
    
    bp.register("QUERY", "First")
    bp.register("STATUS", "Second")
    
    assert len(bp.breakpoints) == 2
    assert "QUERY" in bp.breakpoints
    assert "STATUS" in bp.breakpoints


def test_breakpoint_report_empty():
    """Test report when no breakpoints registered."""
    logger = MagicMock(spec=logging.Logger)
    bp = DebugBreakpoint(logger)
    
    report = bp.report()
    assert "No breakpoints registered" in report


def test_breakpoint_report_with_hits():
    """Test report includes hit counts."""
    logger = MagicMock(spec=logging.Logger)
    bp = DebugBreakpoint(logger)
    
    bp.register("QUERY", "Test breakpoint 1")
    bp.register("STATUS", "Test breakpoint 2")
    
    bp.check("QUERY")
    bp.check("QUERY")
    bp.check("STATUS")
    
    report = bp.report()
    
    assert "QUERY" in report
    assert "STATUS" in report
    assert "hits: 2" in report  # QUERY hit twice
    assert "hits: 1" in report  # STATUS hit once
