#!/usr/bin/env python3
"""
Multi-Battery Manager for aggregating data from multiple BMS units
"""

import logging
from typing import Dict, List, Any, Optional
from statistics import mean

from modbus import request_device_info
from bms_parser import BMSParser
from addon_config import BatteryConfig


logger = logging.getLogger(__name__)


class VirtualBattery:
    """Virtual battery that aggregates data from multiple physical batteries"""
    
    def __init__(self, name: str = "Battery Bank"):
        self.name = name
        self.batteries_data = {}
        
    def add_battery_data(self, battery_id: str, data: Dict[str, Any]):
        """Add data from a single battery"""
        if data:
            self.batteries_data[battery_id] = data
            logger.debug(f"Added data for battery {battery_id}")
    
    def get_aggregated_data(self) -> Dict[str, Any]:
        """Calculate aggregated data from all batteries"""
        if not self.batteries_data:
            return {}
        
        # Get list of all data dictionaries
        all_data = list(self.batteries_data.values())
        
        if not all_data:
            return {}
        
        # Calculate aggregated values
        aggregated = {
            # SOC - average of all batteries
            'soc_percent': self._safe_average([d.get('soc_percent', 0) for d in all_data]),
            
            # Voltages - sum for series, average for parallel (assuming series for now)
            'pack_voltage_v': sum([d.get('pack_voltage_v', 0) for d in all_data]),
            
            # Current - sum of all currents
            'pack_current_a': sum([d.get('pack_current_a', 0) for d in all_data]),
            
            # Capacity - sum of all capacities
            'remaining_capacity_ah': sum([d.get('remaining_capacity_ah', 0) for d in all_data]),
            'full_capacity_ah': sum([d.get('full_capacity_ah', 0) for d in all_data]),
            
            # Temperature - average of all temperatures
            'temperature_1_c': self._safe_average([d.get('temperature_1_c', 20) for d in all_data]),
            'temperature_2_c': self._safe_average([d.get('temperature_2_c', 20) for d in all_data]),
            
            # Status - worst case (any protection triggers for all)
            'protection_status': self._aggregate_protection_status(all_data),
            
            # Cell data - collect from all batteries
            'cell_voltages_v': self._aggregate_cell_voltages(all_data),
            
            # Cycles - maximum of all batteries
            'cycle_count': max([d.get('cycle_count', 0) for d in all_data]) if all_data else 0,
            
            # Additional aggregated fields
            'battery_count': len(all_data),
            'connected_batteries': list(self.batteries_data.keys()),
            
            # Min/Max values across all batteries
            'min_cell_voltage_v': min([d.get('min_cell_voltage_v', 3.0) for d in all_data]) if all_data else 0,
            'max_cell_voltage_v': max([d.get('max_cell_voltage_v', 3.4) for d in all_data]) if all_data else 0,
        }
        
        # Calculate derived values
        aggregated['power_w'] = aggregated['pack_voltage_v'] * aggregated['pack_current_a']
        aggregated['cell_voltage_diff_v'] = aggregated['max_cell_voltage_v'] - aggregated['min_cell_voltage_v']
        
        # Status based on aggregated data
        if aggregated['pack_current_a'] > 0.1:
            aggregated['status'] = 'charging'
        elif aggregated['pack_current_a'] < -0.1:
            aggregated['status'] = 'discharging'
        else:
            aggregated['status'] = 'idle'
        
        return aggregated
    
    def _safe_average(self, values: List[float]) -> float:
        """Calculate average, handling empty lists"""
        valid_values = [v for v in values if v is not None]
        return mean(valid_values) if valid_values else 0.0
    
    def _aggregate_protection_status(self, all_data: List[Dict]) -> str:
        """Aggregate protection status from all batteries"""
        statuses = []
        for data in all_data:
            status = data.get('protection_status', 'normal')
            if status != 'normal':
                statuses.append(status)
        
        if statuses:
            return ', '.join(set(statuses))  # Unique statuses
        return 'normal'
    
    def _aggregate_cell_voltages(self, all_data: List[Dict]) -> List[float]:
        """Collect all cell voltages from all batteries"""
        all_cells = []
        for data in all_data:
            cells = data.get('cell_voltages_v', [])
            if isinstance(cells, list):
                all_cells.extend(cells)
        return all_cells


