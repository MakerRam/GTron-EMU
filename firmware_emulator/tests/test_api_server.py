"""Tests for APIServer - TDD Red Phase.

APIServer wraps Flask with three endpoints:
  GET /api/state         -> full state JSON
  GET /api/state/summary -> compact summary JSON
  GET /health            -> health check

Uses Flask test client — no real HTTP server needed.
"""

import json
import pytest
import sys
import os

from firmware_emulator.src.device_state import DeviceState, GuidePosition
from firmware_emulator.src.state_export import StateExporter
from firmware_emulator.src.api_server import create_app


# --- Fixtures ---

@pytest.fixture
def state():
    """Fresh DeviceState."""
    return DeviceState()


@pytest.fixture
def exporter(state):
    """StateExporter wrapping a fresh DeviceState."""
    return StateExporter(state)


@pytest.fixture
def client(exporter):
    """Flask test client for APIServer."""
    app = create_app(exporter)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# --- Health Endpoint Tests ---

class TestHealthEndpoint:
    """/health returns status and version."""

    def test_returns_200(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200

    def test_returns_json(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data is not None

    def test_status_ok(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data["status"] == "ok"

    def test_api_version(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        assert data["api_version"] == "1.0"


# --- Full State Endpoint Tests ---

class TestStateEndpoint:
    """/api/state returns full device state."""

    def test_returns_200(self, client):
        resp = client.get("/api/state")
        assert resp.status_code == 200

    def test_returns_json(self, client):
        resp = client.get("/api/state")
        data = resp.get_json()
        assert isinstance(data, dict)

    def test_includes_metadata(self, client):
        resp = client.get("/api/state")
        data = resp.get_json()
        assert "_metadata" in data

    def test_includes_guide_top(self, client):
        resp = client.get("/api/state")
        data = resp.get_json()
        assert "guide_top" in data
        assert data["guide_top"]["position"] == "closed"

    def test_includes_cameras(self, client):
        resp = client.get("/api/state")
        data = resp.get_json()
        assert "cameras" in data

    def test_includes_lamps(self, client):
        resp = client.get("/api/state")
        data = resp.get_json()
        assert "lamps" in data

    def test_reflects_state_changes(self, client, state):
        state.guide_top.position = GuidePosition.OPEN
        resp = client.get("/api/state")
        data = resp.get_json()
        assert data["guide_top"]["position"] == "open"

    def test_content_type_json(self, client):
        resp = client.get("/api/state")
        assert resp.content_type.startswith("application/json")


# --- Summary Endpoint Tests ---

class TestSummaryEndpoint:
    """/api/state/summary returns compact state."""

    def test_returns_200(self, client):
        resp = client.get("/api/state/summary")
        assert resp.status_code == 200

    def test_returns_json(self, client):
        resp = client.get("/api/state/summary")
        data = resp.get_json()
        assert isinstance(data, dict)

    def test_includes_guide_positions(self, client):
        resp = client.get("/api/state/summary")
        data = resp.get_json()
        assert "guide_top" in data
        assert "guide_bottom" in data

    def test_includes_reeler_speeds(self, client):
        resp = client.get("/api/state/summary")
        data = resp.get_json()
        assert "reeler_top_speed" in data

    def test_includes_lamps(self, client):
        resp = client.get("/api/state/summary")
        data = resp.get_json()
        assert "lamps" in data

    def test_summary_smaller_than_full(self, client):
        full_resp = client.get("/api/state")
        summary_resp = client.get("/api/state/summary")
        assert len(summary_resp.data) < len(full_resp.data)


# --- CORS Tests ---

class TestCors:
    """Responses include CORS headers for browser access."""

    def test_state_has_cors_header(self, client):
        resp = client.get("/api/state")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"

    def test_health_has_cors_header(self, client):
        resp = client.get("/health")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"

    def test_summary_has_cors_header(self, client):
        resp = client.get("/api/state/summary")
        assert resp.headers.get("Access-Control-Allow-Origin") == "*"


# --- Error Handling Tests ---

class TestErrorHandling:
    """Unknown routes return 404."""

    def test_unknown_route_returns_404(self, client):
        resp = client.get("/api/unknown")
        assert resp.status_code == 404
