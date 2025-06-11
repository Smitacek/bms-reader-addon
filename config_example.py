#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Příklad konfigurace pro BMS Reader
Kopírujte do config.py a upravte dle vašeho prostředí
"""

# BMS komunikace
class BMSConfig:
    """Konfigurace BMS komunikace"""
    PORT = "/dev/tty.usbserial-B003BHLO"  # ⚠️ UPRAVTE! Váš USB port
    BMS_ADDRESS = 0x01                    # Adresa BMS (obvykle 0x01)
    BAUDRATE = 9600                       # Baudrate (obvykle 9600)
    TIMEOUT = 2.0                         # Timeout pro komunikaci


# MQTT/Home Assistant konfigurace
class MQTTConfig:
    """Konfigurace MQTT serveru (Home Assistant)"""
    # MQTT Server
    BROKER_HOST = "192.168.1.100"        # ⚠️ UPRAVTE! IP adresa Home Assistant
    BROKER_PORT = 1883                   # MQTT port (obvykle 1883)
    USERNAME = "mqtt_user"               # ⚠️ UPRAVTE! MQTT uživatel
    PASSWORD = "mqtt_password"           # ⚠️ UPRAVTE! MQTT heslo
    
    # MQTT Topics - Home Assistant Auto Discovery
    DISCOVERY_PREFIX = "homeassistant"   # HA discovery prefix
    DEVICE_NAME = "bms_battery"          # Název zařízení
    DEVICE_ID = "bms_lifepo4_01"         # ⚠️ UPRAVTE! Jedinečné ID zařízení
    
    # Base topic pro data
    @classmethod
    def get_base_topic(cls) -> str:
        """Generuje base topic"""
        return f"bms/{cls.DEVICE_ID}"
    
    # Auto discovery topics
    @classmethod
    def get_discovery_topic(cls, component: str, object_id: str) -> str:
        """Generuje discovery topic pro Home Assistant"""
        return f"{cls.DISCOVERY_PREFIX}/{component}/{cls.DEVICE_ID}/{object_id}/config"
    
    @classmethod
    def get_state_topic(cls, sensor_name: str) -> str:
        """Generuje state topic pro senzor"""
        return f"{cls.get_base_topic()}/{sensor_name}"


# Obecná konfigurace
class AppConfig:
    """Obecná konfigurace aplikace"""
    # Interval čtení dat (sekundy)
    READ_INTERVAL = 30                   # ⚠️ UPRAVTE! Jak často číst data (30s doporučeno)
    
    # Logování
    LOG_LEVEL = "INFO"                   # DEBUG, INFO, WARNING, ERROR
    
    # Home Assistant device info
    @classmethod
    def get_device_info(cls) -> dict:
        """Vrátí device info pro Home Assistant"""
        return {
            "identifiers": [MQTTConfig.DEVICE_ID],
            "name": "BMS LiFePO4 Battery",
            "model": "Daren BMS",
            "manufacturer": "Daren",
            "sw_version": "1.0.0",
            "via_device": None
        }


# 🔧 Jak najít správné hodnoty:
#
# 1. USB PORT:
#    macOS: ls /dev/tty.usbserial-*
#    Linux: ls /dev/ttyUSB*
#
# 2. MQTT BROKER_HOST:
#    IP adresa vašeho Home Assistant serveru
#    Často: 192.168.1.xxx nebo 192.168.0.xxx
#
# 3. MQTT USERNAME/PASSWORD:
#    Vytvořte MQTT uživatele v Home Assistant:
#    Settings → People → Users → Add User
#    Zaškrtněte "Can only log in from the local network"
#
# 4. DEVICE_ID:
#    Jedinečný identifikátor - použijte něco jako:
#    "bms_garage_01", "bms_solar_battery", apod.
#
# 5. READ_INTERVAL:
#    30s je dobré pro domácí použití
#    Pro monitoring můžete snížit na 10s
#    Pro produkci možná zvýšit na 60s
