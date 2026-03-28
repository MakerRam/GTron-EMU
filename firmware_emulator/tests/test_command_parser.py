import pytest
from firmware_emulator.src.command_parser import CommandParser

class TestCommandParser:
    """Test 5-byte ASCII command parsing"""
    
    def test_parse_query_command(self):
        """Parser should convert QUERY bytes to opcode string"""
        cmd_bytes = b'QUERY'
        opcode = CommandParser.parse(cmd_bytes)
        assert opcode == "QUERY"
    
    def test_parse_camera_command(self):
        """Parser should handle camera trigger command"""
        cmd_bytes = b'LCS01'
        opcode = CommandParser.parse(cmd_bytes)
        assert opcode == "LCS01"
    
    def test_parse_unknown_command(self):
        """Parser should handle unknown opcodes"""
        cmd_bytes = b'XXXXX'
        opcode = CommandParser.parse(cmd_bytes)
        assert opcode == "XXXXX"  # Return as-is
    
    def test_is_valid_command_true(self):
        """Validation should accept 5-byte commands"""
        assert CommandParser.is_valid_command(b'QUERY') is True
        assert CommandParser.is_valid_command(b'LCS01') is True
        assert CommandParser.is_valid_command(b'XXXXX') is True
    
    def test_is_valid_command_false_short(self):
        """Validation should reject commands shorter than 5 bytes"""
        assert CommandParser.is_valid_command(b'QUE') is False
        assert CommandParser.is_valid_command(b'') is False
    
    def test_is_valid_command_false_long(self):
        """Validation should reject commands longer than 5 bytes"""
        assert CommandParser.is_valid_command(b'QUERYY') is False
    
    def test_parse_with_hex_bytes(self):
        """Parser should handle raw hex bytes"""
        # QUERY = 0x51 0x55 0x45 0x52 0x59
        cmd_bytes = bytes([0x51, 0x55, 0x45, 0x52, 0x59])
        opcode = CommandParser.parse(cmd_bytes)
        assert opcode == "QUERY"
    
    def test_parse_preserves_case(self):
        """Parser should preserve command case"""
        cmd_bytes = b'LCS01'
        opcode = CommandParser.parse(cmd_bytes)
        assert opcode == "LCS01"
        assert opcode != "lcs01"
