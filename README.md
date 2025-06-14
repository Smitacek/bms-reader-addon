# BMS Reader Add-on for Home Assistant

![Version](https://img.shields.io/badge/version-1.0.4-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1+-green.svg)

Home Assistant Add-on repository for **Battery Monitor** - monitoring Daren BMS LiFePO4 batteries.

## 🔋 Battery Monitor Add-on

Advanced monitoring add-on for Daren BMS batteries with automatic Home Assistant integration via MQTT Auto Discovery.

### Features

- ✅ **Daren BMS Support** - Service 42 protocol compatibility
- ✅ **MQTT Auto Discovery** - Automatic integration with Home Assistant
- ✅ **Real-time Monitoring** - Configurable read intervals (10-300 seconds)
- ✅ **LiFePO4 Optimized** - Designed specifically for LiFePO4 battery systems
- ✅ **Multi-architecture** - Supports ARM64, AMD64, ARMv7
- ✅ **Robust Connection** - Advanced MQTT connection handling with retry logic
- ✅ **Comprehensive Diagnostics** - Built-in troubleshooting tools

### Installation

1. **Add Repository to Home Assistant:**
   ```
   https://github.com/Smitacek/bms-reader-addon
   ```

2. **Install the Add-on:**
   - Go to Home Assistant → Add-ons → Add-on Store
   - Find "Battery Monitor" and click Install

3. **Configure the Add-on:**
   ```yaml
   bms_port: "/dev/ttyUSB0"
   bms_address: 1
   mqtt_host: "core-mosquitto"
   mqtt_port: 1883
   mqtt_username: "your_username"  # if required
   mqtt_password: "your_password"  # if required
   read_interval: 30
   ```

4. **Start the Add-on** and check logs

### Monitored Parameters

- **Battery State of Charge (SOC)** - %
- **Pack Voltage** - V
- **Pack Current** - A (positive = charging, negative = discharging)
- **Remaining Capacity** - Ah
- **Cell Voltages** - Individual cell monitoring
- **Temperature** - Battery temperature
- **Charge/Discharge Status**
- **Protection Status** - Over/under voltage, current, temperature

### Hardware Requirements

- **Daren BMS** with Service 42 support
- **RS485 to USB adapter** or direct serial connection
- **Home Assistant** with Mosquitto MQTT broker

### Supported Devices

- `/dev/ttyUSB0`, `/dev/ttyUSB1` - USB serial adapters
- `/dev/ttyAMA0` - Raspberry Pi hardware UART

### Troubleshooting

If you experience issues, the add-on includes comprehensive diagnostics:

1. **Check Add-on Logs** for detailed connection information
2. **MQTT Connection Issues**: Verify Mosquitto broker is running and configured
3. **BMS Communication**: Ensure correct baud rate (9600) and device address
4. **Serial Port**: Verify device permissions and availability

### Home Assistant Integration

All sensors are automatically discovered in Home Assistant:

- `sensor.bms_soc` - State of Charge
- `sensor.bms_pack_voltage` - Pack Voltage  
- `sensor.bms_pack_current` - Pack Current
- `sensor.bms_remaining_capacity` - Remaining Capacity
- `sensor.bms_temperature` - Temperature
- `sensor.bms_cell_1_voltage` - Cell 1 Voltage
- ... (additional cells as available)

### Version History

- **v1.0.4** - Enhanced MQTT connection handling, improved diagnostics
- **v1.0.3** - Stable release with full Home Assistant integration
- **v1.0.2** - Bug fixes and performance improvements
- **v1.0.1** - Initial release

### Support

For issues and questions, please use the [GitHub Issues](https://github.com/Smitacek/bms-reader-addon/issues).

### License

This project is licensed under the MIT License.

---

**Note:** This add-on is specifically designed for Daren BMS systems. For other BMS types, modifications may be required.