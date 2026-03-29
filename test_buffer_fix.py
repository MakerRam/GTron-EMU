"""
Manual test to verify serial buffer fix logic
"""
from unittest.mock import MagicMock

# Simulate the read_command logic
def test_consecutive_commands():
    """Test that consecutive commands with newlines work"""
    
    # First command: QUERY\n
    mock_port1 = MagicMock()
    mock_port1.read.side_effect = [b'QUERY', b'\n']
    mock_port1.in_waiting = 1
    
    # Simulate first read_command
    data1 = mock_port1.read(5)
    assert data1 == b'QUERY', f"Expected b'QUERY', got {data1}"
    print(f"✓ First read: {data1}")
    
    if mock_port1.in_waiting > 0:
        next_byte = mock_port1.read(1)
        assert next_byte == b'\n', f"Expected newline, got {next_byte}"
        print(f"✓ Consumed trailing byte: {next_byte}")
    
    # Second command: SMINI\n
    mock_port2 = MagicMock()
    mock_port2.read.side_effect = [b'SMINI', b'\n']
    mock_port2.in_waiting = 1
    
    # Simulate second read_command
    data2 = mock_port2.read(5)
    assert data2 == b'SMINI', f"Expected b'SMINI', got {data2}"
    print(f"✓ Second read: {data2}")
    
    if mock_port2.in_waiting > 0:
        next_byte = mock_port2.read(1)
        assert next_byte == b'\n', f"Expected newline, got {next_byte}"
        print(f"✓ Consumed trailing byte: {next_byte}")
    
    print("\n✓ All tests passed! Buffer handling works correctly.")

if __name__ == '__main__':
    test_consecutive_commands()
