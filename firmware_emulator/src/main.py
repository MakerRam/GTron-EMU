"""Main entry point for firmware emulator."""
import sys
import argparse
import logging
from pathlib import Path

from firmware_emulator.src import (
    get_logger,
    MachineConfig,
    SerialMonitor,
)


def create_parser() -> argparse.ArgumentParser:
    """Create and return argument parser."""
    parser = argparse.ArgumentParser(
        prog="firmware_emulator",
        description="GTRON Vision System Firmware Emulator - Virtual COM port backend daemon",
        epilog="""
Examples:
  python3 src/main.py --port COM3
  python3 src/main.py --port COM3 --verbose
  python3 src/main.py --port COM3 --verbose --hex
  python3 src/main.py --port COM3 --config /path/to/config.json --debug
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    
    parser.add_argument(
        "--port",
        required=True,
        type=str,
        help="Virtual COM port to listen on (e.g., COM3, /dev/ttyS0)",
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="Machine Interface Parameters.json",
        help="Path to Machine Interface Parameters.json (default: ./Machine Interface Parameters.json)",
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Enable human-readable console output (Level 1 monitoring)",
    )
    
    parser.add_argument(
        "--hex",
        action="store_true",
        default=False,
        help="Enable hex dump output (Level 2 monitoring)",
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        default=False,
        help="Enable debug mode with breakpoints (Phase 1: warnings, Phase 2: pauses)",
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        default=False,
        help="Enable interactive REPL console (Phase 1: stub, Phase 2: full)",
    )
    
    return parser


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Setup logging
    logger = get_logger("emulator")
    logger.info("=" * 80)
    logger.info("GTRON Vision System Firmware Emulator - Phase 1")
    logger.info("=" * 80)
    logger.info(f"Port: {args.port}")
    logger.info(f"Config: {args.config}")
    logger.info(f"Verbose: {args.verbose}, Hex: {args.hex}, Debug: {args.debug}, Interactive: {args.interactive}")
    
    # Load configuration
    try:
        config = MachineConfig(args.config)
        logger.info(f"Loaded configuration with {len(config.opcodes)} opcodes")
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)
    
    # Setup serial monitor
    monitor = SerialMonitor(
        logger=logger,
        enable_verbose=args.verbose,
        enable_hex=args.hex,
    )
    
    logger.info("Serial monitor initialized")
    
    # TODO: Initialize SerialBridge (Group 9)
    # TODO: Initialize OpcodeHandler (Group 3)
    # TODO: Initialize EmulatorEngine (Group 10)
    # TODO: Start main event loop
    
    if args.verbose:
        print(f"[STARTUP] Emulator started on {args.port}")
        print(f"[STARTUP] Configuration loaded from {args.config}")
        print(f"[STARTUP] Waiting for LabVIEW connection...")


if __name__ == "__main__":
    main()
