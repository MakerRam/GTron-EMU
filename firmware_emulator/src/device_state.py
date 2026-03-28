"""
Device State Machine
Tracks the complete state of the simulated hardware
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List
import time


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

    def log_command(self, command: str):
        """Track last command received"""
        self.last_command = command
        self.last_command_time = time.time()

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
