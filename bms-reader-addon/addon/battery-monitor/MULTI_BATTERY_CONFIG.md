# Sample Configuration for Multi-Battery Monitor

## Simple Configuration (single battery - backward compatibility)
```yaml
bms_port: "/dev/ttyUSB0"
bms_address: 1
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_username: ""
mqtt_password: ""
read_interval: 30
log_level: warning
```

## Multi-battery configuration (up to 16 batteries)
```yaml
# Enable multi-battery mode
multi_battery_mode: true

# Individual battery configuration
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
  - port: "/dev/ttyUSB1"
    address: 2
    name: "Battery_4"
    enabled: false  # temporarily disabled

# Virtual battery (aggregates data from all batteries)
enable_virtual_battery: true
virtual_battery_name: "Battery Bank"

# MQTT configuration
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_username: "mqtt_user"
mqtt_password: "mqtt_password"
read_interval: 30
log_level: warning
```

## Example for solar system with 8 batteries
```yaml
multi_battery_mode: true

batteries:
  # Rack 1 - 4 batteries
  - port: "/dev/ttyUSB0"
    address: 1
    name: "Rack1_Battery1"
    enabled: true
  - port: "/dev/ttyUSB0"
    address: 2
    name: "Rack1_Battery2"
    enabled: true
  - port: "/dev/ttyUSB0"
    address: 3
    name: "Rack1_Battery3"
    enabled: true
  - port: "/dev/ttyUSB0"
    address: 4
    name: "Rack1_Battery4"
    enabled: true
    
  # Rack 2 - 4 batteries
  - port: "/dev/ttyUSB1"
    address: 1
    name: "Rack2_Battery1"
    enabled: true
  - port: "/dev/ttyUSB1"
    address: 2
    name: "Rack2_Battery2"
    enabled: true
  - port: "/dev/ttyUSB1"
    address: 3
    name: "Rack2_Battery3"
    enabled: true
  - port: "/dev/ttyUSB1"
    address: 4
    name: "Rack2_Battery4"
    enabled: true

# Virtual battery for entire system
enable_virtual_battery: true
virtual_battery_name: "Solar Battery System"

mqtt_host: "192.168.1.100"
mqtt_port: 1883
mqtt_username: "homeassistant"
mqtt_password: "ha_password"
read_interval: 30
```

## Home Assistant sensors

### Individual batteries
For each battery, sensors will be created:
- `sensor.battery_1_soc` - SOC of battery 1
- `sensor.battery_1_pack_voltage` - Voltage of battery 1
- `sensor.battery_1_pack_current` - Current of battery 1
- ... (for each battery)

### Virtual battery (aggregated values)
- `sensor.battery_bank_soc` - Average SOC of all batteries
- `sensor.battery_bank_pack_voltage` - Total voltage (sum)
- `sensor.battery_bank_pack_current` - Total current (sum)
- `sensor.battery_bank_power` - Total power
- `sensor.battery_bank_battery_count` - Number of connected batteries
- `sensor.battery_bank_connected_batteries` - List of connected batteries

## Benefits of multi-battery mode

1. **Individual battery monitoring**
   - Each battery has its own sensors in HA
   - Ability to monitor individual cell performance
   - Identification of problematic batteries

2. **Virtual battery**
   - Overall system overview
   - Aggregated values (SOC, power, capacity)
   - Simple automation for the entire system

3. **Flexible configuration**
   - Up to 16 batteries on different ports/addresses
   - Ability to temporarily disable batteries
   - Custom names for better identification

4. **Backward compatibility**
   - Old configuration (single battery) still works
   - Smooth transition to multi-battery mode
