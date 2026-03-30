"""
Unit Tests for Device State Machine
"""
import pytest
import json
from firmware_emulator.src.device_state import (
    DeviceState, GuideState, ReelerState, SensorState, EncoderState,
    CameraState, LampState, GuidePosition, MotorState, RunState
)


class TestGuideState:
    """Test GuideState dataclass"""
    
    def test_guide_state_initialization(self):
        """Test GuideState initializes with defaults"""
        guide = GuideState()
        assert guide.position == GuidePosition.UNKNOWN
        assert guide.moving is False
        assert guide.reached_limit is False
        assert guide.target_position == GuidePosition.UNKNOWN
    
    def test_guide_state_transitions(self):
        """Test guide position state transitions"""
        guide = GuideState()
        guide.position = GuidePosition.OPEN
        assert guide.position == GuidePosition.OPEN
        
        guide.moving = True
        assert guide.moving is True
        
        guide.position = GuidePosition.CLOSED
        assert guide.position == GuidePosition.CLOSED


class TestReelerState:
    """Test ReelerState dataclass"""
    
    def test_reeler_state_initialization(self):
        """Test ReelerState initializes with defaults"""
        reeler = ReelerState()
        assert reeler.speed == 0
        assert reeler.teeth == 0
        assert reeler.running is False
        assert reeler.position == 0
    
    def test_reeler_state_speed_setting(self):
        """Test setting reeler speed"""
        reeler = ReelerState()
        reeler.speed = 4000
        assert reeler.speed == 4000
        
        reeler.running = True
        assert reeler.running is True


class TestSensorState:
    """Test SensorState dataclass"""
    
    def test_sensor_state_initialization(self):
        """Test SensorState initializes with defaults"""
        sensor = SensorState()
        assert sensor.attached is False
        assert sensor.powered is False
        assert sensor.triggered is False
    
    def test_sensor_attach_detach(self):
        """Test sensor attach/detach"""
        sensor = SensorState()
        sensor.attached = True
        assert sensor.attached is True
        
        sensor.powered = True
        assert sensor.powered is True
        
        sensor.attached = False
        assert sensor.attached is False


class TestEncoderState:
    """Test EncoderState dataclass"""
    
    def test_encoder_state_initialization(self):
        """Test EncoderState initializes with defaults"""
        encoder = EncoderState()
        assert encoder.initialized is False
        assert encoder.enabled is False
        assert encoder.position == 0
        assert encoder.initial_angle == 0
        assert encoder.teeth_count == 0
    
    def test_encoder_initialization(self):
        """Test encoder initialization and enabling"""
        encoder = EncoderState()
        encoder.initialized = True
        encoder.initial_angle = 90
        assert encoder.initialized is True
        
        encoder.enabled = True
        assert encoder.enabled is True


class TestCameraState:
    """Test CameraState dataclass"""
    
    def test_camera_state_initialization(self):
        """Test CameraState initializes with flags dict"""
        camera = CameraState()
        assert isinstance(camera.flags, dict)
        assert len(camera.flags) == 7
        assert all(v is False for v in camera.flags.values())
        assert camera.active_sequence == -1
        assert camera.timestamp_enabled is False
    
    def test_camera_flag_setting(self):
        """Test setting camera sequence flags"""
        camera = CameraState()
        camera.flags[0] = True
        assert camera.flags[0] is True
        assert camera.flags[1] is False
        
        camera.active_sequence = 1
        assert camera.active_sequence == 1


class TestLampState:
    """Test LampState dataclass"""
    
    def test_lamp_state_initialization(self):
        """Test LampState initializes with all lamps off"""
        lamp = LampState()
        assert lamp.red is False
        assert lamp.yellow is False
        assert lamp.green is False
        assert lamp.buzzer is False
    
    def test_lamp_control(self):
        """Test controlling individual lamps"""
        lamp = LampState()
        lamp.red = True
        assert lamp.red is True
        assert lamp.yellow is False
        
        lamp.buzzer = True
        assert lamp.buzzer is True


