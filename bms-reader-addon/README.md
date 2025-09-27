# BMS Reader Add-on for Home Assistant

![Version](https://img.shields.io/badge/version-1.1.6-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

🔋 **Advanced multi-battery monitoring** for Daren BMS LiFePO4 batteries with **virtual battery aggregation** and **Home Assistant Auto Discovery**.

## 🆕 Latest: Battery Monitor Multi v1.1.6

Production-ready multi-battery monitoring with improved MQTT reliability and reduced logging noise.

### ✨ Key Features:
- 🔋 **Monitor up to 16 batteries** simultaneously with individual configuration
- 🏦 **Virtual Battery** - Smart aggregation of all batteries into a unified entity  
- 📊 **Individual Monitoring** - Each battery gets dedicated Home Assistant sensors
- ⚙️ **Flexible Configuration** - Different ports, addresses, and names per battery
- 🔄 **Backward Compatibility** - Single battery setups work without changes
- 🔍 **Enhanced Logging** - Reduced noise by default (WARNING), configurable via `log_level`
- 📡 **Auto Discovery** - Seamless Home Assistant integration via MQTT
 - 🟢 **Availability (LWT)** - Publishes `online/offline` status to Home Assistant

### 🚀 Quick Start:
1. **Add Repository:** `https://github.com/Smitacek/bms-reader-addon`
2. **Install:** "Battery Monitor Multi" v1.1.6 (slug: `battery-monitor-v2`)
3. **Configure:** Multi-battery setup or single battery (fully compatible)

---

## 🔋 Battery Monitor Add-on

**Advanced monitoring system for Daren BMS batteries with automatic Home Assistant integration via MQTT Auto Discovery.**

### 🆕 New in Version 1.1.6

- ✅ MQTT reconnect handling hardened (rate-limited auto-reconnect, stable loop)
- ✅ Last Will and Testament (LWT) + availability in HA discovery
- ✅ Default log level lowered to WARNING; `log_level` option added
- ✅ Serial framing fix: robust ASCII frame extraction ending at CR

### Features

- 🔋 **Daren BMS Support** - Service 42 protocol compatibility
- 📡 **MQTT Auto Discovery** - Automatic integration with Home Assistant
- ⏱️ **Real-time Monitoring** - Configurable read intervals (10-300 seconds)
- 🔋 **LiFePO4 Optimized** - Designed specifically for LiFePO4 battery systems
- 🏗️ **Multi-architecture** - Supports ARM64, AMD64, ARMv7
- 🔗 **Robust Connection** - Advanced MQTT connection handling with retry logic
- 🔍 **Comprehensive Diagnostics** - Built-in troubleshooting tools
- 📊 **Enhanced Logging** - Detailed startup and runtime information

### Installation

1. **Add Repository to Home Assistant:**
   ```
   https://github.com/Smitacek/bms-reader-addon
   ```

2. **Install the Add-on:**
   - Go to Home Assistant → Add-ons → Add-on Store
   - Find "Battery Monitor" and click Install

3. **Configure the Add-on:**

   **Single Battery (Simple):**
   ```yaml
   bms_port: "/dev/ttyUSB0"
   bms_address: 1
   mqtt_host: "core-mosquitto"
   mqtt_port: 1883
   read_interval: 30
   # optional
   log_level: warning
   ```

   **Multi-Battery Setup:**
   ```yaml
   multi_battery_mode: true
   batteries:
     - port: "/dev/ttyUSB0"
       address: 1
       name: "Battery_1"
       enabled: true
     - port: "/dev/ttyUSB0"
       address: 2
       name: "Battery_2"
       enabled: true
   enable_virtual_battery: true
   virtual_battery_name: "Battery Bank"
   mqtt_host: "core-mosquitto"
   read_interval: 30
   # optional
   log_level: warning
   ```

4. **Start the Add-on** and check logs

### Monitored Parameters

#### Per Individual Battery
- **Battery State of Charge (SOC)** - %
- **Pack Voltage** - V
- **Pack Current** - A (positive = charging, negative = discharging)
- **Remaining Capacity** - Ah
- **Cell Voltages** - Individual cell monitoring
- **Temperature** - Battery temperature
- **Charge/Discharge Status**
- **Protection Status** - Over/under voltage, current, temperature

#### Virtual Battery (Aggregated from All Batteries)
- **Average SOC** - Weighted average across all batteries
- **Total Voltage** - Sum of all battery voltages
- **Total Current** - Sum of all battery currents  
- **Total Power** - Combined power output
- **Total Capacity** - Sum of remaining capacity
- **Battery Count** - Number of connected batteries

### Hardware Requirements

- **Daren BMS** with Service 42 support (up to 16 units)
- **RS485 to USB adapter(s)** or direct serial connection
- **Home Assistant** with Mosquitto MQTT broker

### Supported Devices

- `/dev/ttyUSB0`, `/dev/ttyUSB1` - USB serial adapters
- `/dev/ttyAMA0` - Raspberry Pi hardware UART
- **Multiple addresses** on same RS485 bus (1-255)

### Use Cases

- **Solar Energy Storage** - Monitor multiple battery banks
- **Electric Vehicle Charging** - Track battery pack modules
- **Backup Power Systems** - Multiple UPS battery monitoring  
- **Large Scale Storage** - Industrial battery systems

### Home Assistant Integration

#### Individual Battery Sensors (per battery)
```
sensor.battery_1_soc
sensor.battery_1_pack_voltage  
sensor.battery_1_pack_current
sensor.battery_1_power
sensor.battery_1_temperature
...
```

#### Virtual Battery Sensors (system overview)
```
sensor.battery_bank_soc              # Average SOC
sensor.battery_bank_pack_voltage     # Total voltage
sensor.battery_bank_pack_current     # Total current
sensor.battery_bank_power            # Total power
sensor.battery_bank_battery_count    # Number of batteries
sensor.battery_bank_connected_batteries  # List of active batteries
```

### Configuration Examples

#### Solar System with 4 Batteries
```yaml
multi_battery_mode: true
batteries:
  - port: "/dev/ttyUSB0"
    address: 1
    name: "Solar_Battery_1"
  - port: "/dev/ttyUSB0"
    address: 2
    name: "Solar_Battery_2"
  - port: "/dev/ttyUSB0"
    address: 3
    name: "Solar_Battery_3"
  - port: "/dev/ttyUSB0"
    address: 4
    name: "Solar_Battery_4"
enable_virtual_battery: true
virtual_battery_name: "Solar Battery Bank"
```

#### Multiple RS485 Adapters
```yaml
multi_battery_mode: true
batteries:
  # First adapter
  - port: "/dev/ttyUSB0"
    address: 1
    name: "Rack1_Battery1"
  - port: "/dev/ttyUSB0"
    address: 2
    name: "Rack1_Battery2"
  # Second adapter  
  - port: "/dev/ttyUSB1"
    address: 1
    name: "Rack2_Battery1"
  - port: "/dev/ttyUSB1"
    address: 2
    name: "Rack2_Battery2"
```

### Troubleshooting

If you experience issues, the add-on includes comprehensive diagnostics:

1. **Check Add-on Logs** for detailed connection information
2. **MQTT Connection Issues**: Verify Mosquitto broker is running and configured
3. **BMS Communication**: Ensure correct baud rate (9600) and device addresses
4. **Serial Port**: Verify device permissions and availability
5. **Multi-Battery Issues**: Check individual battery wiring and addresses

### Availability Topic (LWT)

- Availability published to `bms/<device_id>/availability` with retained `online/offline`.
- Home Assistant discovery includes availability to mark sensors unavailable when addon is down.

### Version History

- v1.1.6 - MQTT reconnect + LWT, lower default logging, serial frame fix
- v1.1.5 - Language unification and docs
- v1.1.4 - New slug battery-monitor-v2; logging/diagnostics improvements
- v1.1.3 - Fixed missing sensor values, data mapping and debug logging
- v1.1.0 - Multi-battery support, virtual battery aggregation
- v1.0.4 - Enhanced MQTT connection handling, improved diagnostics
- v1.0.3 - Stable release with full Home Assistant integration

### Support

For issues and questions, please use the [GitHub Issues](https://github.com/Smitacek/bms-reader-addon/issues).

### License

This project is licensed under the MIT License.

---

**Perfect for monitoring large battery systems, solar installations, and professional setups with multiple batteries!** 🔋⚡
