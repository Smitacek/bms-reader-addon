#!/usr/bin/with-contenv bashio

# Wait for services
bashio::log.info "Waiting for services..."
bashio::services.wait "mqtt"

# Show configuration
bashio::log.info "Starting BMS Reader..."
bashio::log.info "BMS Port: $(bashio::config 'bms.port')"
bashio::log.info "MQTT Host: $(bashio::config 'mqtt.host')"
bashio::log.info "Device ID: $(bashio::config 'device.id')"

# Start the application
cd /app
exec python3 main.py
