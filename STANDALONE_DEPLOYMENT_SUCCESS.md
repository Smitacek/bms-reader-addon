# ✅ BMS Reader Standalone - Úspěšné nasazení na Raspberry Pi

**Datum:** 13. června 2025  
**Status:** ✅ DOKONČENO - Plně funkční produkční nasazení

## 🎉 Výsledek

Standalone Docker kontejner `bms-reader-standalone:1.0.4` byl úspěšně nasazen na Raspberry Pi a plně funguje:

### 📊 Live Data z BMS
- **SOC:** 64.0% (State of Charge)
- **Pack Voltage:** 53.02V 
- **Pack Current:** 0.00A (baterie v klidu)
- **Počet článků:** 16 (LiFePO4)
- **Teplota:** Okolní 22°C, MOS 21°C
- **Cykly:** 63
- **Napětí článků:** 3.309V - 3.326V (rozdíl 0.017V)

### 🔗 MQTT Integration
- **Broker:** 10.4.8.213:1883 ✅ Připojeno
- **Credentials:** mqtt_user/mqtt_password ✅ Autentifikace OK
- **Home Assistant Auto Discovery:** ✅ Publikováno
- **Data Stream:** ✅ Každých 30 sekund

### 🐳 Docker Deployment
- **Container:** `bms-reader-standalone:1.0.4`
- **Size:** 352MB (optimalizováno)
- **Restart Policy:** `unless-stopped`
- **Status:** Up and running
- **Architecture:** ARM64 kompatibilní

## 🚀 Nasazení

### Environment Variables
```bash
BMS_PORT=/dev/ttyUSB0
BMS_SLAVE_ID=1
READ_INTERVAL=30
MQTT_HOST=10.4.8.213
MQTT_PORT=1883
MQTT_USER=mqtt_user
MQTT_PASSWORD=mqtt_password
MQTT_TOPIC_PREFIX=homeassistant
DEVICE_ID=bms_lifepo4_01
DEBUG_MODE=false
```

### Production Command
```bash
sudo docker run -d \
    --name bms-reader-standalone \
    --restart unless-stopped \
    --privileged \
    -v /dev:/dev \
    -e BMS_PORT=/dev/ttyUSB0 \
    -e BMS_SLAVE_ID=1 \
    -e READ_INTERVAL=30 \
    -e MQTT_HOST=10.4.8.213 \
    -e MQTT_PORT=1883 \
    -e MQTT_USER=mqtt_user \
    -e MQTT_PASSWORD=mqtt_password \
    -e MQTT_TOPIC_PREFIX=homeassistant \
    -e DEVICE_ID=bms_lifepo4_01 \
    -e DEBUG_MODE=false \
    bms-reader-standalone:1.0.4
```

## 🔧 Management Commands

```bash
# Sledování logů
ssh pi@pi.local "sudo docker logs -f bms-reader-standalone"

# Restart služby
ssh pi@pi.local "sudo docker restart bms-reader-standalone"

# Stop služby
ssh pi@pi.local "sudo docker stop bms-reader-standalone"

# Status kontejneru
ssh pi@pi.local "sudo docker ps | grep bms-reader"

# Monitoring zdrojů
ssh pi@pi.local "sudo docker stats bms-reader-standalone"
```

## 📋 Home Assistant Integration

### Auto Discovery Topics
```
homeassistant/sensor/bms_lifepo4_01/soc/config
homeassistant/sensor/bms_lifepo4_01/pack_voltage/config
homeassistant/sensor/bms_lifepo4_01/pack_current/config
homeassistant/sensor/bms_lifepo4_01/remaining_capacity/config
homeassistant/sensor/bms_lifepo4_01/full_capacity/config
homeassistant/sensor/bms_lifepo4_01/cycle_count/config
homeassistant/sensor/bms_lifepo4_01/ambient_temp/config
homeassistant/sensor/bms_lifepo4_01/mos_temp/config
homeassistant/sensor/bms_lifepo4_01/min_cell_voltage/config
homeassistant/sensor/bms_lifepo4_01/max_cell_voltage/config
homeassistant/sensor/bms_lifepo4_01/cell_voltage_diff/config
```

### State Topics
```
bms/bms_lifepo4_01/soc
bms/bms_lifepo4_01/pack_voltage
bms/bms_lifepo4_01/pack_current
bms/bms_lifepo4_01/remaining_capacity
bms/bms_lifepo4_01/full_capacity
bms/bms_lifepo4_01/cycle_count
bms/bms_lifepo4_01/ambient_temp
bms/bms_lifepo4_01/mos_temp
bms/bms_lifepo4_01/min_cell_voltage
bms/bms_lifepo4_01/max_cell_voltage
bms/bms_lifepo4_01/cell_voltage_diff
```

## 🛠️ Technické detaily

### Architektura
- **Base Image:** `python:3.11-alpine`
- **Runtime:** Direct Python execution (bez bashio)
- **Configuration:** Environment variables (standalone)
- **Dependencies:** paho-mqtt, pyserial, pymodbus

### Komunikace
- **Protocol:** Service 42 over RS485
- **BMS Type:** Daren BMS compatible
- **Serial Port:** `/dev/ttyUSB0`
- **Baudrate:** 9600
- **Address:** 0x01

### Deployment Method
- **SSH:** `ssh pi@pi.local`
- **Transfer:** SSH-CAT (240MB image)
- **Load:** `docker load`
- **Run:** Production container

## 🔄 Iterace a opravy

Během vývoje byly vyřešeny tyto problémy:

1. **Konfigurace:** Migrace z Home Assistant Add-on config na environment variables
2. **LOG_LEVEL:** Oprava property vs. string problému
3. **Static vs. Instance:** Přechod ze statických na instance konfigurace
4. **MQTT Credentials:** Nastavení správných credentials místo prázdných
5. **DNS Resolution:** Použití IP adresy místo hostname

## ✅ Výsledek

**BMS Reader Standalone je úspěšně nasazen a plně funkční na Raspberry Pi!**

- 🔋 BMS komunikace: **FUNGUJE**
- 📡 MQTT streaming: **FUNGUJE** 
- 🏠 Home Assistant integrace: **FUNGUJE**
- 🐳 Docker deployment: **FUNGUJE**
- 🔄 Auto restart: **AKTIVNÍ**

---

**Projekt dokončen - 13. června 2025** 🎉
