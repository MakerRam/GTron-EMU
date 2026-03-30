"""
start.py — Unified entry point for the Vision System Firmware Emulator.

Starts all three services with a single command:
  python start.py --port COM2

Services started:
  1. Firmware emulator + Flask API server (subprocess, port 5000)
  2. Visualizer HTTP server (daemon thread, port 8000)

Usage:
  python start.py --port COM2
  python start.py --port COM2 --api-port 5001 --visualizer-port 8001
  python start.py --port COM2 --rtscts
"""

import argparse
import http.server
import os
import platform
import socket
import socketserver
import subprocess
import sys
import threading
import time
import webbrowser
from pathlib import Path


# ── Helpers ──────────────────────────────────────────────────────────────────

def check_port_free(port: int) -> bool:
    """Return True if the given TCP port is available (nothing is listening on it)."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        try:
            s.connect(("127.0.0.1", port))
            # Connection succeeded → something is already listening → not free
            return False
        except (ConnectionRefusedError, OSError):
            # Connection refused or timeout → port is free
            return True


def port_hint(port: int) -> str:
    """Return a platform-specific hint for finding what owns a port."""
    if platform.system() == "Windows":
        return f"  Run: netstat -ano | findstr :{port}"
    return f"  Run: lsof -i :{port}"


# ── Visualizer HTTP server ────────────────────────────────────────────────────

class _SilentHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP handler that suppresses per-request log lines."""

    def log_message(self, format, *args):  # noqa: A002
        pass  # suppress request logs to keep console clean


def start_visualizer_server(port: int, directory: str) -> socketserver.TCPServer:
    """
    Start Python's built-in HTTP server in a daemon thread.

    Returns the TCPServer instance (call .shutdown() to stop).
    """
    os.chdir(directory)  # SimpleHTTPRequestHandler serves from cwd
    handler = _SilentHandler
    server = socketserver.TCPServer(("", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


# ── Argument parsing ──────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Vision System Firmware Emulator — unified launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start.py --port COM2
  python start.py --port COM2 --api-port 5001 --visualizer-port 8001
  python start.py --port /dev/ttyS1 --baudrate 9600
        """,
    )
    parser.add_argument("--port", required=True, help="Serial COM port (e.g. COM2 or /dev/ttyS1)")
    parser.add_argument("--baudrate", type=int, default=115200, help="Baud rate (default: 115200)")
    parser.add_argument("--api-port", type=int, default=5000, dest="api_port",
                        help="Flask API server port (default: 5000)")
    parser.add_argument("--visualizer-port", type=int, default=8000, dest="visualizer_port",
                        help="Visualizer HTTP server port (default: 8000)")
    parser.add_argument("--rtscts", action="store_true", help="Enable RTS/CTS flow control")
    parser.add_argument("--dsrdtr", action="store_true", help="Enable DSR/DTR flow control")
    parser.add_argument("--verbose", action="store_true", help="Pass --verbose to emulator")
    parser.add_argument("--no-browser", action="store_true", dest="no_browser",
                        help="Do not auto-open browser on startup")
    return parser


# ── Startup banner ────────────────────────────────────────────────────────────

def print_banner(args: argparse.Namespace) -> None:
    sep = "=" * 60
    print(sep)
    print("  Vision System Firmware Emulator — Unified Launcher")
    print(sep)
    print(f"  Serial port  : {args.port}  ({args.baudrate} baud)")
    print(f"  API server   : http://localhost:{args.api_port}")
    print(f"  Visualizer   : http://localhost:{args.visualizer_port}/index.html")
    print(sep)
    print("  Press Ctrl+C to stop all services.")
    print()


# ── Emulator subprocess ───────────────────────────────────────────────────────

def start_emulator(args: argparse.Namespace) -> subprocess.Popen:
    """Launch the firmware emulator as a subprocess."""
    project_root = Path(__file__).parent
    cmd = [
        sys.executable,
        "-m", "firmware_emulator.src.main",
        "--port", args.port,
        "--baudrate", str(args.baudrate),
        "--api-port", str(args.api_port),
    ]
    if args.rtscts:
        cmd.append("--rtscts")
    if args.dsrdtr:
        cmd.append("--dsrdtr")
    if args.verbose:
        cmd.append("--verbose")

    return subprocess.Popen(
        cmd,
        cwd=str(project_root),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )


def stream_emulator_output(proc: subprocess.Popen) -> None:
    """Stream emulator stdout to the console in a daemon thread."""
    def _reader():
        for line in iter(proc.stdout.readline, ""):
            if line:
                print(f"[EMU] {line.rstrip()}", flush=True)
    t = threading.Thread(target=_reader, daemon=True)
    t.start()


# ── Shutdown ──────────────────────────────────────────────────────────────────

def shutdown(proc: subprocess.Popen, viz_server: socketserver.TCPServer) -> None:
    """Stop all services cleanly."""
    print("\n[INFO] Shutting down all services...")

    if proc and proc.poll() is None:
        proc.terminate()
        try:
            proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            proc.kill()
            print("[WARN] Emulator force-killed.")

    if viz_server:
        viz_server.shutdown()

    print("[INFO] All services stopped.")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    project_root = Path(__file__).parent

    # 1. Port conflict detection
    for label, port in [("API server", args.api_port), ("Visualizer", args.visualizer_port)]:
        if not check_port_free(port):
            print(f"[ERROR] {label} port {port} is already in use.")
            print(port_hint(port))
            sys.exit(1)

    # 2. Print startup banner
    print_banner(args)

    # 3. Start visualizer HTTP server in daemon thread
    visualizer_dir = str(project_root / "visualizer")
    if not Path(visualizer_dir).is_dir():
        print(f"[ERROR] Visualizer directory not found: {visualizer_dir}")
        sys.exit(1)

    viz_server = start_visualizer_server(args.visualizer_port, visualizer_dir)
    print(f"[OK] Visualizer server started on port {args.visualizer_port}")

    # 4. Start emulator subprocess
    print(f"[OK] Starting emulator on {args.port}...")
    proc = start_emulator(args)
    stream_emulator_output(proc)

    # 5. Health-check: give emulator 3 seconds to confirm it didn't immediately crash
    time.sleep(3)
    if proc.poll() is not None:
        # Emulator exited early — collect remaining output
        remaining = proc.stdout.read()
        if remaining:
            for line in remaining.splitlines():
                print(f"[EMU] {line}", flush=True)
        print(f"\n[ERROR] Emulator exited unexpectedly (code {proc.returncode}).")
        print("[INFO] Check the port name and ensure the virtual COM port pair is active.")
        viz_server.shutdown()
        sys.exit(1)

    print(f"[OK] Emulator running. Open your browser:")
    print(f"     http://localhost:{args.visualizer_port}/index.html")
    print()

    # 6. Auto-open browser unless --no-browser was passed
    if not args.no_browser:
        url = f"http://localhost:{args.visualizer_port}/index.html"
        print(f"[OK] Opening browser: {url}")
        webbrowser.open(url)

    # 7. Main wait loop — block until Ctrl+C or emulator dies
    try:
        while True:
            if proc.poll() is not None:
                print(f"\n[WARN] Emulator process exited (code {proc.returncode}).")
                break
            time.sleep(0.5)
    except KeyboardInterrupt:
        pass
    finally:
        shutdown(proc, viz_server)


if __name__ == "__main__":
    main()
