#!/usr/bin/env python3
"""
Battery Monitor Add-on for Home Assistant
Simplified version with clean configuration
"""

import sys
import time
import logging
from typing import Dict, Any

from modbus import request_device_info
from bms_parser import BMSParser
from mqtt_helper import MQTTPublisher
from addon_config import get_config


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='[%(levelname)s] %(message)s',
        stream=sys.stdout
    )


def read_bms_data(config) -> Dict[str, Any]:
    """Read data from BMS"""
    try:
        device_info = request_device_info(
            port=config.bms_port,
            address=config.bms_address,
            baudrate=config.bms_baudrate,
            timeout=config.bms_timeout
        )
        
        if device_info and len(device_info) >= 3:
            parser = BMSParser()
            
            # Convert bytes to hex string if needed
            if isinstance(device_info, bytes):
                if device_info.startswith(b'~') and device_info.endswith(b'\r'):
                    hex_data = device_info[1:-1].decode('ascii', errors='ignore')
                else:
                    hex_data = device_info.hex()
            else:
                hex_data = device_info
                
            parsed_data = parser.parse_service_42_response(hex_data)
            return parsed_data
        else:
            logging.warning("No valid data received from BMS")
            return {}
            
    except Exception as e:
        logging.error(f"Error reading BMS data: {e}")
        return {}


def main():
    """Main function"""
    print("🔋 Battery Monitor Add-on - Version 1.0.0")
    
    # Load configuration
    try:
        config = get_config()
        logging.info("Loading configuration from Home Assistant options")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return 1
    
    # Setup logging
    setup_logging(config.log_level)
    
    # Log configuration
    logging.info(f"BMS Port: {config.bms_port}")
    logging.info(f"BMS Address: {config.bms_address}")
    logging.info(f"MQTT Host: {config.mqtt_host}:{config.mqtt_port}")
    logging.info(f"Read Interval: {config.read_interval}s")
    
    # Initialize MQTT
    try:
        mqtt = MQTTPublisher()
        mqtt.config = config  # Pass config to MQTT publisher
        
        if mqtt.connect():
            logging.info(f"MQTT connection successful!")
            mqtt.publish_discovery_config()
            logging.info("Home Assistant Auto Discovery config published")
        else:
            logging.error("Failed to connect to MQTT broker")
            return 1
            
    except Exception as e:
        logging.error(f"MQTT initialization failed: {e}")
        return 1
    
    # Main monitoring loop
    logging.info(f"Starting monitoring loop (interval: {config.read_interval}s)")
    
    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            logging.info(f"📊 Cycle #{cycle_count}")
            
            # Read BMS data
            logging.info("📤 Communicating with BMS...")
            data = read_bms_data(config)
            
            if data:
                logging.info("✅ Communication completed!")
                
                # Publish to MQTT
                if mqtt.publish_bms_data(data):
                    logging.info("BMS data published via MQTT")
                else:
                    logging.warning("Failed to publish data to MQTT")
                
                # Print summary
                soc = data.get('soc_percent', 0)
                voltage = data.get('pack_voltage_v', 0)
                current = data.get('pack_current_a', 0)
                logging.info(f"📊 SOC: {soc}%, Voltage: {voltage}V, Current: {current}A")
            else:
                logging.warning("❌ No valid BMS data received")
            
            # Wait for next iteration
            time.sleep(config.read_interval)
            
        except KeyboardInterrupt:
            logging.info("🛑 Monitoring stopped by user")
            break
        except Exception as e:
            logging.error(f"Error in monitoring loop: {e}")
            time.sleep(10)  # Wait before retry
    
    # Cleanup
    if mqtt:
        mqtt.disconnect()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())