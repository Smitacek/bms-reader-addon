#!/usr/bin/env python3
"""
Battery Monitor Add-on for Home Assistant
Multi-battery support with virtual battery aggregation
"""

import sys
import time
import logging

from multi_battery import MultiBatteryManager
from mqtt_helper import MultiBatteryMQTTPublisher
from addon_config import get_config
from discovery import run_discovery


def setup_logging(level: str = "INFO"):
    """Setup logging configuration"""
    log_level = getattr(logging, level.upper(), logging.INFO)
    logging.basicConfig(
        level=log_level,
        format='[%(levelname)s] %(message)s',
        stream=sys.stdout
    )


def set_log_level(level: str) -> None:
    """Force-adjust root logging level and handler levels.

    This avoids silent no-op of basicConfig when a handler already exists.
    """
    try:
        desired = getattr(logging, str(level).upper(), logging.INFO)
    except Exception:
        desired = logging.INFO
    root = logging.getLogger()
    root.setLevel(desired)
    for h in root.handlers:
        # Keep handlers permissive; let the root level decide
        h.setLevel(logging.NOTSET)
    logging.info(f"📣 Log level set to {logging.getLevelName(desired)}")


def main():
    """Main function with enhanced multi-battery support and logging"""
    # Ensure we see early logs before config is loaded
    setup_logging("INFO")
    logging.info("🔋 Battery Monitor Add-on - Multi-Battery Version 1.2.1")
    logging.info("🚀 Starting initialization...")
    
    # Load configuration
    try:
        config = get_config()
        logging.debug("✅ Configuration loaded successfully")
    except Exception as e:
        logging.error(f"❌ Failed to load configuration: {e}")
        return 1
    
    # Adjust log level per config; force INFO in discovery mode
    desired = 'INFO' if getattr(config, 'discovery_mode', False) else str(config.log_level)
    set_log_level(desired)
    
    # Enhanced startup logging
    logging.info("🔋 ======== BATTERY MONITOR STARTUP ========")
    logging.info("📊 Battery Monitor Multi v1.2.1")
    logging.info(f"🕐 Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"📝 Log level: {config.log_level}")
    
    # Log configuration summary with more details
    enabled_batteries = config.get_enabled_batteries()
    logging.info("🔧 ======== CONFIGURATION SUMMARY ========")
    logging.info(f"   🔋 Multi-battery mode: {'✅ ENABLED' if config.multi_battery_mode else '❌ DISABLED'}")
    logging.info(f"   📊 Total configured batteries: {len(config.batteries) if config.multi_battery_mode else 1}")
    logging.info(f"   ✅ Enabled batteries: {len(enabled_batteries)}")
    logging.info(f"   🏦 Virtual battery: {'✅ ENABLED' if config.enable_virtual_battery else '❌ DISABLED'}")
    if config.enable_virtual_battery:
        logging.info(f"   📛 Virtual battery name: '{config.virtual_battery_name}'")
    logging.info(f"   📡 MQTT Host: {config.mqtt_host}:{config.mqtt_port}")
    logging.info(f"   ⏱️  Read Interval: {config.read_interval}s")
    logging.info("🔧 =======================================")

    # One-off discovery mode
    if getattr(config, 'discovery_mode', False):
        logging.info("🔎 Discovery mode enabled - scanning for BMS devices...")
        summary = run_discovery({
            'discovery_ports': config.discovery_ports,
            'discovery_address_from': config.discovery_address_from,
            'discovery_address_to': config.discovery_address_to,
            'discovery_timeout_ms': config.discovery_timeout_ms,
        })
        logging.info(f"🔎 Discovery finished. Found: {summary.get('count', 0)} devices.")
        logging.info("📝 Copy batteries:[] block from /data/discovered_batteries.yaml into add-on options.")
        logging.info("🚪 Exiting because discovery_mode is enabled. Disable it to start normal monitoring.")
        return 0
    
    # Initialize multi-battery manager
    try:
        battery_manager = MultiBatteryManager(
            batteries=enabled_batteries,
            enable_virtual=config.enable_virtual_battery
        )
        logging.info("✅ Multi-battery manager initialized")
    except Exception as e:
        logging.error(f"❌ Failed to initialize battery manager: {e}")
        return 1
    
    # Initialize MQTT with enhanced logging
    mqtt = None
    mqtt_connected = False
    
    try:
        logging.info("📡 ======== MQTT INITIALIZATION ========")
        mqtt = MultiBatteryMQTTPublisher()
        
        # MQTT connection attempt with detailed logging
        logging.info(f"🔌 Connecting to MQTT broker: {config.mqtt_host}:{config.mqtt_port}")
        if config.mqtt_username:
            logging.info(f"👤 Using authentication for user: {config.mqtt_username}")
        else:
            logging.info("🔓 Connecting without authentication")
            
        mqtt_connected = mqtt.connect(timeout=15, retries=3)
        
        if mqtt_connected:
            logging.info("✅ MQTT connection successful!")
            logging.info("📡 ===================================")
            
            # Publishing Auto Discovery for all batteries
            try:
                battery_names = [bat.name for bat in enabled_batteries]
                logging.info(f"📤 Publishing Auto Discovery for {len(battery_names)} batteries...")
                
                mqtt.publish_multi_battery_discovery(battery_names)
                logging.info("✅ Home Assistant Auto Discovery config published for all batteries")
            except Exception as e:
                logging.warning(f"⚠️ Error publishing discovery config: {e}")
        else:
            logging.warning("⚠️ MQTT connection failed - application will continue without MQTT")
            logging.info("📡 ===================================")
            
    except Exception as e:
        logging.error(f"❌ MQTT initialization failed: {e}")
        logging.warning("⚠️ Application will continue without MQTT")
    
    # Main monitoring loop
    logging.info(f"🔄 Starting monitoring loop (interval: {config.read_interval}s)")
    
    cycle_count = 0
    while True:
        try:
            cycle_count += 1
            logging.info(f"📊 Cycle #{cycle_count}")
            
            # Reading data from all batteries
            logging.info("📤 Reading data from all batteries...")
            all_data = battery_manager.get_all_data()
            
            if all_data:
                logging.info(f"✅ Data loaded from {len(all_data)} batteries!")
                
                # Summary output for each battery
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
                
                # Publishing to MQTT (only if connected)
                if mqtt_connected and mqtt:
                    try:
                        if mqtt.publish_all_battery_data(all_data):
                            logging.info("📤 Data from all batteries published to MQTT")
                        else:
                            logging.warning("⚠️ Failed to publish to MQTT")
                            # Attempt to restore connection
                            if not mqtt.connected:
                                logging.info("🔄 Attempting to restore MQTT connection...")
                                mqtt_connected = mqtt.ensure_connected(timeout=10)
                    except Exception as e:
                        logging.error(f"❌ Error during MQTT publishing: {e}")
                else:
                    logging.info("📊 Data read (MQTT unavailable)")
                
            else:
                logging.warning("❌ No data loaded from batteries")
            
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
