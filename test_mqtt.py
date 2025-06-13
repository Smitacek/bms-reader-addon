#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test MQTT funkcionalita bez připojení k BMS
"""

from mqtt_helper import MQTTPublisher
from config import MQTTConfig

def test_mqtt_config():
    """Test MQTT konfigurace"""
    print("=== Test MQTT Konfigurace ===")
    print(f"MQTT Broker: {MQTTConfig.BROKER_HOST}:{MQTTConfig.BROKER_PORT}")
    print(f"Username: {MQTTConfig.USERNAME}")
    print(f"Device ID: {MQTTConfig.DEVICE_ID}")
    print(f"Base Topic: {MQTTConfig.get_base_topic()}")
    print()
    
    # Test discovery topics
    print("Discovery Topics:")
    print(f"SOC: {MQTTConfig.get_discovery_topic('sensor', 'soc')}")
    print(f"Voltage: {MQTTConfig.get_discovery_topic('sensor', 'pack_voltage')}")
    print()
    
    # Test state topics
    print("State Topics:")
    print(f"SOC: {MQTTConfig.get_state_topic('soc')}")
    print(f"Voltage: {MQTTConfig.get_state_topic('pack_voltage')}")
    print()

def test_mqtt_data():
    """Test simulovaných MQTT dat"""
    print("=== Test Simulovaných Dat ===")
    
    # Simulovaná BMS data
    test_data = {
        "soc_percent": 64.0,
        "pack_voltage_v": 53.08,
        "pack_current_a": 0.0,
        "cell_count": 16,
        "cycle_count": 63,
        "ambient_temp_c": 23.0,
        "mos_temp_c": 22.0,
        "remaining_capacity_ah": 67.64,
        "full_charge_capacity_ah": 105.7,
        "cell_voltages_v": [3.316, 3.316, 3.311, 3.314, 3.315, 3.318, 3.330, 3.317,
                           3.316, 3.327, 3.317, 3.316, 3.320, 3.321, 3.322, 3.312]
    }
    
    # Vytvoř MQTT publisher (bez připojení)
    publisher = MQTTPublisher()
    
    print("Simulovaná BMS data:")
    for key, value in test_data.items():
        if key != "cell_voltages_v":
            print(f"  {key}: {value}")
    
    print(f"  cell_voltages: {len(test_data['cell_voltages_v'])} článků")
    print(f"  min/max: {min(test_data['cell_voltages_v']):.3f}V / {max(test_data['cell_voltages_v']):.3f}V")
    print()
    
    # Poznámka o připojení
    print("💡 Pro test s reálným MQTT:")
    print("   1. Upravte config.ini s reálnými MQTT údaji")
    print("   2. Spusťte main.py")

if __name__ == "__main__":
    test_mqtt_config()
    test_mqtt_data()
