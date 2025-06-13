#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfigurace pro BMS Reader Home Assistant Add-on
Načítá z /data/options.json (HA Add-on options)
"""

import json
import os
from pathlib import Path


class Config:
    """Hlavní třída pro načítání konfigurace z HA Add-on options"""
    
    def __init__(self):
        self.options_file = Path("/data/options.json")
        self.options = self._load_options()
    
    def _load_options(self):
        """Načte konfiguraci z /data/options.json (HA Add-on)"""
        if not self.options_file.exists():
            # Fallback pro development - zkusí config.ini
            fallback_file = Path(__file__).parent / "config.ini"
            if fallback_file.exists():
                return self._load_from_ini(fallback_file)
            else:
                raise FileNotFoundError(
                    f"Konfigurační soubor {self.options_file} neexistuje!\n"
                    f"Spusťte jako Home Assistant Add-on nebo vytvořte config.ini"
                )
        
        with open(self.options_file, 'r') as f:
            return json.load(f)
    
    def _load_from_ini(self, ini_file):
        """Fallback načítání z config.ini pro development"""
        import configparser
        config = configparser.ConfigParser()
        config.read(ini_file, encoding='utf-8')
        
        # Převod INI na JSON strukturu
        return {
            "bms": {
                "port": config.get('BMS', 'port'),
                "address": config.getint('BMS', 'address'),
                "baudrate": config.getint('BMS', 'baudrate'),
                "timeout": config.getfloat('BMS', 'timeout')
            },
            "mqtt": {
                "host": config.get('MQTT', 'broker_host'),
                "port": config.getint('MQTT', 'broker_port'),
                "username": config.get('MQTT', 'username'),
                "password": config.get('MQTT', 'password'),
                "discovery_prefix": config.get('HOME_ASSISTANT', 'discovery_prefix', fallback='homeassistant')
            },
            "device": {
                "id": config.get('DEVICE', 'device_id'),
                "name": config.get('DEVICE', 'device_name'),
                "manufacturer": config.get('DEVICE', 'device_manufacturer'),
                "model": config.get('DEVICE', 'device_model')
            },
            "application": {
                "read_interval": config.getint('APPLICATION', 'read_interval'),
                "log_level": config.get('APPLICATION', 'log_level')
            }
        }


# Globální instance konfigurace
_config = Config()


class BMSConfig:
    """Konfigurace BMS komunikace"""
    
    @property
    def PORT(self) -> str:
        return _config.options['bms']['port']
    
    @property
    def BMS_ADDRESS(self) -> int:
        return _config.options['bms']['address']
    
    @property
    def BAUDRATE(self) -> int:
        return _config.options['bms']['baudrate']
    
    @property
    def TIMEOUT(self) -> float:
        return _config.options['bms']['timeout']


class MQTTConfig:
    """Konfigurace MQTT serveru (Home Assistant)"""
    
    @property
    def BROKER_HOST(self) -> str:
        return _config.options['mqtt']['host']
    
    @property
    def BROKER_PORT(self) -> int:
        return _config.options['mqtt']['port']
    
    @property
    def USERNAME(self) -> str:
        return _config.options['mqtt'].get('username', '')
    
    @property
    def PASSWORD(self) -> str:
        return _config.options['mqtt'].get('password', '')
    
    @property
    def DISCOVERY_PREFIX(self) -> str:
        return _config.options['mqtt'].get('discovery_prefix', 'homeassistant')
    
    @property
    def DEVICE_ID(self) -> str:
        return _config.options['device']['id']
    
    @classmethod
    def get_base_topic(cls) -> str:
        """Generuje base topic"""
        device_id = _config.options['device']['id']
        return f"bms/{device_id}"
    
    @classmethod
    def get_discovery_topic(cls, component: str, object_id: str) -> str:
        """Generuje discovery topic pro Home Assistant"""
        prefix = _config.options['mqtt'].get('discovery_prefix', 'homeassistant')
        device_id = _config.options['device']['id']
        return f"{prefix}/{component}/{device_id}/{object_id}/config"
    
    @classmethod
    def get_state_topic(cls, sensor_name: str) -> str:
        """Generuje state topic pro senzor"""
        return f"{cls.get_base_topic()}/{sensor_name}"


class AppConfig:
    """Obecná konfigurace aplikace"""
    
    @property
    def READ_INTERVAL(self) -> int:
        return _config.options['application']['read_interval']
    
    @property
    def LOG_LEVEL(self) -> str:
        return _config.options['application']['log_level']
    
    @classmethod
    def get_device_info(cls) -> dict:
        """Vrátí device info pro Home Assistant"""
        device = _config.options['device']
        return {
            "identifiers": [device['id']],
            "name": device['name'],
            "model": device.get('model', 'Daren BMS'),
            "manufacturer": device.get('manufacturer', 'Daren'),
            "sw_version": "1.0.0",
            "via_device": None
        }


# Vytvoření instancí pro zpětnou kompatibilitu
BMSConfig = BMSConfig()
MQTTConfig = MQTTConfig()
AppConfig = AppConfig()
