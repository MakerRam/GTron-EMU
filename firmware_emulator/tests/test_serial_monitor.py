"""Tests for SerialMonitor class - human-readable formatting."""
import logging
from io import StringIO
import sys
from unittest.mock import MagicMock

from firmware_emulator import SerialMonitor


def test_format_timestamp():
    """Test timestamp formatting (YYYY-MM-DD HH:MM:SS.mmm)."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger)
    
    timestamp = monitor._format_timestamp()
    parts = timestamp.split()
    
    assert len(parts) == 2  # Date and time
    assert len(parts[0].split('-')) == 3  # YYYY-MM-DD
    assert len(parts[1].split(':')) == 3  # HH:MM:SS.mmm


def test_log_command_format():
    """Test human-readable command logging format."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger, enable_verbose=True)
    
    captured = StringIO()
    sys.stdout = captured
    
    monitor.log_command("QUERY", "YES")
    
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    
    assert "RECV: QUERY → SEND: YES" in output
    assert "[" in output and "]" in output  # Has timestamp format


def test_log_command_with_state():
    """Test command logging with state delta."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger)
    
    state_before = {"guide_position": "UPPER"}
    state_after = {"guide_position": "LOWER"}
    
    monitor.log_command("tpGOP", "tpGOR", state_before, state_after)
    
    # Verify command counter incremented
    assert monitor.command_counter == 1
    
    # Verify logger called with state delta
    logger.info.assert_called_once()
    call_args = logger.info.call_args[0][0]
    assert "[COMMAND_001]" in call_args
    assert "RECV: tpGOP" in call_args


def test_log_hex_format():
    """Test hex dump format."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger, enable_hex=True)
    
    captured = StringIO()
    sys.stdout = captured
    
    data = b"QUERY"
    monitor.log_hex(data, "RECV")
    
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    
    assert "51 55 45 52 59" in output  # Hex for "QUERY"
    assert "QUERY" in output  # ASCII


def test_log_hex_send():
    """Test hex dump for outgoing bytes (SEND)."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger, enable_hex=True)
    
    captured = StringIO()
    sys.stdout = captured
    
    data = b"YES"
    monitor.log_hex(data, "SEND")
    
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    
    assert "SEND:" in output
    assert "59 45 53" in output  # Hex for "YES"


def test_log_error_format():
    """Test error logging with traceback."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger, enable_verbose=True)
    
    captured = StringIO()
    sys.stdout = captured
    
    monitor.log_error("Test error")
    
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    
    assert "ERROR: Test error" in output
    logger.error.assert_called_once()


def test_command_counter_increments():
    """Test command counter increments [COMMAND_001], [COMMAND_002], etc."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger)
    
    monitor.log_command("CMD1", "RSP1")
    assert monitor.command_counter == 1
    
    monitor.log_command("CMD2", "RSP2")
    assert monitor.command_counter == 2
    
    logger.info.assert_called()
    # Check both calls have correct counter
    call_args_list = logger.info.call_args_list
    assert "[COMMAND_001]" in call_args_list[0][0][0]
    assert "[COMMAND_002]" in call_args_list[1][0][0]


def test_timestamp_precision_milliseconds():
    """Test timestamp has millisecond precision (3 decimal places)."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger)
    
    timestamp = monitor._format_timestamp()
    # Format: YYYY-MM-DD HH:MM:SS.mmm
    time_part = timestamp.split()[1]
    ms_part = time_part.split('.')[-1]
    
    assert len(ms_part) == 3, f"Expected 3 digit milliseconds, got {ms_part}"


def test_nonprintable_bytes_in_hex():
    """Test hex dump handles non-printable bytes correctly."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger)
    
    data = bytes([0x00, 0x51, 0xFF, 0x45])  # NUL, Q, non-printable, E
    result = monitor._bytes_to_ascii(data)
    assert result == ".Q.E"


def test_state_dict_serialization():
    """Test state_before/state_after can be serialized from DeviceState objects."""
    logger = MagicMock(spec=logging.Logger)
    monitor = SerialMonitor(logger)
    
    state_before = {"position": "UPPER", "speed": 100}
    state_after = {"position": "LOWER", "speed": 100}
    
    result = monitor._state_delta(state_before, state_after)
    assert "position: UPPER → LOWER" in result
    assert "speed" not in result
