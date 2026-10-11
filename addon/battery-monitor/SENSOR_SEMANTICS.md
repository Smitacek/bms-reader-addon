# Home Assistant sensor semantics and upgrade (1.2.3)

Each configured pack is a physical MQTT device, identified by its stable configured name under `bms_multi_battery_<name>`. Names must be unique after lowercasing/replacing spaces. Keep configured names stable; USB by-id paths identify adapters, not battery serial numbers. A future configuration for multiple independent installations needs an installation identifier before sharing one broker. This release does not invent a hardware serial number from the USB adapter.

The bank is a distinct logical device (`bms_multi_battery_virtual`), not another physical battery. Discovery now uses entity-only names ("State of charge", "Pack voltage", "Pack current", "Ambient temperature") under their device name. It uses current `default_entity_id` discovery instead of the obsolete `object_id` option, with the same suggested entity IDs. Minimum HA Core 2025.10.0; existing registered IDs/custom names remain managed by HA. MQTT handles entity names; do not send an unsupported `has_entity_name` discovery key.

| Measurement | Unit | device_class | state_class | Meaning |
| --- | --- | --- | --- | --- |
| State of charge | % | battery | measurement | BMS-reported SoC, not relative humidity |
| Pack/cell/mean pack voltage | V | voltage | measurement | Physical pack and cell voltages; bank shows mean/min/max/difference, not sum |
| Pack current | A | current | measurement | Signed BMS current, positive charging / negative discharging by current convention |
| Battery power | W | power | measurement | Pack voltage times signed current; same sign convention |
| Ambient/mean ambient temperature | °C | temperature | measurement | Ambient probe in physical pack; arithmetic mean for full bank |
| Remaining/full charge capacity | Ah | none | measurement | Electric charge capacity (Ah has no appropriate supported HA battery/energy class) |
| Charging/discharging energy total | kWh | energy | total_increasing | Separate nonnegative integrals of power, persisted in /data/bms_energy_counters.json |
| Operating status/contributing batteries | none | none | none | Text, not a numeric measurement |
| Last successful read | ISO8601 UTC | timestamp | none | Diagnostic |
| Data age | s | duration | none | Diagnostic, monotonic elapsed time |
| Read errors/consecutive errors/counts | none | none | none | Diagnostics; error counts reset on process restart |

SoC uses `sum(SoC_i * full_charge_capacity_ah_i) / sum(full_charge_capacity_ah_i)` for every enabled pack in the same successful cycle. This represents capacity-weighted reported pack charge fraction; it is not claimed to be usable bank energy or limiting series-pack SoC. Unknown topology means no aggregate current, summed voltage, summed Ah or power sensor. Missing/zero/invalid capacities make the bank unavailable; no unweighted fallback.

Every ordinary sensor has both process LWT and per-device availability with `availability_mode: all`, and `expire_after` as a fail-safe if the monitoring loop stops. State messages are non-retained (QoS1), discovery and availability are retained. An incomplete cycle immediately marks the bank offline and publishes no bank measurements; a missing pack is online only until its last success reaches the timeout. No missing measurement or error is published as zero. Diagnostic entities have `entity_category: diagnostic`, use process availability only, and continue reporting age/errors during a pack outage.

New optional `stale_timeout` defaults to 60 seconds. Effective timeout is `max(stale_timeout, read_interval + 5 * enabled_pack_count)` for serial/reconnect headroom; at the current 10-second interval with two packs it is 60 seconds. If polling takes longer than that or a device path disappears, sensor `expire_after` independently expires old states. Bank availability stays stricter than pack availability.

Energy totals never decrease intentionally. They survive normal restarts; deleting the persistence file or manually resetting it restarts counters and HA recognizes a total_increasing reset. The first sample after restart or failed serial read establishes a baseline and does not integrate an unobserved interval. These are estimated energy counters, not calibrated BMS metering; polarity of nonzero current still requires physical confirmation. Energy dashboard supports the energy counters, not SoC or Ah capacity.

## Migration and verification

Existing physical/bank identifiers, unique IDs and discovery topics are semantically suitable for this installation and remain stable. Existing discovery configs are replaced in place; entity-only names change friendly names without deliberately renaming entity_id or deleting history. Recorder/statistics units and state classes of existing numeric sensors remain unchanged. A new full charge capacity sensor and diagnostic sensors are added. Verify actual registered names and IDs, dashboards and automations after update because user customization may override a default friendly name.

1. Back up HA, add-on options, and `/data/bms_energy_counters.json`. Do not dump MQTT credentials.
2. Refresh the original repository, select 1.2.3, let Supervisor build for the host architecture, then update/start in the coordinated maintenance window.
3. Compare `/app/*.py` SHA256 to the release checkout, confirm MQTT discovery accepted without deprecated `object_id` or duplicated names, and check units/classes/diagnostic category against the table.
4. Inventory retained discovery topics before deleting anything. Versions before 1.2.1 may have `homeassistant/sensor/bms_multi_battery_virtual/{pack_voltage,pack_current,power,remaining_capacity}/config`. These topology-dependent definitions are obsolete. This release does not publish their state or blindly delete them. If present, first inventory registered IDs, dashboard/automation references and historical statistics; export the configs and retire the entities in a separate migration. Never relabel old summed-voltage history as mean-voltage history, or delete statistics to silence a conflict.
5. Check Developer Tools → Statistics for unit/state-class conflicts and Recorder exclusions. `measurement` qualifies supported numeric sensors for long-term statistics; timestamps/text/diagnostic counters deliberately have no long-term statistical class. No recorder/database migration is performed by this release.
6. Test a pack read failure in a controlled maintenance window: no bank SoC/energy state publishes during partial cycles, bank unavailable immediately, pack unavailable after 60s at current polling, diagnostic age/error counts increase; recovery requires an entire successful bank cycle. Verify MQTT broker/HA reload recovery and restart counter continuity.

Sources checked 2026-10-11: [MQTT Sensor](https://www.home-assistant.io/integrations/sensor.mqtt/), [Sensor](https://www.home-assistant.io/integrations/sensor/), [Sensor entity developer guide](https://developers.home-assistant.io/docs/core/entity/sensor/), [App configuration](https://developers.home-assistant.io/docs/apps/configuration/). Protocol field layout compared with the [Daren RS485 research](https://github.com/cpttinkering/daren-485); signed current scaling remains unchanged.
