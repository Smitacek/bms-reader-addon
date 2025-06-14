#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfigurace pro BMS Reader Home Assistant Add-on
Načítá z /data/options.json (HA Add-on options) s fallback na environment proměnné
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional


class BMSConfig:
    """Konfigurace BMS připojení"""
    def __init__(self, options: Dict = None):
        if options and 'bms' in options:
            bms_opts = options['bms']
            self.port = bms_opts.get('port', '/dev/ttyUSB0')
            self.address = bms_opts.get('address', 1)
            self.baudrate = bms_opts.get('baudrate', 9600)
            self.timeout = bms_opts.get('timeout', 3.0)
        else:
            # Fallback na environment proměnné
            self.port = os.getenv('BMS_PORT', '/dev/ttyUSB0')
            self.address = int(os.getenv('BMS_ADDRESS', '1'))
            self.baudrate = int(os.getenv('BMS_BAUDRATE', '9600'))
            self.timeout = float(os.getenv('BMS_TIMEOUT', '3.0'))


class MQTTConfig:
    """Konfigurace MQTT připojení"""
    def __init__(self, options: Dict = None):
        if options and 'mqtt' in options:
            mqtt_opts = options['mqtt']
            self.host = mqtt_opts.get('host', 'core-mosquitto')
            self.port = mqtt_opts.get('port', 1883)
            self.username = mqtt_opts.get('username', '')
            self.password = mqtt_opts.get('password', '')
            self.discovery_prefix = mqtt_opts.get('discovery_prefix', 'homeassistant')
        else:
            # Fallback na environment proměnné
            self.host = os.getenv('MQTT_HOST', 'core-mosquitto')
            self.port = int(os.getenv('MQTT_PORT', '1883'))
            self.username = os.getenv('MQTT_USER', '')
            self.password = os.getenv('MQTT_PASSWORD', '')
            self.discovery_prefix = os.getenv('MQTT_TOPIC_PREFIX', 'homeassistant')
        
        self.keepalive = 60
    
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
        device_config = DeviceConfig()
        return device_config.id
    
    @classmethod
    def get_base_topic(cls) -> str:
        """Generuje base topic"""
        device_config = DeviceConfig()
        return f"bms/{device_config.id}"
    
    @classmethod
    def get_discovery_topic(cls, component: str, object_id: str) -> str:
        """Generuje discovery topic pro Home Assistant"""
        mqtt_config = MQTTConfig()
        device_config = DeviceConfig()
        return f"{mqtt_config.discovery_prefix}/{component}/{device_config.id}/{object_id}/config"
    
    @classmethod
    def get_state_topic(cls, sensor_name: str) -> str:
        """Generuje state topic pro senzor"""
        return f"{cls.get_base_topic()}/{sensor_name}"


class DeviceConfig:
    """Konfigurace zařízení"""
    def __init__(self, options: Dict = None):
        if options and 'device' in options:
            device_opts = options['device']
            self.id = device_opts.get('id', 'bms_lifepo4_01')
            self.name = device_opts.get('name', 'BMS LiFePO4 Battery')
            self.manufacturer = device_opts.get('manufacturer', 'Daren')
            self.model = device_opts.get('model', 'Daren BMS')
        else:
            # Fallback na environment proměnné
            self.id = os.getenv('DEVICE_ID', 'bms_lifepo4_01')
            self.name = os.getenv('DEVICE_NAME', 'BMS LiFePO4 Battery')
            self.manufacturer = os.getenv('DEVICE_MANUFACTURER', 'Daren')
            self.model = os.getenv('DEVICE_MODEL', 'Daren BMS')


class AppConfig:
    """Konfigurace aplikace"""
    def __init__(self, options: Dict = None):
        if options and 'application' in options:
            app_opts = options['application']
            self.read_interval = app_opts.get('read_interval', 30)
            self.log_level = app_opts.get('log_level', 'INFO')
        else:
            # Fallback na environment proměnné
            self.read_interval = int(os.getenv('READ_INTERVAL', '30'))
            self.log_level = os.getenv('LOG_LEVEL', 'INFO')
    
    @property
    def LOG_LEVEL(self) -> str:
        """Kompatibilita s původním AppConfig rozhraním"""
        return self.log_level
    
    @classmethod
    def get_device_info(cls) -> dict:
        """Vrací device info pro Home Assistant"""
        device_config = DeviceConfig()
        return {
            "identifiers": [device_config.id],
            "name": device_config.name,
            "manufacturer": device_config.manufacturer,
            "model": device_config.model,
            "sw_version": "1.0.4"
        }


class Config:
    """Hlavní třída pro načítání konfigurace z HA Add-on options"""
    
    def __init__(self):
        self.options_file = Path("/data/options.json")
        self.options = self._load_options()
        
        # Inicializace všech config objektů
        self.bms = BMSConfig(self.options)
        self.mqtt = MQTTConfig(self.options)
        self.device = DeviceConfig(self.options)
        self.app = AppConfig(self.options)
    
    def _load_options(self) -> Dict:
        """Načte konfiguraci z /data/options.json (HA Add-on) s fallback"""
        if self.options_file.exists():
            try:
                with open(self.options_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Chyba při načítání {self.options_file}: {e}")
                print("Používám fallback na environment proměnné")
                return {}
        else:
            print(f"Soubor {self.options_file} neexistuje, používám environment proměnné")
            return {}


# Pro zpětnou kompatibilitu
def get_config() -> Config:
    """Factory funkce pro získání konfigurace"""
    return Config()


# Globální instance konfigurace
_config = Config()
