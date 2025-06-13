# 🔄 BMS Reader - Standalone vs Home Assistant Add-on

## 📊 Porovnání variant

| Funkce | Standalone | HA Add-on | Doporučení |
|--------|------------|-----------|------------|
| **Instalace** | Ruční setup | 1-click install | 🏆 Add-on |
| **Konfigurace** | config.ini | HA UI | 🏆 Add-on |
| **MQTT setup** | Ruční | Automatický | 🏆 Add-on |
| **Auto start** | systemd/cron | Integrovaný | 🏆 Add-on |
| **Updates** | Ruční | Automatické | 🏆 Add-on |
| **Monitoring** | Logy | HA logs + UI | 🏆 Add-on |
| **Flexibilita** | 🏆 Vysoká | Střední | 🏆 Standalone |
| **Development** | 🏆 Snadný | Složitější | 🏆 Standalone |

## 🎯 Kdy použít kterou variantu?

### 🏠 Home Assistant Add-on
**Vyberte pokud:**
- ✅ Používáte Home Assistant
- ✅ Chcete jednoduchou instalaci
- ✅ Preferujete automatické updaty
- ✅ Nechcete řešit MQTT konfiguraci
- ✅ Máte Raspberry Pi s HA OS

### 💻 Standalone verze
**Vyberte pokud:**
- ✅ Nepoužíváte Home Assistant
- ✅ Chcete vzdálený monitoring
- ✅ Potřebujete custom úpravy
- ✅ Používáte jiný systém než RPi
- ✅ Chcete odesílat na externí MQTT

## 🚀 Migrace Standalone → Add-on

### Krok 1: Backup konfigurace
```bash
# Uložte současné nastavení
cp config.ini config.ini.backup
```

### Krok 2: Zastavte standalone verzi
```bash
# Pokud běží jako služba
sudo systemctl stop bms-reader
sudo systemctl disable bms-reader

# Pokud běží v terminálu
# Ctrl+C pro ukončení
```

### Krok 3: Instalace Add-on
Postupujte podle `INSTALL_ADDON.md`

### Krok 4: Přenos konfigurace
Z vašeho `config.ini`:
```ini
[BMS]
port = /dev/ttyUSB0
[MQTT]
broker_host = 192.168.1.100
[DEVICE]
device_id = bms_lifepo4_01
```

Do Add-on Configuration:
```yaml
bms:
  port: "/dev/ttyUSB0"
mqtt:
  host: "core-mosquitto"  # Místo externí IP
device:
  id: "bms_lifepo4_01"
```

### Krok 5: Test
1. Spusťte Add-on
2. Zkontrolujte, že senzory fungují
3. Odstraňte standalone instalaci

## 🔄 Migrace Add-on → Standalone

### Krok 1: Export konfigurace
Z Add-on Configuration zkopírujte hodnoty do `config.ini`

### Krok 2: Instalace standalone
```bash
git clone https://github.com/your-repo/bms-reader
cd bms-reader
cp config.ini.example config.ini
# Upravte config.ini
```

### Krok 3: Test standalone
```bash
uv run bms_read_once.py
```

### Krok 4: Zastavte Add-on
V Home Assistant zastavte a odinstalujte BMS Reader Add-on

## 📋 Checklist migrace

### Před migrací
- [ ] Backup současné konfigurace
- [ ] Poznamenejte si Device ID
- [ ] Screenshot současných senzorů HA
- [ ] Zastavte současnou verzi

### Po migraci
- [ ] Zkontrolujte BMS komunikaci
- [ ] Ověřte MQTT připojení
- [ ] Najděte senzory v HA
- [ ] Otestujte po restaru HA
- [ ] Vyčistěte starou instalaci

## 🆘 Řešení problémů při migraci

### Duplikované senzory
```
sensor.bms_soc a sensor.bms_soc_2
```
**Řešení:**
1. Settings → Devices & Services → MQTT
2. Odstraňte staré senzory
3. Restartujte HA Core

### Jiné Device ID
**Problém:** Add-on vytvoří nové senzory s jiným ID
**Řešení:**
1. Použijte stejné `device.id` jako dříve
2. Nebo přejmenujte entity v HA

### MQTT konflikty
**Problém:** Zprávy se posílají na stejné topics
**Řešení:**
1. Zastavte starou verzi úplně
2. Vyčistěte MQTT retain zprávy:
   ```bash
   mosquitto_pub -h localhost -t 'bms/device_id/+' -n -r -d
   ```

## 💡 Tipy pro úspěšnou migraci

1. **Postupujte pomalu** - netestujte vše najednou
2. **Backup vše** - config, entity ID, automation
3. **Testujte offline** - nejdřív BMS komunikaci, pak MQTT
4. **Dokumentujte změny** - pro případ rollback
5. **Používejte stejné ID** - vyhnete se duplikátům
