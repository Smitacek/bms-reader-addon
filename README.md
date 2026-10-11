# BMS Reader Add-on for Home Assistant

![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1+-green.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

🔋 **Advanced multi-battery monitoring** for Daren BMS LiFePO4 batteries with **virtual battery aggregation** and **Home Assistant Auto Discovery**.

## 🆕 Latest: Battery Monitor Multi v1.2.3

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
2. **Install:** "Battery Monitor Multi" v1.2.2 (slug: `battery-monitor-v2`)
3. **Configure:** Multi-battery setup or single battery (fully compatible)

### 🔌 Use Stable Serial Paths (by-id) on Home Assistant

On Raspberry Pi and USB adapters, `/dev/ttyUSB0` can change after reboots or re-plugs. Prefer the stable symlink from `/dev/serial/by-id`:

- In Home Assistant: Settings → System → Hardware → All hardware → Serial.
- Copy the full path like `/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AH06XABC-if00-port0`.
- Use this path in `bms_port` or per-battery `port`.

---

## 🔋 Battery Monitor Add-on

**Advanced monitoring system for Daren BMS batteries with automatic Home Assistant integration via MQTT Auto Discovery.**

### 🆕 New in Version 1.2.0

- ✅ MQTT auto credentials via Home Assistant Supervisor (Mosquitto) discovery; manual values still override when provided

### 🆕 New in Version 1.1.9

- ✅ Energy Dashboard sensors: cumulative energy-in/out in kWh
- ✅ One-off discovery tool (writes `/data/discovered_batteries.yaml`)
- ✅ Counters persist across restarts (stored under `/data`)
- ✅ MQTT reconnect handling hardened (rate-limited auto-reconnect)
- ✅ LWT availability in HA discovery for all sensors

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
   # Prefer by-id path (stable across reboots)
   bms_port: "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AH06XABC-if00-port0"
   bms_address: 1
   # MQTT credentials are auto-detected from Supervisor when available.
   # Optionally override manually:
   # mqtt_host: "core-mosquitto"
   # mqtt_port: 1883
   read_interval: 30
   # optional
   log_level: warning
   ```

   **Multi-Battery Setup:**
   ```yaml
   multi_battery_mode: true
   batteries:
     - port: "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AH06XABC-if00-port0"
       address: 1
       name: "Battery_1"
       enabled: true
     - port: "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_AH06XABC-if00-port0"
       address: 2
       name: "Battery_2"
       enabled: true
   enable_virtual_battery: true
   virtual_battery_name: "Battery Bank"
   # MQTT credentials are auto-detected from Supervisor when available.
   # Optionally override manually:
   # mqtt_host: "core-mosquitto"
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
- **Energy In Total** - kWh (charging; cumulative, total_increasing)
- **Energy Out Total** - kWh (discharging; cumulative, total_increasing)
- **Cell Voltages** - Individual cell monitoring
- **Temperature** - Battery temperature
- **Charge/Discharge Status**
- **Protection Status** - Over/under voltage, current, temperature

#### Virtual Battery (Aggregated from All Batteries)
- **State of charge** - Full-bank capacity-weighted reported SoC
- **Pack voltage statistics** - Mean/minimum/maximum/difference, without topology assumptions
- **Energy In Total** - kWh (cumulative charging into bank)
- **Energy Out Total** - kWh (cumulative discharging from bank)
- No bank current, total voltage, power or Ah capacity without a known topology.
- **Battery Count** - Number of connected batteries

### Hardware Requirements

- **Daren BMS** with Service 42 support (up to 16 units)
- **RS485 to USB adapter(s)** or direct serial connection
- **Home Assistant** with Mosquitto MQTT broker

### Supported Devices

- `/dev/serial/by-id/...` - Recommended stable USB serial path
- `/dev/ttyUSB0`, `/dev/ttyUSB1` - USB serial adapters (may change across reboots)
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
sensor.battery_1_energy_in_total      # kWh, total_increasing
sensor.battery_1_energy_out_total     # kWh, total_increasing
sensor.battery_1_temperature
...
```

#### Virtual Battery Sensors (system overview)
```
sensor.battery_bank_soc                 # Capacity-weighted SoC
sensor.battery_bank_avg_pack_voltage    # Average of pack voltages
sensor.battery_bank_pack_voltage_min    # Minimum pack voltage
sensor.battery_bank_pack_voltage_max    # Maximum pack voltage
sensor.battery_bank_pack_voltage_diff   # Max - Min pack voltage
sensor.battery_bank_energy_in_total     # kWh, total_increasing (sum of batteries)
sensor.battery_bank_energy_out_total    # kWh, total_increasing (sum of batteries)
sensor.battery_bank_battery_count       # Number of batteries
sensor.battery_bank_connected_batteries # List of active batteries
```

### Energy Dashboard

- Provides two required cumulative energy sensors per battery (and for the virtual bank):
  `energy_in_total` and `energy_out_total` with `device_class: energy`, `state_class: total_increasing`, `unit_of_measurement: kWh`.
- These appear under Home Assistant Energy → Home battery storage. Counters persist across restarts.

### One-off Discovery Tool

- To scan connected batteries and generate a ready-to-copy config:
  1) In add-on options set `discovery_mode: true` (optionally adjust `discovery_address_from/to`, `discovery_timeout_ms`, `discovery_ports`).
  2) Start the add-on. It will scan existing serial ports and addresses, then write `/data/discovered_batteries.yaml` with a `batteries:` block.
  3) Copy the `batteries:` block into add-on options, set `multi_battery_mode: true` and desired names, then set `discovery_mode: false` and restart.
  - The log also shows a preview of the generated YAML and the number of devices found.

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

- v1.2.2 - Voltages use 3-decimal display precision via MQTT discovery
- v1.2.1 - Virtual battery is topology-agnostic: remove total voltage/current/power, add avg/min/max/diff pack voltage; sum of per-battery energy kWh
- v1.2.0 - MQTT auto-credentials via Supervisor discovery; manual override preserved; AppArmor enabled; reduced device permissions
- v1.1.9 - Add one-off discovery tool + Energy Dashboard sensors (kWh) + persistence
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

## 1.2.3 sensor semantics and availability

See [SENSOR_SEMANTICS.md](addon/battery-monitor/SENSOR_SEMANTICS.md) for units/classes, SoC weighting, stale_timeout, energy persistence and migration checks. Home Assistant Core 2025.10 or newer is required.
