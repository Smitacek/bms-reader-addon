# Battery Monitor Add-on

## Overview

Battery Monitor Add-on enables reading data from BMS (Battery Management System) LiFePO4 batteries via Modbus RTU and publishing them to Home Assistant through MQTT Auto Discovery.

## Features

- ✅ Reading data from BMS LiFePO4 batteries via Modbus RTU
- ✅ Automatic sensor configuration in Home Assistant (Auto Discovery)
- ✅ MQTT publishing of battery data (voltage, current, SOC, temperatures, etc.)
- ✅ Support for various USB/serial ports
- ✅ Configurable read interval

## Configuration

### BMS Settings

- **BMS Port**: Serial port for BMS communication. On Home Assistant, prefer the stable path under `/dev/serial/by-id` (e.g. `/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_XXXX-if00-port0`).
- **BMS Address**: Modbus address of BMS device (usually 1)
- **Read Interval**: Data reading interval in seconds (10-300s)

### MQTT Settings

- **MQTT Host**: MQTT broker address (default: `core-mosquitto`)
- **MQTT Port**: MQTT broker port (default: 1883)
- **MQTT Username**: Username for MQTT broker (optional)
- **MQTT Password**: Password for MQTT broker (optional)

### Logging

- `log_level`: Controls verbosity: `debug`, `info`, `warning`, `error`, `critical`. Default is `warning`.

### Availability (LWT)

- The add-on publishes availability to `bms/<device_id>/availability` with retained `online/offline` payloads.
- Home Assistant discovery includes availability for each sensor.

### Example configuration

```yaml
# Prefer by-id path for stability on HA
bms_port: "/dev/serial/by-id/usb-FTDI_FT232R_USB_UART_XXXX-if00-port0"
bms_address: 1
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_username: "homeassistant"
mqtt_password: "your_password"
read_interval: 30
log_level: warning
```

## MQTT Authentication

If your MQTT broker requires authentication, you must set `mqtt_username` and `mqtt_password`. For Home Assistant Mosquitto Add-on:

1. Open Mosquitto Add-on configuration
2. Add user to `logins` section:
   ```yaml
   logins:
     - username: homeassistant
       password: your_secure_password
   ```
3. Restart Mosquitto Add-on
4. Set the same credentials in Battery Monitor Add-on

## Supported data

Add-on reads and publishes the following data from BMS:

### Basic data
- **SOC** (State of Charge) - charge level in %
- **Voltage** - total battery voltage in V
- **Current** - current flow in A
- **Power** - power in W
- **Remaining Capacity** - remaining capacity in Ah

### Temperatures
- **Temperature 1-4** - sensor temperatures in °C
- **Average Temperature** - average temperature in °C

### Cell voltages
- **Cell Voltage 1-16** - individual cell voltages in V
- **Cell Voltage Delta** - difference between max and min cell in V

### System status
- **Cycles** - number of charge cycles
- **Balancing Status** - balancing state
- **Protection Status** - protection state

## Troubleshooting

### MQTT Error 5 (Authentication failure)

If you see error "MQTT connection error: 5", it means authentication problem:

1. Check if MQTT broker is correctly configured
2. Verify username/password in configuration
3. Make sure Mosquitto Add-on has created user
4. Try empty username/password if broker doesn't require authentication

### BMS reading error

If data reading from BMS fails:

1. Check USB/serial cable connection
2. Verify correct port. On HA, use Settings → System → Hardware → Serial. Prefer `/dev/serial/by-id/...`.
3. Check BMS address (usually 1)
4. Make sure BMS supports Modbus RTU protocol

### Debug log

For detailed diagnostics you can temporarily change log level to DEBUG in `addon_config.py`:

```python
self.log_level = "DEBUG"
```

## Technical information

- **Protocol**: Modbus RTU
- **Baudrate**: 9600
- **Data bits**: 8
- **Stop bits**: 1
- **Parity**: None
- **Timeout**: 2s

## Support

For support and bug reports use GitHub Issues in repository:
https://github.com/Smitacek/bms-reader-addon/issues
