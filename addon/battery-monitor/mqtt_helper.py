#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced MQTT Helper for Multi-Battery Home Assistant Auto Discovery
"""

import json
import logging
import time
import math
from typing import Dict, Any, List
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
        self._loop_running = False
        self._last_reconnect_attempt = 0.0
        self._discovery_pending = True
        self._battery_names = [b.name for b in self.config.get_enabled_batteries()]

        # Configure exponential backoff for reconnects when supported
        try:
            self.client.reconnect_delay_set(min_delay=1, max_delay=30)
        except Exception:
            pass

        # Availability topic and Last Will (LWT)
        self._availability_topic = f"bms/{self.config.device_id}/availability"
        try:
            self.client.will_set(self._availability_topic, payload="offline", qos=1, retain=True)
        except Exception:
            logger.debug("LWT setup failed (will_set)")
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback for MQTT connection"""
        if rc == 0:
            self.connected = True
            self._discovery_pending = True
            logger.info(f"✅ Connected to MQTT broker {self.config.mqtt_host}:{self.config.mqtt_port}")
            for name in self._battery_names + (['_virtual_battery'] if self.config.enable_virtual_battery else []):
                self._publish(f'bms/{self._device_id(name)}/availability', 'offline', qos=1, retain=True)
            # Publish process availability online
            try:
                self.client.publish(self._availability_topic, payload="online", qos=1, retain=True)
            except Exception as e:
                logger.debug(f"Failed to publish availability online: {e}")
        else:
            self.connected = False
            logger.error(f"❌ MQTT connection error: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback for MQTT disconnection"""
        self.connected = False
        if rc != 0:
            logger.warning("📡 Unexpected MQTT disconnect; attempting reconnect...")
            # Paho loop handles reconnect; main loop also retries initial failures.
        else:
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
                logger.info("🔍 MQTT connection diagnostics:")
                logger.info(f"   Host: {self.config.mqtt_host}")
                logger.info(f"   Port: {self.config.mqtt_port}")
                logger.info(f"   Username: {'***' if self.config.mqtt_username else 'none'}")
                logger.info(f"   Password: {'***' if self.config.mqtt_password else 'none'}")
                
                # Connect to MQTT and start loop once
                self.client.connect(self.config.mqtt_host, self.config.mqtt_port, 60)
                if not self._loop_running:
                    self.client.loop_start()
                    self._loop_running = True
                
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
                    # keep loop running for potential reconnects
                    
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
        # Publish offline for graceful shutdown
        try:
            self.client.publish(self._availability_topic, payload="offline", qos=1, retain=True)
        except Exception:
            pass
        if self._loop_running:
            self.client.loop_stop()
            self._loop_running = False
        self.client.disconnect()

    def _attempt_reconnect(self):
        """Rate-limited reconnect attempt when disconnected"""
        now = time.time()
        if now - self._last_reconnect_attempt < 5:
            return
        self._last_reconnect_attempt = now
        try:
            self.client.reconnect()
            logger.info("🔄 MQTT reconnect initiated")
        except Exception as e:
            logger.debug(f"Reconnect attempt failed: {e}")

    def ensure_connected(self, timeout: int = 5) -> bool:
        """Ensure connection or try to re-establish quickly"""
        if self.connected:
            return True
        if not self._loop_running:
            self.client.loop_start()
            self._loop_running = True
        self._attempt_reconnect()
        waited = 0.0
        while waited < timeout and not self.connected:
            time.sleep(0.5)
            waited += 0.5
        return self.connected
    
    def publish_multi_battery_discovery(self, battery_names: List[str]) -> bool:
        """Publishes Home Assistant Auto Discovery for all batteries"""
        if not self.connected and not self.ensure_connected(timeout=3):
            logger.error("❌ Not connected to MQTT - cannot publish discovery")
            return False
        
        logger.info(f"📤 Publishing Auto Discovery for {len(battery_names)} batteries...")
        
        success_count = 0
        
        # Discovery for each individual battery
        for battery_name in battery_names:
            if self._publish_battery_discovery(battery_name):
                success_count += 1
        
        # Discovery for virtual battery (if enabled)
        if self.config.enable_virtual_battery:
            if self._publish_battery_discovery("_virtual_battery", is_virtual=True):
                success_count += 1
        
        logger.info(f"📤 Auto Discovery published for {success_count} batteries")
        expected_count = len(battery_names) + int(self.config.enable_virtual_battery)
        self._discovery_pending = success_count != expected_count
        return not self._discovery_pending

    def _device_id(self, battery_name):
        if battery_name == '_virtual_battery':
            return f"{self.config.device_id}_virtual"
        return f"{self.config.device_id}_{battery_name.lower().replace(' ', '_')}"

    def _publish(self, topic, payload, **kwargs):
        result = self.client.publish(topic, payload, **kwargs)
        return result.rc == mqtt.MQTT_ERR_SUCCESS

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
            sensors = self._get_sensor_definitions(is_virtual) + self._diagnostic_sensor_definitions(is_virtual)
            
            # Publish discovery for each sensor
            for sensor in sensors:
                discovery_topic = f"homeassistant/sensor/{device_id}/{sensor['object_id']}/config"
                state_topic = f"bms/{device_id}/{sensor['object_id']}"
                
                config = {
                    "name": sensor['name'],
                    "unique_id": f"{device_id}_{sensor['object_id']}",
                    "default_entity_id": f"sensor.{device_id}_{sensor['object_id']}",
                    "state_topic": state_topic,
                    "device": {
                        "identifiers": [device_id],
                        "name": device_name,
                        "manufacturer": self.config.manufacturer,
                        "model": self.config.model + (" Virtual" if is_virtual else ""),
                        "sw_version": "1.2.3"
                    }
                }
                
                # Add optional attributes
                for attr in ['unit_of_measurement', 'device_class', 'state_class', 'icon', 'entity_category']:
                    if attr in sensor:
                        config[attr] = sensor[attr]
                # Hint UI to use 3 decimals for voltage
                try:
                    if sensor.get('device_class') == 'voltage':
                        config['suggested_display_precision'] = 3
                except Exception:
                    pass
                
                # Add availability to discovery so HA shows correct status
                config["availability"] = [{
                    "topic": self._availability_topic,
                    "payload_available": "online",
                    "payload_not_available": "offline"
                }]
                if sensor.get('entity_category') != 'diagnostic':
                    config['availability'].append({
                        'topic': f'bms/{device_id}/availability',
                        'payload_available': 'online', 'payload_not_available': 'offline'
                    })
                config['availability_mode'] = 'all'
                config['expire_after'] = self.config.stale_timeout
                config['qos'] = 1
                # Old per-device retained statuses must not make fresh discovery online.
                # States remain non-retained: HA expiry survives broker/HA reloads.
                if not self._publish(discovery_topic, json.dumps(config), qos=1, retain=True):
                    return False
                logger.debug(f"Published discovery for {device_name} {sensor['name']}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publishing discovery for {battery_name}: {e}")
            return False
    
    def _diagnostic_sensor_definitions(self, is_virtual=False):
        sensors = [
            {'name': 'Last successful read', 'object_id': 'last_success', 'device_class': 'timestamp'},
            {'name': 'Data age', 'object_id': 'data_age', 'device_class': 'duration', 'unit_of_measurement': 's'},
            {'name': 'Read errors since startup', 'object_id': 'error_count'},
            {'name': 'Consecutive read errors', 'object_id': 'consecutive_errors'},
        ]
        if is_virtual:
            sensors += [
                {'name': 'Expected batteries', 'object_id': 'expected_battery_count'},
                {'name': 'Successfully read batteries', 'object_id': 'successful_battery_count'},
            ]
        for sensor in sensors:
            sensor['entity_category'] = 'diagnostic'
        return sensors

    def _get_sensor_definitions(self, is_virtual: bool = False) -> List[Dict]:
        """Returns sensor definitions for battery.

        For virtual battery, avoid topology-dependent sensors (pack current, power, total voltage).
        """
        if is_virtual:
            return [
                {
                    "name": "State of charge",
                    "object_id": "soc",
                    "unit_of_measurement": "%",
                    "device_class": "battery",
                    "state_class": "measurement",
                    "icon": "mdi:battery"
                },
                {
                    "name": "Avg Pack Voltage",
                    "object_id": "avg_pack_voltage",
                    "unit_of_measurement": "V",
                    "device_class": "voltage",
                    "state_class": "measurement",
                    "icon": "mdi:lightning-bolt"
                },
                {
                    "name": "Min Pack Voltage",
                    "object_id": "pack_voltage_min",
                    "unit_of_measurement": "V",
                    "device_class": "voltage",
                    "state_class": "measurement",
                    "icon": "mdi:battery-low"
                },
                {
                    "name": "Max Pack Voltage",
                    "object_id": "pack_voltage_max",
                    "unit_of_measurement": "V",
                    "device_class": "voltage",
                    "state_class": "measurement",
                    "icon": "mdi:battery-high"
                },
                {
                    "name": "Pack Voltage Difference",
                    "object_id": "pack_voltage_diff",
                    "unit_of_measurement": "V",
                    "device_class": "voltage",
                    "state_class": "measurement",
                    "icon": "mdi:arrow-expand-horizontal"
                },
                {
                    "name": "Mean ambient temperature" if is_virtual else "Ambient temperature",
                    "object_id": "temperature",
                    "unit_of_measurement": "°C",
                    "device_class": "temperature",
                    "state_class": "measurement",
                    "icon": "mdi:thermometer"
                },
                {
                    "name": "Status",
                    "object_id": "status",
                    "icon": "mdi:information"
                },
                {
                    "name": "Charging energy total",
                    "object_id": "energy_in_total",
                    "unit_of_measurement": "kWh",
                    "device_class": "energy",
                    "state_class": "total_increasing",
                    "icon": "mdi:battery-arrow-down"
                },
                {
                    "name": "Discharging energy total",
                    "object_id": "energy_out_total",
                    "unit_of_measurement": "kWh",
                    "device_class": "energy",
                    "state_class": "total_increasing",
                    "icon": "mdi:battery-arrow-up"
                },
                {
                    "name": "Battery Count",
                    "object_id": "battery_count",
                    "state_class": "measurement",
                    "icon": "mdi:counter"
                },
                {
                    "name": "Contributing batteries",
                    "entity_category": "diagnostic",
                    "object_id": "connected_batteries",
                    "icon": "mdi:battery-outline"
                },
            ]

        # Non-virtual battery sensors
        base_sensors = [
            {
                "name": "State of charge",
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
                "name": "Battery power",
                "object_id": "power",
                "unit_of_measurement": "W",
                "device_class": "power",
                "state_class": "measurement",
                "icon": "mdi:flash"
            },
            {
                "name": "Remaining capacity",
                "object_id": "remaining_capacity",
                "unit_of_measurement": "Ah",
                "state_class": "measurement",
                "icon": "mdi:battery-charging"
            },
            {
                "name": "Mean ambient temperature" if is_virtual else "Ambient temperature",
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
                "name": "Operating status",
                "object_id": "status",
                "icon": "mdi:information"
            },
            {
                "name": "Charging energy total",
                "object_id": "energy_in_total",
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "total_increasing",
                "icon": "mdi:battery-arrow-down"
            },
            {
                "name": "Discharging energy total",
                "object_id": "energy_out_total",
                "unit_of_measurement": "kWh",
                "device_class": "energy",
                "state_class": "total_increasing",
                "icon": "mdi:battery-arrow-up"
            }
        ]
        
        base_sensors.append({
            'name': 'Full charge capacity', 'object_id': 'full_charge_capacity',
            'unit_of_measurement': 'Ah', 'state_class': 'measurement', 'icon': 'mdi:battery'
        })
        return base_sensors
    
    def publish_battery_data(self, battery_name: str, data: Dict[str, Any], is_virtual: bool = False) -> bool:
        """Publishes data for one battery"""
        if not self.connected:
            # Try a quick reconnect before failing
            if not self.ensure_connected(timeout=3):
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
                'full_charge_capacity': 'full_charge_capacity_ah',
                'temperature': 'temperature_1_c',
                'min_cell_voltage': 'min_cell_voltage_v',
                'max_cell_voltage': 'max_cell_voltage_v',
                'cell_voltage_diff': 'cell_voltage_diff_v',
                'status': 'status',
                # Energy counters (kWh)
                'energy_in_total': 'energy_in_kwh',
                'energy_out_total': 'energy_out_kwh'
            }
            
            # Add special mappings for virtual battery
            if is_virtual:
                # Remove topology-dependent mappings for virtual battery
                for k in ['pack_voltage', 'pack_current', 'power', 'remaining_capacity', 'full_charge_capacity']:
                    sensor_mappings.pop(k, None)
                sensor_mappings.update({
                    'avg_pack_voltage': 'avg_pack_voltage_v',
                    'pack_voltage_min': 'pack_voltage_min_v',
                    'pack_voltage_max': 'pack_voltage_max_v',
                    'pack_voltage_diff': 'pack_voltage_diff_v',
                    'battery_count': 'battery_count',
                    'connected_batteries': 'connected_batteries'
                })
            
            published_count = 0
            for sensor_id, data_key in sensor_mappings.items():
                if data_key in data:
                    topic = f"bms/{device_id}/{sensor_id}"
                    value = data[data_key]
                    if value is None or (isinstance(value, float) and not math.isfinite(value)):
                        continue
                    
                    # Special handling for some data types
                    if isinstance(value, list):
                        value = ', '.join(map(str, value))
                    elif isinstance(value, float):
                        value = round(value, 3)
                    
                    if not self._publish(topic, str(value), qos=1):
                        return False
                    published_count += 1
            
            logger.debug(f"📤 Published {published_count} sensors for {battery_name}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error publishing data for {battery_name}: {e}")
            return False
    
    def publish_all_battery_data(self, all_data, diagnostics=None):
        """Publish health every cycle, measurements only for successful reads."""
        if not self.connected and not self.ensure_connected(timeout=3):
            return False
        if self._discovery_pending:
            if not self.publish_multi_battery_discovery(self._battery_names):
                return False
        if diagnostics is None:
            diagnostics = {name: {'available': name in all_data} for name in self._battery_names}
            if self.config.enable_virtual_battery:
                diagnostics['_virtual_battery'] = {'available': '_virtual_battery' in all_data}
        success = True
        # Mark unavailable first so partial reads cannot expose a partial bank.
        for name, health in diagnostics.items():
            if not health.get('available'):
                success = self._publish(f'bms/{self._device_id(name)}/availability', 'offline', qos=1, retain=True) and success
        for name, data in all_data.items():
            published = self.publish_battery_data(name, data, name == '_virtual_battery')
            success = published and success
            if published and diagnostics.get(name, {}).get('available'):
                success = self._publish(f'bms/{self._device_id(name)}/availability', 'online', qos=1, retain=True) and success
        for name, health in diagnostics.items():
            for sensor in self._diagnostic_sensor_definitions(name == '_virtual_battery'):
                key = 'data_age_seconds' if sensor['object_id'] == 'data_age' else sensor['object_id']
                value = health.get(key)
                # Never turn unknown age/timestamp into zero.
                if value is not None:
                    success = self._publish(f"bms/{self._device_id(name)}/{sensor['object_id']}", str(value), qos=1) and success
        return success


# Backward compatibility alias
MQTTPublisher = MultiBatteryMQTTPublisher
