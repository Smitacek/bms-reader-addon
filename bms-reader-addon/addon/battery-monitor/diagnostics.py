#!/usr/bin/env python3
"""
Diagnostic script for Battery Monitor addon
"""

import os
import sys
import socket
import logging
import subprocess
from pathlib import Path

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='[DIAG] %(message)s',
        stream=sys.stdout
    )

def check_network():
    """Check network availability"""
    logging.info("🌐 Network availability check:")
    
    # DNS resolution
    try:
        import socket
        result = socket.gethostbyname('core-mosquitto')
        logging.info(f"✅ DNS: core-mosquitto -> {result}")
    except Exception as e:
        logging.error(f"❌ DNS: core-mosquitto unreachable: {e}")
    
    # Ping test
    try:
        result = subprocess.run(['ping', '-c', '1', 'core-mosquitto'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logging.info("✅ PING: core-mosquitto reachable")
        else:
            logging.error("❌ PING: core-mosquitto unreachable")
    except Exception as e:
        logging.error(f"❌ PING: Error during test: {e}")

def check_mqtt_port():
    """Check MQTT port"""
    logging.info("🔌 MQTT port check:")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('core-mosquitto', 1883))
        sock.close()
        
        if result == 0:
            logging.info("✅ Port 1883: available")
        else:
            logging.error("❌ Port 1883: unavailable")
            
    except Exception as e:
        logging.error(f"❌ Port test error: {e}")

def check_environment():
    """Check environment"""
    logging.info("🔧 Environment check:")
    
    # Environment variables
    env_vars = ['MQTT_HOST', 'MQTT_PORT', 'MQTT_USERNAME', 'MQTT_PASSWORD']
    for var in env_vars:
        value = os.getenv(var, 'not set')
        if var in ['MQTT_PASSWORD'] and value != 'not set':
            value = '***'
        logging.info(f"   {var}: {value}")
    
    # Options file
    options_file = Path('/data/options.json')
    if options_file.exists():
        logging.info("✅ Options file: exists")
        try:
            import json
            with open(options_file) as f:
                options = json.load(f)
            logging.info(f"   MQTT Host: {options.get('mqtt_host', 'not specified')}")
            logging.info(f"   MQTT Port: {options.get('mqtt_port', 'not specified')}")
            logging.info(f"   MQTT User: {options.get('mqtt_username', 'not specified')}")
        except Exception as e:
            logging.error(f"❌ Error reading options: {e}")
    else:
        logging.warning("⚠️ Options file does not exist")

def check_mqtt_manual():
    """Manual MQTT test"""
    logging.info("🔍 Manual MQTT test:")
    
    try:
        import paho.mqtt.client as mqtt
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logging.info("✅ MQTT: Connection successful")
                client.disconnect()
            else:
                logging.error(f"❌ MQTT: Connection failed (code: {rc})")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        
        # Test without authentication
        logging.info("   Testing without authentication...")
        try:
            client.connect('core-mosquitto', 1883, 10)
            client.loop_start()
            import time
            time.sleep(3)
            client.loop_stop()
        except Exception as e:
            logging.error(f"❌ MQTT test: {e}")
            
    except ImportError:
        logging.error("❌ paho-mqtt library is not available")

def main():
    """Main diagnostic function"""
    setup_logging()
    
    logging.info("🔍 Battery Monitor - Diagnostics")
    logging.info("=" * 50)
    
    check_environment()
    logging.info("-" * 30)
    
    check_network()
    logging.info("-" * 30)
    
    check_mqtt_port()
    logging.info("-" * 30)
    
    check_mqtt_manual()
    logging.info("=" * 50)
    logging.info("✅ Diagnostics completed")

if __name__ == "__main__":
    main()
