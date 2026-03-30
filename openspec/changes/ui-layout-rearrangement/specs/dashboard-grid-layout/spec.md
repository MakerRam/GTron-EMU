## ADDED Requirements

### Requirement: Dashboard uses explicit grid placement matching machine topology

The dashboard `.dashboard-grid` SHALL use CSS Grid with explicit `grid-column` and `grid-row` placement for each panel, arranging panels to match the physical machine layout.

#### Scenario: Desktop layout matches reference image
- **WHEN** dashboard is viewed on a desktop viewport (>960px)
- **THEN** the grid SHALL have 4 columns (3 equal + 1 narrower right column)
- **AND** Front Panel spans columns 1-3 in row 1
- **AND** Tower Lamp occupies column 4, spanning rows 1-2
- **AND** Cameras panel spans columns 1-3 in row 2
- **AND** System Status occupies column 4, spanning rows 2-3
- **AND** Sag Sensors occupies column 1 in row 3
- **AND** Guide Motors occupies column 2 in row 3
- **AND** Reeler Motors occupies column 3 in row 3

#### Scenario: Tablet layout collapses to 2 columns
- **WHEN** viewport width is between 640px and 960px
- **THEN** grid collapses to 2 columns with no multi-row spanning
- **AND** all panels stack in logical order

#### Scenario: Mobile layout collapses to single column
- **WHEN** viewport width is below 640px
- **THEN** grid collapses to 1 column
- **AND** all panels stack vertically in source order
