"""
Tests for main.py CLI argument parsing.

Tests the command-line interface of the firmware emulator,
covering argument parsing, flag handling, and defaults.
"""

import pytest
from firmware_emulator.src.main import create_parser


def test_parser_port_required():
    """Test that --port argument is required."""
    parser = create_parser()
    
    with pytest.raises(SystemExit):
        parser.parse_args([])  # No args should fail


def test_parser_port_provided():
    """Test that --port argument is correctly parsed."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3"])
    
    assert args.port == "COM3"


def test_parser_config_optional_with_default():
    """Test that --config argument is optional with a default value."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3"])
    
    assert args.config == "Machine Interface Parameters.json"


def test_parser_config_custom():
    """Test that --config argument accepts custom paths."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3", "--config", "/custom/path.json"])
    
    assert args.config == "/custom/path.json"


def test_parser_verbose_flag():
    """Test that --verbose flag is parsed correctly."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3", "--verbose"])
    
    assert args.verbose is True


def test_parser_hex_flag():
    """Test that --hex flag is parsed correctly."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3", "--hex"])
    
    assert args.hex is True


def test_parser_debug_flag():
    """Test that --debug flag is parsed correctly."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3", "--debug"])
    
    assert args.debug is True


def test_parser_interactive_flag():
    """Test that --interactive flag is parsed correctly."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3", "--interactive"])
    
    assert args.interactive is True


def test_parser_multiple_flags():
    """Test that multiple flags can be combined correctly."""
    parser = create_parser()
    args = parser.parse_args([
        "--port", "COM3",
        "--verbose",
        "--hex",
        "--debug",
        "--interactive"
    ])
    
    assert args.port == "COM3"
    assert args.verbose is True
    assert args.hex is True
    assert args.debug is True
    assert args.interactive is True


def test_parser_flag_defaults_false():
    """Test that boolean flags default to False."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3"])
    
    assert args.verbose is False
    assert args.hex is False
    assert args.debug is False
    assert args.interactive is False
