#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfigurace pro BMS Reader
"""

# BMS komunikace
class BMSConfig:
    """Konfigurace BMS komunikace"""
    PORT = "/dev/tty.usbserial-B003BHLO"  # Upravte dle vašeho systému
    BMS_ADDRESS = 0x01
    BAUDRATE = 9600
    TIMEOUT = 2.0


# MQTT/Home Assistant konfigurace
class MQTTConfig:
    """Konfigurace MQTT serveru (Home Assistant)"""
    # MQTT Server
    BROKER_HOST = "192.168.1.100"  # IP adresa Home Assistant
    BROKER_PORT = 1883
    USERNAME = "mqtt_user"  # MQTT uživatel
    PASSWORD = "mqtt_password"  # MQTT heslo
    
    # MQTT Topics - Home Assistant Auto Discovery
    DISCOVERY_PREFIX = "homeassistant"
    DEVICE_NAME = "bms_battery"
    DEVICE_ID = "bms_lifepo4_01"
    
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
    READ_INTERVAL = 30
    
    # Logování
    LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
    
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