class MultiBatteryManager:
    """Manager for handling multiple BMS batteries"""
    
    def __init__(self, batteries: List[BatteryConfig], enable_virtual: bool = True):
        self.batteries = batteries
        self.enable_virtual = enable_virtual
        self.virtual_battery = VirtualBattery() if enable_virtual else None
        self.parser = BMSParser()
        
    def read_all_batteries(self) -> Dict[str, Dict[str, Any]]:
        """Read data from all enabled batteries"""
        results = {}
        
        logger.info(f"📊 Reading data from {len(self.batteries)} batteries...")
        
        for battery in self.batteries:
            if not battery.enabled:
                logger.debug(f"Skipping disabled battery: {battery.name}")
                continue
                
            logger.info(f"📤 Reading {battery.name} (Port: {battery.port}, Address: {battery.address})")
            
            try:
                data = self._read_single_battery(battery)
                if data:
                    results[battery.name] = data
                    logger.info(f"✅ {battery.name}: SOC {data.get('soc_percent', 0)}%, "
                              f"Voltage {data.get('pack_voltage_v', 0):.2f}V, "
                              f"Current {data.get('pack_current_a', 0):.2f}A")
                    
                    # Add to virtual battery
                    if self.virtual_battery:
                        self.virtual_battery.add_battery_data(battery.name, data)
                else:
                    logger.warning(f"❌ No data received from {battery.name}")
                    
            except Exception as e:
                logger.error(f"❌ Error reading {battery.name}: {e}")
                continue
        
        logger.info(f"📊 Successfully read {len(results)} out of {len([b for b in self.batteries if b.enabled])} batteries")
        return results
    
    def _read_single_battery(self, battery: BatteryConfig) -> Optional[Dict[str, Any]]:
        """Read data from a single battery"""
        try:
            device_info = request_device_info(
                port=battery.port,
                address=battery.address,
                baudrate=battery.baudrate,
                timeout=battery.timeout
            )
            
            if device_info and len(device_info) >= 3:
                # Convert bytes to hex string if needed
                if isinstance(device_info, bytes):
                    if device_info.startswith(b'~') and device_info.endswith(b'\r'):
                        hex_data = device_info[1:-1].decode('ascii', errors='ignore')
                    else:
                        hex_data = device_info.hex()
                else:
                    hex_data = device_info
                    
                parsed_data = self.parser.parse_service_42_response(hex_data)
                
                # Add battery identification
                parsed_data['battery_name'] = battery.name
                parsed_data['battery_address'] = battery.address
                parsed_data['battery_port'] = battery.port
                
                return parsed_data
            else:
                logger.warning(f"Invalid data length from {battery.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error communicating with {battery.name}: {e}")
            return None
    
    def get_virtual_battery_data(self) -> Optional[Dict[str, Any]]:
        """Get aggregated virtual battery data"""
        if not self.virtual_battery:
            return None
            
        aggregated = self.virtual_battery.get_aggregated_data()
        if aggregated:
            aggregated['device_name'] = self.virtual_battery.name
            aggregated['is_virtual'] = True
            
        return aggregated
    
    def get_all_data(self) -> Dict[str, Dict[str, Any]]:
        """Get data from all batteries including virtual battery"""
        # Read individual batteries
        battery_data = self.read_all_batteries()
        
        # Add virtual battery data if enabled
        if self.enable_virtual and self.virtual_battery:
            virtual_data = self.get_virtual_battery_data()
            if virtual_data:
                battery_data['_virtual_battery'] = virtual_data
        
        return battery_data
