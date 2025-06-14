# BMS Reader Add-ons Repository

![Version](https://img.shields.io/badge/version-1.0.4-blue.svg)
![Home Assistant](https://img.shields.io/badge/Home%20Assistant-2023.1+-green.svg)

Home Assistant Add-ons repository pro BMS Reader - monitoring Daren BMS batteries.

## 🔋 Available Add-ons

### BMS Reader
Monitoring add-on pro Daren BMS batteries s automatickou integrací do Home Assistant.

**Folder:** `bms-reader/`  
**Features:**
- ✅ Daren BMS support (Service 42 protocol)  
- ✅ MQTT Auto Discovery integration
- ✅ Real-time monitoring every 30 seconds
- ✅ LiFePO4 battery optimization
- ✅ Multi-architecture support (ARM64, AMD64)

## 🚀 Installation

### Add Repository to Home Assistant

1. **Open Home Assistant** → Settings → Add-ons → Add-on Store
2. **Click** ⋮ (three dots) → "Repositories"
3. **Add URL:** `https://github.com/Smitacek/bms-reader-addon`
4. **Click** "ADD"
5. **Refresh** the page
6. **Find** "BMS Reader" in the add-ons list
7. **Click** "INSTALL"

### Direct Installation

```bash
# SSH to your Home Assistant device
ssh root@homeassistant.local

# Add repository manually
ha addons repo add https://github.com/Smitacek/bms-reader-addon

# Install addon
ha addons install local_bms_reader
```

## ⚙️ Configuration

After installation, configure the add-on:

```yaml
bms:
  port: "/dev/ttyUSB0"        # Your USB port
  address: 1
  baudrate: 9600
  timeout: 2.0

device:
  name: "BMS LiFePO4 Battery"
  id: "bms_lifepo4_01"       # Unique ID
  manufacturer: "Daren"
  model: "Daren BMS"

mqtt:
  host: "core-mosquitto"      # or IP address
  port: 1883
  username: ""                # Leave empty for local
  password: ""

app:
  read_interval: 30           # Read interval in seconds
  log_level: "INFO"
```

## 📊 Monitored Data

The add-on provides the following sensors:

- **State of Charge (SOC)** - Battery percentage
- **Pack Voltage** - Total battery voltage  
- **Pack Current** - Charging/discharging current
- **Cell Voltages** - Individual cell monitoring
- **Temperatures** - Ambient and MOS temperatures
- **Capacity Data** - Remaining and full capacity
- **Cycle Count** - Battery lifecycle data

## 🔌 Hardware Requirements

### Supported Platforms
- ✅ Raspberry Pi 4 (ARM64)
- ✅ Raspberry Pi 3 (ARM32) 
- ✅ Intel NUC (AMD64)
- ✅ Virtual Machines

### USB-RS485 Converters
- ✅ CH340/CH341 based
- ✅ FTDI FT232R/FT232H
- ✅ CP2102/CP2104 (Silicon Labs)
- ✅ Generic USB-RS485 adapters

### BMS Support
- ✅ **Daren BMS** with Service 42 protocol
- ✅ **LiFePO4 batteries** (optimized)
- ✅ **16S configurations** (typical)

## 🛠️ Troubleshooting

### Common Issues

#### 1. Add-on Won't Start
- Check USB port configuration
- Enable "Privileged" access in Network tab
- Verify BMS is powered and connected

#### 2. No Data from BMS
```bash
# Check USB devices
ls /dev/ttyUSB*

# Test serial connection
sudo screen /dev/ttyUSB0 9600
```

#### 3. MQTT Not Publishing
- Verify MQTT broker is running
- Check credentials and host settings
- Test with Developer Tools → Services → mqtt.publish

### Debug Information

Enable debug logging by setting `log_level: "DEBUG"` in configuration.

Expected log output:
```
[INFO] BMS Reader Standalone - Version 1.0.4
[INFO] Loading configuration from Home Assistant options
[INFO] Connecting to MQTT broker: core-mosquitto:1883
[INFO] MQTT connection successful!
[INFO] 📤 Communicating with BMS...
[INFO] ✅ Communication completed!
[INFO] Home Assistant Auto Discovery config published
[INFO] BMS data published via MQTT
```

## 📋 Support

- **Issues:** [GitHub Issues](https://github.com/Smitacek/bms-reader-addon/issues)
- **Documentation:** [Wiki](https://github.com/Smitacek/bms-reader-addon/wiki)
- **Discussions:** [GitHub Discussions](https://github.com/Smitacek/bms-reader-addon/discussions)

## 📚 Documentation

- [`CHANGELOG.md`](CHANGELOG.md) - Version history and changes
- [`DOCS.md`](DOCS.md) - Technical documentation
- [`bms-reader/README.md`](bms-reader/README.md) - Add-on specific documentation

## 🏷️ Version History

- **1.0.4** - Production release with ARM optimization
- **1.0.3** - MQTT stability improvements
- **1.0.2** - Configuration enhancements
- **1.0.1** - Initial release

---

**Repository URL:** `https://github.com/Smitacek/bms-reader-addon`
