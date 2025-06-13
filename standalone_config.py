#!/usr/bin/env python3
"""
Standalone konfigurace pro BMS Reader bez Home Assistant Add-on závislostí
Používá environment proměnné místo HA options.json
"""

import os
import json
from typing import Dict, Optional


class BMSConfig:
    def __init__(self):
        self.port = os.getenv('BMS_PORT', '/dev/ttyUSB0')
        self.address = int(os.getenv('BMS_ADDRESS', '1'))
        self.baudrate = int(os.getenv('BMS_BAUDRATE', '9600'))
        self.timeout = float(os.getenv('BMS_TIMEOUT', '3.0'))


class MQTTConfig:
    def __init__(self):
        self.host = os.getenv('MQTT_HOST', 'localhost')
        self.port = int(os.getenv('MQTT_PORT', '1883'))
        self.username = os.getenv('MQTT_USER', '')
        self.password = os.getenv('MQTT_PASSWORD', '')
        self.keepalive = int(os.getenv('MQTT_KEEPALIVE', '60'))
        self.discovery_prefix = os.getenv('MQTT_TOPIC_PREFIX', 'homeassistant')
    
    # Kompatibilita s původním MQTTConfig rozhraním
    @property
    def BROKER_HOST(self) -> str:
        return self.host
    
    @property 
    def BROKER_PORT(self) -> int:
        return self.port
    
    @property
    def USERNAME(self) -> str:
        return self.username
    
    @property
    def PASSWORD(self) -> str:
        return self.password
    
    @property
    def DISCOVERY_PREFIX(self) -> str:
        return self.discovery_prefix
    
    @property
    def DEVICE_ID(self) -> str:
        return os.getenv('DEVICE_ID', 'bms_reader')
    
    @classmethod
    def get_base_topic(cls) -> str:
        """Generuje base topic"""
        device_id = os.getenv('DEVICE_ID', 'bms_reader')
        return f"bms/{device_id}"
    
    @classmethod
    def get_discovery_topic(cls, component: str, object_id: str) -> str:
        """Generuje discovery topic pro Home Assistant"""
        prefix = os.getenv('MQTT_TOPIC_PREFIX', 'homeassistant')
        device_id = os.getenv('DEVICE_ID', 'bms_reader')
        return f"{prefix}/{component}/{device_id}/{object_id}/config"
    
    @classmethod
    def get_state_topic(cls, sensor_name: str) -> str:
        """Generuje state topic pro senzor"""
        return f"{cls.get_base_topic()}/{sensor_name}"


class DeviceConfig:
    def __init__(self):
        self.id = os.getenv('DEVICE_ID', 'bms_reader')
        self.name = os.getenv('DEVICE_NAME', 'BMS Reader')
        self.manufacturer = os.getenv('DEVICE_MANUFACTURER', 'BMS Reader')
        self.model = os.getenv('DEVICE_MODEL', 'v1.0')


class AppConfig:
    def __init__(self):
        self.read_interval = int(os.getenv('READ_INTERVAL', '30'))
        self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def LOG_LEVEL(self) -> str:
        """Kompatibilita s původním AppConfig rozhraním"""
        return self.log_level
    
    @classmethod
    def get_device_info(cls) -> dict:
        """Vrací device info pro Home Assistant"""
        return {
            "identifiers": [os.getenv('DEVICE_ID', 'bms_reader')],
            "name": os.getenv('DEVICE_NAME', 'BMS Reader'),
            "manufacturer": os.getenv('DEVICE_MANUFACTURER', 'BMS Reader'),
            "model": os.getenv('DEVICE_MODEL', 'v1.0'),
            "sw_version": "1.0.2"
        }


class Config:
    """Standalone konfigurace bez HA Add-on závislostí"""
    
    def __init__(self):
        # Načtení konfigurace z environment proměnných
        self.bms = BMSConfig()
        self.mqtt = MQTTConfig()
        self.device = DeviceConfig()
        self.app = AppConfig()
    
    def get(self, key: str, default=None):
        """Kompatibilita s původním rozhraním"""
        if key == 'bms.port':
            return self.bms.port
        elif key == 'bms.address':
            return self.bms.address
        elif key == 'bms.baudrate':
            return self.bms.baudrate
        elif key == 'bms.timeout':
            return self.bms.timeout
        elif key == 'mqtt.host':
            return self.mqtt.host
        elif key == 'mqtt.port':
            return self.mqtt.port
        elif key == 'mqtt.username':
            return self.mqtt.username
        elif key == 'mqtt.password':
            return self.mqtt.password
        elif key == 'mqtt.keepalive':
            return self.mqtt.keepalive
        elif key == 'device.id':
            return self.device.id
        elif key == 'device.name':
            return self.device.name
        elif key == 'device.manufacturer':
            return self.device.manufacturer
        elif key == 'device.model':
            return self.device.model
        elif key == 'app.read_interval':
            return self.app.read_interval
        elif key == 'app.log_level':
            return self.app.log_level
        else:
            return default


# Globální instance konfigurace
_config = Config()

# Export pro kompatibilitu
def get_config():
    return _config


if __name__ == "__main__":
    config = get_config()
    print("=== BMS Reader Standalone Configuration ===")
    print(f"BMS Port: {config.bms.port}")
    print(f"BMS Address: {config.bms.address}")
    print(f"MQTT Host: {config.mqtt.host}")
    print(f"MQTT Port: {config.mqtt.port}")
    print(f"Device ID: {config.device.id}")
    print(f"Read Interval: {config.app.read_interval}s")
