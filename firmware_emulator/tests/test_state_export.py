"""Tests for StateExporter - TDD Red Phase.

StateExporter converts DeviceState to dict/JSON for API consumption.
Adds _metadata with timestamp and version. export_summary() returns
a compact subset of essential fields.
"""

import json
import time
import pytest
import sys
import os

from firmware_emulator.src.device_state import DeviceState, GuidePosition
from firmware_emulator.src.state_export import StateExporter


# --- Fixtures ---

@pytest.fixture
def state():
    """Fresh DeviceState."""
    return DeviceState()


@pytest.fixture
def exporter(state):
    """StateExporter wrapping a fresh DeviceState."""
    return StateExporter(state)


# --- get_state_dict Tests ---

class TestGetStateDict:
    """get_state_dict returns full state with metadata."""

    def test_returns_dict(self, exporter):
        result = exporter.get_state_dict()
        assert isinstance(result, dict)

    def test_includes_metadata(self, exporter):
        result = exporter.get_state_dict()
        assert "_metadata" in result

    def test_metadata_has_timestamp(self, exporter):
        before = time.time()
        result = exporter.get_state_dict()
        after = time.time()
        ts = result["_metadata"]["timestamp"]
        assert before <= ts <= after

    def test_metadata_has_version(self, exporter):
        result = exporter.get_state_dict()
        assert result["_metadata"]["version"] == "1.0"

    def test_includes_guide_top(self, exporter):
        result = exporter.get_state_dict()
        assert "guide_top" in result
        assert result["guide_top"]["position"] == "closed"

    def test_includes_guide_bottom(self, exporter):
        result = exporter.get_state_dict()
        assert "guide_bottom" in result

    def test_includes_reeler_top(self, exporter):
        result = exporter.get_state_dict()
        assert "reeler_top" in result
        assert result["reeler_top"]["speed"] == 0

    def test_includes_cameras(self, exporter):
        result = exporter.get_state_dict()
        assert "cameras" in result
        assert "flags" in result["cameras"]

    def test_includes_lamps(self, exporter):
        result = exporter.get_state_dict()
        assert "lamps" in result
        assert result["lamps"]["green"] is True

    def test_includes_sag_sensors(self, exporter):
        result = exporter.get_state_dict()
        assert "sag_top_upper" in result
        assert "sag_bottom_lower" in result

    def test_includes_system_status(self, exporter):
        result = exporter.get_state_dict()
        assert "door_locked" in result
        assert "estop_pressed" in result
        assert "power_on" in result

    def test_includes_last_command(self, exporter):
        result = exporter.get_state_dict()
        assert "last_command" in result
        assert "last_command_time" in result

    def test_reflects_state_changes(self, exporter, state):
        state.guide_top.position = GuidePosition.OPEN
        result = exporter.get_state_dict()
        assert result["guide_top"]["position"] == "open"

    def test_does_not_modify_original_state(self, exporter, state):
        result = exporter.get_state_dict()
        result["guide_top"]["position"] = "TAMPERED"
        assert state.guide_top.position == GuidePosition.CLOSED


# --- get_state_json Tests ---

class TestGetStateJson:
    """get_state_json returns valid JSON string."""

    def test_returns_string(self, exporter):
        result = exporter.get_state_json()
        assert isinstance(result, str)

    def test_valid_json(self, exporter):
        result = exporter.get_state_json()
        parsed = json.loads(result)
        assert isinstance(parsed, dict)

    def test_includes_metadata(self, exporter):
        result = json.loads(exporter.get_state_json())
        assert "_metadata" in result

    def test_matches_dict(self, exporter):
        dict_result = exporter.get_state_dict()
        json_result = json.loads(exporter.get_state_json())
        # Timestamps may differ slightly between calls, so compare structure
        assert set(dict_result.keys()) == set(json_result.keys())


# --- export_summary Tests ---

class TestExportSummary:
    """export_summary returns compact essential-only state."""

    def test_returns_dict(self, exporter):
        result = exporter.export_summary()
        assert isinstance(result, dict)

    def test_includes_guide_positions(self, exporter):
        result = exporter.export_summary()
        assert "guide_top" in result
        assert "guide_bottom" in result

    def test_includes_reeler_speeds(self, exporter):
        result = exporter.export_summary()
        assert "reeler_top_speed" in result
        assert "reeler_bottom_speed" in result

    def test_includes_sag_sensors(self, exporter):
        result = exporter.export_summary()
        assert "sag_top_upper" in result
        assert "sag_top_lower" in result
        assert "sag_bottom_upper" in result
        assert "sag_bottom_lower" in result

    def test_includes_lamps(self, exporter):
        result = exporter.export_summary()
        assert "lamps" in result

    def test_includes_camera_flags(self, exporter):
        result = exporter.export_summary()
        assert "camera_flags" in result

    def test_includes_system_status(self, exporter):
        result = exporter.export_summary()
        assert "door_locked" in result
        assert "estop_pressed" in result
        assert "power_on" in result

    def test_includes_last_command(self, exporter):
        result = exporter.export_summary()
        assert "last_command" in result

    def test_summary_is_smaller_than_full(self, exporter):
        full_json = json.dumps(exporter.get_state_dict())
        summary_json = json.dumps(exporter.export_summary())
        assert len(summary_json) < len(full_json)

    def test_reflects_state_changes(self, exporter, state):
        state.guide_top.position = GuidePosition.OPEN
        result = exporter.export_summary()
        assert result["guide_top"] == "open"
