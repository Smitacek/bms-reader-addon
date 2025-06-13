# 🍓 ARM Deployment pro Raspberry Pi

## 🎯 **Cílové platformy**
- **Raspberry Pi 4** (aarch64) - doporučeno
- **Raspberry Pi 3** (armv7) - podporováno
- **Starší Raspberry Pi** (armhf) - podporováno
- **Apple Silicon Mac** (aarch64) - development

## 🚀 **Quick Start pro Raspberry Pi**

### 1. **Požadavky**
```bash
# Raspberry Pi OS (64-bit doporučeno)
# Home Assistant OS nebo Home Assistant Supervised
# Docker podporovaná verze
# USB/RS485 adaptér připojený k BMS
```

### 2. **Instalace přes Home Assistant Add-on**
```bash
# 1. Kopírování add-on složky
scp -r addon/ pi@your-raspberrypi:/home/pi/

# 2. Na Raspberry Pi
sudo docker build -t bms-reader-arm addon/

# 3. Import do Home Assistant
# Postupujte podle INSTALL_ADDON.md
```

### 3. **Standalone instalace na Raspberry Pi**
```bash
# Instalace závislostí
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Stažení projektu
git clone https://github.com/your-repo/bms-reader.git
cd bms-reader

# Vytvoření virtual environment
python3 -m venv venv
source venv/bin/activate

# Instalace Python balíčků
pip install -r requirements.txt

# Konfigurace
cp config.ini.example config.ini
nano config.ini

# Test BMS komunikace
python bms_read_once.py

# Spuštění s MQTT
python main.py
```

## 🔧 **ARM Build proces**

### 1. **Multi-arch Docker build**
```bash
# Příprava buildx
docker buildx create --name multiarch --driver docker-container
docker buildx use multiarch

# Build pro všechny ARM platformy
./build_arm.sh
```

### 2. **Pouze pro aktuální ARM platform**
```bash
# Rychlý build pro testování
./build_arm_quick.sh
```

### 3. **Verifikace ARM kompatibility**
```bash
# Test ARM závislostí
python test_arm_deployment.py
```

## 📊 **Performance na ARM**

### **Raspberry Pi 4 (aarch64)**
- ✅ **CPU využití:** ~5-10% při čtení každých 30s
- ✅ **RAM:** ~50MB celková spotřeba
- ✅ **Latence MQTT:** <100ms
- ✅ **BMS komunikace:** 2-3s na kompletní čtení

### **Raspberry Pi 3 (armv7)**
- ✅ **CPU využití:** ~10-15% při čtení každých 30s
- ✅ **RAM:** ~60MB celková spotřeba
- ✅ **Latence MQTT:** <200ms
- ✅ **BMS komunikace:** 3-5s na kompletní čtení

## 🛠️ **ARM specifické optimalizace**

### 1. **Python optimalizace**
```bash
# Použití binary wheels pro ARM
pip install --only-binary=all -r requirements.txt

# Alternativně kompilace z source
pip install --no-binary=all -r requirements.txt
```

### 2. **Docker optimalizace**
```dockerfile
# Multi-stage build pro menší image
FROM python:3.11-alpine AS builder
# ... build dependencies

FROM python:3.11-alpine AS runtime
# ... pouze runtime dependencies
```

### 3. **Systemd servis pro produkci**
```bash
# Vytvoření systemd service
sudo cp bms-reader.service /etc/systemd/system/
sudo systemctl enable bms-reader
sudo systemctl start bms-reader
```

## 🔌 **USB/RS485 konfigurace na Raspberry Pi**

### 1. **Detekce USB adaptéru**
```bash
# Seznam USB zařízení
lsusb

# Seznam serial portů
ls -la /dev/tty*

# Práva k serial portu
sudo usermod -a -G dialout $USER
```

### 2. **udev pravidla pro pevný název**
```bash
# /etc/udev/rules.d/99-bms.rules
SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", SYMLINK+="bms485"

# Reload udev
sudo udevadm control --reload-rules
```

### 3. **Test komunikace**
```bash
# Základní test
python -c "import serial; print(serial.Serial('/dev/ttyUSB0').is_open)"

# BMS test
python bms_read_once.py --port /dev/ttyUSB0
```

## 📋 **Troubleshooting ARM**

### **Common Issues:**

1. **"Permission denied" na /dev/ttyUSB0**
   ```bash
   sudo usermod -a -G dialout $USER
   # Logout & login znovu
   ```

2. **Docker permission denied**
   ```bash
   sudo usermod -a -G docker $USER
   # Logout & login znovu
   ```

3. **Python dependencies fail**
   ```bash
   # Instalace build tools
   sudo apt install build-essential python3-dev
   ```

4. **MQTT connection timeout**
   ```bash
   # Kontrola mosquitto
   sudo systemctl status mosquitto
   mosquitto_pub -h localhost -t test -m "hello"
   ```

## 🎯 **Doporučená konfigurace pro produkci**

```ini
[bms]
port = /dev/bms485  # Použijte udev symlink
address = 1
baudrate = 9600
timeout = 3.0  # Vyšší timeout pro stabilitu

[application]
read_interval = 60  # Nižší frekvence pro úsporu výkonu
log_level = WARNING  # Méně logů pro produkci

[mqtt]
host = localhost  # Local mosquitto
port = 1883
keepalive = 60
```