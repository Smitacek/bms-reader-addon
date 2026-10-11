# Battery Monitor Add-on - Multi-Battery Support

![Version](https://img.shields.io/badge/version-1.2.3-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1+-green.svg)

Advanced monitoring add-on for Daren BMS batteries with **multi-battery support** and virtual battery aggregation.

## 🆕 New in Version 1.2.0

- ✅ MQTT auto credentials via Home Assistant Supervisor (Mosquitto) discovery; manual options remain as fallback/override

## 🆕 New in Version 1.1.9

- ✅ One-off discovery tool to generate batteries config (writes `/data/discovered_batteries.yaml`)
- ✅ Energy Dashboard entities: cumulative `energy_in_total` and `energy_out_total` (kWh)
- ✅ Persist energy counters across restarts (stored under `/data`)
- ✅ Hardened MQTT reconnect with rate-limited auto-reconnect
- ✅ Last Will and Testament (LWT) + HA availability in discovery
- ✅ Lower default log level to WARNING, `log_level` option added
- ✅ Robust serial frame handling (stop at CR, sanitize payload)

## 🔋 Features

### Core Features
- ✅ **Daren BMS Support** - Service 42 protocol compatibility
- ✅ **MQTT Auto Discovery** - Automatic integration with Home Assistant (+ availability)
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
- **Energy In Total** - kWh (charging; cumulative, total_increasing)
- **Energy Out Total** - kWh (discharging; cumulative, total_increasing)
- **Remaining Capacity** - Ah
- **Cell Voltages** - Individual cell monitoring
- **Temperature** - Battery temperature
- **Status** - Charge/discharge/idle

### Virtual Battery (Aggregated)
- **State of charge** - Full-bank capacity-weighted reported SoC
- **Average Pack Voltage** - Mean of per-battery pack voltages (topology-agnostic)
- **Pack Voltage Range** - Min/Max pack voltage across batteries and their difference
- **Energy In Total** - kWh (sum of per-battery cumulative charging)
- **Energy Out Total** - kWh (sum of per-battery cumulative discharging)
- **Battery Count** - Number of connected batteries
- **Cell Voltage Range** - Min/Max across all cells

## ⚙️ Configuration

### MQTT Auto Credentials (Supervisor)
- The add-on now automatically fetches MQTT host/port/credentials from Home Assistant Supervisor (Mosquitto add-on) via service discovery.
- If discovered, these credentials are used by default. Manual values in options act as a fallback or override:
  - If you set `mqtt_username/mqtt_password` in options, they override auto creds.
  - If you set a custom `mqtt_host`/`mqtt_port`, that also overrides auto host/port.
  - Leave `mqtt_username`/`mqtt_password` empty to use auto credentials with the Mosquitto add-on.

### Single Battery (Backward Compatible)
```yaml
bms_port: "/dev/ttyUSB0"
bms_address: 1
mqtt_host: "core-mosquitto"
mqtt_port: 1883
read_interval: 30
# optional
log_level: warning
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
# optional
log_level: warning
```

## 🏠 Home Assistant Integration

Security
- AppArmor confinement is enabled (`apparmor: true`). The add-on requests only UART access (`uart: true`) and avoids broader `devices:` mappings.

### Individual Battery Sensors
Each battery creates its own set of sensors:
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

### Virtual Battery Sensors
The virtual battery avoids topology-dependent totals and exposes:
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

## ⚡ Energy Dashboard

- The add-on publishes two cumulative energy sensors per battery (and for the virtual bank): `energy_in_total` and `energy_out_total`.
- Discovery sets `device_class: energy`, `state_class: total_increasing`, unit `kWh`, so they are accepted by Home Assistant Energy → Home battery storage.
- Counters persist across restarts using add-on storage under `/data`.

## 🔎 One-off Discovery Tool

- Quickly discover connected BMS units and generate a `batteries:` config:
  - Set `discovery_mode: true` in add-on options (optionally set `discovery_address_from/to`, `discovery_timeout_ms`, `discovery_ports`).
  - Start the add-on. It scans existing serial ports and writes `/data/discovered_batteries.yaml` with a ready-to-copy YAML snippet.
  - Copy the `batteries:` block to options, set `multi_battery_mode: true`, disable `discovery_mode`, and restart.
  - Logs show a summary and a short preview of the generated YAML.

## Availability (LWT)

- Availability is published to `bms/<device_id>/availability` as retained `online/offline`.
- Discovery includes availability so HA marks sensors unavailable when the add-on is down.

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

## 1.2.3 sensor semantics and availability

See [SENSOR_SEMANTICS.md](SENSOR_SEMANTICS.md) for units/classes, SoC weighting, stale_timeout, energy persistence and migration checks. Home Assistant Core 2025.10 or newer is required.