class TestDeviceState:
    """Test DeviceState container"""
    
    def test_device_state_initialization(self):
        """Test DeviceState initializes all subsystems"""
        state = DeviceState()
        
        # Check all subcomponents are initialized
        assert isinstance(state.guide_top, GuideState)
        assert isinstance(state.guide_bottom, GuideState)
        assert isinstance(state.reeler_top, ReelerState)
        assert isinstance(state.reeler_bottom, ReelerState)
        assert isinstance(state.sensor_top, SensorState)
        assert isinstance(state.sensor_bottom, SensorState)
        assert isinstance(state.encoder_top, EncoderState)
        assert isinstance(state.encoder_bottom, EncoderState)
        assert isinstance(state.lamps, LampState)
        assert isinstance(state.cameras, CameraState)
        
        # Check other state
        assert state.door_locked is True
        assert state.estop_pressed is False
        assert state.power_on is True
        assert state.last_command is None
    
    def test_device_state_reset(self):
        """Test device state reset"""
        state = DeviceState()
        
        # Modify state
        state.door_locked = False
        state.estop_pressed = True
        state.guide_top.position = GuidePosition.OPEN
        state.lamps.red = True
        
        # Reset
        state.reset()
        
        # Check reset to defaults
        assert state.door_locked is True
        assert state.estop_pressed is False
        assert state.guide_top.position == GuidePosition.UNKNOWN
        assert state.lamps.red is False
    
    def test_device_state_log_command(self):
        """Test command logging"""
        state = DeviceState()
        assert state.last_command is None
        
        state.log_command("QUERY")
        assert state.last_command == "QUERY"
        assert state.last_command_time is not None
    
    def test_device_state_to_dict(self):
        """Test serialization to dictionary"""
        state = DeviceState()
        state.guide_top.position = GuidePosition.OPEN
        state.lamps.red = True
        state.estop_pressed = True
        
        state_dict = state.to_dict()
        
        # Verify structure
        assert isinstance(state_dict, dict)
        assert 'guide_top' in state_dict
        assert 'lamps' in state_dict
        assert 'estop_pressed' in state_dict
        
        # Verify values (enums converted to their values)
        assert state_dict['estop_pressed'] is True
        assert state_dict['lamps']['red'] is True
    
    def test_device_state_to_json(self):
        """Test serialization to JSON"""
        state = DeviceState()
        state.guide_top.position = GuidePosition.OPEN
        state.lamps.red = True
        
        json_str = state.to_json()
        
        # Verify it's valid JSON
        data = json.loads(json_str)
        assert isinstance(data, dict)
        assert 'guide_top' in data
        assert 'lamps' in data
        assert data['lamps']['red'] is True
    
    def test_sag_sensor_states(self):
        """Test sag sensor state tracking"""
        state = DeviceState()
        
        # All sag sensors start as False (pass)
        assert state.sag_top_upper is False
        assert state.sag_top_lower is False
        assert state.sag_bottom_upper is False
        assert state.sag_bottom_lower is False
        
        # Simulate sag detection
        state.sag_top_upper = True
        assert state.sag_top_upper is True
    
    def test_solenoid_states(self):
        """Test solenoid state tracking"""
        state = DeviceState()
        
        assert state.solenoid_top is False
        assert state.solenoid_bottom is False
        
        state.solenoid_top = True
        assert state.solenoid_top is True
    
    def test_independent_rack_states(self):
        """Test that top and bottom racks have independent states"""
        state = DeviceState()
        
        # Modify top rack
        state.guide_top.position = GuidePosition.OPEN
        state.reeler_top.speed = 4000
        state.sensor_top.attached = True
        
        # Verify bottom rack unaffected
        assert state.guide_bottom.position == GuidePosition.UNKNOWN
        assert state.reeler_bottom.speed == 0
        assert state.sensor_bottom.attached is False


class TestRunState:
    """Test RunState enum"""

    def test_run_state_values(self):
        """Test RunState enum has expected values"""
        assert RunState.RUNNING.value == "running"
        assert RunState.PAUSED.value == "paused"
        assert RunState.STOPPED.value == "stopped"

    def test_run_state_from_string(self):
        """Test creating RunState from string value"""
        assert RunState("running") == RunState.RUNNING
        assert RunState("paused") == RunState.PAUSED
        assert RunState("stopped") == RunState.STOPPED


