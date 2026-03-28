"""Serial communication bridge for COM port I/O"""

import serial
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SerialBridge:
    """Manages virtual COM port communication with 5-byte ASCII protocol"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0, bytesize: int = 8, stopbits: int = 1, parity: str = 'N') -> None:
        """Initialize serial bridge.
        
        Args:
            port: COM port name (e.g., 'COM3')
            baudrate: Baud rate (default 9600)
            timeout: Read timeout in seconds (default 1.0)
            bytesize: Data bits (default 8)
            stopbits: Stop bits (default 1)
            parity: Parity ('N' = None, 'E' = Even, 'O' = Odd)
            
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
                timeout=timeout
            )
            logger.info(f"Serial port {port} opened at {baudrate} baud")
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
        """Read 5-byte command from serial port.
        
        Returns:
            5-byte command if available, None if no data ready or timeout
        """
        if self._port.in_waiting >= 5:
            data = self._port.read(5)
            if len(data) == 5:
                logger.debug(f"Received: {data}")
                return data
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
