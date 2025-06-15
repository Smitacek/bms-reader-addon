# Ukázková konfigurace pro Multi-Battery Monitor

## Jednoduchá konfigurace (jedna baterie - zpětná kompatibilita)
```yaml
bms_port: "/dev/ttyUSB0"
bms_address: 1
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_username: ""
mqtt_password: ""
read_interval: 30
```

## Multi-battery konfigurace (až 16 baterií)
```yaml
# Povolení multi-battery módu
multi_battery_mode: true

# Konfigurace jednotlivých baterií
batteries:
  - port: "/dev/ttyUSB0"
    address: 1
    name: "Battery_1"
    enabled: true
  - port: "/dev/ttyUSB0"
    address: 2
    name: "Battery_2"
    enabled: true
  - port: "/dev/ttyUSB1"
    address: 1
    name: "Battery_3"
    enabled: true
  - port: "/dev/ttyUSB1"
    address: 2
    name: "Battery_4"
    enabled: false  # dočasně vypnuto

# Virtuální baterie (agreguje data ze všech baterií)
enable_virtual_battery: true
virtual_battery_name: "Battery Bank"

# MQTT konfigurace
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_username: "mqtt_user"
mqtt_password: "mqtt_password"
read_interval: 30
```

## Příklad pro solární systém s 8 bateriemi
```yaml
multi_battery_mode: true

batteries:
  # Rack 1 - 4 baterie
  - port: "/dev/ttyUSB0"
    address: 1
    name: "Rack1_Battery1"
    enabled: true
  - port: "/dev/ttyUSB0"
    address: 2
    name: "Rack1_Battery2"
    enabled: true
  - port: "/dev/ttyUSB0"
    address: 3
    name: "Rack1_Battery3"
    enabled: true
  - port: "/dev/ttyUSB0"
    address: 4
    name: "Rack1_Battery4"
    enabled: true
    
  # Rack 2 - 4 baterie
  - port: "/dev/ttyUSB1"
    address: 1
    name: "Rack2_Battery1"
    enabled: true
  - port: "/dev/ttyUSB1"
    address: 2
    name: "Rack2_Battery2"
    enabled: true
  - port: "/dev/ttyUSB1"
    address: 3
    name: "Rack2_Battery3"
    enabled: true
  - port: "/dev/ttyUSB1"
    address: 4
    name: "Rack2_Battery4"
    enabled: true

# Virtuální baterie pro celý systém
enable_virtual_battery: true
virtual_battery_name: "Solar Battery System"

mqtt_host: "192.168.1.100"
mqtt_port: 1883
mqtt_username: "homeassistant"
mqtt_password: "ha_password"
read_interval: 30
```

## Home Assistant senzory

### Individuální baterie
Pro každou baterii budou vytvořeny senzory:
- `sensor.battery_1_soc` - SOC baterie 1
- `sensor.battery_1_pack_voltage` - Napětí baterie 1
- `sensor.battery_1_pack_current` - Proud baterie 1
- ... (pro každou baterii)

### Virtuální baterie (agregované hodnoty)
- `sensor.battery_bank_soc` - Průměrný SOC všech baterií
- `sensor.battery_bank_pack_voltage` - Celkové napětí (suma)
- `sensor.battery_bank_pack_current` - Celkový proud (suma)
- `sensor.battery_bank_power` - Celkový výkon
- `sensor.battery_bank_battery_count` - Počet připojených baterií
- `sensor.battery_bank_connected_batteries` - Seznam připojených baterií

## Výhody multi-battery módu

1. **Monitorování jednotlivých baterií**
   - Každá baterie má vlastní senzory v HA
   - Možnost sledovat výkon jednotlivých článků
   - Identifikace problémových baterií

2. **Virtuální baterie**
   - Celkový přehled o systému
   - Agregované hodnoty (SOC, výkon, kapacita)
   - Jednoduchá automatizace pro celý systém

3. **Flexibilní konfigurace**
   - Až 16 baterií na různých portech/adresách
   - Možnost dočasně vypnout baterie
   - Vlastní názvy pro lepší identifikaci

4. **Zpětná kompatibilita**
   - Stará konfigurace (jedna baterie) stále funguje
   - Plynulý přechod na multi-battery mód
