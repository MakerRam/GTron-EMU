"""Opcode handlers for firmware commands"""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class OpcodeHandler(ABC):
    """Base class for opcode handlers"""
    
    @abstractmethod
    def handle(self) -> bytes:
        """Execute handler and return response bytes"""
        pass
    
    @abstractmethod
    def get_opcode_name(self) -> str:
        """Return opcode name (e.g., 'QUERY')"""
        pass
    
    @abstractmethod
    def get_response_name(self) -> str:
        """Return response type (e.g., 'YES')"""
        pass

class HandshakeHandler(OpcodeHandler):
    """Handles QUERY opcode for handshake"""
    
    def handle(self) -> bytes:
        """Handle QUERY command."""
        logger.info("QUERY received - responding with YES")
        return b'YES'
    
    def get_opcode_name(self) -> str:
        return "QUERY"
    
    def get_response_name(self) -> str:
        return "YES"

class CameraPlaceholderHandler(OpcodeHandler):
    """Placeholder for camera handlers (Phase 2)"""
    
    def __init__(self, opcode: str):
        self.opcode = opcode
    
    def handle(self) -> bytes:
        """Placeholder response"""
        return b'LCS1'
    
    def get_opcode_name(self) -> str:
        return self.opcode
    
    def get_response_name(self) -> str:
        return "LCS1"

class OpcodeDispatcher:
    """Routes opcodes to appropriate handlers"""
    
    def __init__(self):
        """Initialize dispatcher with built-in handlers"""
        self.handlers: Dict[str, OpcodeHandler] = {
            'QUERY': HandshakeHandler(),
            'LCS01': CameraPlaceholderHandler('LCS01'),
            'LCS02': CameraPlaceholderHandler('LCS02'),
            'LCS03': CameraPlaceholderHandler('LCS03'),
        }
    
    def dispatch(self, opcode: str) -> bytes:
        """Route opcode to handler."""
        if opcode in self.handlers:
            handler = self.handlers[opcode]
            logger.info(f"Dispatching {opcode} to {handler.get_response_name()}")
            return handler.handle()
        else:
            logger.warning(f"Unknown opcode: {opcode}, returning FLS")
            return b'FLS'  # "Failed" response
