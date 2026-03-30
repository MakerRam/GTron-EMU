"""Main emulator entry point and event loop"""

import argparse
import logging
import sys
import time
from pathlib import Path
from firmware_emulator.src.serial_bridge import SerialBridge
from firmware_emulator.src.command_parser import CommandParser
from firmware_emulator.src.opcode_handler import OpcodeHandler, PARAM_OPCODES
from firmware_emulator.src.device_state import DeviceState
from firmware_emulator.src.logging_config import setup_logging
from firmware_emulator.src.state_export import StateExporter
from firmware_emulator.src.api_server import APIServer

logger = logging.getLogger(__name__)

class EmulatorEngine:
    """Main event loop for firmware emulator"""
    
    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 1.0, verbose: bool = False, hex_output: bool = False,
                 rtscts: bool = False, dsrdtr: bool = False, xonxoff: bool = False, api_port: int = 5000, enable_api: bool = True):
        """Initialize emulator engine."""
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.verbose = verbose
        self.hex_output = hex_output
        
        try:
            self.serial_bridge = SerialBridge(port=port, baudrate=baudrate, timeout=timeout,
                                             rtscts=rtscts, dsrdtr=dsrdtr, xonxoff=xonxoff)
        except Exception as e:
            logger.error(f"Failed to initialize serial bridge: {e}")
            raise
        
        self.opcode_handler = OpcodeHandler(logger, delays={
            # Configurable simulated delays (seconds) for mechanical operations
            "TPGOP": 0.5,   # Top guide open
            "TPGCL": 0.5,   # Top guide close
            "BMGOP": 0.5,   # Bottom guide open
            "BMGCL": 0.5,   # Bottom guide close
            "RFS01": 0.3,   # Top reference search
            "RFS02": 0.3,   # Bottom reference search
            "TPRTR": 0.2,   # Top reeler rotate (diagnostic)
            "BMRTR": 0.2,   # Bottom reeler rotate (diagnostic)
        })
        self.device_state = DeviceState()
        self.running = False
        
        # Initialize state exporter and API server
        self.state_exporter = StateExporter(self.device_state)
        self.api_server = None
        self.enable_api = enable_api
        if enable_api:
            self.api_server = APIServer(
                self.state_exporter,
                port=api_port,
                command_handler=self.opcode_handler.dispatch,
                device_state_ref=[self.device_state],
                param_command_handler=self.opcode_handler.dispatch_with_param,
                serial_write=self.serial_bridge.write_response,
            )
        
        logger.info(f"Emulator engine initialized on {port}")
    
    def _process_command(self, cmd_bytes: bytes, param_str: str = "") -> list:
        """
        Process received command.

        Args:
            cmd_bytes: The 5-byte opcode frame.
            param_str: Optional parameter string from a second 5-byte frame
                       (only for parameter opcodes like TPGDI, TPRSP, etc.).

        Returns a list of 5-byte response frames (may be empty, single, or multi).
        """
        print(f"[DBG-SERIAL] _process_command: raw={cmd_bytes!r} param={param_str!r}", flush=True)
        if not CommandParser.is_valid_command(cmd_bytes):
            logger.warning(f"Invalid command format: {cmd_bytes}")
            print(f"[DBG-SERIAL] rejected invalid command", flush=True)
            return [b'FLS  ']

        opcode = CommandParser.parse(cmd_bytes)
        print(f"[DBG-SERIAL] opcode={opcode!r}", flush=True)

        try:
            # Use param dispatch if a parameter was provided
            if param_str:
                response, self.device_state = self.opcode_handler.dispatch_with_param(
                    opcode, self.device_state, param_str
                )
            else:
                response, self.device_state = self.opcode_handler.dispatch(opcode, self.device_state)

            # Log the command to device state for tracking in UI
            self.device_state.log_command(opcode)

            # Sync exporter's state reference to the new state object
            if self.state_exporter is not None:
                self.state_exporter._state = self.device_state
                print(f"[DBG-SERIAL] exporter synced: last_command={self.state_exporter._state.last_command!r}", flush=True)

            # Apply configurable delay for mechanical operations
            delay = self.opcode_handler.get_delay(opcode)
            if delay > 0:
                time.sleep(delay)

            # Normalize response to a list of strings
            if isinstance(response, list):
                resp_strings = response
            elif response:
                resp_strings = [response]
            else:
                resp_strings = []

            # Convert each response string to a 5-byte padded frame
            frames = []
            for r in resp_strings:
                frame = r.encode('ascii').ljust(5, b' ')[:5]
                frames.append(frame)
            return frames

        except Exception as e:
            logger.error(f"Error processing opcode {opcode}: {e}")
            print(f"[DBG-SERIAL] EXCEPTION: {e}", flush=True)
            return [b'FLS  ']
    
    def _log_transaction(self, cmd_bytes: bytes, response: bytes):
        """Log command/response transaction."""
        opcode = CommandParser.parse(cmd_bytes) if CommandParser.is_valid_command(cmd_bytes) else "???"
        
        if self.hex_output:
            cmd_hex = ' '.join(f'{b:02X}' for b in cmd_bytes)
            resp_hex = ' '.join(f'{b:02X}' for b in response)
            msg = f"RECV: [{cmd_hex}] -> SEND: [{resp_hex}]"
        else:
            cmd_str = cmd_bytes.decode('ascii', errors='replace')
            resp_str = response.decode('ascii', errors='replace')
            msg = f"RECV: {cmd_str} -> SEND: {resp_str}"
        
        if self.verbose:
            try:
                print(f"[{opcode}] {msg}")
            except UnicodeEncodeError:
                # Fallback for Windows terminals that don't support UTF-8
                print(f"[{opcode}] {msg}".encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding))
        
        logger.info(msg)
    
    def run(self):
        """Start main event loop"""
        logger.info("=== Emulator Started ===")
        print(f"Emulator running on {self.port} at {self.baudrate} baud")
        
        # Start API server if enabled
        if self.enable_api and self.api_server:
            self.api_server.start()
            print(f"API server started on http://localhost:{self.api_server._port}")
        
        print("Waiting for commands... (Ctrl+C to stop)")
        
        self.running = True
        try:
            while self.running:
                cmd_bytes = self.serial_bridge.read_command()
                
                if cmd_bytes is not None:
                    # Check if this opcode expects a parameter frame
                    param_str = ""
                    if CommandParser.is_valid_command(cmd_bytes):
                        opcode = CommandParser.parse(cmd_bytes).upper()
                        if opcode in PARAM_OPCODES:
                            # Read variable-length numeric parameter
                            param_str = self.serial_bridge.read_param() or ""
                            logger.info(f"[SERIAL-RX] opcode={opcode} param={param_str!r}")
                            print(f"[SERIAL-RX] opcode={opcode} param={param_str!r}", flush=True)
                        else:
                            logger.info(f"[SERIAL-RX] opcode={opcode}")
                            print(f"[SERIAL-RX] opcode={opcode}", flush=True)
                    else:
                        logger.warning(f"[SERIAL-RX] invalid frame: {cmd_bytes!r}")
                        print(f"[SERIAL-RX] invalid frame: {cmd_bytes!r}", flush=True)

                    response_frames = self._process_command(cmd_bytes, param_str)
                    
                    for frame in response_frames:
                        if self.serial_bridge.write_response(frame):
                            resp_str = frame.decode('ascii', errors='replace').strip()
                            logger.info(f"[SERIAL-TX] {resp_str!r}")
                            print(f"[SERIAL-TX] -> {resp_str!r}", flush=True)
                            self._log_transaction(cmd_bytes, frame)
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

