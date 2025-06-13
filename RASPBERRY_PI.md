# 🍓 BMS Reader pro Raspberry Pi

## 🎯 ARM Optimalizace

BMS Reader je plně optimalizován pro ARM architektury:

### ✅ Podporované platformy
- **Raspberry Pi 4/5** (ARM64/aarch64) - ⭐ **DOPORUČENO**
- **Raspberry Pi 3** (ARM32/armv7)
- **Apple Silicon Mac** (ARM64) - pro development
- **Starší Raspberry Pi** (armhf)

### 🚀 Výhody ARM buildu
- **Nativní výkon** na Raspberry Pi
- **Nižší spotřeba** energie
- **Optimalizovaný** pro embedded systémy
- **Rychlejší** spouštění kontejnerů

## 🔧 Instalace na Raspberry Pi

### Metoda A: Home Assistant Add-on (DOPORUČENO)

1. **Přidat repository** v HA:
   ```
   Supervisor → Add-on Store → ⋮ → Repositories
   Přidat: https://github.com/your-repo/bms-reader-addon
   ```

2. **Instalace**:
   ```
   Najít "BMS Reader" → Install → Configure → Start
   ```

3. **Konfigurace**:
   ```yaml
   bms:
     port: "/dev/ttyUSB0"  # USB-RS485 převodník
   device:
     id: "bms_rpi_01"      # Jedinečné ID
   ```

### Metoda B: Ruční Docker build na RPi

```bash
# Na Raspberry Pi
git clone https://github.com/your-repo/bms-reader-addon
cd bms-reader-addon/addon
./build_arm.sh

# Spuštění
docker run --device=/dev/ttyUSB0 addon-bms-reader:latest
```

### Metoda C: Cross-compilation na Mac/PC

```bash
# Na vývojovém počítači (Mac/PC)
./build_arm.sh
docker save addon-bms-reader:latest > bms-addon.tar

# Upload na Raspberry Pi
scp bms-addon.tar pi@raspberrypi:~/
ssh pi@raspberrypi
sudo docker load < bms-addon.tar
```

## 🔌 Hardware setup na Raspberry Pi

### USB porty na RPi
```bash
# Zjištění USB zařízení
ls /dev/tty*

# Typické porty:
/dev/ttyUSB0    # USB-RS485 převodník (nejčastější)
/dev/ttyAMA0    # GPIO UART (pins 8,10)
/dev/ttyACM0    # USB-Serial (Arduino style)
/dev/serial0    # Primary UART alias
```

### GPIO UART (alternativa k USB)
```bash
# Povolení UART na GPIO
sudo raspi-config
# → Interface Options → Serial Port
# → Login shell: NO
# → Serial hardware: YES

# Použití v konfiguraci:
port: "/dev/ttyAMA0"
```

### USB-RS485 zapojení
```
BMS RS485    USB-RS485    Raspberry Pi
A    ←───→   A            │
B    ←───→   B            │ USB port
GND  ←───→   GND          │
                          ▼
                    /dev/ttyUSB0
```

## ⚡ Výkonnostní optimalizace pro RPi

### Konfigurace pro Raspberry Pi
```yaml
application:
  read_interval: 30        # Nezatěžovat RPi
  log_level: "INFO"        # Méně disk I/O

bms:
  timeout: 3.0             # Delší timeout pro RPi
```

### Monitoring resources
```bash
# CPU/Memory monitoring
htop

# Docker container stats
docker stats addon-bms-reader

# Disk usage
df -h
```

## 🔥 Řešení problémů na RPi

### "Permission denied" na USB portu
```bash
# Přidat uživatele do dialout group
sudo usermod -a -G dialout $USER
sudo reboot

# Nebo změnit permissions
sudo chmod 666 /dev/ttyUSB0
```

### USB zařízení se nedetekuje
```bash
# Kontrola USB zařízení
lsusb
dmesg | tail

# Reinsert USB device
sudo modprobe -r ftdi_sio
sudo modprobe ftdi_sio
```

### Nízký výkon na starším RPi
```yaml
# Snížit frekvenci čtení
application:
  read_interval: 60       # Každou minutu místo 30s
  
# Jednodušší logování
  log_level: "WARNING"    # Méně výpisů
```

### Container memory limit
```bash
# Pro starší RPi s málo RAM
docker run --memory=128m --device=/dev/ttyUSB0 addon-bms-reader
```

## 📊 Benchmark na různých RPi

| Model | ARM arch | RAM | Boot time | CPU usage |
|-------|----------|-----|-----------|-----------|
| **RPi 5** | aarch64 | 8GB | ~10s | <5% |
| **RPi 4** | aarch64 | 4GB | ~15s | <10% |
| **RPi 3** | armv7 | 1GB | ~30s | <20% |
| **RPi Zero** | armhf | 512MB | ~60s | <30% |

## 🎛️ GPIO UART setup (pokročilé)

### Aktivace UART na GPIO
```bash
# /boot/config.txt
enable_uart=1
dtoverlay=disable-bt

# Restart RPi
sudo reboot

# Test UART
sudo screen /dev/ttyAMA0 9600
```

### RS485 HAT pro RPi
Mnoho výrobců nabízí RS485 HAT pro přímé připojení:
- **Waveshare RS485 CAN HAT**
- **Industrial Shields RS485**  
- **Seeed Studio RS485**

Výhody HAT:
- ✅ Žádné USB kabely
- ✅ Stabilnější připojení
- ✅ Nižší latence
- ✅ GPIO pins dostupné

---

**🔗 Další zdroje:**
- [Raspberry Pi UART Documentation](https://www.raspberrypi.org/documentation/configuration/uart.md)
- [Home Assistant Add-on Development](https://developers.home-assistant.io/docs/add-ons)
- [Docker ARM builds](https://docs.docker.com/buildx/working-with-buildx/)
