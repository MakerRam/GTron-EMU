"""Tests for interactive REPL console stub."""
import logging
from io import StringIO
import sys
from unittest.mock import MagicMock

from firmware_emulator.src.interactive_monitor import InteractiveMonitor


def test_interactive_init():
    """Test InteractiveMonitor initialization."""
    logger = MagicMock(spec=logging.Logger)
    monitor = InteractiveMonitor(logger)
    
    assert monitor.is_running is False


def test_interactive_help_message():
    """Test help message is available and contains Phase 2 info."""
    help_text = InteractiveMonitor.help_message()
    
    assert "Phase 1 Stub" in help_text
    assert "Phase 2" in help_text
    assert "inspect" in help_text  # Phase 2 feature
    assert "exit" in help_text


def test_interactive_startup_message():
    """Test startup displays help (Phase 1 stub)."""
    logger = MagicMock(spec=logging.Logger)
    monitor = InteractiveMonitor(logger)
    
    captured = StringIO()
    sys.stdout = captured
    
    monitor.start()
    
    sys.stdout = sys.__stdout__
    output = captured.getvalue()
    
    assert "INTERACTIVE MONITOR" in output
    assert "Phase 1 Stub" in output


def test_interactive_is_running():
    """Test is_running flag during execution."""
    logger = MagicMock(spec=logging.Logger)
    monitor = InteractiveMonitor(logger)
    
    # Suppress output
    captured = StringIO()
    sys.stdout = captured
    
    monitor.start()
    
    sys.stdout = sys.__stdout__
    
    # After start(), is_running should be False again (Phase 1)
    assert monitor.is_running is False
