import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from firmware_emulator.src.serial_bridge import SerialBridge

class TestSerialBridge:
    """Test serial communication layer"""
    
    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_init_opens_port(self, mock_serial):
        """SerialBridge should open COM port on initialization"""
        mock_port = Mock()
        mock_serial.return_value = mock_port
        
        bridge = SerialBridge(port="COM3", baudrate=9600, timeout=1.0)
        
        assert bridge.is_open() is True
        mock_serial.assert_called_once_with(
            port="COM3",
            baudrate=9600,
            bytesize=8,
            stopbits=1,
            parity='N',
            timeout=1.0
        )
    
    def test_read_command_returns_bytes(self):
        """read_command should return 5-byte command or None"""
        with patch('firmware_emulator.src.serial_bridge.serial.Serial') as mock_serial:
            mock_port = MagicMock()
            mock_port.in_waiting = 5
            mock_port.read.return_value = b'QUERY'
            mock_serial.return_value = mock_port
            
            bridge = SerialBridge(port="COM3")
            cmd = bridge.read_command()
            
            assert cmd == b'QUERY'
            assert len(cmd) == 5
    
    def test_read_command_returns_none_on_timeout(self):
        """read_command should return None if no data available"""
        with patch('firmware_emulator.src.serial_bridge.serial.Serial') as mock_serial:
            mock_port = MagicMock()
            mock_port.in_waiting = 0
            mock_serial.return_value = mock_port
            
            bridge = SerialBridge(port="COM3")
            cmd = bridge.read_command()
            
            assert cmd is None
    
    def test_write_response_writes_bytes(self):
        """write_response should send bytes to serial port"""
        with patch('firmware_emulator.src.serial_bridge.serial.Serial') as mock_serial:
            mock_port = MagicMock()
            mock_port.write.return_value = 3
            mock_serial.return_value = mock_port
            
            bridge = SerialBridge(port="COM3")
            success = bridge.write_response(b'YES')
            
            assert success is True
            mock_port.write.assert_called_once_with(b'YES')
    
    def test_context_manager_support(self):
        """SerialBridge should support 'with' statement"""
        with patch('firmware_emulator.src.serial_bridge.serial.Serial') as mock_serial:
            mock_port = MagicMock()
            mock_serial.return_value = mock_port
            
            with SerialBridge(port="COM3") as bridge:
                assert bridge.is_open() is True
            
            mock_port.close.assert_called_once()
