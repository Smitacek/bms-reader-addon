#!/usr/bin/env python3
"""
Simplified configuration for Battery Monitor Add-on
"""

import json
import os
from pathlib import Path
from typing import Dict


class Config:
    """Simplified configuration for Battery Monitor"""
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from Home Assistant options or environment"""
        options = self.load_addon_options()
        
        # BMS Configuration
        self.bms_port = options.get('bms_port', os.getenv('BMS_PORT', '/dev/ttyUSB0'))
        self.bms_address = int(options.get('bms_address', os.getenv('BMS_ADDRESS', '1')))
        self.bms_baudrate = 9600
        self.bms_timeout = 2.0
        
        # MQTT Configuration  
        self.mqtt_host = options.get('mqtt_host', os.getenv('MQTT_HOST', 'core-mosquitto'))
        self.mqtt_port = int(options.get('mqtt_port', os.getenv('MQTT_PORT', '1883')))
        self.mqtt_username = options.get('mqtt_username', os.getenv('MQTT_USERNAME', ''))
        self.mqtt_password = options.get('mqtt_password', os.getenv('MQTT_PASSWORD', ''))
        
        # Device Configuration
        self.device_name = "BMS LiFePO4 Battery"
        self.device_id = "bms_lifepo4_battery"
        self.manufacturer = "Daren"
        self.model = "Daren BMS"
        
        # Application Configuration
        self.read_interval = int(options.get('read_interval', os.getenv('READ_INTERVAL', '30')))
        self.log_level = "INFO"
        
        # Diagnostika konfigurace
        self._print_diagnostics()
    
    def _print_diagnostics(self):
        """Print configuration diagnostics"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🔧 Konfigurace Battery Monitor:")
        logger.info(f"   BMS Port: {self.bms_port}")
        logger.info(f"   BMS Address: {self.bms_address}")
        logger.info(f"   MQTT Host: {self.mqtt_host}")
        logger.info(f"   MQTT Port: {self.mqtt_port}")
        logger.info(f"   MQTT Auth: {'Ano' if self.mqtt_username else 'Ne'}")
        logger.info(f"   Read Interval: {self.read_interval}s")
        
        # MQTT Discovery
        self.discovery_prefix = "homeassistant"
    
    def load_addon_options(self) -> Dict:
        """Load Home Assistant add-on options"""
        options_file = Path('/data/options.json')
        if options_file.exists():
            try:
                with open(options_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading options.json: {e}")
                return {}
        return {}


def get_config() -> Config:
    """Get configuration instance"""
    return Config()
