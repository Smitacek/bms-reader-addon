# 🏠 BMS Reader - Home Assistant Add-on

## 🎯 Přehled

BMS Reader jako Home Assistant Add-on umožňuje:
- ✅ **Snadná instalace** přímo v Home Assistant
- ✅ **Automatická konfigurace MQTT** (žádné ruční nastavení)
- ✅ **Automatický start** při spuštění HA
- ✅ **Běží v kontejneru** - izolováno a bezpečné
- ✅ **Podporuje Raspberry Pi** všech verzí

## 📋 Požadavky

### Hardware
- **Raspberry Pi** s Home Assistant OS/Supervised
- **USB/RS485 převodník** připojený k BMS
- **BMS Daren** s podporou Service 42

### Software
- **Home Assistant** 2023.1+
- **Mosquitto broker** Add-on (doporučeno)

## 🚀 Instalace

### Krok 1: Mosquitto broker
1. **Supervisor → Add-on Store**
2. Najděte "**Mosquitto broker**"
3. **Install** → **Start** → **Enable "Start on boot"**

### Krok 2: Přidání repository
1. **Supervisor → Add-on Store**
2. **⋮ (tři tečky)** → **Repositories**
3. Přidejte: `https://github.com/your-repo/bms-reader-addon`
4. **Add** → **Close**

### Krok 3: Instalace BMS Reader
1. Obnovte Add-on Store (refresh)
2. Najděte "**BMS Reader**"
3. **Install**

### Krok 4: Hardware zjištění
Před konfigurací zjistěte USB port:

**Option A: Hardware info**
1. **Supervisor → System → Hardware**
2. Najděte váš USB device (např. `/dev/ttyUSB0`)

**Option B: Terminal**
1. Nainstalujte "**Terminal & SSH**" Add-on
2. Spusťte terminál
3. `ls /dev/tty*` - najděte USB port

### Krok 5: Konfigurace
V BMS Reader Add-on → **Configuration**:

```yaml
bms:
  port: "/dev/ttyUSB0"        # ⚠️ UPRAVTE! Váš USB port
  address: 1
  baudrate: 9600
  timeout: 2.0
device:
  name: "BMS LiFePO4 Battery"
  id: "bms_garage_01"         # ⚠️ UPRAVTE! Jedinečné ID
  manufacturer: "Daren"
  model: "Daren BMS"
mqtt:
  host: "core-mosquitto"      # Ponechte jako je
  port: 1883
  username: ""                # Ponechte prázdné
  password: ""                # Ponechte prázdné
application:
  read_interval: 30
  log_level: "INFO"
```

### Krok 6: Spuštění
1. **Save** konfiguraci
2. **Start** Add-on
3. **Enable "Start on boot"**
4. Zkontrolujte **Logs** - měli byste vidět:
   ```
   [INFO] BMS Reader starting...
   [INFO] Připojeno k MQTT broker
   [INFO] ✅ Data úspěšně načtena!
   ```

## 📊 Senzory v Home Assistant

Po úspěšném spuštění se automaticky vytvoří senzory:

### Základní senzory
- `sensor.bms_soc` - Stav nabití (%)
- `sensor.bms_pack_voltage` - Napětí baterie (V)
- `sensor.bms_pack_current` - Proud baterie (A)

### Kapacita a cykly
- `sensor.bms_remaining_capacity` - Zbývající kapacita (Ah)
- `sensor.bms_full_capacity` - Celková kapacita (Ah)
- `sensor.bms_cycle_count` - Počet cyklů

### Teploty
- `sensor.bms_ambient_temperature` - Teplota okolí (°C)
- `sensor.bms_mos_temperature` - Teplota MOS (°C)

### Články
- `sensor.bms_min_cell_voltage` - Min. napětí článku (V)
- `sensor.bms_max_cell_voltage` - Max. napětí článku (V)
- `sensor.bms_cell_voltage_difference` - Rozdíl napětí (V)

## 🎨 Dashboard

Vytvořte dashboard kartu:

```yaml
type: entities
title: BMS LiFePO4 Battery
entities:
  - entity: sensor.bms_soc
    name: State of Charge
  - entity: sensor.bms_pack_voltage
    name: Voltage
  - entity: sensor.bms_pack_current
    name: Current
  - entity: sensor.bms_remaining_capacity
    name: Remaining
  - entity: sensor.bms_cycle_count
    name: Cycles
  - entity: sensor.bms_ambient_temperature
    name: Temperature
  - entity: sensor.bms_cell_voltage_difference
    name: Cell Balance
```

## 🔧 Řešení problémů

### Add-on se nespustí
```
[ERROR] Konfigurační soubor neexistuje
```
**Řešení:**
1. Zkontrolujte konfiguraci Add-on
2. Save → Restart Add-on

### USB port nenalezen
```
[ERROR] Permission denied: '/dev/ttyUSB0'
```
**Řešení:**
1. Zkontrolujte fyzické připojení USB
2. Ověřte správný port v Hardware info
3. Restartujte Home Assistant

### BMS neodpovídá
```
[ERROR] Žádná odpověď z BMS
```
**Řešení:**
1. Zkontrolujte USB kabel
2. Ověřte, že je BMS zapnutý
3. Zkuste jiný baudrate (115200)
4. Zkontrolujte adresu BMS

### MQTT nepracuje
```
[ERROR] Chyba připojení k MQTT
```
**Řešení:**
1. Zkontrolujte, že Mosquitto broker běží
2. V MQTT konfiguraci použijte `host: "core-mosquitto"`
3. Ponechte username/password prázdné

### Senzory se nezobrazují
**Řešení:**
1. **Settings → Devices & Services**
2. Najděte "MQTT" integraci
3. Zkontrolujte, že discovery je enabled
4. Restart Home Assistant Core

## 🔄 Aktualizace

Add-on se aktualizuje automaticky. Pro ruční update:
1. **Supervisor → Add-on Store**
2. Najděte "BMS Reader"
3. Klikněte **Update** (pokud je dostupný)

## 🛠️ Development a přispívání

```bash
# Klonování repository
git clone https://github.com/your-repo/bms-reader-addon
cd bms-reader-addon/addon

# Lokální build
./build.sh

# Test
python3 test_addon.py
```

## 📞 Podpora

- **GitHub Issues**: [Nahlásit problém](https://github.com/your-repo/bms-reader-addon/issues)
- **Home Assistant Community**: [Diskuze](https://community.home-assistant.io/)
- **Dokumentace**: [Wiki](https://github.com/your-repo/bms-reader-addon/wiki)
