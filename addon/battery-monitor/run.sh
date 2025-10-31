#!/usr/bin/with-contenv bashio

set -euo pipefail

# Diagnostics mode
if [ "${1:-}" = "diag" ] || [ "${1:-}" = "diagnostics" ]; then
    bashio::log.info "🔍 Spouštění diagnostiky..."
    cd /app
    exec python3 diagnostics.py
fi

# Wait for MQTT service (when available in Supervisor)
if command -v bashio::services.wait &> /dev/null; then
    bashio::log.info "⏳ Čekám na MQTT službu (Supervisor Discovery)..."
    bashio::services.wait "mqtt" || true
fi

# Auto-discover MQTT credentials from Supervisor and export as env vars.
# Manual options in /data/options.json still override in Python if set.
if command -v bashio::services.available &> /dev/null && bashio::services.available "mqtt"; then
    MQTT_HOST_DISC=$(bashio::services "mqtt" "host" || echo "")
    MQTT_PORT_DISC=$(bashio::services "mqtt" "port" || echo "")
    MQTT_USER_DISC=$(bashio::services "mqtt" "username" || echo "")
    MQTT_PASS_DISC=$(bashio::services "mqtt" "password" || echo "")

    # Export only when values exist to keep env clean
    [ -n "${MQTT_HOST_DISC}" ] && export MQTT_HOST="${MQTT_HOST_DISC}"
    [ -n "${MQTT_PORT_DISC}" ] && export MQTT_PORT="${MQTT_PORT_DISC}"
    [ -n "${MQTT_USER_DISC}" ] && export MQTT_USERNAME="${MQTT_USER_DISC}"
    [ -n "${MQTT_PASS_DISC}" ] && export MQTT_PASSWORD="${MQTT_PASS_DISC}"

    bashio::log.info "📡 MQTT přihlašovací údaje získány ze Supervisoru (auto)."
else
    bashio::log.info "ℹ️ MQTT discovery není dostupné, použiji ruční nastavení (fallback)."
fi

# Start the application
cd /app
exec python3 main.py
