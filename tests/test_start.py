"""
Unit tests for start.py — unified launcher entry point.
"""

import socket
import subprocess
import sys
from pathlib import Path

import pytest

# Add project root to path so we can import start
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from start import check_port_free  # noqa: E402


# ── check_port_free ───────────────────────────────────────────────────────────

class TestCheckPortFree:
    def test_free_port_returns_true(self):
        """A port with nothing bound on it should be reported as free."""
        # Use a high ephemeral port unlikely to be in use
        free_port = 49800
        # Confirm nothing is bound first (might still conflict on busy systems,
        # but 49800 is almost always free)
        result = check_port_free(free_port)
        assert result is True

    def test_occupied_port_returns_false(self):
        """A port that is actively listening should be reported as not free."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
            srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            srv.bind(("127.0.0.1", 0))
            srv.listen(1)  # must call listen() so the port accepts connections
            occupied_port = srv.getsockname()[1]
            result = check_port_free(occupied_port)
        assert result is False


# ── CLI argument parsing ──────────────────────────────────────────────────────

class TestCLI:
    """Tests that exercise start.py as a subprocess to check CLI behaviour."""

    _start_script = str(PROJECT_ROOT / "start.py")

    def _run(self, *extra_args, timeout=10):
        return subprocess.run(
            [sys.executable, self._start_script, *extra_args],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

    def test_help_exits_zero(self):
        """--help should exit 0 and list all key flags."""
        result = self._run("--help")
        assert result.returncode == 0
        assert "--port" in result.stdout
        assert "--api-port" in result.stdout
        assert "--visualizer-port" in result.stdout

    def test_missing_port_exits_nonzero(self):
        """Omitting --port should exit with a non-zero code and print a usage error."""
        result = self._run()
        assert result.returncode != 0
        # argparse writes the error to stderr
        combined = result.stdout + result.stderr
        assert "required" in combined.lower() or "error" in combined.lower()
