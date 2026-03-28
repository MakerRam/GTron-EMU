"""5-byte ASCII command parser"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

class CommandParser:
    """Parses 5-byte ASCII commands into opcode strings"""
    
    @staticmethod
    def parse(command_bytes: bytes) -> str:
        """Parse 5-byte command into opcode string.
        
        Args:
            command_bytes: 5-byte ASCII command
            
        Returns:
            Opcode string (e.g., 'QUERY')
        """
        try:
            opcode = command_bytes.decode('ascii').strip()
            logger.debug(f"Parsed opcode: {opcode}")
            return opcode
        except (UnicodeDecodeError, AttributeError) as e:
            logger.error(f"Failed to parse command: {e}")
            return "ERR"
    
    @staticmethod
    def is_valid_command(command_bytes: bytes) -> bool:
        """Validate command format (exactly 5 bytes).
        
        Args:
            command_bytes: Bytes to validate
            
        Returns:
            True if exactly 5 bytes, False otherwise
        """
        return isinstance(command_bytes, bytes) and len(command_bytes) == 5
