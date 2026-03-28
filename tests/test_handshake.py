"""Tests for handshake handler (QUERY/YES protocol)"""

import unittest
from unittest.mock import Mock, patch
from firmware_emulator.src.opcode_handlers import HandshakeHandler, OpcodeDispatcher
from firmware_emulator.src.device_state import DeviceState


class TestHandshakeHandler(unittest.TestCase):
    """Test QUERY/YES handshake protocol"""
    
    def test_handle_query_returns_yes(self):
        """QUERY opcode should return YES response"""
        handler = HandshakeHandler()
        response = handler.handle()
        
        self.assertEqual(response, b'YES')
    
    def test_handle_query_returns_3_bytes(self):
        """YES response should be exactly 3 bytes"""
        handler = HandshakeHandler()
        response = handler.handle()
        
        self.assertEqual(len(response), 3)
        self.assertEqual(response, bytes([0x59, 0x45, 0x53]))  # Y, E, S
    
    def test_get_response_name(self):
        """Handler should identify response type"""
        handler = HandshakeHandler()
        self.assertEqual(handler.get_response_name(), "YES")
    
    def test_get_opcode_name(self):
        """Handler should identify opcode"""
        handler = HandshakeHandler()
        self.assertEqual(handler.get_opcode_name(), "QUERY")


class TestOpcodeDispatcher(unittest.TestCase):
    """Test opcode routing"""
    
    def test_dispatcher_routes_query(self):
        """Dispatcher should route QUERY to HandshakeHandler"""
        dispatcher = OpcodeDispatcher()
        response = dispatcher.dispatch("QUERY")
        
        self.assertEqual(response, b'YES')
    
    def test_dispatcher_unknown_opcode(self):
        """Dispatcher should return FLS for unknown opcodes"""
        dispatcher = OpcodeDispatcher()
        response = dispatcher.dispatch("XXXXX")
        
        self.assertEqual(response, b'FLS')
    
    def test_dispatcher_handles_camera_placeholders(self):
        """Dispatcher should have placeholders for camera handlers"""
        dispatcher = OpcodeDispatcher()
        
        # Camera handlers exist (even if placeholders for now)
        self.assertIn("LCS01", dispatcher.handlers)
        self.assertIn("LCS02", dispatcher.handlers)
        self.assertIn("LCS03", dispatcher.handlers)


class TestHandshakeIntegration(unittest.TestCase):
    """Test handshake within context"""
    
    def test_query_command_triggers_handshake(self):
        """Receiving QUERY should activate handshake"""
        from firmware_emulator.src.command_parser import CommandParser
        
        cmd_bytes = b'QUERY'
        self.assertTrue(CommandParser.is_valid_command(cmd_bytes))
        self.assertEqual(CommandParser.parse(cmd_bytes), "QUERY")
        
        dispatcher = OpcodeDispatcher()
        response = dispatcher.dispatch("QUERY")
        self.assertEqual(response, b'YES')


if __name__ == '__main__':
    unittest.main()
