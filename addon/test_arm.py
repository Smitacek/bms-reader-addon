#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test ARM kompatibility a konfigurace pro Raspberry Pi
"""

import platform
import sys
import json
from pathlib import Path

def check_arm_compatibility():
    """Zkontroluje ARM kompatibilitu"""
    print("🔍 ARM Compatibility Check")
    print("=" * 30)
    
    # Architektura
    arch = platform.machine()
    print(f"📱 Architektura: {arch}")
    
    if arch in ['arm64', 'aarch64']:
        print("✅ ARM64 - Kompatibilní s Raspberry Pi 4/5 a Apple Silicon")
        target_arch = "aarch64"
    elif arch in ['armv7l', 'armv6l']:
        print("✅ ARM32 - Kompatibilní s Raspberry Pi 3 a starší")
        target_arch = "armv7" if 'armv7' in arch else "armhf"
    elif arch in ['x86_64', 'amd64']:
        print("💻 x86_64 - Pro cross-compilation na ARM")
        target_arch = "aarch64"  # Default ARM64
    else:
        print(f"⚠️  Neznámá architektura: {arch}")
        target_arch = "aarch64"
    
    print(f"🎯 Target Home Assistant arch: {target_arch}")
    return target_arch

def check_python_deps():
    """Zkontroluje Python závislosti"""
    print("\n🐍 Python Dependencies Check")
    print("=" * 30)
    
    required_modules = ['serial', 'paho.mqtt.client', 'json', 'configparser']
    
    for module in required_modules:
        try:
            if module == 'serial':
                import serial
                print(f"✅ pyserial: {serial.__version__}")
            elif module == 'paho.mqtt.client':
                import paho.mqtt.client as mqtt
                print(f"✅ paho-mqtt: {mqtt.__version__}")
            elif module == 'json':
                import json
                print(f"✅ json: built-in")
            elif module == 'configparser':
                import configparser
                print(f"✅ configparser: built-in")
        except ImportError:
            print(f"❌ {module}: MISSING")

def create_rpi_config():
    """Vytvoří optimalizovanou konfiguraci pro Raspberry Pi"""
    print("\n🍓 Raspberry Pi Configuration")
    print("=" * 30)
    
    rpi_config = {
        "bms": {
            "port": "/dev/ttyUSB0",  # Nejčastější USB-RS485
            "address": 1,
            "baudrate": 9600,
            "timeout": 3.0  # Delší timeout pro RPi
        },
        "mqtt": {
            "host": "core-mosquitto",  # HA Mosquitto Add-on
            "port": 1883,
            "username": "",
            "password": "",
            "discovery_prefix": "homeassistant"
        },
        "device": {
            "id": "bms_rpi_01",
            "name": "BMS Raspberry Pi Battery",
            "manufacturer": "Daren",
            "model": "Daren BMS"
        },
        "application": {
            "read_interval": 30,  # Rozumný interval pro RPi
            "log_level": "INFO"
        }
    }
    
    config_file = Path("rpi_config_example.json")
    with open(config_file, 'w') as f:
        json.dump(rpi_config, f, indent=2)
    
    print(f"✅ Vytvořena konfigurace: {config_file}")
    
    # Alternativní porty pro RPi
    print("\n📡 Raspberry Pi USB/Serial porty:")
    print("   /dev/ttyUSB0     - USB-RS485 převodník")
    print("   /dev/ttyAMA0     - GPIO UART (pins 8,10)")
    print("   /dev/ttyACM0     - USB-Serial Arduino style")
    print("   /dev/serial0     - Primary UART alias")

def deployment_instructions():
    """Instrukce pro nasazení na Raspberry Pi"""
    print("\n🚀 Raspberry Pi Deployment")
    print("=" * 30)
    
    print("1️⃣ Příprava na vývojovém počítači:")
    print("   ./build_arm.sh                    # Build ARM image")
    print("   docker save addon-bms-reader:latest > bms-addon.tar")
    print()
    
    print("2️⃣ Upload na Raspberry Pi:")
    print("   scp bms-addon.tar pi@raspberrypi:~/")
    print("   ssh pi@raspberrypi")
    print("   sudo docker load < bms-addon.tar")
    print()
    
    print("3️⃣ Nebo přímý build na RPi:")
    print("   git clone https://github.com/your-repo/bms-reader-addon")
    print("   cd bms-reader-addon/addon")
    print("   ./build_arm.sh")
    print()
    
    print("4️⃣ Home Assistant Add-on instalace:")
    print("   - Supervisor → Add-on Store")
    print("   - Add Repository → GitHub URL")
    print("   - Install BMS Reader")

def main():
    """Hlavní funkce"""
    print("🍓🍎 BMS Reader ARM Compatibility Test")
    print("=" * 50)
    
    target_arch = check_arm_compatibility()
    check_python_deps()
    create_rpi_config()
    deployment_instructions()
    
    print("\n" + "=" * 50)
    print("✅ ARM compatibility check complete!")
    print(f"🎯 Recommended target architecture: {target_arch}")

if __name__ == "__main__":
    main()
