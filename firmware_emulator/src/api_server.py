"""API Server for Vision System Firmware Emulator.

Provides a Flask HTTP REST API that exposes device state to
visualization clients. Runs in a background daemon thread so it
does not block the main serial communication loop.

Endpoints:
  GET /api/state         -> Full device state with metadata
  GET /api/state/summary -> Compact essential-only state
  GET /health            -> Health check {status, api_version}

All responses include CORS headers for browser access.
"""

import logging
import threading
from typing import Optional

from flask import Flask, jsonify
from flask_cors import CORS

from firmware_emulator.src.state_export import StateExporter

logger = logging.getLogger(__name__)


def create_app(exporter: StateExporter) -> Flask:
    """Create and configure Flask application.

    Args:
        exporter: StateExporter instance for reading device state.

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

    return app


class APIServer:
    """Wrapper that runs the Flask API in a background daemon thread.

    Args:
        exporter: StateExporter instance for reading device state.
        port: TCP port to bind to (default 5000).
        host: Host to bind to (default "0.0.0.0" for all interfaces).
    """

    def __init__(
        self,
        exporter: StateExporter,
        port: int = 5000,
        host: str = "0.0.0.0",
    ):
        self._app = create_app(exporter)
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
