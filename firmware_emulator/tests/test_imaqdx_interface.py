import pytest
from unittest.mock import Mock
from dataclasses import dataclass
from firmware_emulator.src.imaqdx_interface import (
    IMAQdxImageInfo,
    IMAQdxInterface
)
from firmware_emulator.src.virtual_camera import CameraFrame
import time

class TestIMAQdxImageInfo:
    """Test IMAQDX metadata structure"""
    
    def test_image_info_creation(self):
        """IMAQdxImageInfo should hold metadata"""
        info = IMAQdxImageInfo(
            image_id=1,
            timestamp=int(time.time() * 1000),
            camera_id="top",
            trigger_count=1,
            frame_number=0,
            width=640,
            height=480,
            bytes_per_pixel=3,
            image_data_ptr=12345
        )
        
        assert info.camera_id == "top"
        assert info.width == 640
        assert info.height == 480
    
    def test_image_info_fields(self):
        """IMAQdxImageInfo should have LabVIEW-compatible fields"""
        info = IMAQdxImageInfo(
            image_id=1,
            timestamp=1000,
            camera_id="top",
            trigger_count=5,
            frame_number=2,
            width=800,
            height=600,
            bytes_per_pixel=1,
            image_data_ptr=0
        )
        
        assert hasattr(info, 'image_id')
        assert hasattr(info, 'timestamp')
        assert hasattr(info, 'camera_id')
        assert hasattr(info, 'trigger_count')
        assert hasattr(info, 'frame_number')
        assert hasattr(info, 'width')
        assert hasattr(info, 'height')

class TestIMAQdxInterface:
    """Test IMAQDX interface compatibility"""
    
    def test_interface_initialization(self):
        """IMAQdxInterface should initialize with virtual camera"""
        mock_camera = Mock()
        mock_camera.camera_id = "top"
        mock_camera.is_ready.return_value = True
        
        interface = IMAQdxInterface(mock_camera)
        assert interface.is_ready() is True
    
    def test_get_image_info_from_frame(self):
        """get_image_info should return metadata from current frame"""
        mock_camera = Mock()
        mock_camera.camera_id = "top"
        mock_camera.is_ready.return_value = True
        
        frame = CameraFrame(
            camera_id="top",
            image_bytes=b'\x89PNG\r\n\x1a\n' + b'\x00' * 100,
            timestamp=time.time(),
            trigger_count=1,
            frame_index=0,
            filename="top_001.png"
        )
        mock_camera.get_current_frame.return_value = frame
        
        interface = IMAQdxInterface(mock_camera)
        info = interface.get_image_info()
        
        assert info is not None
        assert info.camera_id == "top"
        assert info.trigger_count == 1
        assert info.frame_number == 0
    
    def test_get_image_data_from_frame(self):
        """get_image_data should return raw image bytes"""
        mock_camera = Mock()
        mock_camera.camera_id = "top"
        mock_camera.is_ready.return_value = True
        
        test_image_data = b'\x89PNG\r\n\x1a\n' + b'test' * 25
        frame = CameraFrame(
            camera_id="top",
            image_bytes=test_image_data,
            timestamp=time.time(),
            trigger_count=1,
            frame_index=0,
            filename="top_001.png"
        )
        mock_camera.get_current_frame.return_value = frame
        
        interface = IMAQdxInterface(mock_camera)
        data = interface.get_image_data()
        
        assert data == test_image_data
    
    def test_get_image_info_returns_none_if_no_frame(self):
        """get_image_info should return None if no frame triggered"""
        mock_camera = Mock()
        mock_camera.camera_id = "top"
        mock_camera.is_ready.return_value = True
        mock_camera.get_current_frame.return_value = None
        
        interface = IMAQdxInterface(mock_camera)
        info = interface.get_image_info()
        
        assert info is None
    
    def test_is_ready_reflects_camera_status(self):
        """is_ready should reflect camera readiness"""
        mock_camera = Mock()
        mock_camera.camera_id = "top"
        mock_camera.is_ready.return_value = False
        
        interface = IMAQdxInterface(mock_camera)
        assert interface.is_ready() is False
        
        mock_camera.is_ready.return_value = True
        assert interface.is_ready() is True
