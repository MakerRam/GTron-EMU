import pytest
from unittest.mock import Mock, patch, MagicMock, PropertyMock, call
from firmware_emulator.src.serial_bridge import SerialBridge


def _make_bridge(mock_serial, in_waiting_sequence=None):
    """Helper: create a SerialBridge with a mocked serial.Serial.

    Args:
        mock_serial: The patched serial.Serial class.
        in_waiting_sequence: List of int values returned by successive
            accesses to ``in_waiting``.  If *None*, defaults to ``[0]``
            (nothing waiting initially).

    Returns:
        (bridge, mock_port) tuple.
    """
    mock_port = MagicMock()
    mock_port.is_open = True
    mock_serial.return_value = mock_port

    if in_waiting_sequence is not None:
        type(mock_port).in_waiting = PropertyMock(side_effect=in_waiting_sequence)
    else:
        type(mock_port).in_waiting = PropertyMock(return_value=0)

    bridge = SerialBridge(port="COM3", baudrate=9600, timeout=1.0)
    return bridge, mock_port


class TestSerialBridge:
    """Test serial communication layer"""

    # ------------------------------------------------------------------
    # Initialisation
    # ------------------------------------------------------------------

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_init_opens_port(self, mock_serial):
        """SerialBridge should open COM port on initialization."""
        bridge, mock_port = _make_bridge(mock_serial)
        assert bridge.is_open() is True
        mock_serial.assert_called_once()

    # ------------------------------------------------------------------
    # Single opcode reads
    # ------------------------------------------------------------------

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_read_single_opcode_from_waiting(self, mock_serial):
        """5 bytes already in OS buffer → returned immediately."""
        bridge, mock_port = _make_bridge(mock_serial, in_waiting_sequence=[5])
        mock_port.read.return_value = b'QUERY'

        cmd = bridge.read_command()

        assert cmd == b'QUERY'
        assert len(cmd) == 5

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_read_single_opcode_blocking(self, mock_serial):
        """Nothing waiting → blocking read returns 5 bytes."""
        bridge, mock_port = _make_bridge(mock_serial, in_waiting_sequence=[0])
        mock_port.read.return_value = b'SMINI'

        cmd = bridge.read_command()

        assert cmd == b'SMINI'

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_read_returns_none_on_timeout(self, mock_serial):
        """Timeout (no data at all) → returns None."""
        bridge, mock_port = _make_bridge(mock_serial, in_waiting_sequence=[0])
        mock_port.read.return_value = b''

        cmd = bridge.read_command()
        assert cmd is None

    # ------------------------------------------------------------------
    # Newline handling
    # ------------------------------------------------------------------

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_trailing_newline_stripped(self, mock_serial):
        """Opcode followed by \\n → newline consumed, opcode returned."""
        # 6 bytes waiting: 5 opcode + 1 newline
        bridge, mock_port = _make_bridge(mock_serial, in_waiting_sequence=[6])
        mock_port.read.return_value = b'QUERY\n'

        cmd = bridge.read_command()

        assert cmd == b'QUERY'

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_leading_newline_stripped_on_blocking_read(self, mock_serial):
        """Blocking read returns \\n + 5 bytes → newline stripped, opcode returned."""
        bridge, mock_port = _make_bridge(mock_serial, in_waiting_sequence=[0])
        # Blocking read for 5 bytes actually returns \n + 4 bytes,
        # then we need 1 more byte on next blocking read
        mock_port.read.side_effect = [b'\nQUER', b'Y']

        cmd = bridge.read_command()

        assert cmd == b'QUERY'

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_consecutive_commands_with_newlines(self, mock_serial):
        """Two opcodes each followed by \\n → both extracted correctly."""
        # First call: 11 bytes waiting (QUERY\\nSMINI)
        # After extracting QUERY, 6 bytes remain (\\nSMINI)
        # Second call: in_waiting=0 but buffer has data
        bridge, mock_port = _make_bridge(
            mock_serial, in_waiting_sequence=[11, 0]
        )
        mock_port.read.side_effect = [b'QUERY\nSMINI']

        cmd1 = bridge.read_command()
        assert cmd1 == b'QUERY'

        cmd2 = bridge.read_command()
        assert cmd2 == b'SMINI'

    # ------------------------------------------------------------------
    # Burst-send: multiple opcodes arrive in one OS read
    # ------------------------------------------------------------------

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_burst_two_opcodes_no_newlines(self, mock_serial):
        """Two opcodes concatenated without newlines → both extracted."""
        bridge, mock_port = _make_bridge(
            mock_serial, in_waiting_sequence=[10, 0]
        )
        mock_port.read.side_effect = [b'SMINISMINI']

        cmd1 = bridge.read_command()
        assert cmd1 == b'SMINI'

        cmd2 = bridge.read_command()
        assert cmd2 == b'SMINI'

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_burst_three_opcodes_no_newlines(self, mock_serial):
        """Three opcodes in one burst → all three extracted in order."""
        bridge, mock_port = _make_bridge(
            mock_serial, in_waiting_sequence=[15, 0, 0]
        )
        mock_port.read.side_effect = [b'SMINIDHBLSQUERY']

        cmd1 = bridge.read_command()
        assert cmd1 == b'SMINI'

        cmd2 = bridge.read_command()
        assert cmd2 == b'DHBLS'

        cmd3 = bridge.read_command()
        assert cmd3 == b'QUERY'

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_burst_with_trailing_partial(self, mock_serial):
        """Burst of 2.5 opcodes → first two extracted, third completes on next read."""
        # 12 bytes: SMINIDHBLS + tp (partial)
        # Then 3 more bytes arrive: RSP
        bridge, mock_port = _make_bridge(
            mock_serial, in_waiting_sequence=[12, 0, 3]
        )
        mock_port.read.side_effect = [
            b'SMINIDHBLStp',  # Drain: 12 bytes
            b'RSP',           # Blocking read for remaining 3
            b'RSP',           # Drain: 3 bytes from in_waiting
        ]

        cmd1 = bridge.read_command()
        assert cmd1 == b'SMINI'

        cmd2 = bridge.read_command()
        assert cmd2 == b'DHBLS'

        cmd3 = bridge.read_command()
        assert cmd3 == b'tpRSP'

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_burst_with_newlines_between(self, mock_serial):
        """Burst with \\n between opcodes → newlines stripped, opcodes correct."""
        # SMINI\nDHBLS\n = 12 bytes
        bridge, mock_port = _make_bridge(
            mock_serial, in_waiting_sequence=[12, 0]
        )
        mock_port.read.side_effect = [b'SMINI\nDHBLS\n']

        cmd1 = bridge.read_command()
        assert cmd1 == b'SMINI'

        cmd2 = bridge.read_command()
        assert cmd2 == b'DHBLS'

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_burst_labview_scenario(self, mock_serial):
        """Reproduce the real LabVIEW burst from the capture: SMINIDHBLSDHBLStpRSP..."""
        # 17 bytes arrive in first read: SMINI DHBLS DHBLS tp
        # Then 8 bytes arrive: RSP\nENItp  (5 bytes for tpRSP + leftover)
        bridge, mock_port = _make_bridge(
            mock_serial, in_waiting_sequence=[17, 0, 3, 0]
        )
        mock_port.read.side_effect = [
            b'SMINIDHBLSDHBLStp',  # First burst
            b'RSP',                # Blocking completes tpRSP
        ]

        cmd1 = bridge.read_command()
        assert cmd1 == b'SMINI'

        cmd2 = bridge.read_command()
        assert cmd2 == b'DHBLS'

        cmd3 = bridge.read_command()
        assert cmd3 == b'DHBLS'

        cmd4 = bridge.read_command()
        assert cmd4 == b'tpRSP'

    # ------------------------------------------------------------------
    # Partial reads
    # ------------------------------------------------------------------

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_partial_read_returns_none(self, mock_serial):
        """Less than 5 bytes and no more arriving → returns None."""
        bridge, mock_port = _make_bridge(mock_serial, in_waiting_sequence=[3])
        mock_port.read.side_effect = [b'QUE', b'']  # Drain 3, blocking returns nothing

        cmd = bridge.read_command()
        assert cmd is None

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_partial_then_complete(self, mock_serial):
        """3 bytes arrive, then 2 more on blocking read → frame extracted."""
        bridge, mock_port = _make_bridge(mock_serial, in_waiting_sequence=[3])
        mock_port.read.side_effect = [b'QUE', b'RY']

        cmd = bridge.read_command()
        assert cmd == b'QUERY'

    # ------------------------------------------------------------------
    # Write
    # ------------------------------------------------------------------

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_write_response(self, mock_serial):
        """write_response sends bytes and returns True on success."""
        bridge, mock_port = _make_bridge(mock_serial)
        mock_port.write.return_value = 3

        success = bridge.write_response(b'YES')

        assert success is True
        mock_port.write.assert_called_once_with(b'YES')

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_write_response_5byte_frame(self, mock_serial):
        """write_response sends a full 5-byte frame."""
        bridge, mock_port = _make_bridge(mock_serial)
        mock_port.write.return_value = 5

        success = bridge.write_response(b'FLS  ')

        assert success is True
        mock_port.write.assert_called_once_with(b'FLS  ')

    # ------------------------------------------------------------------
    # Context manager
    # ------------------------------------------------------------------

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_context_manager_support(self, mock_serial):
        """SerialBridge should support 'with' statement."""
        bridge, mock_port = _make_bridge(mock_serial)

        with bridge:
            assert bridge.is_open() is True

        mock_port.close.assert_called_once()

    # ------------------------------------------------------------------
    # Edge cases
    # ------------------------------------------------------------------

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_only_newlines_returns_none(self, mock_serial):
        """Buffer contains only newlines → all stripped, returns None."""
        bridge, mock_port = _make_bridge(mock_serial, in_waiting_sequence=[3])
        mock_port.read.side_effect = [b'\n\r\n', b'']

        cmd = bridge.read_command()
        assert cmd is None

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_multiple_newlines_between_opcodes(self, mock_serial):
        """Multiple \\r\\n between opcodes → all stripped."""
        data = b'SMINI\r\n\r\nDHBLS'  # 14 bytes
        bridge, mock_port = _make_bridge(
            mock_serial, in_waiting_sequence=[len(data), 0]
        )
        mock_port.read.side_effect = [data]

        cmd1 = bridge.read_command()
        assert cmd1 == b'SMINI'

        cmd2 = bridge.read_command()
        assert cmd2 == b'DHBLS'
    
    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_multiple_newlines_between_opcodes_v2(self, mock_serial):
        """Multiple \\r\\n between opcodes → all stripped."""
        data = b'SMINI\r\n\r\nDHBLS'  # 14 bytes
        bridge, mock_port = _make_bridge(
            mock_serial, in_waiting_sequence=[len(data), 0]
        )
        mock_port.read.side_effect = [data]

        cmd1 = bridge.read_command()
        assert cmd1 == b'SMINI'

        cmd2 = bridge.read_command()
        assert cmd2 == b'DHBLS'

    @patch('firmware_emulator.src.serial_bridge.serial.Serial')
    def test_buffer_persists_across_calls(self, mock_serial):
        """Internal buffer persists between read_command() calls."""
        # 7 bytes: SMINI + 2 leftover from next opcode
        bridge, mock_port = _make_bridge(
            mock_serial, in_waiting_sequence=[7, 0]
        )
        mock_port.read.side_effect = [b'SMINIDH', b'BLS']

        cmd1 = bridge.read_command()
        assert cmd1 == b'SMINI'

        # Buffer has 'DH', blocking read adds 'BLS'
        cmd2 = bridge.read_command()
        assert cmd2 == b'DHBLS'
