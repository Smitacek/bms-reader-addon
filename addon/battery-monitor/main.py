#!/usr/bin/env python3
"""
Battery Monitor Add-on for Home Assistant
Multi-battery support with virtual battery aggregation
"""

import sys
import time
import logging
from typing import Dict, Any

from multi_battery import MultiBatteryManager
from mqtt_helper import MultiBatteryMQTTPublisher
from addon_config import get_config


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='[%(levelname)s] %(message)s',
        stream=sys.stdout
    )


def main():
    """Main function with multi-battery support"""
    print("🔋 Battery Monitor Add-on - Multi-Battery Version 1.1.4")
    
    # Load configuration
    try:
        config = get_config()
        logging.info("Loading multi-battery configuration from Home Assistant options")
    except Exception as e:
        logging.error(f"Failed to load configuration: {e}")
        return 1
    
    # Setup logging
    setup_logging(config.log_level)
    
    # Log configuration summary
    enabled_batteries = config.get_enabled_batteries()
    logging.info(f"🔧 Configuration loaded:")
    logging.info(f"   Multi-battery mode: {'Yes' if config.multi_battery_mode else 'No'}")
    logging.info(f"   Enabled batteries: {len(enabled_batteries)}")
    logging.info(f"   Virtual battery: {'Yes' if config.enable_virtual_battery else 'No'}")
    logging.info(f"   MQTT Host: {config.mqtt_host}:{config.mqtt_port}")
    logging.info(f"   Read Interval: {config.read_interval}s")
    
    # Initialize multi-battery manager
    try:
        battery_manager = MultiBatteryManager(
            batteries=enabled_batteries,
            enable_virtual=config.enable_virtual_battery
        )
        logging.info(f"✅ Multi-battery manager initialized")
    except Exception as e:
        logging.error(f"❌ Failed to initialize battery manager: {e}")
        return 1
    
    # Initialize MQTT
    mqtt = None
    mqtt_connected = False
    
    try:
        mqtt = MultiBatteryMQTTPublisher()
        
        # Pokus o připojení k MQTT s retry
        logging.info("🔌 Inicializace MQTT připojení...")
        mqtt_connected = mqtt.connect(timeout=15, retries=3)
        
        if mqtt_connected:
            logging.info("✅ MQTT připojení úspěšné!")
            
            # Publikování Auto Discovery pro všechny baterie
            try:
                battery_names = [bat.name for bat in enabled_batteries]
                mqtt.publish_multi_battery_discovery(battery_names)
                logging.info("✅ Home Assistant Auto Discovery config publikován pro všechny baterie")
            except Exception as e:
                logging.warning(f"⚠️ Chyba při publikování discovery config: {e}")
        else:
            logging.warning("⚠️ MQTT připojení selhalo - aplikace bude pokračovat bez MQTT")
            
    except Exception as e:
        logging.error(f"❌ MQTT inicializace selhala: {e}")
        logging.warning("⚠️ Aplikace bude pokračovat bez MQTT")
    
    # Main monitoring loop
    logging.info(f"🔄 Spouštění monitoring loop (interval: {config.read_interval}s)")
    
    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            logging.info(f"📊 Cycle #{cycle_count}")
            
            # Čtení dat ze všech baterií
            logging.info("📤 Čtení dat ze všech baterií...")
            all_data = battery_manager.get_all_data()
            
            if all_data:
                logging.info(f"✅ Načtena data z {len(all_data)} baterií!")
                
                # Výpis shrnutí pro každou baterii
                for battery_name, data in all_data.items():
                    if battery_name == "_virtual_battery":
                        logging.info(f"🏦 Virtual Battery: "
                                   f"SOC {data.get('soc_percent', 0):.1f}%, "
                                   f"Voltage {data.get('pack_voltage_v', 0):.2f}V, "
                                   f"Current {data.get('pack_current_a', 0):.2f}A, "
                                   f"Batteries: {data.get('battery_count', 0)}")
                    else:
                        logging.info(f"🔋 {battery_name}: "
                                   f"SOC {data.get('soc_percent', 0):.1f}%, "
                                   f"Voltage {data.get('pack_voltage_v', 0):.2f}V, "
                                   f"Current {data.get('pack_current_a', 0):.2f}A")
                
                # Publikování do MQTT (jen pokud je připojeno)
                if mqtt_connected and mqtt:
                    try:
                        if mqtt.publish_all_battery_data(all_data):
                            logging.info("📤 Data všech baterií publikována do MQTT")
                        else:
                            logging.warning("⚠️ Selhalo publikování do MQTT")
                            # Pokus o obnovení připojení
                            if not mqtt.connected:
                                logging.info("🔄 Pokus o obnovení MQTT připojení...")
                                mqtt_connected = mqtt.connect(timeout=10, retries=1)
                    except Exception as e:
                        logging.error(f"❌ Chyba při MQTT publikování: {e}")
                else:
                    logging.info("📊 Data přečtena (MQTT nedostupné)")
                
            else:
                logging.warning("❌ Nebyla načtena žádná data z baterií")
            
            # Wait for next iteration
            time.sleep(config.read_interval)
            
        except KeyboardInterrupt:
            logging.info("🛑 Monitoring zastaven uživatelem")
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