def create_parser():
    """Create argument parser for emulator CLI"""
    parser = argparse.ArgumentParser(description="Vision System Firmware Emulator")
    parser.add_argument('--port', required=True, help='Serial port (e.g., COM3)')
    parser.add_argument('--baudrate', type=int, default=115200, help='Baud rate (default 115200)')
    parser.add_argument('--verbose', action='store_true', help='Print human-readable commands')
    parser.add_argument('--hex', action='store_true', dest='hex_output', help='Print hex bytes instead of ASCII')
    parser.add_argument('--rtscts', action='store_true', help='Enable RTS/CTS flow control')
    parser.add_argument('--dsrdtr', action='store_true', help='Enable DSR/DTR flow control')
    parser.add_argument('--xonxoff', action='store_true', help='Enable XON/XOFF flow control')
    parser.add_argument('--api-port', type=int, default=5000, help='API server port (default 5000)')
    parser.add_argument('--no-api', action='store_true', help='Disable HTTP API server')
    parser.add_argument('--debug', nargs='*', default=[], help='Debug breakpoint opcodes (Phase 2)')
    parser.add_argument('--interactive', action='store_true', help='Interactive monitor mode (Phase 2)')
    return parser

def main():
    """Entry point for emulator"""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    setup_logging()
    
    # Create and run emulator
    engine = EmulatorEngine(port=args.port, baudrate=args.baudrate, verbose=args.verbose, hex_output=args.hex_output,
                           rtscts=args.rtscts, dsrdtr=args.dsrdtr, xonxoff=args.xonxoff,
                           api_port=args.api_port, enable_api=not args.no_api)
    
    logger.info(f"Command line args: {args}")
    
    try:
        engine.run()
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
