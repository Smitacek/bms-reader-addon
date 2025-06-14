# Changelog

## [1.1.5] - 2025-06-15
### Changed
- **Language Unification**: Complete translation of all Czech text to English
- Translated all logging messages, comments, and documentation to English
- Updated user interface text for professional consistency
- Enhanced documentation with English-only content

### Technical
- All Python code comments translated to English
- Error messages and diagnostic output now in English
- Documentation files (DOCS.md, MULTI_BATTERY_CONFIG.md) fully translated
- Consistent terminology across all components

## [1.1.4] - 2025-06-15

### Added
- Enhanced startup logging with detailed battery configuration display
- Comprehensive battery reading cycle logging with success/failure tracking
- Virtual battery summary logging with aggregated data display
- Debug logging for individual battery data enhancement
- Clean repository structure with removed legacy files

### Changed
- Refactored multi_battery.py with improved code structure and documentation
- Enhanced error handling and logging throughout the codebase
- Updated main.py with detailed initialization and MQTT connection logging
- Improved README with better documentation and visual formatting
- New unique slug: battery-monitor-v2 to avoid Home Assistant caching conflicts

### Fixed
- Resolved Home Assistant add-on caching issues with new slug
- Better data mapping and sensor value calculations
- Improved temperature sensor mapping from BMS data
- Enhanced cell voltage statistics calculations

### Removed
- Legacy addon_config_old.py and mqtt_helper_old.py files
- Python cache directories and temporary files

## [1.1.3] - 2025-06-15

### Fixed
- Missing sensor values issue with enhanced data mapping
- Temperature sensor mapping from ambient_temp_c to temperature_1_c
- Power calculation (voltage × current) for individual batteries
- Min/Max cell voltage calculations from cell_voltages_v array

## [1.1.2] - 2025-06-15

### Added
- Multi-battery support (up to 16 batteries)
- Virtual battery aggregation
- Enhanced MQTT discovery for multiple batteries
- Individual battery monitoring with custom names
- Automatic battery detection and configuration

### Changed
- Updated add-on slug from `battery-monitor` to `battery-monitor-multi`
- Enhanced configuration schema for multi-battery setup
- Improved MQTT publisher with multi-battery support
- Updated documentation for multi-battery configuration

### Fixed
- Repository structure for Home Assistant compatibility
- Dockerfile build process
- Version consistency across all files

## [1.0.4] - Previous Release
- Single battery monitoring
- Basic MQTT integration
- Simple configuration
