#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced MQTT Helper for Multi-Battery Home Assistant Auto Discovery
"""

import json
import logging
import time
from typing import Dict, Any, Optional, List
import paho.mqtt.client as mqtt

from addon_config import get_config


logger = logging.getLogger(__name__)


class MultiBatteryMQTTPublisher:
    """Enhanced MQTT publisher for multi-battery Home Assistant integration"""
    
    def __init__(self):
        self.config = get_config()
        self.client = mqtt.Client()
        if self.config.mqtt_username:
            self.client.username_pw_set(self.config.mqtt_username, self.config.mqtt_password)
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        self.connected = False
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Connected to MQTT broker {self.config.mqtt_host}:{self.config.mqtt_port}")
        else:
            self.connected = False
            logger.error(f"❌ MQTT connection error: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        self.connected = False
        logger.info("📡 Disconnected from MQTT broker")
    
    def _on_publish(self, client, userdata, mid):
        """Callback for MQTT message publishing"""
        logger.debug(f"📤 MQTT message published: {mid}")
    
    def connect(self, timeout: int = 10, retries: int = 3) -> bool:
        """Connects to MQTT broker with retry mechanism"""
        for attempt in range(retries):
            try:
                logger.info(f"📡 Attempt #{attempt + 1}: Connecting to MQTT {self.config.mqtt_host}:{self.config.mqtt_port}")
                
                # Network availability diagnostics
                logger.info(f"🔍 MQTT connection diagnostics:")
                logger.info(f"   Host: {self.config.mqtt_host}")
                logger.info(f"   Port: {self.config.mqtt_port}")
                logger.info(f"   Username: {'***' if self.config.mqtt_username else 'none'}")
                logger.info(f"   Password: {'***' if self.config.mqtt_password else 'none'}")
                
                # Connect to MQTT
                self.client.connect(self.config.mqtt_host, self.config.mqtt_port, 60)
                self.client.loop_start()
                
                # Wait for connection with timeout
                wait_time = 0
                while wait_time < timeout and not self.connected:
                    time.sleep(0.5)
                    wait_time += 0.5
                
                if self.connected:
                    logger.info(f"✅ MQTT connection successful after {wait_time:.1f}s")
                    return True
                else:
                    logger.warning(f"⏱️ Timeout waiting for MQTT connection ({timeout}s)")
                    self.client.loop_stop()
                    
            except Exception as e:
                logger.error(f"❌ MQTT connection error (attempt #{attempt + 1}): {e}")
                
            if attempt < retries - 1:
                wait_time = 5 * (attempt + 1)  # Progressive backoff
                logger.info(f"⏳ Waiting {wait_time}s before next attempt...")
                time.sleep(wait_time)
        
        logger.error(f"❌ Failed to connect to MQTT after {retries} attempts")
        return False
    
    def disconnect(self):
        """Disconnects from MQTT broker"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish_multi_battery_discovery(self, battery_names: List[str]) -> bool:
        """Publishes Home Assistant Auto Discovery for all batteries"""
        if not self.connected:
            logger.error("❌ Not connected to MQTT - cannot publish discovery")
            return False
        
        logger.info(f"📤 Publishing Auto Discovery for {len(battery_names)} batteries...")
        
        success_count = 0
        
        # Discovery for each individual battery
        for battery_name in battery_names:
            if self._publish_battery_discovery(battery_name):
                success_count += 1
        
        # Discovery for virtual battery (if enabled)
        if self.config.enable_virtual_battery and len(battery_names) > 1:
            if self._publish_battery_discovery("_virtual_battery", is_virtual=True):
                success_count += 1
        
        logger.info(f"📤 Auto Discovery published for {success_count} batteries")
        return success_count > 0
    
    def _publish_battery_discovery(self, battery_name: str, is_virtual: bool = False) -> bool:
        """Publishes discovery config for one battery"""
        try:
            # Determine device name
            if is_virtual:
                device_name = self.config.virtual_battery_name
                device_id = f"{self.config.device_id}_virtual"
            else:
                device_name = battery_name
                device_id = f"{self.config.device_id}_{battery_name.lower().replace(' ', '_')}"
            
            # Sensor definitions
            sensors = self._get_sensor_definitions(is_virtual)
            
            # Publish discovery for each sensor
            for sensor in sensors:
                discovery_topic = f"homeassistant/sensor/{device_id}/{sensor['object_id']}/config"
                state_topic = f"bms/{device_id}/{sensor['object_id']}"
                
                config = {
                    "name": f"{device_name} {sensor['name']}",
                    "unique_id": f"{device_id}_{sensor['object_id']}",
                    "object_id": f"{device_id}_{sensor['object_id']}",
                    "state_topic": state_topic,
                    "device": {
                        "identifiers": [device_id],
                        "name": device_name,
                        "manufacturer": self.config.manufacturer,
                        "model": self.config.model + (" Virtual" if is_virtual else ""),
                        "sw_version": "1.1.0"
                    }
                }
                
                # Add optional attributes
                for attr in ['unit_of_measurement', 'device_class', 'state_class', 'icon']:
                    if attr in sensor:
                        config[attr] = sensor[attr]
                
                # Publish
                self.client.publish(discovery_topic, json.dumps(config), retain=True)
                logger.debug(f"Published discovery for {device_name} {sensor['name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publishing discovery for {battery_name}: {e}")
            return False
    
    def _get_sensor_definitions(self, is_virtual: bool = False) -> List[Dict]:
        """Returns sensor definitions for battery"""
        base_sensors = [
            {
                "name": "SOC",
                "object_id": "soc",
                "unit_of_measurement": "%",
                "device_class": "battery",
                "state_class": "measurement",
                "icon": "mdi:battery"
            },
            {
                "name": "Pack Voltage",
                "object_id": "pack_voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "icon": "mdi:lightning-bolt"
            },
            {
                "name": "Pack Current",
                "object_id": "pack_current",
                "unit_of_measurement": "A",
                "device_class": "current",
                "state_class": "measurement",
                "icon": "mdi:current-dc"
            },
            {
                "name": "Power",
                "object_id": "power",
                "unit_of_measurement": "W",
                "device_class": "power",
                "state_class": "measurement",
                "icon": "mdi:flash"
            },
            {
                "name": "Remaining Capacity",
                "object_id": "remaining_capacity",
                "unit_of_measurement": "Ah",
                "state_class": "measurement",
                "icon": "mdi:battery-charging"
            },
            {
                "name": "Temperature",
                "object_id": "temperature",
                "unit_of_measurement": "°C",
                "device_class": "temperature",
                "state_class": "measurement",
                "icon": "mdi:thermometer"
            },
            {
                "name": "Min Cell Voltage",
                "object_id": "min_cell_voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "icon": "mdi:battery-low"
            },
            {
                "name": "Max Cell Voltage",
                "object_id": "max_cell_voltage",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "icon": "mdi:battery-high"
            },
            {
                "name": "Cell Voltage Difference",
                "object_id": "cell_voltage_diff",
                "unit_of_measurement": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "icon": "mdi:battery-alert"
            },
            {
                "name": "Status",
                "object_id": "status",
                "icon": "mdi:information"
            }
        ]
        
        # Add special sensors for virtual battery
        if is_virtual:
            virtual_sensors = [
                {
                    "name": "Battery Count",
                    "object_id": "battery_count",
                    "state_class": "measurement",
                    "icon": "mdi:counter"
                },
                {
                    "name": "Connected Batteries",
                    "object_id": "connected_batteries",
                    "icon": "mdi:battery-outline"
                }
            ]
            base_sensors.extend(virtual_sensors)
        
        return base_sensors
    
    def publish_battery_data(self, battery_name: str, data: Dict[str, Any], is_virtual: bool = False) -> bool:
        """Publishes data for one battery"""
        if not self.connected:
            logger.error("❌ Not connected to MQTT - cannot publish data")
            return False
        
        try:
            # Determine device_id
            if is_virtual:
                device_id = f"{self.config.device_id}_virtual"
            else:
                device_id = f"{self.config.device_id}_{battery_name.lower().replace(' ', '_')}"
            
            # Publish individual sensors
            sensor_mappings = {
                'soc': 'soc_percent',
                'pack_voltage': 'pack_voltage_v',
                'pack_current': 'pack_current_a',
                'power': 'power_w',
                'remaining_capacity': 'remaining_capacity_ah',
                'temperature': 'temperature_1_c',
                'min_cell_voltage': 'min_cell_voltage_v',
                'max_cell_voltage': 'max_cell_voltage_v',
                'cell_voltage_diff': 'cell_voltage_diff_v',
                'status': 'status'
            }
            
            # Add special mappings for virtual battery
            if is_virtual:
                sensor_mappings.update({
                    'battery_count': 'battery_count',
                    'connected_batteries': 'connected_batteries'
                })
            
            published_count = 0
            for sensor_id, data_key in sensor_mappings.items():
                if data_key in data:
                    topic = f"bms/{device_id}/{sensor_id}"
                    value = data[data_key]
                    
                    # Special handling for some data types
                    if isinstance(value, list):
                        value = ', '.join(map(str, value))
                    elif isinstance(value, float):
                        value = round(value, 3)
                    
                    self.client.publish(topic, str(value))
                    published_count += 1
            
            logger.debug(f"📤 Published {published_count} sensors for {battery_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publishing data for {battery_name}: {e}")
            return False
    
    def publish_all_battery_data(self, all_data: Dict[str, Dict[str, Any]]) -> bool:
        """Publishes data for all batteries"""
        if not self.connected:
            logger.error("❌ Not connected to MQTT - cannot publish data")
            return False
        
        success_count = 0
        
        for battery_name, data in all_data.items():
            is_virtual = battery_name == "_virtual_battery"
            if self.publish_battery_data(battery_name, data, is_virtual):
                success_count += 1
        
        logger.info(f"📤 Published data for {success_count}/{len(all_data)} batteries")
        return success_count > 0


# Backward compatibility alias
MQTTPublisher = MultiBatteryMQTTPublisher
