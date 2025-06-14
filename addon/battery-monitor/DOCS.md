# Battery Monitor Add-on

## Přehled

Battery Monitor Add-on umožňuje čtení dat z BMS (Battery Management System) LiFePO4 baterií přes Modbus RTU a jejich publikování do Home Assistant prostřednictvím MQTT Auto Discovery.

## Funkce

- ✅ Čtení dat z BMS LiFePO4 baterií přes Modbus RTU
- ✅ Automatická konfigurace senzorů v Home Assistant (Auto Discovery)
- ✅ MQTT publikování dat baterií (napětí, proud, SOC, teploty atd.)
- ✅ Podpora různých USB/sériových portů
- ✅ Konfigurovatelný interval čtení

## Konfigurace

### BMS Nastavení

- **BMS Port**: Sériový port pro komunikaci s BMS (např. `/dev/ttyUSB0`)
- **BMS Address**: Modbus adresa BMS zařízení (obvykle 1)
- **Read Interval**: Interval čtení dat v sekundách (10-300s)

### MQTT Nastavení

- **MQTT Host**: Adresa MQTT brokeru (výchozí: `core-mosquitto`)
- **MQTT Port**: Port MQTT brokeru (výchozí: 1883)
- **MQTT Username**: Uživatelské jméno pro MQTT broker (volitelné)
- **MQTT Password**: Heslo pro MQTT broker (volitelné)

### Příklad konfigurace

```yaml
bms_port: "/dev/ttyUSB0"
bms_address: 1
mqtt_host: "core-mosquitto"
mqtt_port: 1883
mqtt_username: "homeassistant"
mqtt_password: "your_password"
read_interval: 30
```

## MQTT Autentizace

Pokud váš MQTT broker vyžaduje autentizaci, musíte nastavit `mqtt_username` a `mqtt_password`. Pro Home Assistant Mosquitto Add-on:

1. Otevřete Mosquitto Add-on konfiguraci
2. Přidejte uživatele do sekce `logins`:
   ```yaml
   logins:
     - username: homeassistant
       password: your_secure_password
   ```
3. Restartujte Mosquitto Add-on
4. V Battery Monitor Add-on nastavte stejné údaje

## Podporovaná data

Add-on čte a publikuje následující data z BMS:

### Základní údaje
- **SOC** (State of Charge) - stav nabití v %
- **Voltage** - celkové napětí baterie v V
- **Current** - aktuální proud v A
- **Power** - výkon v W
- **Remaining Capacity** - zbývající kapacita v Ah

### Teploty
- **Temperature 1-4** - teploty senzorů v °C
- **Average Temperature** - průměrná teplota v °C

### Napětí článků
- **Cell Voltage 1-16** - napětí jednotlivých článků v V
- **Cell Voltage Delta** - rozdíl mezi max a min článkem v V

### Stav systému
- **Cycles** - počet cyklů nabíjení
- **Balancing Status** - stav balancování
- **Protection Status** - stav ochrany

## Řešení problémů

### MQTT Error 5 (Authentication failure)

Pokud vidíte chybu "Chyba připojení k MQTT: 5", znamená to problém s autentizací:

1. Zkontrolujte, zda je MQTT broker správně nakonfigurován
2. Ověřte username/password v konfiguraci
3. Ujistěte se, že Mosquitto Add-on má vytvořený uživatel
4. Zkuste prázdné username/password pokud broker nevyžaduje autentizaci

### Chyba čtení z BMS

Pokud se nepodaří číst data z BMS:

1. Zkontrolujte připojení USB/sériového kabelu
2. Ověřte správný port (můžete použít `dmesg | grep tty`)
3. Zkontrolujte BMS adresu (obvykle 1)
4. Ujistěte se, že BMS podporuje Modbus RTU protokol

### Debug log

Pro detailní diagnostiku můžete dočasně změnit log level na DEBUG v `addon_config.py`:

```python
self.log_level = "DEBUG"
```

## Technické informace

- **Protokol**: Modbus RTU
- **Baudrate**: 9600
- **Data bits**: 8
- **Stop bits**: 1
- **Parity**: None
- **Timeout**: 2s

## Podpora

Pro podporu a hlášení chyb použijte GitHub Issues v repositáři:
https://github.com/Smitacek/bms-reader-addon/issues
