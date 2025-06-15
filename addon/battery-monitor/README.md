# Battery Monitor Add-on - Multi-Battery Support

![Version](https://img.shields.io/badge/version-1.1.5-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1+-green.svg)

Advanced monitoring add-on for Daren BMS batteries with **multi-battery support** and virtual battery aggregation.

## 🆕 New in Version 1.1.5

- ✅ **Language Unification** - Complete English interface and documentation
- ✅ **Fixed Icons** - Proper PNG and SVG icons working correctly
- ✅ **Enhanced Logging** - Detailed startup and runtime diagnostics
- ✅ **Code Refactoring** - Cleaner, more maintainable codebase
- ✅ **Multi-Battery Support** - Monitor up to 16 batteries simultaneously
- ✅ **Virtual Battery** - Aggregated data from all batteries in one entity
- ✅ **Flexible Configuration** - Different ports and addresses for each battery
- ✅ **Individual Monitoring** - Each battery gets its own Home Assistant sensors
- ✅ **Backward Compatibility** - Single battery configurations still work

## 🔋 Features

### Core Features
- ✅ **Daren BMS Support** - Service 42 protocol compatibility
- ✅ **MQTT Auto Discovery** - Automatic integration with Home Assistant
- ✅ **Real-time Monitoring** - Configurable read intervals (10-300 seconds)
- ✅ **LiFePO4 Optimized** - Designed specifically for LiFePO4 battery systems
- ✅ **Multi-architecture** - Supports ARM64, AMD64, ARMv7

### Multi-Battery Features
- 🔋 **Up to 16 Batteries** - Monitor multiple batteries with different addresses
- 🏦 **Virtual Battery** - Aggregated view of entire battery bank
- 📊 **Individual Tracking** - Each battery monitored separately
- ⚡ **Flexible Wiring** - Multiple RS485 ports and addresses supported
- 🔧 **Easy Configuration** - YAML-based setup with examples

## 📊 Monitored Parameters

### Per Battery
- **Battery State of Charge (SOC)** - %
- **Pack Voltage** - V  
- **Pack Current** - A (positive = charging, negative = discharging)
- **Power** - W
- **Remaining Capacity** - Ah
- **Cell Voltages** - Individual cell monitoring
- **Temperature** - Battery temperature
- **Status** - Charge/discharge/idle

### Virtual Battery (Aggregated)
- **Average SOC** - Weighted average across all batteries
- **Total Voltage** - Sum of all battery voltages (series configuration)
- **Total Current** - Sum of all battery currents
- **Total Power** - Combined power output
- **Total Capacity** - Sum of remaining capacity
- **Battery Count** - Number of connected batteries
- **Cell Voltage Range** - Min/max across all cells

## ⚙️ Configuration

### Single Battery (Backward Compatible)
```yaml
bms_port: "/dev/ttyUSB0"
bms_address: 1
mqtt_host: "core-mosquitto"
mqtt_port: 1883
read_interval: 30
```

### Multi-Battery Setup
```yaml
# Enable multi-battery mode
multi_battery_mode: true

# Configure individual batteries
batteries:
  - port: "/dev/ttyUSB0"
    address: 1
    name: "Battery_1"
    enabled: true
  - port: "/dev/ttyUSB0"
    address: 2
    name: "Battery_2"
    enabled: true
  - port: "/dev/ttyUSB1"
    address: 1
    name: "Battery_3"
    enabled: true

# Virtual battery settings
enable_virtual_battery: true
virtual_battery_name: "Battery Bank"

# MQTT settings
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_username: "mqtt_user"
mqtt_password: "mqtt_password"
read_interval: 30
```

## 🏠 Home Assistant Integration

### Individual Battery Sensors
Each battery creates its own set of sensors:
```
sensor.battery_1_soc
sensor.battery_1_pack_voltage  
sensor.battery_1_pack_current
sensor.battery_1_power
sensor.battery_1_temperature
...
```

### Virtual Battery Sensors
The virtual battery provides system-wide monitoring:
```
sensor.battery_bank_soc              # Average SOC
sensor.battery_bank_pack_voltage     # Total voltage
sensor.battery_bank_pack_current     # Total current
sensor.battery_bank_power            # Total power
sensor.battery_bank_battery_count    # Number of batteries
sensor.battery_bank_connected_batteries  # List of active batteries
```

## 🔧 Hardware Setup

### Supported Configurations

#### Single RS485 Port with Multiple Addresses
```
RS485 Adapter → BMS 1 (Address 1)
              → BMS 2 (Address 2)
              → BMS 3 (Address 3)
              → BMS 4 (Address 4)
```

#### Multiple RS485 Ports
```
/dev/ttyUSB0 → BMS 1 (Address 1)
             → BMS 2 (Address 2)

/dev/ttyUSB1 → BMS 3 (Address 1)
             → BMS 4 (Address 2)
```

## 🚀 Quick Start

1. **Single Battery (Easy Start):**
   ```yaml
   bms_port: "/dev/ttyUSB0"
   bms_address: 1
   mqtt_host: "core-mosquitto"
   read_interval: 30
   ```

2. **Add More Batteries:**
   ```yaml
   multi_battery_mode: true
   batteries:
     - port: "/dev/ttyUSB0"
       address: 1
       name: "Battery_1"
     - port: "/dev/ttyUSB0"
       address: 2
       name: "Battery_2"
   enable_virtual_battery: true
   ```

## 📈 Use Cases

- **Solar Energy Storage** - Monitor multiple battery banks
- **Electric Vehicle Charging** - Track battery pack modules  
- **Backup Power Systems** - Multiple UPS battery monitoring
- **Large Scale Storage** - Industrial battery systems

## 🔍 Troubleshooting

See `MULTI_BATTERY_CONFIG.md` for detailed configuration examples and troubleshooting guide.

---

**Perfect for large battery systems and professional monitoring setups!** 🔋⚡
