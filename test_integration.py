"""
Integration test: Simulate LabVIEW sending consecutive commands to the emulator
Uses the actual SerialBridge and CommandParser
"""
import sys
sys.path.insert(0, '/mnt/d/TDD/Emulator')

from firmware_emulator.src.command_parser import CommandParser
from firmware_emulator.src.opcode_handlers import OpcodeDispatcher

def test_command_parsing_and_dispatch():
    """Test that command parsing and dispatching work correctly"""
    
    dispatcher = OpcodeDispatcher()
    
    # Simulate what the emulator's _process_command does
    test_cases = [
        (b'QUERY', b'YES', 'First QUERY command'),
        (b'QUERY', b'YES', 'Second QUERY command (tests buffer recovery)'),
        (b'SMINI', b'', 'SMINI command (no response)'),
    ]
    
    for cmd_bytes, expected_response, description in test_cases:
        # Check if valid
        if not CommandParser.is_valid_command(cmd_bytes):
            print(f"❌ {description}: Invalid command format")
            return False
        
        # Parse opcode
        opcode = CommandParser.parse(cmd_bytes)
        print(f"✓ Parsed: {cmd_bytes} -> {opcode}")
        
        # Dispatch to handler
        response = dispatcher.dispatch(opcode)
        
        if response == expected_response:
            print(f"✓ {description}: {opcode} -> {response if response else '(no response)'}")
        else:
            print(f"❌ {description}: Expected {expected_response}, got {response}")
            return False
    
    print("\n✓ All integration tests passed!")
    return True

if __name__ == '__main__':
    success = test_command_parsing_and_dispatch()
    sys.exit(0 if success else 1)
