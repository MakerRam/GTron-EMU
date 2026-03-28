"""Debug breakpoint infrastructure for Phase 1 and Phase 2."""
import logging
from typing import Dict, List, Optional, Any


class DebugBreakpoint:
    """Manages debug breakpoints on specific opcodes (Phase 1 stub, Phase 2 full)."""
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize DebugBreakpoint manager.
        
        Args:
            logger: logging.Logger instance
        """
        self.logger = logger
        self.breakpoints: Dict[str, Dict[str, Any]] = {}
    
    def register(self, opcode: str, description: str = "") -> None:
        """
        Register a breakpoint on an opcode.
        
        Phase 1: Log a warning when triggered
        Phase 2: Pause execution for inspection
        
        Args:
            opcode: The opcode to break on
            description: Optional description of why we're breaking
        """
        self.breakpoints[opcode] = {
            "description": description,
            "hit_count": 0,
        }
        self.logger.info(f"Breakpoint registered on opcode: {opcode} ({description})")
    
    def check(self, opcode: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if opcode has a breakpoint registered.
        
        Phase 1: Logs warning and returns False (no pause)
        Phase 2: Pauses execution and returns True when resumed
        
        Args:
            opcode: The opcode to check
            context: Optional context dict (state, request, response, etc.)
        
        Returns:
            True if breakpoint was hit and user wants to continue; False otherwise
        """
        if opcode not in self.breakpoints:
            return False
        
        # Phase 1: Log warning and continue
        self.breakpoints[opcode]["hit_count"] += 1
        hit_count = self.breakpoints[opcode]["hit_count"]
        description = self.breakpoints[opcode]["description"]
        
        warning_msg = f"BREAKPOINT HIT: {opcode} (count: {hit_count}) - {description}"
        self.logger.warning(warning_msg)
        
        # Phase 2: Would pause here for inspection
        # For now, return False to indicate no pause
        return False
    
    def report(self) -> str:
        """
        Generate a report of all breakpoint hits.
        
        Returns:
            Human-readable breakpoint report
        """
        if not self.breakpoints:
            return "No breakpoints registered."
        
        lines = ["=== Breakpoint Report ==="]
        for opcode, data in sorted(self.breakpoints.items()):
            hit_count = data["hit_count"]
            description = data["description"]
            lines.append(f"{opcode} | hits: {hit_count} | {description}")
        
        return "\n".join(lines)
