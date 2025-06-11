# BMS Reader + MQTT/Home Assistant

Aplikace pro čtení dat z Daren BMS a odesílání na MQTT server (Home Assistant).

## 🚀 Funkce

- **Čtení BMS dat** přes RS485/Service 42
- **MQTT publikování** s Home Assistant Auto Discovery
- **Kontinuální monitoring** s konfigurovatelným intervalem
- **Kompletní BMS data**: SOC, napětí, proud, teploty, články, cykly

## 📋 Požadavky

- Python 3.13+
- RS485/USB převodník připojený k BMS
- MQTT broker (Home Assistant)

## ⚙️ Konfigurace

### 1. Upravte `config.py`

```python
# BMS komunikace
class BMSConfig:
    PORT = "/dev/tty.usbserial-XXXXX"  # Váš USB port
    BMS_ADDRESS = 0x01                 # Adresa BMS (obvykle 0x01)
    BAUDRATE = 9600
    TIMEOUT = 2.0

# MQTT/Home Assistant
class MQTTConfig:
    BROKER_HOST = "192.168.1.100"      # IP adresa Home Assistant
    BROKER_PORT = 1883
    USERNAME = "mqtt_user"             # MQTT uživatel
    PASSWORD = "mqtt_password"         # MQTT heslo
    DEVICE_ID = "bms_lifepo4_01"       # Jedinečné ID zařízení

# Aplikace
class AppConfig:
    READ_INTERVAL = 30                 # Interval čtení (sekundy)
    LOG_LEVEL = "INFO"                 # DEBUG, INFO, WARNING, ERROR
```

### 2. Najděte USB port

```bash
# macOS/Linux
ls /dev/tty.usbserial-*
# nebo
ls /dev/ttyUSB*
```

### 3. Nastavte MQTT v Home Assistant

V `configuration.yaml`:
```yaml
mqtt:
  broker: localhost
  port: 1883
  username: mqtt_user
  password: mqtt_password
  discovery: true
  discovery_prefix: homeassistant
```

## 🏃‍♂️ Spuštění

### Instalace závislostí
```bash
uv sync
```

### Test konfigurace
```bash
uv run test_mqtt.py
```

### Spuštění aplikace
```bash
uv run main.py
```

### Spuštění na pozadí
```bash
# Linux/macOS
nohup uv run main.py > bms.log 2>&1 &

# Nebo použijte systemd service (Linux)
```

## 📊 Home Assistant senzory

Po spuštění se automaticky vytvoří tyto senzory:

| Senzor | Jednotka | Popis |
|--------|----------|-------|
| `sensor.bms_soc` | % | Stav nabití |
| `sensor.bms_pack_voltage` | V | Napětí baterie |
| `sensor.bms_pack_current` | A | Proud baterie |
| `sensor.bms_remaining_capacity` | Ah | Zbývající kapacita |
| `sensor.bms_full_capacity` | Ah | Celková kapacita |
| `sensor.bms_cycle_count` | cykly | Počet cyklů |
| `sensor.bms_ambient_temperature` | °C | Teplota okolí |
| `sensor.bms_mos_temperature` | °C | Teplota MOS |
| `sensor.bms_min_cell_voltage` | V | Min. napětí článku |
| `sensor.bms_max_cell_voltage` | V | Max. napětí článku |
| `sensor.bms_cell_voltage_difference` | V | Rozdíl napětí článků |

## 🐛 Řešení problémů

### Chyba "No module named 'serial'"
```bash
uv add pyserial
```

### Chyba "Permission denied" na USB portu
```bash
# Linux
sudo usermod -a -G dialout $USER
# Odhlaste se a přihlaste znovu

# macOS - obvykle není nutné
```

### BMS nereaguje
- Zkontrolujte zapojení RS485 (A, B správně)
- Ověřte správný USB port
- Zkontrolujte baudrate (obvykle 9600)
- Ověřte adresu BMS (obvykle 0x01)

### MQTT connection failed
- Zkontrolujte IP adresu a port
- Ověřte username/password
- Zkontrolujte firewall
- Ověřte, že MQTT broker běží

### Home Assistant neukazuje senzory
- Zkontrolujte MQTT discovery v HA
- Ověřte MQTT logs v HA
- Restartujte Home Assistant

## 📝 Logy

Program zapisuje detailní logy. Pro ladění změňte v `config.py`:
```python
LOG_LEVEL = "DEBUG"
```

## 🔧 Systemd služba (Linux)

Vytvořte `/etc/systemd/system/bms-reader.service`:
```ini
[Unit]
Description=BMS Reader
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/path/to/BMS
ExecStart=/path/to/uv run main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Povolte a spusťte:
```bash
sudo systemctl enable bms-reader
sudo systemctl start bms-reader
```

## 📋 MQTT Topics

### Discovery topics
```
homeassistant/sensor/bms_lifepo4_01/soc/config
homeassistant/sensor/bms_lifepo4_01/pack_voltage/config
...
```

### State topics
```
bms/bms_lifepo4_01/soc
bms/bms_lifepo4_01/pack_voltage
bms/bms_lifepo4_01/pack_current
...
```
