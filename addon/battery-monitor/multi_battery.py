#!/usr/bin/env python3
"""
Multi-Battery Manager for aggregating data from multiple BMS units
"""

import logging
import time
import math
import re
from datetime import datetime, timezone
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
        capacities = [d.get('full_charge_capacity_ah') for d in all_data]
        socs = [d.get('soc_percent') for d in all_data]
        if any(not isinstance(c, (int, float)) or not math.isfinite(c) or c <= 0 for c in capacities):
            logger.warning("Bank unavailable: missing or invalid full charge capacity")
            return {}
        if any(not isinstance(s, (int, float)) or not math.isfinite(s) or not 0 <= s <= 100 for s in socs):
            return {}
        weighted_soc = sum(s * c for s, c in zip(socs, capacities)) / sum(capacities)

        aggregated = {
            # Capacity-weighted BMS SoC; no series/parallel inference.
            'soc_percent': weighted_soc,

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
        self.stale_timeout = cfg.stale_timeout
        self._health = {b.name: {'last_success': None, 'last_success_monotonic': None,
                                'error_count': 0, 'consecutive_errors': 0}
                        for b in batteries if b.enabled}
        if len(self._health) != sum(b.enabled for b in batteries) or len({b.name.lower().replace(" ", "_") for b in batteries if b.enabled}) != len(self._health):
            raise ValueError("Enabled battery names must be unique")
        for battery in batteries:
            if not battery.enabled:
                continue
            normalized = battery.name.lower().replace(' ', '_')
            if normalized in ('virtual', '_virtual_battery') or not re.fullmatch(r'[a-z0-9_-]+', normalized):
                raise ValueError("Battery name is reserved or invalid for MQTT discovery")
        self._bank_complete = False
        self._bank_last_success = None
        self._bank_last_success_monotonic = None
        self._bank_errors = 0
        self._bank_consecutive_errors = 0
        
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
        self._bank_complete = False

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
                    health = self._health[battery.name]
                    health['last_success_monotonic'] = time.monotonic()
                    health['last_success'] = datetime.now(timezone.utc).isoformat()
                    health['consecutive_errors'] = 0
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
                    self._record_failure(battery.name)
                    logger.warning(f"❌ No data received from {battery.name}")
                    
            except Exception as e:
                failed_reads += 1
                self._record_failure(battery.name)
                logger.error(f"❌ Error reading {battery.name}: {e}")
                continue
        
        # Summary logging
        logger.info("📊 ===== READING SUMMARY =====")
        logger.info(f"✅ Successful reads: {successful_reads}/{len(enabled_batteries)}")
        if failed_reads > 0:
            logger.warning(f"❌ Failed reads: {failed_reads}")
        logger.info("🔋 ===========================")
        
        return results

    def _record_failure(self, name):
        health = self._health[name]
        health['error_count'] += 1
        health['consecutive_errors'] += 1
        key = f"{self._base_device_id}_{name.lower().replace(' ', '_')}"
        self._energy_tracker.mark_gap(key)

    def get_diagnostics(self):
        now = time.monotonic()
        diagnostics = {}
        for name, health in self._health.items():
            last = health['last_success_monotonic']
            age = max(0.0, now - last) if last is not None else None
            diagnostics[name] = {k: v for k, v in health.items() if k != 'last_success_monotonic'}
            diagnostics[name].update(data_age_seconds=age, available=age is not None and age < self.stale_timeout)
        if self.virtual_battery:
            last = self._bank_last_success_monotonic
            diagnostics['_virtual_battery'] = {
                'available': self._bank_complete and all(d['available'] for d in diagnostics.values()),
                'last_success': self._bank_last_success,
                'data_age_seconds': max(0.0, now - last) if last is not None else None,
                'error_count': self._bank_errors,
                'consecutive_errors': self._bank_consecutive_errors,
                'expected_battery_count': len(self._health),
                'successful_battery_count': len(self.virtual_battery.batteries_data),
            }
        return diagnostics

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
                if not isinstance(device_info, bytes) or not device_info.startswith(b'~') or not device_info.endswith(b'\r'):
                    raise ValueError("Invalid BMS frame boundaries")
                hex_data = device_info[1:-1].decode('ascii')
                parsed_data = self.parser.parse_service_42_response(hex_data)
                if int(parsed_data['adr_hex'], 16) != battery.address:
                    raise ValueError("Response belongs to a different BMS address")

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
        if not self.virtual_battery or not self._health:
            return None
        if set(self.virtual_battery.batteries_data) != set(self._health):
            return None
        if not all(d['available'] for name, d in self.get_diagnostics().items() if name != '_virtual_battery'):
            return None
            
        aggregated = self.virtual_battery.get_aggregated_data()
        if aggregated:
            aggregated['device_name'] = self.virtual_battery.name
            aggregated['is_virtual'] = True

            # Missing counters are unknown, never a reset to zero.
            for key in ('energy_in_kwh', 'energy_out_kwh'):
                values = [d.get(key) for d in self.virtual_battery.batteries_data.values()]
                if all(isinstance(v, (int, float)) and math.isfinite(v) and v >= 0 for v in values):
                    aggregated[key] = sum(values)

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
                self._bank_complete = True
                self._bank_last_success = datetime.now(timezone.utc).isoformat()
                self._bank_last_success_monotonic = time.monotonic()
                self._bank_consecutive_errors = 0
            else:
                self._bank_errors += 1
                self._bank_consecutive_errors += 1
        
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
        
        if temperature is not None:
            data['temperature_1_c'] = temperature
        
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
            logger.warning('Energy counters unavailable; skipping energy publication')
        
        # Debug logging for troubleshooting
        logger.debug(f"📋 Enhanced data for {battery_name}:")
        logger.debug(f"   Power: {data.get('power_w', 'N/A'):.1f}W")
        logger.debug(f"   Temperature: {data.get('temperature_1_c', 'N/A'):.1f}°C")
        logger.debug(f"   Cell voltages: {len(cell_voltages)} cells")
        logger.debug(f"   Min/Max cell: {data.get('min_cell_voltage_v', 'N/A'):.3f}V / {data.get('max_cell_voltage_v', 'N/A'):.3f}V")
        logger.debug(f"   Status: {data.get('status', 'N/A')}")
