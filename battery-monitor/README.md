# Battery Monitor Add-on

Monitor LiFePO4 batteries using Daren BMS with MQTT integration.

## Configuration

### Basic Options

- **bms_port**: USB port for BMS communication (default: `/dev/ttyUSB0`)
- **bms_address**: BMS device address (default: `1`)
- **mqtt_host**: MQTT broker hostname (default: `core-mosquitto`)
- **mqtt_port**: MQTT broker port (default: `1883`)
- **read_interval**: Data reading interval in seconds (default: `30`)

### Example Configuration

```yaml
bms_port: "/dev/ttyUSB0"
bms_address: 1
mqtt_host: "core-mosquitto"
mqtt_port: 1883
read_interval: 30
```

## Hardware Requirements

- USB-RS485 converter
- Daren BMS with Service 42 protocol support
- LiFePO4 battery

## Features

- Real-time battery monitoring
- MQTT Auto Discovery for Home Assistant
- Cell voltage monitoring
- Temperature monitoring
- Current and power readings
- State of Charge (SOC) tracking