class TestDeviceStateEmulatorControl:
    """Test new emulator control fields on DeviceState"""

    def test_default_run_state(self):
        """Test run_state defaults to STOPPED"""
        state = DeviceState()
        assert state.run_state == RunState.STOPPED

    def test_default_buzzer_override(self):
        """Test buzzer_override defaults to False"""
        state = DeviceState()
        assert state.buzzer_override is False

    def test_default_query_responsive(self):
        """Test query_responsive defaults to True"""
        state = DeviceState()
        assert state.query_responsive is True

    def test_default_light_channels(self):
        """Test light_channels defaults to 6 channels all False"""
        state = DeviceState()
        assert isinstance(state.light_channels, dict)
        assert len(state.light_channels) == 6
        for i in range(1, 7):
            assert state.light_channels[str(i)] is False

    def test_run_state_transitions(self):
        """Test run_state can be set to all valid values"""
        state = DeviceState()
        state.run_state = RunState.RUNNING
        assert state.run_state == RunState.RUNNING
        state.run_state = RunState.PAUSED
        assert state.run_state == RunState.PAUSED
        state.run_state = RunState.STOPPED
        assert state.run_state == RunState.STOPPED

    def test_buzzer_override_toggle(self):
        """Test buzzer_override can be toggled"""
        state = DeviceState()
        state.buzzer_override = True
        assert state.buzzer_override is True
        state.buzzer_override = False
        assert state.buzzer_override is False

    def test_query_responsive_toggle(self):
        """Test query_responsive can be toggled"""
        state = DeviceState()
        state.query_responsive = False
        assert state.query_responsive is False
        state.query_responsive = True
        assert state.query_responsive is True

    def test_light_channels_individual_toggle(self):
        """Test individual light channels can be toggled"""
        state = DeviceState()
        state.light_channels["3"] = True
        assert state.light_channels["3"] is True
        assert state.light_channels["1"] is False  # others unaffected

    def test_to_dict_includes_run_state(self):
        """Test to_dict includes run_state as string"""
        state = DeviceState()
        state.run_state = RunState.RUNNING
        d = state.to_dict()
        assert d["run_state"] == "running"

    def test_to_dict_includes_buzzer_override(self):
        """Test to_dict includes buzzer_override"""
        state = DeviceState()
        state.buzzer_override = True
        d = state.to_dict()
        assert d["buzzer_override"] is True

    def test_to_dict_includes_query_responsive(self):
        """Test to_dict includes query_responsive"""
        state = DeviceState()
        d = state.to_dict()
        assert d["query_responsive"] is True

    def test_to_dict_includes_light_channels(self):
        """Test to_dict includes light_channels as dict"""
        state = DeviceState()
        state.light_channels["1"] = True
        state.light_channels["5"] = True
        d = state.to_dict()
        assert d["light_channels"]["1"] is True
        assert d["light_channels"]["5"] is True
        assert d["light_channels"]["2"] is False

    def test_to_json_includes_new_fields(self):
        """Test to_json serializes new fields correctly"""
        state = DeviceState()
        state.run_state = RunState.PAUSED
        state.buzzer_override = True
        data = json.loads(state.to_json())
        assert data["run_state"] == "paused"
        assert data["buzzer_override"] is True
        assert data["query_responsive"] is True
        assert "light_channels" in data

    def test_reset_restores_new_field_defaults(self):
        """Test reset() restores all new fields to defaults"""
        state = DeviceState()
        state.run_state = RunState.RUNNING
        state.buzzer_override = True
        state.query_responsive = False
        state.light_channels["1"] = True
        state.light_channels["4"] = True

        state.reset()

        assert state.run_state == RunState.STOPPED
        assert state.buzzer_override is False
        assert state.query_responsive is True
        for i in range(1, 7):
            assert state.light_channels[str(i)] is False

    def test_copy_preserves_new_fields(self):
        """Test copy() deep-copies new fields"""
        state = DeviceState()
        state.run_state = RunState.RUNNING
        state.buzzer_override = True
        state.light_channels["2"] = True

        copied = state.copy()

        assert copied.run_state == RunState.RUNNING
        assert copied.buzzer_override is True
        assert copied.light_channels["2"] is True
        # Verify deep copy - modifying copy doesn't affect original
        copied.light_channels["2"] = False
        assert state.light_channels["2"] is True


class TestDeviceStateTransitions:
    """Test complete state transition scenarios"""
    
    def test_guide_open_close_sequence(self):
        """Test guide open/close sequence"""
        state = DeviceState()
        
        # Initial state
        assert state.guide_top.position == GuidePosition.UNKNOWN
        
        # Open guide
        state.guide_top.position = GuidePosition.MOVING
        state.guide_top.moving = True
        state.guide_top.target_position = GuidePosition.OPEN
        assert state.guide_top.moving is True
        
        # Complete open
        state.guide_top.position = GuidePosition.OPEN
        state.guide_top.moving = False
        state.guide_top.reached_limit = True
        assert state.guide_top.position == GuidePosition.OPEN
        assert state.guide_top.moving is False
        
        # Close guide
        state.guide_top.position = GuidePosition.MOVING
        state.guide_top.moving = True
        state.guide_top.target_position = GuidePosition.CLOSED
        
        # Complete close
        state.guide_top.position = GuidePosition.CLOSED
        state.guide_top.moving = False
        assert state.guide_top.position == GuidePosition.CLOSED
    
    def test_sensor_enable_disable_sequence(self):
        """Test sensor attach/power sequence"""
        state = DeviceState()
        sensor = state.sensor_top
        
        # Attach sensor
        sensor.attached = True
        assert sensor.attached is True
        
        # Power on
        sensor.powered = True
        assert sensor.powered is True
        
        # Trigger
        sensor.triggered = True
        assert sensor.triggered is True
        
        # Detach
        sensor.attached = False
        sensor.powered = False
        assert sensor.attached is False
        assert sensor.powered is False
    
    def test_encoder_initialization_sequence(self):
        """Test encoder init/enable sequence"""
        state = DeviceState()
        encoder = state.encoder_top
        
        # Initialize
        encoder.initialized = True
        encoder.initial_angle = 0
        assert encoder.initialized is True
        
        # Enable
        encoder.enabled = True
        assert encoder.enabled is True
        
        # Track position
        encoder.position = 100
        assert encoder.position == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
