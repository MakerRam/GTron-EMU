"""
Device State Machine
Tracks the complete state of the simulated hardware
"""

from enum import Enum
from dataclasses import dataclass, asdict
from typing import Dict, List, Any
import time
import json
from .logging_config import get_logger

logger = get_logger(__name__)


class GuidePosition(Enum):
    """Guide motor positions"""
    CLOSED = "closed"
    OPEN = "open"
    MOVING = "moving"
    UNKNOWN = "unknown"


class MotorState(Enum):
    """Motor operational states"""
    IDLE = "idle"
    RUNNING = "running"
    STOPPED = "stopped"


@dataclass
class GuideState:
    """Guide motor state (Top and Bottom racks)"""
    position: GuidePosition = GuidePosition.UNKNOWN
    moving: bool = False
    reached_limit: bool = False
    target_position: GuidePosition = GuidePosition.UNKNOWN


@dataclass
class ReelerState:
    """Reeler motor state"""
    speed: int = 0  # steps/sec
    teeth: int = 0  # number of teeth
    running: bool = False
    position: int = 0  # current position


@dataclass
class SensorState:
    """Trigger sensor state"""
    attached: bool = False
    powered: bool = False
    triggered: bool = False


@dataclass
class EncoderState:
    """Encoder state"""
    initialized: bool = False
    enabled: bool = False
    position: int = 0
    initial_angle: int = 0
    teeth_count: int = 0


@dataclass
class LampState:
    """Tower lamp state"""
    red: bool = False
    yellow: bool = False
    green: bool = False
    buzzer: bool = False


@dataclass
class CameraState:
    """Light-Camera sequence state"""
    flags: Dict[int, bool] = None  # 7 camera flags (0-6)
    active_sequence: int = -1
    timestamp_enabled: bool = False

    def __post_init__(self):
        if self.flags is None:
            self.flags = {i: False for i in range(7)}


class DeviceState:
    """Complete device state container"""

    def __init__(self):
        # Guide motors (Top and Bottom racks)
        self.guide_top = GuideState()
        self.guide_bottom = GuideState()

        # Reeler motors
        self.reeler_top = ReelerState()
        self.reeler_bottom = ReelerState()

        # Sensors (Top and Bottom)
        self.sensor_top = SensorState()
        self.sensor_bottom = SensorState()

        # Encoders
        self.encoder_top = EncoderState()
        self.encoder_bottom = EncoderState()

        # Lamps
        self.lamps = LampState()

        # Cameras
        self.cameras = CameraState()

        # Door lock
        self.door_locked = True

        # E-stop
        self.estop_pressed = False

        # Machine power
        self.power_on = True

        # Sag sensors
        self.sag_top_upper = False  # False = pass (sensor not triggered)
        self.sag_top_lower = False
        self.sag_bottom_upper = False
        self.sag_bottom_lower = False

        # Solenoid
        self.solenoid_top = False
        self.solenoid_bottom = False

        # Stamping relay
        self.stamping_relay = False

        # Initialization flags
        self.stepper_initialized = False
        self.reeler_initialized = False

        # Command tracking
        self.last_command = None
        self.last_command_time = None

    def reset(self):
        """Reset device to initial state"""
        self.__init__()
        logger.info("Device state reset to initial values")

    def log_command(self, command: str):
        """Track last command received"""
        self.last_command = command
        self.last_command_time = time.time()
        logger.debug(f"Command logged: {command}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize device state to dictionary.
        
        Returns:
            Dictionary representation of device state
        """
        return {
            'guide_top': asdict(self.guide_top),
            'guide_bottom': asdict(self.guide_bottom),
            'reeler_top': asdict(self.reeler_top),
            'reeler_bottom': asdict(self.reeler_bottom),
            'sensor_top': asdict(self.sensor_top),
            'sensor_bottom': asdict(self.sensor_bottom),
            'encoder_top': asdict(self.encoder_top),
            'encoder_bottom': asdict(self.encoder_bottom),
            'lamps': asdict(self.lamps),
            'cameras': {
                'flags': self.cameras.flags,
                'active_sequence': self.cameras.active_sequence,
                'timestamp_enabled': self.cameras.timestamp_enabled,
            },
            'door_locked': self.door_locked,
            'estop_pressed': self.estop_pressed,
            'power_on': self.power_on,
            'sag_top_upper': self.sag_top_upper,
            'sag_top_lower': self.sag_top_lower,
            'sag_bottom_upper': self.sag_bottom_upper,
            'sag_bottom_lower': self.sag_bottom_lower,
            'solenoid_top': self.solenoid_top,
            'solenoid_bottom': self.solenoid_bottom,
            'stamping_relay': self.stamping_relay,
            'stepper_initialized': self.stepper_initialized,
            'reeler_initialized': self.reeler_initialized,
            'last_command': self.last_command,
            'last_command_time': self.last_command_time,
        }

    def to_json(self) -> str:
        """
        Serialize device state to JSON string.
        
        Returns:
            JSON representation of device state
        """
        state_dict = self.to_dict()
        # Convert enum values to strings for JSON serialization
        def convert_enums(obj):
            if isinstance(obj, Enum):
                return obj.value
            elif isinstance(obj, dict):
                return {k: convert_enums(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_enums(item) for item in obj]
            return obj
        
        return json.dumps(convert_enums(state_dict), indent=2, default=str)

    def __repr__(self):
        return (
            f"DeviceState(\n"
            f"  guide_top={self.guide_top.position.value}\n"
            f"  guide_bottom={self.guide_bottom.position.value}\n"
            f"  sensor_top_attached={self.sensor_top.attached}\n"
            f"  sensor_bottom_attached={self.sensor_bottom.attached}\n"
            f"  encoder_top_enabled={self.encoder_top.enabled}\n"
            f"  encoder_bottom_enabled={self.encoder_bottom.enabled}\n"
            f"  cameras_active={[i for i, v in self.cameras.flags.items() if v]}\n"
            f"  lamps={self.lamps}\n"
            f")"
        )
