"""Serial communication bridge for COM port I/O"""

import serial
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SerialBridge:
    """Manages virtual COM port communication with 5-byte ASCII protocol"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0, bytesize: int = 8, stopbits: int = 1, parity: str = 'N', 
                 rtscts: bool = False, dsrdtr: bool = False, xonxoff: bool = False) -> None:
        """Initialize serial bridge.
        
        Args:
            port: COM port name (e.g., 'COM3')
            baudrate: Baud rate (default 9600)
            timeout: Read timeout in seconds (default 1.0)
            bytesize: Data bits (default 8)
            stopbits: Stop bits (default 1)
            parity: Parity ('N' = None, 'E' = Even, 'O' = Odd)
            rtscts: Enable RTS/CTS flow control (default False)
            dsrdtr: Enable DSR/DTR flow control (default False)
            xonxoff: Enable XON/XOFF software flow control (default False)
            
        Raises:
            serial.SerialException: If port cannot be opened
        """
        try:
            self._port = serial.Serial(
                port=port, 
                baudrate=baudrate, 
                bytesize=bytesize, 
                stopbits=stopbits, 
                parity=parity, 
                timeout=timeout,
                write_timeout=timeout,  # Also set write timeout to match read timeout
                rtscts=rtscts,
                dsrdtr=dsrdtr,
                xonxoff=xonxoff
            )
            # Clear any residual data in the buffer
            self._port.reset_input_buffer()
            self._port.reset_output_buffer()
            
            # Log port configuration for debugging
            flow_control = []
            if rtscts:
                flow_control.append("RTS/CTS")
            if dsrdtr:
                flow_control.append("DSR/DTR")
            if xonxoff:
                flow_control.append("XON/XOFF")
            
            flow_str = f"(flow control: {', '.join(flow_control)})" if flow_control else "(no flow control)"
            logger.info(f"Serial port {port} opened at {baudrate} baud {flow_str}")
        except serial.SerialException as e:
            logger.error(f"Failed to open serial port {port}: {e}")
            raise
    
    def is_open(self) -> bool:
        """Check if serial port is open.
        
        Returns:
            True if port is open, False otherwise
        """
        return self._port.is_open
    
    def read_command(self) -> Optional[bytes]:
        """Read command from serial port.
        
        Reads 5-byte commands, handling optional trailing newline from LabVIEW.
        Protocol: Expects 5-byte ASCII opcode, optionally followed by newline.
        
        Returns:
            5-byte command if valid, None if timeout or no complete command
        """
        try:
            # Strategy: Read exactly 5 bytes (the opcode)
            data = self._port.read(5)
            
            if len(data) < 5:
                # Timeout or incomplete read
                if len(data) > 0:
                    logger.warning(f"Incomplete read: got {len(data)} bytes, expected 5: {data}")
                return None
            
            # We have exactly 5 bytes
            logger.debug(f"Received: {data}")
            
            # Check if there's a trailing newline (6th byte) and consume it
            # This prevents it from being picked up as the start of the next command
            if self._port.in_waiting > 0:
                next_byte = self._port.read(1)
                if next_byte and next_byte not in (b'\n', b'\r'):
                    # Unexpected byte after command - this might be part of next command
                    logger.warning(f"Unexpected byte after command: {next_byte}")
                    # Put it back by... well, we can't, so log it
                    logger.debug(f"Note: {next_byte} consumed from buffer")
                else:
                    logger.debug(f"Consumed trailing newline: {next_byte}")
            
            return data
            
        except Exception as e:
            logger.error(f"Error reading from serial port: {e}")
            return None
    
    def write_response(self, response: bytes) -> bool:
        """Write response to serial port.
        
        Args:
            response: Bytes to send
            
        Returns:
            True if all bytes sent, False on error
        """
        try:
            bytes_written = self._port.write(response)
            self._port.flush()
            logger.debug(f"Sent: {response} ({bytes_written} bytes)")
            return bytes_written == len(response)
        except serial.SerialException as e:
            logger.error(f"Serial write error: {e}")
            return False
    
    def close(self) -> None:
        """Close the serial port"""
        if self._port.is_open:
            self._port.close()
            logger.info("Serial port closed")
    
    def __enter__(self) -> 'SerialBridge':
        """Enter context manager"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Exit context manager"""
        self.close()
        return False
