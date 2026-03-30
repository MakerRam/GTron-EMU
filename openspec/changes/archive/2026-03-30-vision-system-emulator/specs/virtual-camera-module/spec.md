## ADDED Requirements

### Requirement: Provide IMAQDX-compatible camera interface
The emulator SHALL expose a camera interface that LabVIEW's IMAQDX acquire calls can interact with to retrieve images.

#### Scenario: LabVIEW opens virtual camera
- **WHEN** LabVIEW initializes IMAQDX and lists available cameras
- **THEN** virtual camera(s) appear in the available camera list (TOP, SIDE, FRONT cameras for each rack)

#### Scenario: LabVIEW acquires image
- **WHEN** LabVIEW calls IMAQDX acquire() on a virtual camera
- **THEN** acquire() returns an image frame (width/height/format matching camera config)

### Requirement: Load pre-captured images from folder
The emulator SHALL load pre-captured images from a local folder on disk.

#### Scenario: Image folder initialization
- **WHEN** emulator starts
- **THEN** it scans a configured image folder and loads available images for each camera

#### Scenario: Camera-specific images
- **WHEN** virtual camera is triggered
- **THEN** it delivers a pre-captured image from the folder corresponding to that camera (TOP, SIDE, FRONT)

### Requirement: Image folder structure
The emulator SHALL support a standard image folder structure.

#### Scenario: Folder organization
- **WHEN** folder is configured
- **THEN** emulator expects structure: `/images/top/`, `/images/side/`, `/images/front/` containing image files

#### Scenario: Image rotation/cycling
- **WHEN** camera is triggered multiple times
- **THEN** emulator cycles through available images in the folder (sequential or random, configurable)

### Requirement: Synchronize with firmware triggers
The emulator SHALL ensure camera capture happens when firmware signals trigger, not at arbitrary times.

#### Scenario: Capture triggered by light-camera sequence
- **WHEN** firmware executes LightCameraSequence_Top (after LCSI0/1/2 flags set and TSENB enabled)
- **THEN** virtual camera captures image at the moment of camera trigger pulse

### Requirement: Phase 2: Support multiple cameras
The emulator SHALL support multiple virtual cameras (TOP, SIDE, FRONT for each of 2 racks = 6 total).

#### Scenario: Phase 1 - Top Rack only
- **WHEN** Phase 1 emulator is running
- **THEN** 3 virtual cameras are available (top, side, front)

#### Scenario: Phase 2 - Multi-rack support
- **WHEN** Phase 2 is implemented
- **THEN** 6 virtual cameras are available (top_camera_1, side_camera_2, front_camera_3, and bottom equivalents)
