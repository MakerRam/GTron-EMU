"""Serial communication bridge for COM port I/O"""

import serial
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class SerialBridge:
    """Manages virtual COM port communication with 5-byte ASCII protocol.
    
    Uses an internal byte buffer to handle burst-send scenarios where
    LabVIEW writes multiple opcodes back-to-back. The buffer accumulates
    incoming bytes and extracts 5-byte frames, stripping any \\n / \\r
    characters that may appear between frames.
    """
    
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
        self._read_buffer = bytearray()  # Internal accumulation buffer
        
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
        """Read next 5-byte command from the serial port.
        
        Uses an internal buffer to handle burst-send scenarios where
        multiple opcodes arrive in a single OS read. Strips \\n and \\r
        characters between frames (LabVIEW may or may not append them).
        
        Flow:
          1. Drain all available bytes from the serial port into the buffer.
          2. If buffer is still < 5 bytes, do a blocking read for the remainder.
          3. Strip leading \\n / \\r bytes (inter-frame noise).
          4. If >= 5 bytes available, extract and return the first 5.
          5. Otherwise return None (timeout / incomplete).
        
        Returns:
            5-byte command if a complete frame is available, None otherwise.
        """
        try:
            # Step 1: Drain all available bytes into the internal buffer
            waiting = self._port.in_waiting
            if waiting > 0:
                chunk = self._port.read(waiting)
                if chunk:
                    self._read_buffer.extend(chunk)
            
            # Step 2: Strip leading newlines / carriage returns
            while self._read_buffer and self._read_buffer[0] in (0x0A, 0x0D):
                self._read_buffer.pop(0)
            
            # Step 3: If buffer still doesn't have 5 bytes, do a blocking read.
            # Loop because the blocking read may return leading newlines that
            # get stripped, leaving us still short of 5 bytes.
            while len(self._read_buffer) < 5:
                needed = 5 - len(self._read_buffer)
                data = self._port.read(needed)
                if not data:
                    break  # Timeout — no more data coming
                self._read_buffer.extend(data)
                
                # Strip leading newlines (the blocking read may have
                # returned newline bytes from LabVIEW)
                while self._read_buffer and self._read_buffer[0] in (0x0A, 0x0D):
                    self._read_buffer.pop(0)
            
            # Step 4: Need at least 5 bytes for a complete frame
            if len(self._read_buffer) < 5:
                if len(self._read_buffer) > 0:
                    logger.warning(
                        f"Incomplete frame in buffer: {len(self._read_buffer)} bytes: "
                        f"{bytes(self._read_buffer)!r}"
                    )
                return None
            
            # Step 5: Extract exactly 5 bytes
            frame = bytes(self._read_buffer[:5])
            del self._read_buffer[:5]
            
            logger.debug(f"Received: {frame}")
            return frame
            
        except Exception as e:
            logger.error(f"Error reading from serial port: {e}")
            return None
    
    def read_param(self) -> Optional[str]:
        """Read a variable-length numeric parameter from the serial buffer.
        
        LabVIEW sends parameter values as variable-length ASCII digit strings
        (e.g., "50000", "10", "0") immediately after a param opcode frame.
        The parameter ends when a non-digit byte is encountered (the start
        of the next opcode) or when no more data arrives (timeout).
        
        This method:
          1. Drains all available bytes from the serial port into the buffer.
          2. If buffer is empty, does a blocking read to wait for data.
          3. Extracts consecutive ASCII digit bytes (0x30-0x39) from the
             front of the buffer. Non-digit bytes are left for the next
             read_command() call.
        
        Returns:
            Parameter string (e.g., "50000") if digits found, None on timeout.
        """
        try:
            # Step 1: Drain all available bytes into the buffer
            waiting = self._port.in_waiting
            if waiting > 0:
                chunk = self._port.read(waiting)
                if chunk:
                    self._read_buffer.extend(chunk)
            
            # Step 2: Strip leading newlines / carriage returns
            while self._read_buffer and self._read_buffer[0] in (0x0A, 0x0D):
                self._read_buffer.pop(0)
            
            # Step 3: If buffer is empty, do a blocking read
            if len(self._read_buffer) == 0:
                data = self._port.read(1)
                if not data:
                    return None  # Timeout
                self._read_buffer.extend(data)
                
                # Strip newlines
                while self._read_buffer and self._read_buffer[0] in (0x0A, 0x0D):
                    self._read_buffer.pop(0)
                
                if len(self._read_buffer) == 0:
                    return None
            
            # Step 4: If the first byte is NOT a digit, there's no param —
            # the next opcode arrived immediately.
            if self._read_buffer[0] < 0x30 or self._read_buffer[0] > 0x39:
                logger.warning("read_param: first byte is not a digit, no param available")
                return None
            
            # Step 5: Drain more bytes to capture the full param value.
            # We do a short blocking read to ensure we get all digits that
            # LabVIEW sends in this burst before the next opcode starts.
            # After the initial drain, try one more drain pass.
            waiting = self._port.in_waiting
            if waiting > 0:
                chunk = self._port.read(waiting)
                if chunk:
                    self._read_buffer.extend(chunk)
            
            # Step 6: Extract consecutive digit bytes from the front
            param_bytes = bytearray()
            while self._read_buffer and 0x30 <= self._read_buffer[0] <= 0x39:
                param_bytes.append(self._read_buffer.pop(0))
            
            if not param_bytes:
                return None
            
            param_str = param_bytes.decode('ascii')
            logger.debug(f"Param read: {param_str!r} (remaining buffer: {len(self._read_buffer)} bytes)")
            return param_str
            
        except Exception as e:
            logger.error(f"Error reading param from serial port: {e}")
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
