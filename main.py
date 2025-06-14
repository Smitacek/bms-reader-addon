#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BMS Reader - Čtení a parsování dat z Daren BMS přes Service 42
Podporuje odesílání dat na MQTT (Home Assistant)
"""

import sys
import time
import logging
from typing import Dict, Any

from modbus import request_device_info
from bms_parser import BMSParser
from mqtt_helper import MQTTPublisher
from config import BMSConfig, MQTTConfig, AppConfig


def print_bms_summary(data: Dict[str, Any]) -> None:
    """Vypíše shrnutí klíčových BMS hodnot"""
    print("📊 KLÍČOVÉ HODNOTY BMS:")
    print("-" * 40)
    
    # Základní data
    if 'soc_percent' in data:
        print(f"🔋 SOC:                 {data['soc_percent']:.1f}%")
    if 'pack_voltage_v' in data:
        print(f"⚡ Pack Voltage:        {data['pack_voltage_v']:.2f}V")
    if 'pack_current_a' in data:
        current = data['pack_current_a']
        direction = "nabíjení" if current > 0 else "vybíjení" if current < 0 else "klid"
        print(f"🔌 Pack Current:        {current:.2f}A ({direction})")
    if 'cell_count' in data:
        print(f"📱 Počet článků:        {data['cell_count']}")
    if 'cycle_count' in data:
        print(f"🔄 Cykly:               {data['cycle_count']}")
    
    # Teploty
    if any(key in data for key in ['ambient_temp_c', 'mos_temp_c']):
        print("\n🌡️  TEPLOTY:")
        if 'ambient_temp_c' in data:
            print(f"   Okolní:              {data['ambient_temp_c']:.1f}°C")
        if 'mos_temp_c' in data:
            print(f"   MOS:                 {data['mos_temp_c']:.1f}°C")


def print_cell_voltages(voltages: list) -> None:
    """Vypíše napětí článků s statistikami"""
    if not voltages:
        return
        
    print(f"\n📱 NAPĚTÍ ČLÁNKŮ ({len(voltages)}):")
    
    # Zobraz prvních 8 článků
    for i in range(min(8, len(voltages))):
        print(f"   Článek {i+1:2d}: {voltages[i]:.3f}V")
    
    if len(voltages) > 8:
        print(f"   ... a {len(voltages) - 8} dalších")
    
    # Statistiky
    min_v, max_v = min(voltages), max(voltages)
    avg_v = sum(voltages) / len(voltages)
    diff_v = max_v - min_v
    
    print(f"   📊 Rozsah: {min_v:.3f}V - {max_v:.3f}V (Δ{diff_v:.3f}V)")
    print(f"   📊 Průměr: {avg_v:.3f}V")
    
    if diff_v > 0.1:
        print(f"   ⚠️  VAROVÁNÍ: Velký rozdíl napětí ({diff_v*1000:.0f}mV)")


def read_bms_data() -> Dict[str, Any]:
    """Přečte a zparsuje data z BMS"""
    print("📤 Komunikace s BMS...")
    
    # Získání raw dat
    raw_response = request_device_info(
        port=BMSConfig.PORT,
        address=BMSConfig.BMS_ADDRESS,
        baudrate=BMSConfig.BAUDRATE,
        timeout=BMSConfig.TIMEOUT
    )
    
    print("✅ Komunikace dokončena!")
    
    if not raw_response:
        raise Exception("Žádná odpověď z BMS")
    
    # Konverze na hex string pro parser
    print("🔄 Konverze dat...")
    if raw_response.startswith(b'~') and raw_response.endswith(b'\r'):
        ascii_hex = raw_response[1:-1].decode('ascii', errors='ignore')
    else:
        ascii_hex = raw_response.hex()
    
    # Parsování
    print("🔍 Parsování dat...")
    parsed_data = BMSParser.parse_service_42_response(ascii_hex)
    print("✅ Parsování dokončeno!")
    return parsed_data


def main() -> int:
    """Hlavní funkce"""
    # Nastavení logování
    logging.basicConfig(
        level=getattr(logging, AppConfig.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    print("=" * 50)
    print("🔋 BMS Reader - Service 42 + MQTT")
    print("=" * 50)
    print(f"📡 Port: {BMSConfig.PORT}")
    print(f"📡 Adresa: 0x{BMSConfig.BMS_ADDRESS:02X}")
    print(f"📡 MQTT: {MQTTConfig.BROKER_HOST}:{MQTTConfig.BROKER_PORT}")
    print(f"🔄 Interval: {AppConfig.READ_INTERVAL}s")
    print()
    
    # Inicializace MQTT
    mqtt_publisher = MQTTPublisher()
    
    try:
        # Připojení k MQTT
        print("📡 Připojování k MQTT...")
        if not mqtt_publisher.connect():
            print("❌ Nepodařilo se připojit k MQTT")
            return 1
        
        # Počkáme na připojení
        time.sleep(2)
        
        # Publikuj Home Assistant Auto Discovery
        print("🏠 Publikování Home Assistant Auto Discovery...")
        if not mqtt_publisher.publish_discovery_config():
            print("⚠️  Nepodařilo se publikovat Auto Discovery")
        
        print("✅ MQTT inicializace dokončena!")
        print()
        
        # Hlavní smyčka
        cycle_count = 0
        while True:
            cycle_count += 1
            print(f"📊 Cyklus #{cycle_count}")
            print("-" * 30)
            
            try:
                # Čtení a parsování dat
                data = read_bms_data()
                print("✅ Data úspěšně načtena!")
                
                # Zobrazení shrnutí
                print_bms_summary(data)
                
                # Zobrazení napětí článků
                if 'cell_voltages_v' in data:
                    print_cell_voltages(data['cell_voltages_v'])
                
                # Publikování na MQTT
                print("\n📤 Odesílání na MQTT...")
                if mqtt_publisher.publish_bms_data(data):
                    print("✅ Data odeslána na MQTT")
                else:
                    print("❌ Chyba při odesílání na MQTT")
                
                print(f"\n⏰ Další čtení za {AppConfig.READ_INTERVAL}s...")
                print("=" * 50)
                
                # Čekání do dalšího cyklu
                time.sleep(AppConfig.READ_INTERVAL)
                
            except KeyboardInterrupt:
                print("\n⏹️  Přerušeno uživatelem")
                break
            except Exception as e:
                print(f"❌ Chyba v cyklu: {e}")
                print(f"⏰ Pokus za {AppConfig.READ_INTERVAL}s...")
                time.sleep(AppConfig.READ_INTERVAL)
        
        return 0
        
    except Exception as e:
        print(f"❌ Kritická chyba: {e}")
        print("\n🔧 Zkontrolujte:")
        print("   - Je BMS zapnutý?")
        print("   - Je správný port v config.ini?")
        print("   - Je dostupný MQTT server?")
        return 1
    finally:
        print("\n📡 Odpojování od MQTT...")
        mqtt_publisher.disconnect()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️  Přerušeno uživatelem")
        sys.exit(1)