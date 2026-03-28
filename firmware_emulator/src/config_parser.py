"""
Configuration Parser for Machine Interface Parameters.json
Handles loading and validation of machine interface opcodes and timing.
"""
import json
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class DelayConfig:
    """Timing configuration values from Machine Interface Parameters.json"""
    timing_unit_setup: int = 2000  # ms
    strobing_for_cam_optics: int = 100  # ms
    tower_lamp_diagnostics: int = 1000  # ms
    run: int = 50  # ms
    disable_sensors: int = 250  # ms
    disable_encoder: int = 5  # ms
    communication_board_config: int = 1  # ms
    send_encoder_opcodes: int = 1  # ms


@dataclass
class TimeoutConfig:
    """Timeout configuration values"""
    ping: int = 5000  # ms
    machine_power_status: int = 5000  # ms
    limit_switch_status_check: int = 2000  # ms
    motor_diagnostics: int = 50000  # ms
    reference_search: int = 50000  # ms
    ready_to_insert: int = 50000  # ms
    ready_to_run: int = 5000  # ms


@dataclass
class LightCameraTimings:
    """Light-camera sequence timing values (in microseconds)"""
    light_on_delay: int = 1000  # µs
    camera_on_delay: int = 500  # µs
    camera_off_delay: int = 100  # µs
    light_off_delay: int = 5  # µs
    top_light_on_delay: int = 5000  # µs (Top Rack with backlight)
    top_camera_on_delay: int = 500  # µs
    top_camera_off_delay: int = 100  # µs
    top_light_off_delay: int = 5  # µs


