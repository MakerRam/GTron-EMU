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
    """Test that parser initializes correctly with just --port."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3"])
    
    assert args.port == "COM3"
    assert args.baudrate == 115200  # Check a default value instead


def test_parser_config_custom():
    """Test that --api-port argument accepts custom values."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3", "--api-port", "8080"])
    
    assert args.api_port == 8080


def test_parser_verbose_flag():
    """Test that --verbose flag is parsed correctly."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3", "--verbose"])
    
    assert args.verbose is True


def test_parser_hex_flag():
    """Test that --hex flag is parsed correctly as hex_output."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3", "--hex"])
    
    assert args.hex_output is True


def test_parser_debug_flag():
    """Test that --debug flag is parsed correctly as a list."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3", "--debug"])
    
    assert isinstance(args.debug, list)


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
        "--api-port", "8080",
        "--interactive"
    ])
    
    assert args.port == "COM3"
    assert args.verbose is True
    assert args.hex_output is True
    assert args.api_port == 8080
    assert args.interactive is True


def test_parser_flag_defaults_false():
    """Test that boolean flags default to False or empty."""
    parser = create_parser()
    args = parser.parse_args(["--port", "COM3"])
    
    assert args.verbose is False
    assert args.hex_output is False
    assert args.debug == []
    assert args.interactive is False
