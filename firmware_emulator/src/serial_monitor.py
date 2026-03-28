"""Serial port monitoring and command logging."""
import logging
from datetime import datetime
from typing import Optional, Dict, Any


class SerialMonitor:
    """Handles human-readable formatting of serial commands and hex dumps."""
    
    def __init__(self, logger: logging.Logger, enable_verbose: bool = False, enable_hex: bool = False):
        """
        Initialize SerialMonitor.
        
        Args:
            logger: logging.Logger instance from logging_config
            enable_verbose: If True, print human-readable commands to console
            enable_hex: If True, print hex dumps to console
        """
        self.logger = logger
        self.enable_verbose = enable_verbose
        self.enable_hex = enable_hex
        self.command_counter = 0
    
    def log_command(self, opcode: str, response: str, 
                   state_before: Optional[Dict[str, Any]] = None,
                   state_after: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a command-response pair in human-readable format.
        
        Format (verbose): [2026-03-28 07:53:25.123] RECV: QUERY → SEND: YES
        Format (command log): [COMMAND_001] RECV: QUERY → SEND: YES [state_before → state_after]
        
        Args:
            opcode: The received opcode (e.g., "QUERY")
            response: The response sent (e.g., "YES")
            state_before: State dict before handling (optional)
            state_after: State dict after handling (optional)
        """
        self.command_counter += 1
        timestamp = self._format_timestamp()
        
        # Format verbose output
        if self.enable_verbose:
            verbose_msg = f"[{timestamp}] RECV: {opcode} → SEND: {response}"
            print(verbose_msg)
        
        # Format command log entry
        state_delta = ""
        if state_before and state_after:
            state_delta = f" [{self._state_delta(state_before, state_after)}]"
        
        command_log_msg = f"[COMMAND_{self.command_counter:03d}] RECV: {opcode} → SEND: {response}{state_delta}"
        self.logger.info(command_log_msg)
    
    def log_hex(self, data: bytes, direction: str = "RECV") -> None:
        """
        Log raw bytes in hex format with ASCII representation.
        
        Format: [2026-03-28 07:53:25.123] RECV: [51 55 45 52 59] "QUERY"
        
        Args:
            data: Raw bytes to log
            direction: "RECV" or "SEND"
        """
        timestamp = self._format_timestamp()
        hex_str = " ".join(f"{b:02X}" for b in data)
        ascii_str = self._bytes_to_ascii(data)
        
        if self.enable_hex:
            hex_msg = f"[{timestamp}] {direction}: [{hex_str}] \"{ascii_str}\""
            print(hex_msg)
        
        self.logger.debug(f"{direction}: [{hex_str}] \"{ascii_str}\"")
    
    def log_error(self, error_msg: str, exception: Optional[Exception] = None) -> None:
        """
        Log an error with optional exception traceback.
        
        Args:
            error_msg: Description of the error
            exception: Optional exception object
        """
        timestamp = self._format_timestamp()
        
        if self.enable_verbose:
            print(f"[{timestamp}] ERROR: {error_msg}")
        
        if exception:
            self.logger.error(error_msg, exc_info=exception)
        else:
            self.logger.error(error_msg)
    
    @staticmethod
    def _format_timestamp() -> str:
        """Format current time as YYYY-MM-DD HH:MM:SS.mmm"""
        now = datetime.now()
        return now.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    
    @staticmethod
    def _bytes_to_ascii(data: bytes) -> str:
        """Convert bytes to ASCII string, replacing non-printable chars with '.'"""
        return ''.join(chr(b) if 32 <= b < 127 else '.' for b in data)
    
    @staticmethod
    def _state_delta(state_before: Dict[str, Any], state_after: Dict[str, Any]) -> str:
        """Generate human-readable state change description."""
        changes = []
        for key in state_before:
            if key in state_after and state_before[key] != state_after[key]:
                changes.append(f"{key}: {state_before[key]} → {state_after[key]}")
        
        if not changes:
            return "no state change"
        return ", ".join(changes)
