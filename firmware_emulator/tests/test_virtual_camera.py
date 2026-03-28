import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from dataclasses import dataclass
from firmware_emulator.src.virtual_camera import VirtualCamera, CameraFrame
import tempfile
import os
import time

class TestVirtualCamera:
    """Test virtual camera module"""
    
    @pytest.fixture
    def temp_camera_folder(self):
        """Create temporary folder with test images"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create subdirectories
            for camera_id in ['top', 'side', 'front']:
                os.makedirs(os.path.join(tmpdir, camera_id), exist_ok=True)
            
            # Create test images
            for camera_id in ['top', 'side', 'front']:
                camera_dir = os.path.join(tmpdir, camera_id)
                for i in range(1, 4):
                    img_file = os.path.join(camera_dir, f'{camera_id}_{i:03d}.png')
                    with open(img_file, 'wb') as f:
                        f.write(b'\x89PNG\r\n\x1a\n' + f'test_image_{i}'.encode() + b'\x00' * 50)
            
            yield tmpdir
    
    def test_init_loads_images_from_folder(self, temp_camera_folder):
        """VirtualCamera should load images from folder"""
        camera = VirtualCamera('top', temp_camera_folder)
        assert camera.is_ready()
    
    def test_trigger_returns_frame(self, temp_camera_folder):
        """Trigger should return CameraFrame with metadata"""
        camera = VirtualCamera('top', temp_camera_folder)
        frame = camera.trigger()
        
        assert frame is not None
        assert frame.camera_id == 'top'
        assert isinstance(frame.image_bytes, bytes)
        assert frame.trigger_count == 1
        assert frame.frame_index == 0
    
    def test_trigger_advances_frame(self, temp_camera_folder):
        """Multiple triggers should advance frame index"""
        camera = VirtualCamera('top', temp_camera_folder)
        
        frame1 = camera.trigger()
        frame2 = camera.trigger()
        frame3 = camera.trigger()
        
        assert frame1.frame_index == 0
        assert frame2.frame_index == 1
        assert frame3.frame_index == 2
        assert frame3.trigger_count == 3
    
    def test_trigger_wraps_around(self, temp_camera_folder):
        """Trigger should wrap to first image after last"""
        camera = VirtualCamera('top', temp_camera_folder)
        
        frame1 = camera.trigger()
        frame2 = camera.trigger()
        frame3 = camera.trigger()
        frame4 = camera.trigger()  # Should wrap to first
        
        assert frame4.frame_index == 0  # Wraps
        assert frame4.trigger_count == 4
    
    def test_get_current_frame_no_advance(self, temp_camera_folder):
        """get_current_frame should NOT advance"""
        camera = VirtualCamera('top', temp_camera_folder)
        
        camera.trigger()
        frame1 = camera.get_current_frame()
        frame2 = camera.get_current_frame()
        
        assert frame1.frame_index == frame2.frame_index
        assert frame1.image_bytes == frame2.image_bytes
    
    def test_is_ready_false_empty_folder(self):
        """is_ready should be False if folder is empty"""
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(os.path.join(tmpdir, 'top'), exist_ok=True)
            camera = VirtualCamera('top', tmpdir)
            assert camera.is_ready() is False
    
    def test_camera_frame_has_timestamp(self, temp_camera_folder):
        """CameraFrame should have timestamp"""
        camera = VirtualCamera('top', temp_camera_folder)
        frame = camera.trigger()
        
        assert hasattr(frame, 'timestamp')
        assert isinstance(frame.timestamp, float)
        assert frame.timestamp > 0
    
    def test_multiple_cameras_independent(self, temp_camera_folder):
        """Each camera should have independent frame state"""
        camera_top = VirtualCamera('top', temp_camera_folder)
        camera_side = VirtualCamera('side', temp_camera_folder)
        
        frame_top1 = camera_top.trigger()
        frame_side1 = camera_side.trigger()
        frame_top2 = camera_top.trigger()
        
        assert frame_top1.frame_index == 0
        assert frame_side1.frame_index == 0
        assert frame_top2.frame_index == 1
