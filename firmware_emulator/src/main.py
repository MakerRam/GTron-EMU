"""Main emulator entry point and event loop"""

import argparse
import logging
import sys
from pathlib import Path
from firmware_emulator.src.serial_bridge import SerialBridge
from firmware_emulator.src.command_parser import CommandParser
from firmware_emulator.src.opcode_handlers import OpcodeDispatcher
from firmware_emulator.src.logging_config import setup_logging

logger = logging.getLogger(__name__)

class EmulatorEngine:
    """Main event loop for firmware emulator"""
    
    def __init__(self, port: str, baudrate: int = 9600, timeout: float = 1.0, verbose: bool = False, hex_output: bool = False):
        """Initialize emulator engine."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.verbose = verbose
        self.hex_output = hex_output
        
        try:
            self.serial_bridge = SerialBridge(port=port, baudrate=baudrate, timeout=timeout)
        except Exception as e:
            logger.error(f"Failed to initialize serial bridge: {e}")
            raise
        
        self.dispatcher = OpcodeDispatcher()
        self.running = False
        logger.info(f"Emulator engine initialized on {port}")
    
    def _process_command(self, cmd_bytes: bytes) -> bytes:
        """Process received command."""
        if not CommandParser.is_valid_command(cmd_bytes):
            logger.warning(f"Invalid command format: {cmd_bytes}")
            return b'FLS'
        
        opcode = CommandParser.parse(cmd_bytes)
        response = self.dispatcher.dispatch(opcode)
        
        return response
    
    def _log_transaction(self, cmd_bytes: bytes, response: bytes):
        """Log command/response transaction."""
        opcode = CommandParser.parse(cmd_bytes) if CommandParser.is_valid_command(cmd_bytes) else "???"
        
        if self.hex_output:
            cmd_hex = ' '.join(f'{b:02X}' for b in cmd_bytes)
            resp_hex = ' '.join(f'{b:02X}' for b in response)
            msg = f"RECV: [{cmd_hex}] → SEND: [{resp_hex}]"
        else:
            cmd_str = cmd_bytes.decode('ascii', errors='replace')
            resp_str = response.decode('ascii', errors='replace')
            msg = f"RECV: {cmd_str} → SEND: {resp_str}"
        
        if self.verbose:
            print(f"[{opcode}] {msg}")
        
        logger.info(msg)
    
    def run(self):
        """Start main event loop"""
        logger.info("=== Emulator Started ===")
        print(f"Emulator running on {self.port} at {self.baudrate} baud")
        print("Waiting for commands... (Ctrl+C to stop)")
        
        self.running = True
        try:
            while self.running:
                cmd_bytes = self.serial_bridge.read_command()
                
                if cmd_bytes is not None:
                    response = self._process_command(cmd_bytes)
                    
                    if self.serial_bridge.write_response(response):
                        self._log_transaction(cmd_bytes, response)
                    else:
                        logger.error("Failed to send response")
        
        except KeyboardInterrupt:
            logger.info("Shutdown signal received (Ctrl+C)")
            print("\nShutting down...")
        
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
        
        finally:
            self.stop()
    
    def stop(self):
        """Stop the emulator and cleanup"""
        self.running = False
        self.serial_bridge.close()
        logger.info("=== Emulator Stopped ===")

def main():
    """Entry point for emulator"""
    parser = argparse.ArgumentParser(description="Vision System Firmware Emulator")
    parser.add_argument('--port', required=True, help='Serial port (e.g., COM3)')
    parser.add_argument('--baudrate', type=int, default=9600, help='Baud rate (default 9600)')
    parser.add_argument('--verbose', action='store_true', help='Print human-readable commands')
    parser.add_argument('--hex', action='store_true', dest='hex_output', help='Print hex bytes instead of ASCII')
    parser.add_argument('--debug', nargs='*', default=[], help='Debug breakpoint opcodes (Phase 2)')
    parser.add_argument('--interactive', action='store_true', help='Interactive monitor mode (Phase 2)')
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Create and run emulator
    engine = EmulatorEngine(port=args.port, verbose=args.verbose, hex_output=args.hex_output)
    
    logger.info(f"Command line args: {args}")
    
    try:
        engine.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
