"""Interactive REPL console for state inspection (Phase 1 stub, Phase 2 full)."""
import logging
from typing import Optional, Dict, Any


class InteractiveMonitor:
    """
    Interactive REPL console for inspecting and modifying emulator state.
    
    Phase 1: Displays stub message with help
    Phase 2: Full REPL with state inspection, injection, snapshots
    """
    
    def __init__(self, logger: logging.Logger):
        """
        Initialize InteractiveMonitor.
        
        Args:
            logger: logging.Logger instance
        """
        self.logger = logger
        self.is_running = False
    
    def start(self) -> None:
        """
        Start the interactive REPL console.
        
        Phase 1: Display help message and exit
        Phase 2: Enter full REPL loop
        """
        self.is_running = True
        
        self.logger.info("Interactive monitor starting (Phase 1 stub)")
        
        print("\n" + "=" * 80)
        print("INTERACTIVE MONITOR - Phase 1 Stub")
        print("=" * 80)
        print(self.help_message())
        print("=" * 80 + "\n")
        
        # Phase 1: Just display help and exit
        # Phase 2: Would enter REPL loop here
        
        self.is_running = False
    
    @staticmethod
    def help_message() -> str:
        """
        Get help message for interactive console.
        
        Returns:
            Formatted help text
        """
        return """
Interactive Monitor - Phase 1 Stub

Phase 1 Capabilities (Stub):
  - Display this help message
  
Phase 2 Planned Capabilities:
  - inspect      View current device state (all 24 keys)
  - watch        Watch specific state key for changes
  - inject       Inject state value for testing
  - snapshot     Save/load state snapshots
  - trigger      Simulate sensor triggers/encoder ticks
  - replay       Replay command sequence from log
  - exit         Exit interactive mode

Use '--interactive' flag when starting emulator:
  python3 src/main.py --port COM3 --interactive

Note: This is a Phase 1 stub. Full REPL will be implemented in Phase 2.
        """
