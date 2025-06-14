# BMS Reader Home Assistant Add-on

![Supports aarch64 Architecture][aarch64-shield] ![Supports armv7 Architecture][armv7-shield] ![Supports armhf Architecture][armhf-shield] ![Supports amd64 Architecture][amd64-shield]

Daren BMS Reader Add-on pro Home Assistant. Optimalizován pro **Raspberry Pi** a **Apple Silicon Mac**. Čte data z LiFePO4 BMS a automaticky vytváří senzory v Home Assistant.

## 🚀 Funkce

- **Automatické čtení** dat z Daren BMS přes RS485/USB
- **Home Assistant integrace** s Auto Discovery
- **Kompletní monitoring**: SOC, napětí, proud, teploty, články, cykly
- **Žádná ruční konfigurace MQTT** - používá vestavěný Mosquitto
- **Automatický start** při spuštění HA

## 📋 Požadavky

- **Raspberry Pi** 3/4/5 s Home Assistant OS/Supervised
- **Apple Silicon Mac** s Docker Desktop (pro development)
- **USB/RS485 převodník** připojený k BMS
- **Mosquitto broker** Add-on (doporučeno)

## 🔧 Instalace

### 1. Přidejte repository
Do Home Assistant jděte na **Supervisor → Add-on Store → ⋮ → Repositories** a přidejte:
```
https://github.com/your-repo/bms-reader-addon
```

### 2. Nainstalujte Add-on
Najděte "BMS Reader" v Add-on Store a nainstalujte.

### 3. Konfigurace
Před spuštěním upravte konfiguraci v záložce **Configuration**:

```yaml
bms:
  port: "/dev/ttyUSB0"        # USB port vašeho BMS
  address: 1                  # Adresa BMS (obvykle 1)
  baudrate: 9600
  timeout: 2.0
device:
  name: "BMS LiFePO4 Battery"
  id: "bms_lifepo4_01"       # Jedinečné ID (bez mezer!)
  manufacturer: "Daren"
  model: "Daren BMS"
mqtt:
  host: "core-mosquitto"      # Název Mosquitto Add-on
  port: 1883
  username: ""                # Ponechte prázdné pro lokální
  password: ""                # Ponechte prázdné pro lokální
  discovery_prefix: "homeassistant"
application:
  read_interval: 30           # Interval čtení (sekundy)
  log_level: "INFO"
```

### 4. Hardware setup
Ujistěte se, že váš USB/RS485 převodník je připojen:

**Zjištění USB portu:**
- Jděte na **Supervisor → System → Hardware**
- Najděte váš USB device (obvykle `/dev/ttyUSB0`)
- Nebo použijte **Terminal & SSH** Add-on: `ls /dev/tty*`

**Typické porty:**
- `/dev/ttyUSB0` - USB-RS485 převodník
- `/dev/ttyAMA0` - GPIO UART na RPi
- `/dev/ttyACM0` - USB-Serial

### 5. Spuštění
1. **Zapněte** Add-on
2. **Povolte** "Start on boot" pro automatický start
3. Zkontrolujte **Logs** pro případné chyby

## 📊 Home Assistant Senzory

Po spuštění se automaticky vytvoří:

| Entity ID | Popis | Jednotka |
|-----------|-------|----------|
| `sensor.bms_soc` | Stav nabití | % |
| `sensor.bms_pack_voltage` | Napětí baterie | V |
| `sensor.bms_pack_current` | Proud baterie | A |
| `sensor.bms_remaining_capacity` | Zbývající kapacita | Ah |
| `sensor.bms_full_capacity` | Celková kapacita | Ah |
| `sensor.bms_cycle_count` | Počet cyklů | cykly |
| `sensor.bms_ambient_temperature` | Teplota okolí | °C |
| `sensor.bms_mos_temperature` | Teplota MOS | °C |
| `sensor.bms_min_cell_voltage` | Min. napětí článku | V |
| `sensor.bms_max_cell_voltage` | Max. napětí článku | V |
| `sensor.bms_cell_voltage_difference` | Rozdíl napětí článků | V |

## 🔧 Řešení problémů

### Add-on se nespustí
1. **Zkontrolujte logs** v záložce "Log"
2. **Ověřte USB port** v konfiguraci
3. **Zkontrolujte připojení** BMS

### BMS data se nečtou
```
[ERROR] Žádná odpověď z BMS
```
- Zkontrolujte USB kabel
- Ověřte správný port (`/dev/ttyUSB0`)
- Zkontrolujte, že je BMS zapnutý
- Zkuste jiný baudrate (9600, 115200)

### MQTT nepracuje
```
[ERROR] Chyba připojení k MQTT
```
- Nainstalujte **Mosquitto broker** Add-on
- Zkontrolujte, že běží
- Použijte host: `core-mosquitto`

### Permission denied na USB
```
[ERROR] Permission denied: '/dev/ttyUSB0'
```
- Restartujte Home Assistant
- Zkontrolujte, že Add-on má povolen přístup k `uart: true`

### Senzory se nezobrazují v HA
1. Jděte na **Settings → Devices & Services**
2. Najděte "MQTT" integraci
3. Zkontrolujte, že discovery je povoleno
4. Restartujte Add-on

## 🔄 Update
Add-on se automaticky aktualizuje. Pro ruční update:
1. **Supervisor → Add-on Store**
2. Najděte "BMS Reader"
3. Klikněte **Update**

## 📝 Development

Pro vývoj a testování:
```bash
# Klonování
git clone https://github.com/your-repo/bms-reader-addon
cd bms-reader-addon

# Build lokálně
docker build -t addon-bms-reader .

# Test
docker run --device=/dev/ttyUSB0 addon-bms-reader
```

## 🆘 Podpora

- **Issues**: [GitHub Issues](https://github.com/your-repo/bms-reader-addon/issues)
- **Dokumentace**: [README](https://github.com/your-repo/bms-reader-addon)
- **Home Assistant**: [Community Forum](https://community.home-assistant.io/)

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[armhf-shield]: https://img.shields.io/badge/armhf-yes-green.svg
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
