"""API Server for Vision System Firmware Emulator.

Provides a Flask HTTP REST API that exposes device state to
visualization clients. Runs in a background daemon thread so it
does not block the main serial communication loop.

Endpoints:
   GET /api/state         -> Full device state with metadata
   GET /api/state/summary -> Compact essential-only state
   GET /health            -> Health check {status, api_version}
   POST /api/command      -> Send command to emulator (5-byte opcode)

All responses include CORS headers for browser access.
"""

import logging
import threading
from typing import Optional, Callable, Tuple

from flask import Flask, jsonify, request
from flask_cors import CORS

from firmware_emulator.src.state_export import StateExporter
from firmware_emulator.src.device_state import DeviceState

logger = logging.getLogger(__name__)


def create_app(exporter: StateExporter, command_handler: Optional[Callable[[str, DeviceState], Tuple[str, DeviceState]]] = None, device_state_ref: Optional[list] = None) -> Flask:
    """Create and configure Flask application.

    Args:
        exporter: StateExporter instance for reading device state.
        command_handler: Optional callable to process commands
        device_state_ref: Optional list [DeviceState] for command injection

    Returns:
        Configured Flask app with routes and CORS enabled.
    """
    app = Flask(__name__)
    CORS(app)

    @app.route("/health", methods=["GET"])
    def health():
        """Health check endpoint."""
        return jsonify({"status": "ok", "api_version": "1.0"})

    @app.route("/api/state", methods=["GET"])
    def get_state():
        """Full device state endpoint."""
        try:
            state_dict = exporter.get_state_dict()
            print(f"[DBG-STATE] /api/state: last_command={state_dict.get('last_command')!r}", flush=True)
            return jsonify(state_dict)
        except Exception as e:
            logger.error("Error exporting state: %s", e)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/state/summary", methods=["GET"])
    def get_summary():
        """Compact summary state endpoint."""
        try:
            summary = exporter.export_summary()
            return jsonify(summary)
        except Exception as e:
            logger.error("Error exporting summary: %s", e)
            return jsonify({"error": str(e)}), 500

    @app.route("/api/command", methods=["POST"])
    def send_command():
        """Send a command to the emulator.
        
        Expects JSON: {"command": "TPGOP"} (5-byte opcode string)
        Returns: {"response": "TPGOR", "responses": ["TPGOR"], "last_command": "TPGOP"}
        
        For multi-response opcodes (e.g. TPSAG), "responses" contains all frames
        and "response" contains the first one.
        """
        if not command_handler or not device_state_ref:
            print(f"[DBG-API] /api/command: 501 - command_handler={command_handler!r}, device_state_ref={device_state_ref!r}", flush=True)
            return jsonify({"error": "Command handler not configured"}), 501
        
        try:
            data = request.get_json()
            if not data or "command" not in data:
                return jsonify({"error": "Missing 'command' field"}), 400
            
            opcode = data["command"].strip().upper()
            if len(opcode) > 5:
                opcode = opcode[:5]
            
            print(f"[DBG-API] /api/command: opcode={opcode!r}", flush=True)
            
            # Get current state from exporter's internal reference
            current_state = exporter._state
            
            # Call handler (dispatch returns FLS for unknown opcodes, never raises KeyError)
            response, new_state = command_handler(opcode, current_state)
            
            # Record command in state for UI tracking (same as serial path in main.py)
            new_state.log_command(opcode)
            
            # Update exporter's state reference to point to new state
            exporter._state = new_state
            
            # Normalize response to list
            if isinstance(response, list):
                responses = response
            elif response:
                responses = [response]
            else:
                responses = []
            
            primary_response = responses[0] if responses else ""
            
            print(f"[DBG-API] /api/command: done. response={primary_response!r}, all={responses!r}", flush=True)
            logger.info(f"Command processed: {opcode} -> {responses}")
            return jsonify({
                "command": opcode,
                "response": primary_response,
                "responses": responses,
                "last_command": new_state.last_command,
                "status": "ok"
            })
        except Exception as e:
            logger.error(f"Error processing command: {e}")
            print(f"[DBG-API] /api/command: EXCEPTION: {e}", flush=True)
            return jsonify({"error": str(e)}), 500

    return app


class APIServer:
    """Wrapper that runs the Flask API in a background daemon thread.

    Args:
        exporter: StateExporter instance for reading device state.
        port: TCP port to bind to (default 5000).
        host: Host to bind to (default "0.0.0.0" for all interfaces).
        command_handler: Optional callable(opcode, state) -> (response, new_state)
        device_state_ref: Optional list containing DeviceState reference for command injection
    """

    def __init__(
        self,
        exporter: StateExporter,
        port: int = 5000,
        host: str = "0.0.0.0",
        command_handler: Optional[Callable[[str, DeviceState], Tuple[str, DeviceState]]] = None,
        device_state_ref: Optional[list] = None,
    ):
        self._app = create_app(exporter, command_handler, device_state_ref)
        self._port = port
        self._host = host
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        """Start the API server in a background daemon thread.

        The thread is a daemon, so it will be killed when the main
        process exits. Does not block the caller.
        """
        self._thread = threading.Thread(
            target=self._run,
            name="api-server",
            daemon=True,
        )
        self._thread.start()
        logger.info(
            "API server started on http://%s:%d", self._host, self._port
        )

    def _run(self) -> None:
        """Run Flask WSGI server (blocking, runs in thread)."""
        self._app.run(
            host=self._host,
            port=self._port,
            debug=False,
            use_reloader=False,
        )

    @property
    def app(self) -> Flask:
        """Access the underlying Flask app (for testing)."""
        return self._app
