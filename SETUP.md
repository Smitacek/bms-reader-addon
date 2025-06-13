# 🚀 Rychlé nastavení BMS Reader

## 1️⃣ Kopírování konfigurace
```bash
cp config.ini.example config.ini
```

## 2️⃣ Upravte config.ini
Otevřete `config.ini` a upravte:

### BMS sekce:
```ini
[BMS]
port = /dev/tty.usbserial-VÁŠE_ZAŘÍZENÍ
```
**Jak najít port:**
- macOS: `ls /dev/tty.usbserial-*`
- Linux: `ls /dev/ttyUSB*`

### MQTT sekce:
```ini
[MQTT]
broker_host = VAŠE_HA_IP_ADRESA
username = VÁŠE_MQTT_JMÉNO
password = VÁŠE_MQTT_HESLO
```

### Device sekce:
```ini
[DEVICE]
device_id = bms_garage_01  # Jedinečné ID bez mezer
```

## 3️⃣ Test komunikace s BMS
```bash
uv run bms_read_once.py
```
✅ Měli byste vidět data ze svého BMS

## 4️⃣ Test MQTT konfigurace
```bash
uv run test_mqtt.py
```
✅ Ověří správnost MQTT nastavení

## 5️⃣ Spuštění s MQTT
```bash
uv run main.py
```
✅ Spustí kontinuální čtení a odesílání na Home Assistant

## 🏠 Home Assistant
Po spuštění se automaticky vytvoří senzory:
- `sensor.bms_soc`
- `sensor.bms_pack_voltage`
- `sensor.bms_pack_current`
- A další...

## 🔧 Časté problémy

**BMS nereaguje:**
- Zkontrolujte USB kabel
- Ověřte správný port v config.ini
- Zkontrolujte, že je BMS zapnutý

**MQTT se nepřipojí:**
- Ověřte IP adresu Home Assistant
- Zkontrolujte MQTT credentials
- Ujistěte se, že MQTT broker běží v HA

## 📖 Více informací
Podrobnosti v `README_MQTT.md`
