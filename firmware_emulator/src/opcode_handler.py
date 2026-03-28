"""Opcode handler registry and dispatch mechanism."""
import logging
from typing import Callable, Dict, Tuple, Optional, Any
from firmware_emulator.src.device_state import DeviceState


# Handler function signature: (state) -> (response, new_state)
HandlerFunc = Callable[[DeviceState], Tuple[str, DeviceState]]


class OpcodeHandler:
    """
    Registry and dispatcher for opcode handlers.
    
    Each opcode maps to a handler function with signature:
        handler(state: DeviceState) -> (response: str, new_state: DeviceState)
    
    Handlers are stateless - they receive immutable state and return new state.
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize OpcodeHandler with logger.
        
        Args:
            logger: logging.Logger instance
        """
        self.logger = logger
        self.handlers: Dict[str, HandlerFunc] = {}
        
        # Register built-in handlers
        self._register_builtin_handlers()
    
    def register(self, opcode: str, handler: HandlerFunc) -> None:
        """
        Register a handler for an opcode.
        
        Args:
            opcode: Opcode string (e.g., 'QUERY', 'tpGOP')
            handler: Handler function with signature (state) -> (response, new_state)
        """
        self.handlers[opcode] = handler
        self.logger.info(f"Handler registered for opcode: {opcode}")
    
    def get_handler(self, opcode: str) -> HandlerFunc:
        """
        Retrieve a handler for an opcode.
        
        Args:
            opcode: Opcode string
        
        Returns:
            Handler function
        
        Raises:
            KeyError: If opcode has no registered handler
        """
        if opcode not in self.handlers:
            raise KeyError(f"No handler registered for opcode: {opcode}")
        return self.handlers[opcode]
    
    def dispatch(self, opcode: str, state: DeviceState) -> Tuple[str, DeviceState]:
        """
        Dispatch opcode to appropriate handler.
        
        Args:
            opcode: Opcode string
            state: Current DeviceState
        
        Returns:
            Tuple (response, new_state)
        
        Raises:
            KeyError: If opcode has no registered handler
        """
        handler = self.get_handler(opcode)
        response, new_state = handler(state)
        return response, new_state
    
    def list_handlers(self) -> list:
        """
        List all registered opcode handlers.
        
        Returns:
            List of registered opcode strings
        """
        return sorted(self.handlers.keys())
    
    def _register_builtin_handlers(self) -> None:
        """Register built-in handlers for common opcodes."""
        # QUERY: Always returns "YES"
        def handle_query(state: DeviceState) -> Tuple[str, DeviceState]:
            return "YES", state
        
        self.register("QUERY", handle_query)
        
        # STATUS: Returns device status (Phase 1: simplified version)
        def handle_status(state: DeviceState) -> Tuple[str, DeviceState]:
            # Phase 1: Return simple status
            # Phase 2: Return detailed device status based on current state
            return "OK", state
        
        self.register("STATUS", handle_status)
