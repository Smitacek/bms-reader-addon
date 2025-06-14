#!/usr/bin/env python3
"""
Diagnostický script pro Battery Monitor addon
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
    """Kontrola síťové dostupnosti"""
    logging.info("🌐 Kontrola síťové dostupnosti:")
    
    # DNS resolution
    try:
        import socket
        result = socket.gethostbyname('core-mosquitto')
        logging.info(f"✅ DNS: core-mosquitto -> {result}")
    except Exception as e:
        logging.error(f"❌ DNS: core-mosquitto nedostupné: {e}")
    
    # Ping test
    try:
        result = subprocess.run(['ping', '-c', '1', 'core-mosquitto'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            logging.info("✅ PING: core-mosquitto dostupné")
        else:
            logging.error("❌ PING: core-mosquitto nedostupné")
    except Exception as e:
        logging.error(f"❌ PING: Chyba při testování: {e}")

def check_mqtt_port():
    """Kontrola MQTT portu"""
    logging.info("🔌 Kontrola MQTT portu:")
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex(('core-mosquitto', 1883))
        sock.close()
        
        if result == 0:
            logging.info("✅ Port 1883: dostupný")
        else:
            logging.error("❌ Port 1883: nedostupný")
            
    except Exception as e:
        logging.error(f"❌ Port test chyba: {e}")

def check_environment():
    """Kontrola prostředí"""
    logging.info("🔧 Kontrola prostředí:")
    
    # Environment variables
    env_vars = ['MQTT_HOST', 'MQTT_PORT', 'MQTT_USERNAME', 'MQTT_PASSWORD']
    for var in env_vars:
        value = os.getenv(var, 'není nastaveno')
        if var in ['MQTT_PASSWORD'] and value != 'není nastaveno':
            value = '***'
        logging.info(f"   {var}: {value}")
    
    # Options file
    options_file = Path('/data/options.json')
    if options_file.exists():
        logging.info("✅ Options file: existuje")
        try:
            import json
            with open(options_file) as f:
                options = json.load(f)
            logging.info(f"   MQTT Host: {options.get('mqtt_host', 'neuvedeno')}")
            logging.info(f"   MQTT Port: {options.get('mqtt_port', 'neuvedeno')}")
            logging.info(f"   MQTT User: {options.get('mqtt_username', 'neuvedeno')}")
        except Exception as e:
            logging.error(f"❌ Chyba čtení options: {e}")
    else:
        logging.warning("⚠️ Options file neexistuje")

def check_mqtt_manual():
    """Manuální test MQTT"""
    logging.info("🔍 Manuální MQTT test:")
    
    try:
        import paho.mqtt.client as mqtt
        
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                logging.info("✅ MQTT: Připojení úspěšné")
                client.disconnect()
            else:
                logging.error(f"❌ MQTT: Připojení selhalo (kód: {rc})")
        
        client = mqtt.Client()
        client.on_connect = on_connect
        
        # Test bez autentifikace
        logging.info("   Testování bez autentifikace...")
        try:
            client.connect('core-mosquitto', 1883, 10)
            client.loop_start()
            import time
            time.sleep(3)
            client.loop_stop()
        except Exception as e:
            logging.error(f"❌ MQTT test: {e}")
            
    except ImportError:
        logging.error("❌ paho-mqtt knihovna není dostupná")

def main():
    """Hlavní diagnostická funkce"""
    setup_logging()
    
    logging.info("🔍 Battery Monitor - Diagnostika")
    logging.info("=" * 50)
    
    check_environment()
    logging.info("-" * 30)
    
    check_network()
    logging.info("-" * 30)
    
    check_mqtt_port()
    logging.info("-" * 30)
    
    check_mqtt_manual()
    logging.info("=" * 50)
    logging.info("✅ Diagnostika dokončena")

if __name__ == "__main__":
    main()
