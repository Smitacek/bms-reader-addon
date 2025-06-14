#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MQTT Helper pro Home Assistant Auto Discovery
"""

import json
import logging
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt

from addon_config import get_config


logger = logging.getLogger(__name__)


class MQTTPublisher:
    """MQTT publisher pro Home Assistant"""
    
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
        """Callback při připojení k MQTT"""
        if rc == 0:
            self.connected = True
            logger.info(f"✅ Připojeno k MQTT broker {self.config.mqtt_host}:{self.config.mqtt_port}")
        else:
            self.connected = False
            logger.error(f"❌ Chyba připojení k MQTT: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback při odpojení od MQTT"""
        self.connected = False
        logger.info("📡 Odpojeno od MQTT broker")
    
    def _on_publish(self, client, userdata, mid):
        """Callback při publikování zprávy"""
        logger.debug(f"📤 MQTT zpráva publikována: {mid}")
    
    def connect(self, timeout: int = 10, retries: int = 3) -> bool:
        """Připojí se k MQTT brokeru s retry mechanikou"""
        import time
        
        for attempt in range(retries):
            try:
                logger.info(f"📡 Pokus #{attempt + 1}: Připojování k MQTT {self.config.mqtt_host}:{self.config.mqtt_port}")
                
                # Diagnostika síťové dostupnosti
                logger.info(f"🔍 Diagnostika MQTT připojení:")
                logger.info(f"   Host: {self.config.mqtt_host}")
                logger.info(f"   Port: {self.config.mqtt_port}")
                logger.info(f"   Username: {'***' if self.config.mqtt_username else 'žádné'}")
                logger.info(f"   Password: {'***' if self.config.mqtt_password else 'žádné'}")
                
                # Připojení k MQTT
                self.client.connect(self.config.mqtt_host, self.config.mqtt_port, 60)
                self.client.loop_start()
                
                # Čekání na připojení s timeoutem
                wait_time = 0
                while wait_time < timeout and not self.connected:
                    time.sleep(0.5)
                    wait_time += 0.5
                
                if self.connected:
                    logger.info(f"✅ MQTT připojení úspěšné po {wait_time:.1f}s")
                    return True
                else:
                    logger.warning(f"⏱️ Timeout při čekání na MQTT připojení ({timeout}s)")
                    self.client.loop_stop()
                    
            except Exception as e:
                logger.error(f"❌ Chyba připojení k MQTT (pokus #{attempt + 1}): {e}")
                
            if attempt < retries - 1:
                wait_time = 5 * (attempt + 1)  # Progressive backoff
                logger.info(f"⏳ Čekání {wait_time}s před dalším pokusem...")
                time.sleep(wait_time)
        
        logger.error(f"❌ Nepodařilo se připojit k MQTT po {retries} pokusech")
        return False
    
    def disconnect(self):
        """Odpojí se od MQTT brokeru"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish_discovery_config(self) -> bool:
        """Publikuje Home Assistant Auto Discovery konfigurace"""
        if not self.connected:
            logger.error("❌ Není připojeno k MQTT - nelze publikovat discovery")
            return False
        
        logger.info("📤 Publikování Home Assistant Auto Discovery config...")
        
        # Definice senzorů pro Home Assistant
        sensors = [
            {
                "name": "SOC",
                "object_id": "soc",
                "unit": "%",
                "device_class": "battery",
                "state_class": "measurement",
                "icon": "mdi:battery"
            },
            {
                "name": "Pack Voltage",
                "object_id": "pack_voltage",
                "unit": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "icon": "mdi:lightning-bolt"
            },
            {
                "name": "Pack Current",
                "object_id": "pack_current",
                "unit": "A",
                "device_class": "current",
                "state_class": "measurement",
                "icon": "mdi:current-dc"
            },
            {
                "name": "Remaining Capacity",
                "object_id": "remaining_capacity",
                "unit": "Ah",
                "device_class": "energy_storage",
                "state_class": "measurement",
                "icon": "mdi:battery-charging"
            },
            {
                "name": "Full Capacity",
                "object_id": "full_capacity",
                "unit": "Ah",
                "device_class": "energy_storage",
                "state_class": "measurement",
                "icon": "mdi:battery-plus"
            },
            {
                "name": "Cycle Count",
                "object_id": "cycle_count",
                "unit": "cycles",
                "state_class": "total_increasing",
                "icon": "mdi:counter"
            },
            {
                "name": "Cell Count",
                "object_id": "cell_count",
                "unit": "cells",
                "icon": "mdi:battery-outline"
            },
            {
                "name": "Ambient Temperature",
                "object_id": "ambient_temp",
                "unit": "°C",
                "device_class": "temperature",
                "state_class": "measurement",
                "icon": "mdi:thermometer"
            },
            {
                "name": "MOS Temperature",
                "object_id": "mos_temp",
                "unit": "°C",
                "device_class": "temperature",
                "state_class": "measurement",
                "icon": "mdi:thermometer-lines"
            },
            {
                "name": "Min Cell Voltage",
                "object_id": "min_cell_voltage",
                "unit": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "icon": "mdi:battery-low"
            },
            {
                "name": "Max Cell Voltage",
                "object_id": "max_cell_voltage",
                "unit": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "icon": "mdi:battery-high"
            },
            {
                "name": "Cell Voltage Difference",
                "object_id": "cell_voltage_diff",
                "unit": "V",
                "device_class": "voltage",
                "state_class": "measurement",
                "icon": "mdi:battery-alert-variant"
            }
        ]
        
        # Publikuj discovery config pro každý senzor
        success = True
        for sensor in sensors:
            config = {
                "name": f"BMS {sensor['name']}",
                "unique_id": f"{self.config.device_id}_{sensor['object_id']}",
                "state_topic": self.get_state_topic(sensor['object_id']),
                "unit_of_measurement": sensor.get("unit"),
                "device_class": sensor.get("device_class"),
                "state_class": sensor.get("state_class"),
                "icon": sensor.get("icon"),
                "device": self.get_device_info()
            }
            
            # Odstraň None hodnoty
            config = {k: v for k, v in config.items() if v is not None}
            
            topic = self.get_discovery_topic("sensor", sensor['object_id'])
            result = self.client.publish(topic, json.dumps(config), retain=True)
            
            if result.rc != mqtt.MQTT_ERR_SUCCESS:
                logger.error(f"❌ Chyba publikování discovery pro {sensor['name']}")
                success = False
            else:
                logger.debug(f"✅ Discovery config publikován: {sensor['name']}")
        
        if success:
            logger.info("✅ Home Assistant Auto Discovery config publikován")
        
        return success
    
    def publish_bms_data(self, data: Dict[str, Any]) -> bool:
        """Publikuje BMS data na MQTT"""
        if not self.connected:
            logger.error("❌ Není připojeno k MQTT - nelze publikovat data")
            return False
        
        logger.info("📤 Publikování BMS dat na MQTT...")
        
        # Mapování dat na MQTT topics
        mqtt_data = {
            "soc": data.get("soc_percent"),
            "pack_voltage": data.get("pack_voltage_v"),
            "pack_current": data.get("pack_current_a"),
            "remaining_capacity": data.get("remaining_capacity_ah"),
            "full_capacity": data.get("full_charge_capacity_ah"),
            "cycle_count": data.get("cycle_count"),
            "cell_count": data.get("cell_count"),
            "ambient_temp": data.get("ambient_temp_c"),
            "mos_temp": data.get("mos_temp_c")
        }
        
        # Přidej statistiky napětí článků
        if "cell_voltages_v" in data and data["cell_voltages_v"]:
            voltages = data["cell_voltages_v"]
            mqtt_data.update({
                "min_cell_voltage": min(voltages),
                "max_cell_voltage": max(voltages),
                "cell_voltage_diff": max(voltages) - min(voltages)
            })
        
        # Publikuj každou hodnotu samostatně
        success = True
        for key, value in mqtt_data.items():
            if value is not None:
                topic = self.get_state_topic(key)
                result = self.client.publish(topic, value)
                
                if result.rc != mqtt.MQTT_ERR_SUCCESS:
                    logger.error(f"❌ Chyba publikování {key}: {value}")
                    success = False
                else:
                    logger.debug(f"📤 {key}: {value}")
        
        if success:
            logger.info("✅ BMS data publikována na MQTT")
        
        return success
    
    def get_device_info(self) -> Dict[str, Any]:
        """Vrací informace o zařízení pro Home Assistant"""
        return {
            "identifiers": [self.config.device_id],
            "name": self.config.device_name,
            "model": self.config.model,
            "manufacturer": self.config.manufacturer,
            "sw_version": "1.0.1"
        }
    
    def get_discovery_topic(self, component: str, object_id: str) -> str:
        """Vrací discovery topic pro Home Assistant"""
        return f"{self.config.discovery_prefix}/{component}/{self.config.device_id}/{object_id}/config"
    
    def get_state_topic(self, object_id: str) -> str:
        """Vrací state topic pro senzor"""
        return f"{self.config.discovery_prefix}/sensor/{self.config.device_id}/{object_id}/state"
