#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BMS Reader - Jednorázové čtění bez MQTT
Pro testování komunikace s BMS
"""

import sys
from typing import Dict, Any

from modbus import request_device_info
from bms_parser import BMSParser
from config import BMSConfig


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
    
    # Kapacity
    if 'remaining_capacity_ah' in data:
        print(f"🔋 Zbývající kapacita:  {data['remaining_capacity_ah']:.1f}Ah")
    if 'full_charge_capacity_ah' in data:
        print(f"🔋 Celková kapacita:    {data['full_charge_capacity_ah']:.1f}Ah")
    
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
    
    # Zobraz všechny články
    for i in range(len(voltages)):
        print(f"   Článek {i+1:2d}: {voltages[i]:.3f}V")
    
    # Statistiky
    min_v, max_v = min(voltages), max(voltages)
    avg_v = sum(voltages) / len(voltages)
    diff_v = max_v - min_v
    
    print(f"\n   📊 Statistiky:")
    print(f"      Minimum:          {min_v:.3f}V")
    print(f"      Maximum:          {max_v:.3f}V")
    print(f"      Průměr:           {avg_v:.3f}V")
    print(f"      Rozdíl:           {diff_v:.3f}V ({diff_v*1000:.0f}mV)")
    
    if diff_v > 0.1:
        print(f"   ⚠️  VAROVÁNÍ: Velký rozdíl napětí ({diff_v*1000:.0f}mV)")
    elif diff_v > 0.05:
        print(f"   ⚠️  POZOR: Mírný rozdíl napětí ({diff_v*1000:.0f}mV)")
    else:
        print(f"   ✅ Články dobře vyvážené")


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
    print("=" * 50)
    print("🔋 BMS Reader - Jednorázové čtení")
    print("=" * 50)
    print(f"📡 Port: {BMSConfig.PORT}")
    print(f"📡 Adresa: 0x{BMSConfig.BMS_ADDRESS:02X}")
    print()
    
    try:
        # Čtení a parsování dat
        data = read_bms_data()
        print("✅ Data úspěšně načtena!")
        print()
        
        # Zobrazení shrnutí
        print_bms_summary(data)
        
        # Zobrazení napětí článků
        if 'cell_voltages_v' in data:
            print_cell_voltages(data['cell_voltages_v'])
        
        print("\n" + "=" * 50)
        print("✅ Čtení dokončeno!")
        
        return 0
        
    except Exception as e:
        print(f"❌ Chyba: {e}")
        print("\n🔧 Zkontrolujte:")
        print("   - Je BMS zapnutý?")
        print("   - Je správný port v config.py?")
        print("   - Je USB kabel připojený?")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️  Přerušeno uživatelem")
        sys.exit(1)
