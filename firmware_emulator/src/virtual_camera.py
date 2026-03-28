"""Virtual camera module for synthetic image generation"""

import os
import logging
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
import time

logger = logging.getLogger(__name__)

@dataclass
class CameraFrame:
    """Metadata and image data for a camera frame"""
    camera_id: str          # "top", "side", "front"
    image_bytes: bytes      # Raw image data
    timestamp: float        # Unix timestamp when triggered
    trigger_count: int      # Total number of triggers
    frame_index: int        # Index in sequence
    filename: str = ""      # Source filename

class VirtualCamera:
    """Simulates a physical camera by serving images from a folder"""
    
    def __init__(self, camera_id: str, camera_images_folder: str):
        """Initialize virtual camera."""
        self.camera_id = camera_id
        self.images_folder = Path(camera_images_folder) / camera_id
        self.frames: list[Path] = []
        self.current_frame_index = -1
        self.trigger_count = 0
        self.current_frame: Optional[CameraFrame] = None
        
        self._load_images()
    
    def _load_images(self):
        """Load all images from camera folder"""
        if not self.images_folder.exists():
            logger.error(f"Camera folder not found: {self.images_folder}")
            return
        
        # Load all PNG, BMP, JPG files
        image_extensions = {'.png', '.bmp', '.jpg', '.jpeg'}
        self.frames = sorted([
            f for f in self.images_folder.iterdir()
            if f.is_file() and f.suffix.lower() in image_extensions
        ])
        
        if self.frames:
            logger.info(f"Camera '{self.camera_id}' loaded {len(self.frames)} images")
        else:
            logger.warning(f"No images found in {self.images_folder}")
    
    def is_ready(self) -> bool:
        """Check if camera has images loaded"""
        return len(self.frames) > 0
    
    def trigger(self) -> Optional[CameraFrame]:
        """Trigger camera and advance to next frame."""
        if not self.is_ready():
            logger.warning(f"Camera '{self.camera_id}' not ready (no images)")
            return None
        
        self.current_frame_index = (self.current_frame_index + 1) % len(self.frames)
        self.trigger_count += 1
        
        image_path = self.frames[self.current_frame_index]
        with open(image_path, 'rb') as f:
            image_bytes = f.read()
        
        frame = CameraFrame(
            camera_id=self.camera_id,
            image_bytes=image_bytes,
            timestamp=time.time(),
            trigger_count=self.trigger_count,
            frame_index=self.current_frame_index,
            filename=image_path.name
        )
        
        self.current_frame = frame
        logger.info(
            f"Camera '{self.camera_id}' triggered: "
            f"frame {self.current_frame_index + 1}/{len(self.frames)}, "
            f"trigger #{self.trigger_count}"
        )
        
        return frame
    
    def get_current_frame(self) -> Optional[CameraFrame]:
        """Get current frame without advancing."""
        return self.current_frame