class MachineConfig:
    """
    Parses and provides access to Machine Interface Parameters.json
    """
    
    def __init__(self, config_path: str = "Machine Interface Parameters.json"):
        """
        Initialize config parser.
        
        Args:
            config_path: Path to Machine Interface Parameters.json
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        self.config_path = config_path
        self.config_data: Dict[str, Any] = {}
        self.delays = DelayConfig()
        self.timeouts = TimeoutConfig()
        self.light_camera_timings = LightCameraTimings()
        self.baud_rate = 9600
        self.opcode_map: Dict[str, str] = {}
        self.camera_light_config: List[Dict[str, Any]] = []
        
        self._load_config()
        self._parse_delays()
        self._parse_timeouts()
        self._parse_light_camera_timings()
        self._parse_opcode_map()
        self._parse_camera_light_config()
        
        logger.info(f"Configuration loaded from {config_path}")
    
    def _load_config(self) -> None:
        """Load and parse JSON configuration file."""
        if not os.path.exists(self.config_path):
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        
        try:
            with open(self.config_path, 'r') as f:
                self.config_data = json.load(f)
            logger.debug(f"Successfully loaded {self.config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON: {e}")
            raise
    
    def _parse_delays(self) -> None:
        """Parse delay values from config."""
        delays_data = self.config_data.get(
            "MachineInterfaceParameters", {}
        ).get("DelayValuesInms", {})
        
        if delays_data:
            self.delays.timing_unit_setup = delays_data.get("TimingUnitSetup", 2000)
            self.delays.strobing_for_cam_optics = delays_data.get("StrobingForCamOpticsDiagnostics", 100)
            self.delays.tower_lamp_diagnostics = delays_data.get("TowerLampDiagnostics", 1000)
            self.delays.run = delays_data.get("Run", 50)
            self.delays.disable_sensors = delays_data.get("DisableSensors", 250)
            self.delays.disable_encoder = delays_data.get("DisableEncoder", 5)
            self.delays.communication_board_config = delays_data.get("CommunicationBoardConfiguration", 1)
            self.delays.send_encoder_opcodes = delays_data.get("SendEncoderOpcodes", 1)
            
            logger.debug(f"Parsed delay values: {self.delays}")
    
    def _parse_timeouts(self) -> None:
        """Parse timeout values from config."""
        timeouts_data = self.config_data.get(
            "MachineInterfaceParameters", {}
        ).get("TimeoutInms", {})
        
        if timeouts_data:
            self.timeouts.ping = timeouts_data.get("Ping", 5000)
            self.timeouts.machine_power_status = timeouts_data.get("MachinePowerStatus", 5000)
            self.timeouts.limit_switch_status_check = timeouts_data.get("LimitSwitchStatusCheck", 2000)
            self.timeouts.motor_diagnostics = timeouts_data.get("MotorDiagnostics", 50000)
            self.timeouts.reference_search = timeouts_data.get("ReferenceSearch", 50000)
            self.timeouts.ready_to_insert = timeouts_data.get("ReadyToInsert", 50000)
            self.timeouts.ready_to_run = timeouts_data.get("ReadyToRun", 5000)
            
            logger.debug(f"Parsed timeout values: {self.timeouts}")
    
    def _parse_light_camera_timings(self) -> None:
        """Parse light-camera sequence timing from firmware defaults."""
        # These are hardcoded from the firmware; can be extended to read from JSON
        # Current values from LightCam_Sequence.ino (lines 405-414)
        logger.debug("Using hardware light-camera timings from firmware defaults")
    
    def _parse_opcode_map(self) -> None:
        """Extract opcode mappings from Machine Interface Recipe Opcodes."""
        mi_opcodes = self.config_data.get(
            "MachineInterfaceParameters", {}
        ).get("MachineInterfaceRecipeOpcodes", {})
        
        # Flatten all opcode definitions
        for section_name, section_data in mi_opcodes.items():
            if isinstance(section_data, dict):
                # Handle nested dict structures like "Ping" with "Ping" and "PingResponse"
                for key, value in section_data.items():
                    if isinstance(value, list):
                        for opcode in value:
                            if isinstance(opcode, str) and opcode:
                                self.opcode_map[opcode] = section_name
                    elif isinstance(value, str) and value:
                        self.opcode_map[value] = section_name
            
            elif isinstance(section_data, list):
                # Handle list of opcodes
                for item in section_data:
                    if isinstance(item, dict):
                        for key, value in item.items():
                            if isinstance(value, list):
                                for opcode in value:
                                    if isinstance(opcode, str) and opcode:
                                        self.opcode_map[opcode] = section_name
                            elif isinstance(value, str) and value:
                                self.opcode_map[value] = section_name
                    elif isinstance(item, str) and item:
                        self.opcode_map[item] = section_name
        
        logger.info(f"Loaded {len(self.opcode_map)} opcodes")
        logger.debug(f"Opcode map: {list(self.opcode_map.keys())[:20]}...")
    
    def _parse_camera_light_config(self) -> None:
        """Parse camera-to-light configuration."""
        camera_light_data = self.config_data.get(
            "MachineInterfaceParameters", {}
        ).get("CameraLightConfig", [])
        
        self.camera_light_config = camera_light_data
        logger.debug(f"Parsed {len(self.camera_light_config)} camera-light configurations")
    
    def get_opcode_category(self, opcode: str) -> Optional[str]:
        """
        Get the category of an opcode.
        
        Args:
            opcode: The opcode string (e.g., "QUERY", "tpGOP")
        
        Returns:
            Category name or None if opcode not found
        """
        return self.opcode_map.get(opcode)
    
    def is_valid_opcode(self, opcode: str) -> bool:
        """
        Check if opcode is valid.
        
        Args:
            opcode: The opcode string
        
        Returns:
            True if opcode is registered
        """
        return opcode in self.opcode_map
    
    def get_camera_light_config(self, sequence_name: str) -> Optional[Dict[str, Any]]:
        """
        Get camera-light configuration for a sequence.
        
        Args:
            sequence_name: Name of the light-camera sequence (e.g., "LightCameraSequence1")
        
        Returns:
            Configuration dict or None if not found
        """
        for config in self.camera_light_config:
            if config.get("Name") == sequence_name:
                return config
        return None
    
    def validate(self) -> bool:
        """
        Validate configuration.
        
        Returns:
            True if all critical values are present
        """
        errors = []
        
        if self.baud_rate != 9600:
            errors.append(f"Baud rate should be 9600, got {self.baud_rate}")
        
        if not self.opcode_map:
            errors.append("No opcodes loaded from configuration")
        
        if self.delays.timing_unit_setup <= 0:
            errors.append("TimingUnitSetup must be positive")
        
        if errors:
            logger.warning(f"Configuration validation warnings:\n" + "\n".join(errors))
            return False
        
        logger.info("Configuration validation passed")
        return True
