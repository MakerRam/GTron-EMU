"""IMAQDX compatibility layer for LabVIEW image acquisition"""

import logging
from dataclasses import dataclass
from typing import Optional
import time
from firmware_emulator.src.virtual_camera import VirtualCamera, CameraFrame

logger = logging.getLogger(__name__)

@dataclass
class IMAQdxImageInfo:
    """IMAQDX-compatible image metadata structure."""
    image_id: int           # Unique identifier for this frame
    timestamp: int          # Milliseconds since epoch
    camera_id: str          # "top", "side", "front"
    trigger_count: int      # Total number of triggers for this camera
    frame_number: int       # Sequential frame index (0-based)
    width: int              # Image width in pixels
    height: int             # Image height in pixels
    bytes_per_pixel: int    # 1 (grayscale) or 3 (RGB)
    image_data_ptr: int     # Pointer to image data (for LabVIEW)

class IMAQdxInterface:
    """IMAQDX-compatible interface for serving camera frames to LabVIEW."""
    
    def __init__(self, virtual_camera: VirtualCamera):
        """Initialize IMAQDX interface."""
        self.camera = virtual_camera
        self._next_image_id = 1
        logger.info(f"IMAQdxInterface initialized for camera '{virtual_camera.camera_id}'")
    
    def is_ready(self) -> bool:
        """Check if camera interface is ready."""
        return self.camera.is_ready()
    
    def get_image_info(self) -> Optional[IMAQdxImageInfo]:
        """Get metadata for current image."""
        frame = self.camera.get_current_frame()
        if frame is None:
            return None
        
        # Extract image dimensions
        width, height = self._estimate_image_dimensions(frame.image_bytes)
        
        info = IMAQdxImageInfo(
            image_id=self._next_image_id,
            timestamp=int(frame.timestamp * 1000),  # Convert to milliseconds
            camera_id=frame.camera_id,
            trigger_count=frame.trigger_count,
            frame_number=frame.frame_index,
            width=width,
            height=height,
            bytes_per_pixel=3,  # RGB
            image_data_ptr=id(frame.image_bytes)
        )
        
        self._next_image_id += 1
        logger.debug(f"Image info: {info.camera_id} frame {info.frame_number}")
        
        return info
    
    def get_image_data(self) -> Optional[bytes]:
        """Get raw image data for current frame."""
        frame = self.camera.get_current_frame()
        if frame is None:
            return None
        
        return frame.image_bytes
    
    @staticmethod
    def _estimate_image_dimensions(image_bytes: bytes) -> tuple[int, int]:
        """Estimate image dimensions from file header."""
        try:
            # PNG header detection and dimension parsing
            if image_bytes.startswith(b'\x89PNG'):
                # PNG dimensions are at bytes 16-24 (big-endian)
                if len(image_bytes) >= 24:
                    width = int.from_bytes(image_bytes[16:20], 'big')
                    height = int.from_bytes(image_bytes[20:24], 'big')
                    return (width, height)
            
            # JPEG detection
            if image_bytes.startswith(b'\xff\xd8\xff'):
                return (640, 480)
            
            # Default fallback
            return (640, 480)
        except (IndexError, ValueError):
            logger.warning("Could not parse image dimensions, using defaults")
            return (640, 480)
