"""5-byte ASCII opcode parsing and validation."""
import logging
from typing import Optional, Tuple, Any
from firmware_emulator.src.config_parser import MachineConfig


class OpcodeParser:
    """Parse 5-byte ASCII commands into opcode and optional parameters."""
    
    def __init__(self, config: MachineConfig, logger: logging.Logger):
        """
        Initialize OpcodeParser.
        
        Args:
            config: MachineConfig instance with registered opcodes
            logger: logging.Logger instance
        """
        self.config = config
        self.logger = logger
    
    def parse(self, data: bytes) -> Tuple[str, Optional[Any]]:
        """
        Parse 5-byte ASCII command into opcode and optional parameters.
        
        Format: 5 bytes total
        - Bytes 0-4: Opcode (5-char ASCII string, e.g., 'QUERY', 'tpGOP')
        - If opcode has parameters, they may be encoded in bytes 0-4
        
        Args:
            data: Raw 5 bytes from serial port
        
        Returns:
            Tuple (opcode, params) where params is None if no parameters
        
        Raises:
            ValueError: If command is not 5 bytes, not ASCII, or opcode not registered
        """
        # Validate data
        if len(data) != 5:
            raise ValueError(f"Command must be 5 bytes, got {len(data)}")
        
        # Convert to ASCII string
        try:
            command_str = data.decode('ascii')
        except UnicodeDecodeError as e:
            raise ValueError(f"Command contains non-ASCII bytes: {data.hex()}") from e
        
        # Extract opcode (first 5 chars, or validate against registered opcodes)
        opcode = command_str.strip()  # Remove any trailing spaces
        
        # Validate opcode is registered
        if not self.validate_opcode(opcode):
            raise ValueError(f"Unregistered opcode: {opcode}")
        
        # Extract parameters (if any)
        params = self.extract_params(command_str)
        
        return opcode, params
    
    def validate_opcode(self, opcode: str) -> bool:
        """
        Validate that opcode is registered in MachineConfig.
        
        Args:
            opcode: Opcode string (e.g., 'QUERY', 'tpGOP')
        
        Returns:
            True if opcode is registered, False otherwise
        """
        return self.config.is_valid_opcode(opcode)
    
    @staticmethod
    def extract_params(command_str: str) -> Optional[Any]:
        """
        Extract parameters from command string.
        
        Phase 1: No parameters (return None for all commands)
        Phase 2: Support parameter encoding in specific opcodes
        
        Args:
            command_str: 5-character command string
        
        Returns:
            None (Phase 1 stub)
        """
        # Phase 1: No parameter parsing
        # Phase 2: Add support for encoded parameters in specific opcodes
        return None
