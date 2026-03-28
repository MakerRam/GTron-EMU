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


def test_parser_command_with_numeric_params():
    """Test parsing command with numeric parameters."""
    config = MagicMock(spec=MachineConfig)
    config.is_valid_opcode.return_value = True
    logger = MagicMock()
    
    parser = OpcodeParser(config, logger)
    data = b"tpGOP"
    
    opcode, params = parser.parse(data)
    
    assert opcode == "tpGOP"
    assert params is None  # Phase 1: no parameter extraction


def test_parser_extract_params_with_encoding():
    """Test extracting params from encoded command format."""
    command_str = "tpGOP"
    params = OpcodeParser.extract_params(command_str)
    
    # Phase 1: Returns None
    assert params is None
