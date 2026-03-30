## ADDED Requirements

### Requirement: Dashboard displays 6 camera light indicators
The dashboard SHALL display 6 light indicators near the camera panel representing physical illumination channels used during camera capture.

#### Scenario: Light indicators are visible below camera grid
- **WHEN** user opens the dashboard
- **THEN** 6 light indicators (labeled L1 through L6) are displayed below the camera flag grid within the Cameras panel
- **AND** each indicator is a circular dot with a label
- **AND** the styling matches the existing camera flag indicators

#### Scenario: Light indicator shows green when channel is on
- **WHEN** the dashboard polls `/api/state` and `light_channels.1` is true
- **THEN** the L1 indicator dot is green with glow effect
- **AND** the label shows "L1"

#### Scenario: Light indicator shows grey when channel is off
- **WHEN** the dashboard polls `/api/state` and `light_channels.1` is false
- **THEN** the L1 indicator dot is grey (dim)
- **AND** no glow effect is applied

#### Scenario: All 6 light channels update independently
- **WHEN** the dashboard receives state with `light_channels` = {1: true, 2: false, 3: true, 4: false, 5: true, 6: false}
- **THEN** L1, L3, L5 indicators are green
- **AND** L2, L4, L6 indicators are grey
- **AND** each updates within the 100ms polling cycle

#### Scenario: Light indicators render in mock mode
- **WHEN** dashboard is in mock mode
- **THEN** light indicators reflect `light_channels` from mock state data
- **AND** if mock state does not include `light_channels`, all default to false (grey)

### Requirement: DeviceState tracks 6 light channels
The DeviceState SHALL include a `light_channels` dictionary with 6 boolean entries representing physical illumination channels.

#### Scenario: light_channels defaults to all off
- **WHEN** DeviceState is initialized
- **THEN** `light_channels` is `{1: False, 2: False, 3: False, 4: False, 5: False, 6: False}`
- **AND** it is included in `to_dict()` output and API state export

#### Scenario: light_channels is serialized in API state
- **WHEN** client sends `GET /api/state`
- **THEN** response JSON includes `light_channels` object with keys "1" through "6"
- **AND** each value is a boolean (true/false)
