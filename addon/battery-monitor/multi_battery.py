#!/usr/bin/env python3
"""
Multi-Battery Manager for aggregating data from multiple BMS units
"""

import logging
import time
from typing import Dict, List, Any, Optional
from statistics import mean

from modbus import request_device_info
from bms_parser import BMSParser
from addon_config import BatteryConfig, get_config
from energy_tracker import EnergyTracker


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
        # Aggregate without assuming series/parallel topology
        voltages = [d.get('pack_voltage_v', 0.0) for d in all_data]
        currents = [d.get('pack_current_a', 0.0) for d in all_data]

        aggregated = {
            # SOC - simple average across batteries
            'soc_percent': self._safe_average([d.get('soc_percent', 0) for d in all_data]),

            # Voltage stats across batteries (topology-agnostic)
            'avg_pack_voltage_v': self._safe_average(voltages),
            'pack_voltage_min_v': min(voltages) if voltages else 0.0,
            'pack_voltage_max_v': max(voltages) if voltages else 0.0,
            'pack_voltage_diff_v': (max(voltages) - min(voltages)) if voltages else 0.0,

            # Temperature - average of available readings
            'temperature_1_c': self._safe_average([d.get('temperature_1_c', 20) for d in all_data]),
            'temperature_2_c': self._safe_average([d.get('temperature_2_c', 20) for d in all_data]),

            # Status - worst case (any non-normal protection takes precedence)
            'protection_status': self._aggregate_protection_status(all_data),

            # Cell data - collect from all batteries
            'cell_voltages_v': self._aggregate_cell_voltages(all_data),

            # Min/Max cell voltages across all cells
            'min_cell_voltage_v': min([d.get('min_cell_voltage_v', 3.0) for d in all_data]) if all_data else 0,
            'max_cell_voltage_v': max([d.get('max_cell_voltage_v', 3.4) for d in all_data]) if all_data else 0,

            # Meta
            'battery_count': len(all_data),
            'connected_batteries': list(self.batteries_data.keys()),
        }

        # Status based on per-battery statuses (charging wins over idle)
        statuses = [d.get('status', 'idle') for d in all_data]
        if any(s == 'charging' for s in statuses):
            aggregated['status'] = 'charging'
        elif any(s == 'discharging' for s in statuses):
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
        # Energy tracking setup
        cfg = get_config()
        self._base_device_id = cfg.device_id
        self._energy_tracker = EnergyTracker()
        
        # Log battery configuration on startup
        self._log_battery_configuration()
        
    def read_all_batteries(self) -> Dict[str, Dict[str, Any]]:
        """Read data from all enabled batteries with detailed logging"""
        results = {}
        enabled_batteries = [b for b in self.batteries if b.enabled]

        logger.info("📊 ===== BATTERY READING CYCLE =====")
        logger.info(f"🔄 Reading data from {len(enabled_batteries)} enabled batteries...")

        successful_reads = 0
        failed_reads = 0

        # Reset virtual battery aggregation each cycle to avoid stale data
        if self.virtual_battery is not None:
            self.virtual_battery.batteries_data = {}
        
        for battery in self.batteries:
            if not battery.enabled:
                logger.debug(f"⏭️  Skipping disabled battery: {battery.name}")
                continue
                
            logger.info(f"📤 Reading {battery.name} (Port: {battery.port}, Address: {battery.address})")
            
            try:
                data = self._read_single_battery(battery)
                if data:
                    results[battery.name] = data
                    successful_reads += 1
                    
                    # Enhanced logging with more details
                    soc = data.get('soc_percent', 0)
                    voltage = data.get('pack_voltage_v', 0)
                    current = data.get('pack_current_a', 0)
                    power = data.get('power_w', 0)
                    temp = data.get('temperature_1_c', 0)
                    status = data.get('status', 'unknown')
                    
                    logger.info(f"✅ {battery.name}: SOC {soc:.1f}%, "
                              f"Voltage {voltage:.2f}V, Current {current:.2f}A, "
                              f"Power {power:.1f}W, Temp {temp:.1f}°C, Status: {status}")
                    
                    # Add to virtual battery
                    if self.virtual_battery:
                        self.virtual_battery.add_battery_data(battery.name, data)
                else:
                    failed_reads += 1
                    logger.warning(f"❌ No data received from {battery.name}")
                    
            except Exception as e:
                failed_reads += 1
                logger.error(f"❌ Error reading {battery.name}: {e}")
                continue
        
        # Summary logging
        logger.info("📊 ===== READING SUMMARY =====")
        logger.info(f"✅ Successful reads: {successful_reads}/{len(enabled_batteries)}")
        if failed_reads > 0:
            logger.warning(f"❌ Failed reads: {failed_reads}")
        logger.info("🔋 ===========================")
        
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
                # Convert bytes to clean hex payload: between '~' and first '\r'
                if isinstance(device_info, bytes):
                    resp = device_info
                    start = resp.find(b'~')
                    if start == -1:
                        start = 0
                    end = resp.find(b'\r', start + 1)
                    if end == -1:
                        end = len(resp)
                    payload = resp[start + 1:end] if start < end else resp[:end]
                    ascii_hex = payload.decode('ascii', errors='ignore')
                    # keep only hex digits
                    hex_data = ''.join(ch for ch in ascii_hex if ch in '0123456789abcdefABCDEF').upper()
                else:
                    # assume already hex string
                    hex_data = str(device_info)
                    
                parsed_data = self.parser.parse_service_42_response(hex_data)
                
                # Add battery identification
                parsed_data['battery_name'] = battery.name
                parsed_data['battery_address'] = battery.address
                parsed_data['battery_port'] = battery.port
                
                # Enhance data with calculated values for MQTT compatibility
                self._enhance_battery_data(parsed_data)
                
                return parsed_data
            else:
                logger.warning(f"Invalid data length from {battery.name}")
                return None
                
        except Exception as e:
            logger.error(f"Error communicating with {battery.name}: {e}")
            return None
    
    def get_virtual_battery_data(self) -> Optional[Dict[str, Any]]:
        """Get aggregated virtual battery data with detailed logging"""
        if not self.virtual_battery:
            return None
            
        aggregated = self.virtual_battery.get_aggregated_data()
        if aggregated:
            aggregated['device_name'] = self.virtual_battery.name
            aggregated['is_virtual'] = True

            # Sum per-battery energy counters to avoid topology assumptions
            try:
                e_in = 0.0
                e_out = 0.0
                for bname, bdata in self.virtual_battery.batteries_data.items():
                    e_in += float(bdata.get('energy_in_kwh', 0.0))
                    e_out += float(bdata.get('energy_out_kwh', 0.0))
                aggregated['energy_in_kwh'] = e_in
                aggregated['energy_out_kwh'] = e_out
            except Exception:
                aggregated['energy_in_kwh'] = aggregated.get('energy_in_kwh', 0.0)
                aggregated['energy_out_kwh'] = aggregated.get('energy_out_kwh', 0.0)
            
            # Log virtual battery summary
            logger.info(f"🏦 Virtual Battery '{self.virtual_battery.name}':")
            logger.info(f"   📊 Aggregated from {aggregated.get('battery_count', 0)} batteries")
            logger.info(f"   🔋 SOC: {aggregated.get('soc_percent', 0):.1f}%")
            logger.info(f"   ⚡ Avg Voltage: {aggregated.get('avg_pack_voltage_v', 0):.2f}V (min {aggregated.get('pack_voltage_min_v', 0):.2f}V / max {aggregated.get('pack_voltage_max_v', 0):.2f}V, diff {aggregated.get('pack_voltage_diff_v', 0):.2f}V)")
            logger.info(f"   🌡️  Avg Temperature: {aggregated.get('temperature_1_c', 0):.1f}°C")
            
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
    
    def _log_battery_configuration(self):
        """Log detailed battery configuration on startup"""
        logger.info("🔋 ===== BATTERY CONFIGURATION =====")
        logger.info(f"📊 Total configured batteries: {len(self.batteries)}")
        logger.info(f"🔗 Virtual battery enabled: {'Yes' if self.enable_virtual else 'No'}")
        
        enabled_count = sum(1 for b in self.batteries if b.enabled)
        disabled_count = len(self.batteries) - enabled_count
        
        logger.info(f"✅ Enabled batteries: {enabled_count}")
        if disabled_count > 0:
            logger.info(f"❌ Disabled batteries: {disabled_count}")
        
        logger.info("📋 Battery Details:")
        for i, battery in enumerate(self.batteries, 1):
            status = "✅ ENABLED" if battery.enabled else "❌ DISABLED"
            logger.info(f"   {i}. {battery.name}")
            logger.info(f"      Port: {battery.port}")
            logger.info(f"      Address: {battery.address}")
            logger.info(f"      Status: {status}")
            logger.info(f"      Timeout: {battery.timeout}s")
            logger.info(f"      Baudrate: {battery.baudrate}")
        
        logger.info("🔋 =================================")
    
    def _enhance_battery_data(self, data: Dict[str, Any]) -> None:
        """Enhance parsed BMS data with calculated values for MQTT compatibility"""
        battery_name = data.get('battery_name', 'Unknown')
        
        # Calculate power (Voltage * Current)
        voltage = data.get('pack_voltage_v', 0)
        current = data.get('pack_current_a', 0)
        data['power_w'] = voltage * current
        
        # Map temperature data (BMS parser provides different temperature keys)
        temperature = None
        if 'ambient_temp_c' in data:
            temperature = data['ambient_temp_c']
        elif 'pack_avg_temp_c' in data:
            temperature = data['pack_avg_temp_c']
        elif 'mos_temp_c' in data:
            temperature = data['mos_temp_c']
        
        data['temperature_1_c'] = temperature if temperature is not None else 20.0
        
        # Map capacity fields to match MQTT expectations
        if 'full_charge_capacity_ah' in data:
            data['full_capacity_ah'] = data['full_charge_capacity_ah']
        
        # Calculate cell voltage statistics
        cell_voltages = data.get('cell_voltages_v', [])
        if cell_voltages and isinstance(cell_voltages, list) and len(cell_voltages) > 0:
            data['min_cell_voltage_v'] = min(cell_voltages)
            data['max_cell_voltage_v'] = max(cell_voltages)
            data['cell_voltage_diff_v'] = data['max_cell_voltage_v'] - data['min_cell_voltage_v']
        else:
            data['min_cell_voltage_v'] = 0.0
            data['max_cell_voltage_v'] = 0.0
            data['cell_voltage_diff_v'] = 0.0
        
        # Determine status based on current
        if current > 0.1:
            data['status'] = 'charging'
        elif current < -0.1:
            data['status'] = 'discharging'
        else:
            data['status'] = 'idle'

        # Integrate power into energy counters (kWh in/out)
        try:
            device_key = f"{self._base_device_id}_{battery_name.lower().replace(' ', '_')}"
            e_in, e_out = self._energy_tracker.update(device_key, data.get('power_w', 0.0), now_ts=time.time())
            data['energy_in_kwh'] = e_in
            data['energy_out_kwh'] = e_out
        except Exception:
            # Do not fail if persistence/integration has issues
            data.setdefault('energy_in_kwh', 0.0)
            data.setdefault('energy_out_kwh', 0.0)
        
        # Debug logging for troubleshooting
        logger.debug(f"📋 Enhanced data for {battery_name}:")
        logger.debug(f"   Power: {data.get('power_w', 'N/A'):.1f}W")
        logger.debug(f"   Temperature: {data.get('temperature_1_c', 'N/A'):.1f}°C")
        logger.debug(f"   Cell voltages: {len(cell_voltages)} cells")
        logger.debug(f"   Min/Max cell: {data.get('min_cell_voltage_v', 'N/A'):.3f}V / {data.get('max_cell_voltage_v', 'N/A'):.3f}V")
        logger.debug(f"   Status: {data.get('status', 'N/A')}")
