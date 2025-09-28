#!/usr/bin/env python3
"""
Simplified configuration for Battery Monitor Add-on with Multi-battery support
"""

import glob
import json
import os
from pathlib import Path
from typing import Dict, List


class BatteryConfig:
    """Configuration for a single battery"""
    def __init__(self, port: str = "/dev/ttyUSB0", address: int = 1, 
                 name: str = None, enabled: bool = True):
        self.port = port
        self.address = address
        self.name = name or f"Battery_{address}"
        self.enabled = enabled
        self.baudrate = 9600
        self.timeout = 2.0


class Config:
    """Enhanced configuration for Battery Monitor with multi-battery support"""
    def __init__(self):
        self.load_config()
    
    def load_config(self):
        """Load configuration from Home Assistant options or environment"""
        options = self.load_addon_options()

        # Multi-battery mode
        self.multi_battery_mode = options.get('multi_battery_mode', False)
        self.batteries = self._load_batteries(options)

        # Virtual battery settings
        self.enable_virtual_battery = options.get('enable_virtual_battery', True)
        self.virtual_battery_name = options.get('virtual_battery_name', 'Battery Bank')
        
        # Prefer stable by-id device paths if available (can be disabled)
        self.prefer_by_id = bool(options.get('prefer_by_id', os.getenv('PREFER_BY_ID', 'true')).__str__().lower() in ['1','true','yes'])
        if self.prefer_by_id:
            self._prefer_by_id_paths()
        
        # Backward compatibility - single battery mode
        if not self.multi_battery_mode:
            single_port = options.get('bms_port', os.getenv('BMS_PORT', '/dev/ttyUSB0'))
            single_address = int(options.get('bms_address', os.getenv('BMS_ADDRESS', '1')))
            self.batteries = [BatteryConfig(single_port, single_address)]
        
        # MQTT Configuration  
        self.mqtt_host = options.get('mqtt_host', os.getenv('MQTT_HOST', 'core-mosquitto'))
        self.mqtt_port = int(options.get('mqtt_port', os.getenv('MQTT_PORT', '1883')))
        self.mqtt_username = options.get('mqtt_username', os.getenv('MQTT_USERNAME', ''))
        self.mqtt_password = options.get('mqtt_password', os.getenv('MQTT_PASSWORD', ''))
        
        # Device Configuration
        self.device_name = "BMS LiFePO4 Battery Monitor"
        self.device_id = "bms_multi_battery"
        self.manufacturer = "Daren"
        self.model = "Daren BMS Multi"
        
        # Application Configuration
        self.read_interval = int(options.get('read_interval', os.getenv('READ_INTERVAL', '30')))
        # Default to WARNING to reduce log verbosity; allow override via option or env
        self.log_level = str(options.get('log_level', os.getenv('LOG_LEVEL', 'WARNING'))).upper()

        # Discovery (one-off scan) options
        self.discovery_mode = bool(options.get('discovery_mode', False))
        self.discovery_address_from = int(options.get('discovery_address_from', 1))
        self.discovery_address_to = int(options.get('discovery_address_to', 16))
        self.discovery_timeout_ms = int(options.get('discovery_timeout_ms', 300))
        self.discovery_ports = options.get('discovery_ports', [])
        
        # Configuration diagnostics
        self._print_diagnostics()
    
    def _load_batteries(self, options: Dict) -> List[BatteryConfig]:
        """Load battery configurations from options"""
        batteries = []
        battery_configs = options.get('batteries', [])
        
        for i, bat_config in enumerate(battery_configs):
            if i >= 16:  # Limit to 16 batteries
                break
                
            port = bat_config.get('port', f'/dev/ttyUSB{i}')
            address = bat_config.get('address', i + 1)
            name = bat_config.get('name', f'Battery_{address}')
            enabled = bat_config.get('enabled', True)
            
            batteries.append(BatteryConfig(port, address, name, enabled))
        
        return batteries

    def _prefer_by_id_paths(self) -> None:
        """Replace /dev/ttyUSBx with stable /dev/serial/by-id symlinks when possible."""
        try:
            by_id_dir = Path('/dev/serial/by-id')
            if not by_id_dir.exists():
                return

            # Build mapping from real device (e.g., /dev/ttyUSB0) to by-id path
            candidates = glob.glob(str(by_id_dir / '*'))
            resolved_map: Dict[str, str] = {}
            for link in candidates:
                try:
                    real = os.path.realpath(link)
                    resolved_map[real] = link
                except Exception:
                    continue

            for bat in self.batteries:
                # Skip if already using a by-id path
                if bat.port.startswith('/dev/serial/by-id/'):
                    continue
                # Resolve current port and swap to by-id if we find a match
                try:
                    real = os.path.realpath(bat.port)
                except Exception:
                    real = bat.port

                if real in resolved_map:
                    stable = resolved_map[real]
                    # Update to stable path
                    bat.port = stable
        except Exception:
            # Fail silently; this is a best-effort improvement
            pass
    
    def get_enabled_batteries(self) -> List[BatteryConfig]:
        """Get list of enabled batteries"""
        return [bat for bat in self.batteries if bat.enabled]
    
    def _print_diagnostics(self):
        """Print configuration diagnostics"""
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("🔧 Battery Monitor Multi-Battery Configuration:")
        logger.info(f"   Multi-battery mode: {'Yes' if self.multi_battery_mode else 'No'}")
        logger.info(f"   Number of batteries: {len(self.batteries)}")
        
        for i, battery in enumerate(self.batteries):
            status = "✅" if battery.enabled else "❌"
            logger.info(f"   Battery {i+1}: {status} {battery.name} (Port: {battery.port}, Address: {battery.address})")
        
        logger.info(f"   Virtual battery: {'Yes' if self.enable_virtual_battery else 'No'}")
        if self.enable_virtual_battery:
            logger.info(f"   Virtual battery name: {self.virtual_battery_name}")
        
        logger.info(f"   MQTT Host: {self.mqtt_host}")
        logger.info(f"   MQTT Port: {self.mqtt_port}")
        logger.info(f"   MQTT Auth: {'Yes' if self.mqtt_username else 'No'}")
        logger.info(f"   Read Interval: {self.read_interval}s")
        logger.info(f"   Discovery mode: {'Yes' if self.discovery_mode else 'No'}")
    
    def load_addon_options(self) -> Dict:
        """Load options from Home Assistant add-on options.json"""
        options_file = Path('/data/options.json')
        if options_file.exists():
            try:
                with open(options_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading {options_file}: {e}")
                return {}
        return {}

    # Backward compatibility properties
    @property
    def bms_port(self):
        """Primary battery port for backward compatibility"""
        return self.batteries[0].port if self.batteries else "/dev/ttyUSB0"
    
    @property
    def bms_address(self):
        """Primary battery address for backward compatibility"""
        return self.batteries[0].address if self.batteries else 1
    
    @property
    def bms_baudrate(self):
        """BMS baudrate"""
        return 9600
    
    @property
    def bms_timeout(self):
        """BMS timeout"""
        return 2.0


def get_config() -> Config:
    """Factory function to get configuration"""
    return Config()
