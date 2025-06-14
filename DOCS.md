# Documentation

Dokumentace pro BMS Reader Home Assistant Add-on.

## 📁 Adresářová struktura

```
addon/
├── README.md              # Hlavní dokumentace
├── CHANGELOG.md           # Historie změn
├── DOCS.md               # Tato dokumentace
├── config.yaml           # HA Add-on konfigurace
├── Dockerfile            # Docker build
├── run.sh               # Startup script
├── requirements.txt     # Python závislosti
├── icon.png            # Add-on ikona
├── main.py             # Hlavní aplikace
├── addon_config.py     # Konfigurace pro HA
├── bms_parser.py      # BMS parsování
├── modbus.py          # Modbus komunikace
├── mqtt_helper.py     # MQTT a HA integrace
└── build_addon.sh     # Build script
```

## 🔧 Konfigurace

### config.yaml
Hlavní konfigurace Home Assistant Add-onu. Definuje:
- Podporované architektury
- Default hodnoty konfigurace
- Schema validace
- Síťová oprávnění

### addon_config.py
Python konfigurace třída, která:
- Načítá nastavení z `/data/options.json`
- Poskytuje fallback na environment proměnné
- Validuje konfiguraci
- Vytváří config objekty pro různé komponenty

## 🏗️ Build proces

### Lokální build
```bash
./build_addon.sh
```

### ARM build (pro Raspberry Pi)
```bash
./build_arm.sh
```

### Test build
```bash
docker run --rm bms-reader-addon:1.0.4 python3 -c "from config import get_config; print('OK')"
```

## 🐳 Docker informace

### Base image
- `python:3.11-alpine` - minimální Python prostředí
- Velikost: ~121MB po build

### Instalované balíčky
- `pyserial>=3.5` - sériová komunikace
- `paho-mqtt>=1.6.0` - MQTT klient

### Runtime oprávnění
- `--privileged` - přístup k USB zařízením
- Volume mount `/dev` - hardware přístup

## 🔌 Hardware podpory

### USB-RS485 převodníky
- ✅ CH340/CH341 (běžné)
- ✅ FTDI FT232R/FT232H
- ✅ CP2102/CP2104 (Silicon Labs)
- ✅ Generic USB-RS485

### Testované platformy
- ✅ Raspberry Pi 4 (ARM64)
- ✅ Raspberry Pi 3 (ARM32)
- ✅ Intel NUC (AMD64)
- ✅ Virtuální stroje

## 📊 BMS podpory

### Daren BMS
- ✅ Service 42 protocol
- ✅ LiFePO4 optimalizace
- ✅ 16S konfigurace (typická)
- ✅ Real-time monitoring

### Podporovaná data
- State of Charge (SOC) %
- Pack Voltage/Current
- Individual Cell Voltages
- Temperatures (Ambient, MOS)
- Capacity data (Remaining/Full)
- Cycle count
- Alarm status

## 🏠 Home Assistant integrace

### Auto Discovery
Addon automaticky vytvoří MQTT discovery zprávy pro:
```
homeassistant/sensor/bms_[device_id]/[sensor]/config
```

### Entity naming
- Prefix: `sensor.bms_`
- Device ID: z konfigurace
- Sensor: např. `soc`, `pack_voltage`

### Device info
```json
{
  "identifiers": ["bms_lifepo4_01"],
  "name": "BMS LiFePO4 Battery",
  "manufacturer": "Daren",
  "model": "Daren BMS",
  "sw_version": "1.0.4"
}
```

## 🔧 Troubleshooting

### Běžné problémy

#### 1. Add-on se nespustí
```bash
# Zkontrolujte logy
docker logs addon_bms_reader

# Ověřte USB port
ls /dev/ttyUSB*

# Test privileged přístup
docker run --rm --privileged -v /dev:/dev alpine ls /dev/ttyUSB*
```

#### 2. BMS nekomunikuje
```bash
# Test sériového portu
sudo screen /dev/ttyUSB0 9600

# Zkontrolujte dmesg
dmesg | grep ttyUSB

# Ověřte USB převodník
lsusb
```

#### 3. MQTT nepublikuje
```bash
# Test MQTT připojení
mosquitto_pub -h core-mosquitto -t test -m "hello"

# Zkontrolujte credentials
# V addon konfiguraci nebo MQTT nastavení
```

#### 4. Žádné entity v HA
```bash
# Zkontrolujte MQTT topics
mosquitto_sub -h core-mosquitto -t "homeassistant/#"

# Force refresh
Developer Tools → Services → mqtt.reload
```

### Debug informace

#### Logging levels
- `DEBUG` - Všechny detaily
- `INFO` - Základní informace (default)
- `WARNING` - Varování
- `ERROR` - Pouze chyby

#### Důležité logy
```bash
# Addon startup
[INFO] BMS Reader Standalone - Verze 1.0.4
[INFO] Připojování k MQTT broker: core-mosquitto:1883

# BMS komunikace
[INFO] 📤 Komunikace s BMS...
[INFO] ✅ Komunikace dokončena!

# MQTT publishing
[INFO] Home Assistant Auto Discovery config publikován
[INFO] BMS data publikována přes MQTT
```

## 🚀 Deployment

### Home Assistant Add-on Store
1. Přidejte repository: `https://github.com/Smitacek/bms-reader-addon`
2. Install & Configure
3. Start addon

### Lokální development
```bash
# Clone repository
git clone https://github.com/Smitacek/bms-reader-addon.git

# Build lokálně
cd bms-reader-addon
./build_addon.sh

# Test
docker run --rm bms-reader-addon:1.0.4
```

## 📋 Support

### GitHub Issues
https://github.com/Smitacek/bms-reader-addon/issues

### Požadované informace při hlášení problému:
1. **Home Assistant verze**
2. **Platform** (Raspberry Pi, NUC, VM)
3. **USB převodník** (lsusb output)
4. **BMS model** a firmware
5. **Add-on logy** (celý output)
6. **Konfigurace** (bez passwords)

### Community
- Home Assistant Community Forum
- Discord - Home Assistant
