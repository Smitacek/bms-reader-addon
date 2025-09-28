#!/usr/bin/with-contenv bashio

# Function to safely get config value with fallback to environment
get_config_value() {
    local key=$1
    local env_var=$2
    local default=$3
    
    # Try to get from HA Add-on options first
    local value
    if command -v bashio::config &> /dev/null; then
        value=$(bashio::config "$key" 2>/dev/null || echo "")
    fi
    
    # If not available, use environment variable
    if [ -z "$value" ]; then
        value=${!env_var:-$default}
    fi
    
    echo "$value"
}

# Diagnostika mode
if [ "$1" = "diag" ] || [ "$1" = "diagnostics" ]; then
    echo "🔍 Spouštění diagnostiky..."
    cd /app
    python3 diagnostics.py
    exit 0
fi

# Wait for MQTT service if running in HA Add-on environment
if command -v bashio::services.wait &> /dev/null; then
    bashio::log.info "Waiting for MQTT service..."
    bashio::services.wait "mqtt" || true
fi

# Get configuration values with fallbacks
BMS_PORT=$(get_config_value 'bms.port' 'BMS_PORT' '/dev/ttyUSB0')
MQTT_HOST=$(get_config_value 'mqtt.host' 'MQTT_HOST' 'core-mosquitto')
DEVICE_ID=$(get_config_value 'device.id' 'DEVICE_ID' 'bms_lifepo4_01')
LOG_LEVEL=$(get_config_value 'log_level' 'LOG_LEVEL' 'WARNING' )

# Show configuration only for INFO/DEBUG levels to reduce noise
if [[ "$LOG_LEVEL" =~ ^(DEBUG|INFO)$ ]]; then
    if command -v bashio::log.info &> /dev/null; then
        bashio::log.info "Starting BMS Reader v1.1.9..."
        bashio::log.info "BMS Port: $BMS_PORT"
        bashio::log.info "MQTT Host: $MQTT_HOST"
        bashio::log.info "Device ID: $DEVICE_ID"
        bashio::log.info "Log Level: $LOG_LEVEL"
    else
        echo "Starting BMS Reader v1.1.9..."
        echo "BMS Port: $BMS_PORT"
        echo "MQTT Host: $MQTT_HOST"
        echo "Device ID: $DEVICE_ID"
        echo "Log Level: $LOG_LEVEL"
    fi
fi

# Start the application
cd /app
exec python3 main.py
