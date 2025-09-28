#!/usr/bin/env python3
"""
Energy tracking helper: integrates power (W) over time to kWh and
keeps separate cumulative counters for energy flowing into and out of
the battery. Values are persisted to a JSON file so they survive restarts.

Counters are designed for Home Assistant Energy Dashboard as
total_increasing sensors.
"""

from __future__ import annotations

import json
import os
import time
from threading import RLock
from typing import Dict, Tuple


DEFAULT_STORAGE_PATHS = [
    "/data/bms_energy_counters.json",  # HA Add-on persistent storage
    os.path.join(os.getcwd(), "bms_energy_counters.json"),  # fallback for dev
]


class EnergyTracker:
    """Tracks cumulative charge/discharge energy per device.

    - update(device_id, power_w) integrates using wall-clock delta time
    - maintains separate totals for energy_in_kwh (charging, power > 0)
      and energy_out_kwh (discharging, power < 0)
    - persists state to JSON periodically (every update is fine at 30s cadence)
    """

    def __init__(self, storage_path: str | None = None) -> None:
        self._storage_path = self._resolve_storage_path(storage_path)
        self._state: Dict[str, Dict[str, float]] = {}
        self._lock = RLock()
        self._load()

    def _resolve_storage_path(self, explicit: str | None) -> str:
        if explicit:
            return explicit
        # Prefer first writeable path
        for path in DEFAULT_STORAGE_PATHS:
            try:
                base_dir = os.path.dirname(path) or "."
                os.makedirs(base_dir, exist_ok=True)
                # If file exists or directory is writable, accept path
                if os.path.exists(path) or os.access(base_dir, os.W_OK):
                    return path
            except Exception:
                continue
        # Fallback to CWD
        return os.path.join(os.getcwd(), "bms_energy_counters.json")

    def _load(self) -> None:
        with self._lock:
            try:
                if os.path.exists(self._storage_path):
                    with open(self._storage_path, "r") as f:
                        data = json.load(f)
                        if isinstance(data, dict):
                            self._state = data
            except Exception:
                # Start fresh on any load error
                self._state = {}

    def _save(self) -> None:
        with self._lock:
            try:
                tmp = self._storage_path + ".tmp"
                with open(tmp, "w") as f:
                    json.dump(self._state, f)
                os.replace(tmp, self._storage_path)
            except Exception:
                # Ignore save errors to not break main loop
                pass

    def reset(self, device_id: str) -> None:
        with self._lock:
            self._state[device_id] = {
                "energy_in_kwh": 0.0,
                "energy_out_kwh": 0.0,
                "last_ts": time.time(),
            }
            self._save()

    def _ensure_device(self, device_id: str) -> None:
        if device_id not in self._state:
            self.reset(device_id)

    def update(self, device_id: str, power_w: float, now_ts: float | None = None) -> Tuple[float, float]:
        """Update counters for a device based on current power in watts.

        Returns a tuple (energy_in_kwh, energy_out_kwh) after the update.
        """
        with self._lock:
            self._ensure_device(device_id)

            entry = self._state[device_id]
            last_ts = float(entry.get("last_ts", 0.0))
            now = float(now_ts if now_ts is not None else time.time())

            # Guard against non-monotonic clocks
            dt = max(0.0, now - last_ts) if last_ts > 0 else 0.0

            # Integrate: W * s = Ws => Wh = Ws/3600 => kWh = Wh/1000
            if dt > 0 and isinstance(power_w, (int, float)):
                wh = (float(power_w) * dt) / 3600.0
                kwh = wh / 1000.0
                if kwh > 0:
                    entry["energy_in_kwh"] = float(entry.get("energy_in_kwh", 0.0)) + kwh
                elif kwh < 0:
                    entry["energy_out_kwh"] = float(entry.get("energy_out_kwh", 0.0)) + abs(kwh)

            entry["last_ts"] = now

            # Persist on every update (30s cadence by default)
            self._save()

            return float(entry.get("energy_in_kwh", 0.0)), float(entry.get("energy_out_kwh", 0.0))

