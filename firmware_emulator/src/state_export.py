"""State Exporter for Vision System Firmware Emulator.

Converts DeviceState to dictionary and JSON formats for the HTTP API.
Adds _metadata (timestamp, version) to every export. Provides a
compact summary export for high-frequency polling.

Does NOT modify DeviceState — read-only access.
"""

import json
import time
from typing import Any, Dict
from dataclasses import asdict
from enum import Enum

from firmware_emulator.src.device_state import DeviceState

API_VERSION = "1.0"


class StateExporter:
    """Export DeviceState as dict/JSON for API consumption.

    Args:
        device_state: Shared DeviceState instance (read-only access).
    """

    def __init__(self, device_state: DeviceState):
        self._state = device_state

    def get_state_dict(self) -> Dict[str, Any]:
        """Export full device state as dictionary with metadata.

        Returns:
            Dict containing _metadata (timestamp, version) and all
            DeviceState fields. Enums are string values, nested
            dataclasses are nested dicts.
        """
        state_dict = self._state.to_dict()
        # Convert enum values to strings
        def convert_enums(obj):
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_enums(item) for item in obj]
            return obj
        
        state_dict = convert_enums(state_dict)
        state_dict["_metadata"] = {
            "timestamp": time.time(),
            "version": API_VERSION,
        }
        return state_dict

    def get_state_json(self) -> str:
        """Export full device state as JSON string.

        Returns:
            Valid UTF-8 JSON string, indented for readability.
        """
        return json.dumps(self.get_state_dict(), indent=2)

    def export_summary(self) -> Dict[str, Any]:
        """Export compact essential-only state for high-frequency polling.

        Returns only the fields needed for real-time UI updates:
        guide positions, reeler speeds, sag sensors, lamps, camera
        flags, system status, emulator control state, and last command.

        Returns:
            Compact dict — significantly smaller than full state.
        """
        s = self._state
        return {
            "guide_top": s.guide_top.position.value,
            "guide_bottom": s.guide_bottom.position.value,
            "reeler_top_speed": s.reeler_top.speed,
            "reeler_bottom_speed": s.reeler_bottom.speed,
            "sag_top_upper": s.sag_top_upper,
            "sag_top_lower": s.sag_top_lower,
            "sag_bottom_upper": s.sag_bottom_upper,
            "sag_bottom_lower": s.sag_bottom_lower,
            "lamps": asdict(s.lamps),
            "button_lamps": asdict(s.button_lamps),
            "camera_flags": {str(k): v for k, v in s.cameras.flags.items()},
            "door_locked": s.door_locked,
            "estop_pressed": s.estop_pressed,
            "power_on": s.power_on,
            "last_command": s.last_command,
            "run_state": s.run_state.value,
            "buzzer_override": s.buzzer_override,
            "query_responsive": s.query_responsive,
            "light_channels": dict(s.light_channels),
        }
