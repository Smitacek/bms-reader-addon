#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script pro lokální spuštění BMS Reader Add-on
Simuluje Home Assistant Add-on prostředí
"""

import json
import os
import sys
from pathlib import Path

# Vytvoř test options.json
def create_test_options():
    """Vytvoří testovací /data/options.json pro simulaci HA Add-on"""
    
    # Vytvoř /data složku
    data_dir = Path("/tmp/bms_addon_test/data")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Test konfigurace
    test_options = {
        "bms": {
            "port": "/dev/tty.usbserial-B003BHLO",  # Upravte dle vašeho systému
            "address": 1,
            "baudrate": 9600,
            "timeout": 2.0
        },
        "mqtt": {
            "host": "localhost",  # Pro lokální test
            "port": 1883,
            "username": "",
            "password": "",
            "discovery_prefix": "homeassistant"
        },
        "device": {
            "id": "bms_test_01",
            "name": "BMS Test Battery",
            "manufacturer": "Daren",
            "model": "Daren BMS"
        },
        "application": {
            "read_interval": 10,  # Kratší interval pro test
            "log_level": "DEBUG"
        }
    }
    
    options_file = data_dir / "options.json"
    with open(options_file, 'w') as f:
        json.dump(test_options, f, indent=2)
    
    print(f"✅ Vytvořen test options.json: {options_file}")
    return options_file

def setup_test_environment():
    """Nastaví testovací prostředí"""
    
    # Vytvoř test options
    options_file = create_test_options()
    
    # Symlink pro /data/options.json
    target_dir = Path("/data")
    if not target_dir.exists():
        print("⚠️  /data neexistuje - vytváříme symlink...")
        try:
            target_dir.parent.mkdir(parents=True, exist_ok=True)
            target_dir.symlink_to(options_file.parent)
            print(f"✅ Vytvořen symlink: {target_dir} -> {options_file.parent}")
        except PermissionError:
            print("❌ Nemáte oprávnění vytvořit /data")
            print("💡 Spusťte s sudo nebo upravte addon_config.py pro fallback")
            return False
    
    return True

def main():
    """Hlavní funkce pro test"""
    print("🧪 BMS Reader Add-on Test")
    print("=" * 40)
    
    # Setup
    if not setup_test_environment():
        print("❌ Nepodařilo se nastavit testovací prostředí")
        sys.exit(1)
    
    print("🔧 Testovací konfigurace vytvořena")
    print("💡 Nyní můžete spustit Add-on kód:")
    print("   cd addon && python3 main.py")
    print()
    print("📝 Pro úpravu konfigurace editujte:")
    print("   /tmp/bms_addon_test/data/options.json")

if __name__ == "__main__":
    main()
