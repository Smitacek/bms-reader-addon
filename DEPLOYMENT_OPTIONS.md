# 🚀 BMS Reader - Deployment Možnosti

Máte k dispozici několik způsobů deploymentu BMS Reader aplikace na Raspberry Pi v závislosti na tom, jaký typ připojení máte dostupný.

## 🎯 **Quick Start - Automatický deployment**

```bash
# Nejjednodušší způsob - automaticky vybere nejlepší metodu
./deploy_smart.sh
```

---

## 📋 **Všechny dostupné deployment možnosti:**

### **1. 🔄 Smart Deployment (DOPORUČENO)**
```bash
./deploy_smart.sh
# ✅ Automaticky testuje SSH a SCP
# ✅ Vybere nejlepší dostupnou metodu
# ✅ Fallback na alternativní způsoby
```

### **2. 📦 Standardní SCP Deployment** 
```bash
./deploy_to_pi.sh
# ✅ Nejrychlejší když SCP funguje
# ❌ Selže pokud SCP subsystém nefunguje
```

### **3. 🔧 SSH-CAT Deployment**
```bash
./deploy_ssh_cat.sh
# ✅ Funguje když SSH funguje ale SCP ne
# ✅ Používá cat místo SCP
# ⚠️ Pomalejší než SCP
```

### **4. 📡 HTTP Deployment**
```bash
./deploy_http.sh
# ✅ Funguje přes HTTP server
# ✅ Spolehlivé pro větší soubory
# ⚠️ Vyžaduje HTTP server na Mac
```

---

## 🔍 **Diagnostika problémů**

### **SSH Diagnostika**
```bash
./ssh_diagnostic.sh
# Otestuje:
# ✅ Ping test
# ✅ SSH port dostupnost
# ✅ SSH autentifikaci
# ✅ SCP funkčnost
# ✅ Docker na Pi
```

### **Typické problémy a řešení:**

**1. "subsystem request failed on channel 0"**
```bash
# Příčina: SCP subsystém není povolen
# Řešení: Použijte SSH-CAT deployment
./deploy_ssh_cat.sh
```

**2. "pi.local: nodename nor servname provided"**
```bash
# Příčina: Hostname není dostupný
# Řešení: Použijte IP adresu
export PI_HOST=192.168.1.XXX
./deploy_smart.sh
```

**3. "Connection refused"**
```bash
# Příčina: SSH daemon neběží
# Řešení: Na Pi spusťte:
sudo systemctl enable --now ssh
```

**4. "Permission denied"**
```bash
# Příčina: Špatné přihlašovací údaje
# Řešení: Zkontrolujte username/password nebo SSH klíče
```

---

## 🌐 **Síťová konfigurace**

### **Možné hostname pro Raspberry Pi:**
```bash
export PI_HOST=pi.local              # Výchozí
export PI_HOST=raspberrypi.local     # Alternativa
export PI_HOST=homeassistant.local   # Pro HA OS
export PI_HOST=192.168.1.XXX         # IP adresa
```

### **Změna uživatele:**
```bash
export PI_USER=pi                    # Výchozí
export PI_USER=root                  # Pro některé instalace
export PI_USER=homeassistant         # Pro HA OS
```

---

## 🔧 **Ruční deployment (když nic nefunguje)**

### **1. USB Transfer**
```bash
# Zkopírujte image na USB
cp bms-reader-arm-1.0.0.tar.gz /Volumes/USB/

# Na Pi vložte USB a spusťte:
docker load < /media/usb/bms-reader-arm-1.0.0.tar.gz
docker run -d --name bms-reader --restart unless-stopped \
    --privileged -v /dev:/dev \
    -e BMS_PORT="/dev/ttyUSB0" \
    -e MQTT_HOST="homeassistant.local" \
    bms-reader-arm:1.0.0
```

### **2. Direct build na Pi**
```bash
# Zkopírujte pouze addon složku
scp -r addon/ pi@pi.local:~/

# Na Pi spusťte build
ssh pi@pi.local
cd addon
./build_arm_quick.sh
```

### **3. Manual HTTP server**
```bash
# Na Mac spusťte HTTP server
python3 -m http.server 8000

# Na Pi stáhněte image
wget http://YOUR_MAC_IP:8000/bms-reader-arm-1.0.0.tar.gz
docker load < bms-reader-arm-1.0.0.tar.gz
```

---

## ✅ **Validace deploymentu**

Po úspěšném deploymentu zkontrolujte:

```bash
# Kontrola běžícího kontejneru
ssh pi@pi.local 'docker ps | grep bms-reader'

# Sledování logů
ssh pi@pi.local 'docker logs -f bms-reader'

# Test BMS komunikace
ssh pi@pi.local 'docker logs bms-reader | grep -i "bms"'

# Test MQTT publikování
ssh pi@pi.local 'docker logs bms-reader | grep -i "mqtt"'
```

---

## 🏠 **Home Assistant integrace**

Po úspěšném deploymentu:

1. **Zkontrolujte MQTT broker** - kontejner se automaticky připojí
2. **Otevřete Home Assistant** > Configuration > Integrations  
3. **Hledejte BMS sensory** - automaticky objevené přes MQTT auto-discovery
4. **Přidejte na dashboard** - entity začínají `sensor.bms_*`

---

## 🎯 **Doporučený postup:**

1. **Spusťte diagnostiku**: `./ssh_diagnostic.sh`
2. **Pokud vše funguje**: `./deploy_smart.sh` 
3. **Při problémech**: použijte specifický deployment script
4. **Ověřte funkčnost**: kontrola logů a Home Assistant

📚 **Pro detailní návod**: `ARM_DEPLOYMENT_FINAL.md`
