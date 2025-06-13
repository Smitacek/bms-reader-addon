# 📁 BMS Reader - Přehled všech souborů projektu

## 🎯 **Hlavní aplikace**
```
main.py              # Hlavní aplikace s MQTT integrací
bms_parser.py         # BMS komunikace a parsing dat
modbus.py            # Modbus RTU protokol
mqtt_helper.py       # MQTT helper s Home Assistant auto-discovery
```

## 🏠 **Home Assistant Add-on**
```
addon/
├── config.yaml      # HA Add-on konfigurace
├── Dockerfile       # ARM optimalizovaný Docker build
├── run.sh          # Add-on startup script
├── requirements.txt # Python závislosti
└── build_arm_quick.sh  # Rychlý ARM build script (spustitelný)
```

## 🍓 **ARM Deployment**
```
bms-reader-arm-1.0.0.tar.gz   # ARM Docker image (117MB, export pro Pi)
deploy_to_pi.sh               # Automatický deployment na Raspberry Pi (spustitelný)
validate_deployment.py        # Kompletní validace projektu (spustitelný)
bms-reader.service           # Systemd service pro produkční nasazení
```

## 📖 **Dokumentace**
```
ARM_DEPLOYMENT.md            # Původní ARM deployment návod
ARM_DEPLOYMENT_FINAL.md      # KOMPLETNÍ finální návod s všemi instrukcemi
test_arm_deployment.py       # ARM test script (spustitelný)
```

## 🐳 **Docker komponenty**
```
Docker image: bms-reader-arm:1.0.0  # ARM image (498MB)
Export file:  bms-reader-arm-1.0.0.tar.gz  # Komprimovaný pro transfer (117MB)
```

---

## 🚀 **Rychlé spuštění - 3 způsoby:**

### **1. Automatický deployment (NEJRYCHLEJŠÍ)**
```bash
./deploy_to_pi.sh
# Automaticky nahraje a spustí na Raspberry Pi
```

### **2. Home Assistant Add-on**
```bash
# Kopírování addon složky do HA
scp -r addon/ root@homeassistant.local:/addons/
# Pak instalace přes HA UI
```

### **3. Systemd služba**
```bash
sudo cp bms-reader.service /etc/systemd/system/
sudo systemctl enable --now bms-reader.service
```

---

## ✅ **Validace - 6/6 testů prošlo**

```bash
./validate_deployment.py

# Výsledek:
# ✅ Docker Images
# ✅ ARM Image Funkčnost  
# ✅ Exportovaný Image
# ✅ Zdrojové soubory
# ✅ Deployment skripty
# ✅ Konfigurační soubory
```

---

## 🎯 **Pro produkční použití:**

1. **Spusťte validaci**: `./validate_deployment.py`
2. **Deploy na Pi**: `./deploy_to_pi.sh`
3. **Připojte USB/RS485** adaptér k BMS
4. **Zkontrolujte Home Assistant** - automaticky objevené sensory
5. **Monitoring**: `docker logs -f bms-reader`

📚 **Kompletní návod**: `ARM_DEPLOYMENT_FINAL.md`
