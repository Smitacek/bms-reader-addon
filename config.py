#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Konfigurace pro BMS Reader - načítá z config.ini
"""

import configparser
import os
from pathlib import Path


class Config:
    """Hlavní třída pro načítání konfigurace z config.ini"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_file = Path(__file__).parent / "config.ini"
        self._load_config()
    
    def _load_config(self):
        """Načte konfiguraci z config.ini"""
        if not self.config_file.exists():
            raise FileNotFoundError(
                f"Konfigurační soubor {self.config_file} neexistuje!\n"
                f"Vytvořte jej podle config.ini vzoru."
            )
        
        self.config.read(self.config_file, encoding='utf-8')
        
        # Ověření povinných sekcí
        required_sections = ['BMS', 'MQTT', 'DEVICE', 'HOME_ASSISTANT', 'APPLICATION']
        for section in required_sections:
            if not self.config.has_section(section):
                raise ValueError(f"Chybí sekce [{section}] v config.ini")


# Globální instance konfigurace
_config = Config()


class BMSConfig:
    """Konfigurace BMS komunikace"""
    
    @property
    def PORT(self) -> str:
        return _config.config.get('BMS', 'port')
    
    @property
    def BMS_ADDRESS(self) -> int:
        return _config.config.getint('BMS', 'address')
    
    @property
    def BAUDRATE(self) -> int:
        return _config.config.getint('BMS', 'baudrate')
    
    @property
    def TIMEOUT(self) -> float:
        return _config.config.getfloat('BMS', 'timeout')


class MQTTConfig:
    """Konfigurace MQTT serveru (Home Assistant)"""
    
    @property
    def BROKER_HOST(self) -> str:
        return _config.config.get('MQTT', 'broker_host')
    
    @property
    def BROKER_PORT(self) -> int:
        return _config.config.getint('MQTT', 'broker_port')
    
    @property
    def USERNAME(self) -> str:
        return _config.config.get('MQTT', 'username')
    
    @property
    def PASSWORD(self) -> str:
        return _config.config.get('MQTT', 'password')
    
    @property
    def DISCOVERY_PREFIX(self) -> str:
        return _config.config.get('HOME_ASSISTANT', 'discovery_prefix')
    
    @property
    def DEVICE_ID(self) -> str:
        return _config.config.get('DEVICE', 'device_id')
    
    @classmethod
    def get_base_topic(cls) -> str:
        """Generuje base topic"""
        base = _config.config.get('HOME_ASSISTANT', 'base_topic')
        device_id = _config.config.get('DEVICE', 'device_id')
        return f"{base}/{device_id}"
    
    @classmethod
    def get_discovery_topic(cls, component: str, object_id: str) -> str:
        """Generuje discovery topic pro Home Assistant"""
        prefix = _config.config.get('HOME_ASSISTANT', 'discovery_prefix')
        device_id = _config.config.get('DEVICE', 'device_id')
        return f"{prefix}/{component}/{device_id}/{object_id}/config"
    
    @classmethod
    def get_state_topic(cls, sensor_name: str) -> str:
        """Generuje state topic pro senzor"""
        return f"{cls.get_base_topic()}/{sensor_name}"


class AppConfig:
    """Obecná konfigurace aplikace"""
    
    @property
    def READ_INTERVAL(self) -> int:
        return _config.config.getint('APPLICATION', 'read_interval')
    
    @property
    def LOG_LEVEL(self) -> str:
        return _config.config.get('APPLICATION', 'log_level')
    
    @classmethod
    def get_device_info(cls) -> dict:
        """Vrátí device info pro Home Assistant"""
        return {
            "identifiers": [_config.config.get('DEVICE', 'device_id')],
            "name": _config.config.get('DEVICE', 'device_name'),
            "model": _config.config.get('DEVICE', 'device_model'),
            "manufacturer": _config.config.get('DEVICE', 'device_manufacturer'),
            "sw_version": _config.config.get('DEVICE', 'software_version'),
            "via_device": None
        }


# Vytvoření instancí pro zpětnou kompatibilitu
BMSConfig = BMSConfig()
MQTTConfig = MQTTConfig()
AppConfig = AppConfig()
