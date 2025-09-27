#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BMS Parser pro Daren BMS Service 42 response
"""

import json


class BMSParser:
    """Parser pro Service 42 (GetDeviceInfo) odpovědi z Daren BMS"""

    @staticmethod
    def _hex_to_int(hex_str: str) -> int:
        """Převod hex stringu na integer"""
        return int(hex_str, 16)

    @staticmethod
    def _hex_to_signed_int(hex_str: str, bits: int = 16) -> int:
        """Převod hex stringu na signed integer"""
        val = int(hex_str, 16)
        if bits == 16 and val & 0x8000:
            val -= 0x10000
        elif bits == 8 and val & 0x80:
            val -= 0x100
        return val

    @staticmethod
    def parse_service_42_response(hex_data_string: str) -> dict:
        """
        Parsuje Service 42 response a vrací dictionary.
        
        Args:
            hex_data_string: Hex string odpovědi (bez ~ a \r)
            
        Returns:
            Dictionary s parsovanými daty
        """
        if not isinstance(hex_data_string, str):
            raise TypeError("Vstup musí být hex string")

        data = {}
        ptr = 0

        # 1. Header and length
        data["ver_hex"] = hex_data_string[ptr:ptr+2]
        ptr += 2
        data["adr_hex"] = hex_data_string[ptr:ptr+2]
        ptr += 2
        data["cid1_hex"] = hex_data_string[ptr:ptr+2]
        ptr += 2
        data["rtn_code_hex"] = hex_data_string[ptr:ptr+2]
        ptr += 2  # Return code (00 = OK)

        length_field_hex = hex_data_string[ptr:ptr+4]
        ptr += 4
        # LSB 12 bits (3 hex characters) for INFO length in characters (nibbles)
        info_len_chars = BMSParser._hex_to_int(length_field_hex[1:])
        data["length_field"] = {
            "hex": length_field_hex,
            "info_len_chars": info_len_chars,
            "info_len_bytes": info_len_chars // 2,
            "len_checksum_nibble_hex": length_field_hex[0]
        }

        # Check total expected length
        # Length = header_without_len(8) + len(4) + info_len_chars + checksum(4)
        expected_total_len_chars = 8 + 4 + info_len_chars + 4
        if len(hex_data_string) != expected_total_len_chars:
            raise ValueError(
                f"Length mismatch. Header indicates INFO length (chars): {info_len_chars}. "
                f"Expected total length: {expected_total_len_chars}, Received: {len(hex_data_string)}"
            )

        # Extract INFO block and Checksum
        info_hex_block = hex_data_string[ptr : ptr + info_len_chars]
        ptr += info_len_chars
        data["checksum_hex"] = hex_data_string[ptr : ptr + 4] # Last 4 characters (2 bytes)

        # 2. Parse INFO block (99 bytes / 198 characters in example)
        info_ptr = 0 # Pointer within info_hex_block

        def read_from_info(num_chars):
            nonlocal info_ptr
            if info_ptr + num_chars > len(info_hex_block):
                raise ValueError(f"Attempt to read beyond INFO block boundaries: need {num_chars} from position {info_ptr} in block of length {len(info_hex_block)}")
            segment = info_hex_block[info_ptr : info_ptr + num_chars]
            info_ptr += num_chars
            return segment

        # DATAFLAG (1 byte)
        data["data_flag_hex"] = read_from_info(2)
        # TODO: Detailed parsing of DATAFLAG bits according to documentation

        # State of Charge (SOC) (2 bytes, /100)
        soc_hex = read_from_info(4)
        data["soc_percent"] = BMSParser._hex_to_int(soc_hex) / 100.0

        # Pack voltage (2 bytes, /100)
        pack_voltage_hex = read_from_info(4)
        data["pack_voltage_v"] = BMSParser._hex_to_int(pack_voltage_hex) / 100.0

        # Cell count (m) (1 byte)
        cell_count_hex = read_from_info(2)
        cell_count = BMSParser._hex_to_int(cell_count_hex)
        data["cell_count"] = cell_count

        # Cell voltages (m * 2 bytes, /1000)
        data["cell_voltages_v"] = []
        for i in range(cell_count):
            cv_hex = read_from_info(4)
            data["cell_voltages_v"].append(BMSParser._hex_to_int(cv_hex) / 1000.0)

        # Ambient temperature (ENV_TEMP) (2 bytes, signed, /10)
        data["ambient_temp_c"] = BMSParser._hex_to_signed_int(read_from_info(4)) / 10.0

        # Pack average temperature (pack_TEMP) (2 bytes, signed, /10)
        data["pack_avg_temp_c"] = BMSParser._hex_to_signed_int(read_from_info(4)) / 10.0

        # MOS temperature (MOS_TEMP) (2 bytes, signed, /10)
        data["mos_temp_c"] = BMSParser._hex_to_signed_int(read_from_info(4)) / 10.0

        # TOT_TEMPs (n) - number of cell temperature sensors (1 byte)
        tot_temps_hex = read_from_info(2)
        tot_temps = BMSParser._hex_to_int(tot_temps_hex)
        data["temp_sensor_count"] = tot_temps

        # Cell temperatures (n * 2 bytes, signed, /10)
        data["cell_temps_c"] = []
        for i in range(tot_temps):
            ct_hex = read_from_info(4)
            data["cell_temps_c"].append(BMSParser._hex_to_signed_int(ct_hex) / 10.0)

        # Pack current (2 bytes, signed, /100)
        pack_current_hex = read_from_info(4)
        data["pack_current_a"] = BMSParser._hex_to_signed_int(pack_current_hex) / 100.0

        # Pack Internal Resistance (pack_inter_RES) (2 bytes, /10)
        pack_ir_hex = read_from_info(4)
        data["pack_internal_resistance_mohm"] = BMSParser._hex_to_int(pack_ir_hex) / 10.0 # Assumption: mOhm

        # State of Health (SOH) (2 bytes)
        soh_hex = read_from_info(4)
        data["soh_percent"] = BMSParser._hex_to_int(soh_hex) # According to README without division

        # User-defined number (user_custom) (1 byte)
        user_custom_hex = read_from_info(2)
        data["user_defined_number"] = BMSParser._hex_to_int(user_custom_hex)

        # Full charge capacity in Ah (2 bajty, /100)
        full_cap_hex = read_from_info(4)
        data["full_charge_capacity_ah"] = BMSParser._hex_to_int(full_cap_hex) / 100.0

        # Remaining capacity in Ah (2 bajty, /100)
        rem_cap_hex = read_from_info(4)
        data["remaining_capacity_ah"] = BMSParser._hex_to_int(rem_cap_hex) / 100.0

        # Cycle count (2 bytes)
        cycle_count_hex = read_from_info(4)
        data["cycle_count"] = BMSParser._hex_to_int(cycle_count_hex)

        # Status bits (15 fields of 2 bytes each = 30 bytes)
        # For now as hex, detailed bit parsing would require more logic
        status_fields_description = [
            "voltage_status", "current_status", "temperature_status", "alarm_status", "fet_status",
            "overvoltage_protection_status_low", "undervolt_protection_status_low",
            "overvoltage_alarm_status_low", "undervolt_alarm_status_low",
            "cell_balance_state_low", "cell_balance_state_high",
            "overvoltage_protection_status_high", "undervolt_protection_status_high",
            "overvoltage_alarm_status_high", "undervolt_alarm_status_high" # These are according to *** in README
        ]
        data["status_flags_hex"] = {}
        for desc in status_fields_description:
            data["status_flags_hex"][desc] = read_from_info(4)

        # Machine status list (1 byte)
        data["machine_status_list_hex"] = read_from_info(2)
        # TODO: Detailed parsing of Machine status list bits according to documentation

        # IO status list (2 bytes)
        data["io_status_list_hex"] = read_from_info(4)
        # TODO: Detailed parsing of IO status list bits according to documentation

        if info_ptr != info_len_chars:
            raise ValueError(
                f"Error parsing INFO block. Expected {info_len_chars} characters, "
                f"read {info_ptr} characters."
            )

        return data


# Test function
if __name__ == "__main__":
    # Test with sample data
    test_hex = "22014A00E0C60118FE14BC100CF40CF40CF00CF20CF30CF60D020CF50CF50CFF0CF50CF40CF80CF90CFA0CF000E600C800D20400C800C800C800C800000000006400294A1A6B003F000000000000000000230000000000000000000000000000000000000000000000D3EF"
    
    print("=== BMS Parser Test ===")
    try:
        result = BMSParser.parse_service_42_response(test_hex)
        print("✅ Parsing successful!")
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"❌ Error: {e}")