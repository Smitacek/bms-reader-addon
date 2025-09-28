#!/usr/bin/env python3
"""
One-off discovery tool: scans available serial ports for Daren BMS devices
by trying Service 42 on a range of Modbus addresses. Emits a ready-to-copy
YAML snippet and stores it under /data/discovered_batteries.yaml.
"""

from __future__ import annotations

import glob
import json
import logging
import os
from typing import Dict, List, Tuple

from modbus import request_device_info
from bms_parser import BMSParser


logger = logging.getLogger(__name__)


def _list_candidate_ports(explicit_ports: List[str] | None = None) -> List[str]:
    if explicit_ports:
        return [p for p in explicit_ports if os.path.exists(p)]

    # Prefer stable /dev/serial/by-id first
    by_id = sorted(glob.glob("/dev/serial/by-id/*"))
    # Other common serial devices
    usb = sorted(glob.glob("/dev/ttyUSB*"))
    acm = sorted(glob.glob("/dev/ttyACM*"))
    ama = sorted(glob.glob("/dev/ttyAMA*"))

    # De-duplicate by real path; prefer by-id symlinks when available
    dedup: Dict[str, str] = {}
    for path in by_id + usb + acm + ama:
        if not os.path.exists(path):
            continue
        try:
            real = os.path.realpath(path)
        except Exception:
            real = path
        # Prefer first occurrence (by-id comes first)
        if real not in dedup:
            dedup[real] = path

    return list(dedup.values())


def _try_probe(port: str, address: int, timeout_s: float) -> Tuple[bool, Dict]:
    try:
        raw = request_device_info(port=port, address=address, baudrate=9600, timeout=timeout_s)
        if not raw or len(raw) < 3:
            return False, {}
        # Extract ASCII hex between '~' and first CR, keep only hex chars
        if isinstance(raw, (bytes, bytearray)):
            start = raw.find(b"~")
            if start == -1:
                start = 0
            end = raw.find(b"\r", start + 1)
            if end == -1:
                end = len(raw)
            payload = raw[start + 1 : end] if start < end else raw[:end]
            ascii_hex = payload.decode("ascii", errors="ignore")
        else:
            ascii_hex = str(raw)
        hex_data = "".join(ch for ch in ascii_hex if ch in "0123456789abcdefABCDEF").upper()
        if not hex_data:
            return False, {}
        parsed = BMSParser.parse_service_42_response(hex_data)
        return True, parsed
    except Exception:
        return False, {}


def run_discovery(options: Dict) -> Dict:
    """Run discovery and return summary with results list.

    Options expected keys:
      - discovery_ports: List[str]
      - discovery_address_from: int
      - discovery_address_to: int
      - discovery_timeout_ms: int
    """
    addr_from = int(options.get("discovery_address_from", 1))
    addr_to = int(options.get("discovery_address_to", 16))
    timeout_ms = int(options.get("discovery_timeout_ms", 300))
    ports = _list_candidate_ports(options.get("discovery_ports") or None)

    timeout_s = max(0.05, min(5.0, timeout_ms / 1000.0))
    if not ports:
        logger.warning("No serial ports found to scan.")
        ports = []

    logger.info("🔎 ===== BMS DISCOVERY START =====")
    logger.info(f"Ports: {len(ports)} | Address range: {addr_from}..{addr_to} | Timeout: {timeout_ms} ms")

    discovered: List[Dict] = []
    for port in ports:
        found_on_port = 0
        for addr in range(addr_from, addr_to + 1):
            ok, parsed = _try_probe(port, addr, timeout_s)
            if not ok:
                continue
            found_on_port += 1
            entry = {
                "port": port,
                "address": addr,
                # Suggest default name based on address
                "name": f"Battery_{addr}",
                "enabled": True,
            }
            discovered.append(entry)
        logger.info(f"Port {port}: {found_on_port} device(s)")

    total = len(discovered)
    logger.info(f"✅ Discovery complete: {total} device(s) found")

    # Build YAML snippet
    yaml_lines: List[str] = []
    yaml_lines.append("# === Battery Monitor Discovery (copy into options) ===")
    yaml_lines.append("multi_battery_mode: true")
    yaml_lines.append("batteries:")
    for d in discovered:
        yaml_lines.append(f"  - port: \"{d['port']}\"")
        yaml_lines.append(f"    address: {d['address']}")
        yaml_lines.append(f"    name: \"{d['name']}\"")
        yaml_lines.append(f"    enabled: true")
    yaml_lines.append("enable_virtual_battery: true")
    yaml_lines.append("# === End of generated block ===")
    yaml_text = "\n".join(yaml_lines)

    # Persist to /data
    out_path = "/data/discovered_batteries.yaml"
    try:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w") as f:
            f.write(yaml_text + "\n")
        logger.info(f"📝 Discovery YAML saved to: {out_path}")
    except Exception as e:
        logger.warning(f"Could not write discovery YAML: {e}")

    # Also store JSON summary for tooling
    try:
        json_path = "/data/discovered_batteries.json"
        with open(json_path, "w") as f:
            json.dump({"count": total, "results": discovered}, f)
        logger.info(f"📝 Discovery JSON saved to: {json_path}")
    except Exception:
        pass

    # Log a short YAML snippet preview
    preview = "\n".join(yaml_lines[: min(len(yaml_lines), 20)])
    logger.info("\n" + preview)

    return {"count": total, "results": discovered, "yaml_path": out_path}

