"""Integration tests for main emulator event loop"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from io import StringIO
import sys
from firmware_emulator.src.main import EmulatorEngine
from firmware_emulator.src.serial_bridge import SerialBridge
from firmware_emulator.src.command_parser import CommandParser
from firmware_emulator.src.opcode_handlers import OpcodeDispatcher


class TestEmulatorEngine(unittest.TestCase):
    """Test main emulator event loop"""
    
    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_engine_initialization(self, mock_serial):
        """EmulatorEngine should initialize with dependencies"""
        mock_port = MagicMock()
        mock_serial.return_value = mock_port
        
        with patch('firmware_emulator.src.main.logging.getLogger'):
            engine = EmulatorEngine(port="COM3")
            self.assertIsNotNone(engine)
            self.assertIsNotNone(engine.serial_bridge)
            self.assertIsNotNone(engine.dispatcher)
    
    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_process_command_query(self, mock_serial):
        """Engine should handle QUERY → YES"""
        mock_port = MagicMock()
        mock_serial.return_value = mock_port
        
        with patch('firmware_emulator.src.main.logging.getLogger'):
            engine = EmulatorEngine(port="COM3")
            
            # Simulate receiving QUERY
            response = engine._process_command(b'QUERY')
            
            self.assertEqual(response, b'YES')
    
    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_process_command_unknown(self, mock_serial):
        """Engine should return FLS for unknown opcodes"""
        mock_port = MagicMock()
        mock_serial.return_value = mock_port
        
        with patch('firmware_emulator.src.main.logging.getLogger'):
            engine = EmulatorEngine(port="COM3")
            
            response = engine._process_command(b'XXXXX')
            
            self.assertEqual(response, b'FLS')


class TestEndToEndHandshake(unittest.TestCase):
    """Test complete handshake flow"""
    
    def test_query_byte_sequence(self):
        """QUERY should encode to correct bytes"""
        cmd_bytes = b'QUERY'
        opcode = CommandParser.parse(cmd_bytes)
        
        dispatcher = OpcodeDispatcher()
        response = dispatcher.dispatch(opcode)
        
        self.assertEqual(opcode, "QUERY")
        self.assertEqual(response, b'YES')
    
    def test_query_to_yes_handshake_bytes(self):
        """End-to-end: QUERY bytes → YES bytes"""
        # Receive
        cmd_bytes = bytes([0x51, 0x55, 0x45, 0x52, 0x59])  # QUERY
        self.assertTrue(CommandParser.is_valid_command(cmd_bytes))
        
        opcode = CommandParser.parse(cmd_bytes)
        self.assertEqual(opcode, "QUERY")
        
        # Process
        dispatcher = OpcodeDispatcher()
        response = dispatcher.dispatch(opcode)
        
        # Send
        self.assertEqual(response, bytes([0x59, 0x45, 0x53]))  # YES
        self.assertEqual(len(response), 3)


if __name__ == '__main__':
    unittest.main()
