#!/bin/bash

# BMS Reader Standalone Deployment Script
# Deployment standalone Docker kontejneru na Raspberry Pi

set -e

echo "🔧 BMS Reader Standalone Deployment"
echo "==================================="

# Konfigurace
IMAGE_FILE="bms-reader-standalone-1.0.4.tar.gz"
PI_USER=${PI_USER:-"pi"}
PI_HOST=${PI_HOST:-"pi.local"}
SSH_OPTS="-o ConnectTimeout=10 -o StrictHostKeyChecking=no"

# Kontrola existence image souboru
if [ ! -f "$IMAGE_FILE" ]; then
    echo "❌ Chyba: $IMAGE_FILE nenalezen!"
    echo "💡 Spusťte nejdříve: ./build_standalone.sh"
    exit 1
fi

echo "📦 Nalezen image: $IMAGE_FILE ($(du -h $IMAGE_FILE | cut -f1))"

# Test SSH připojení s retry
echo "🔍 Testování SSH připojení..."
retry_count=0
max_retries=3

while [ $retry_count -lt $max_retries ]; do
    if ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "echo 'SSH OK'" 2>/dev/null; then
        echo "✅ SSH připojení funguje"
        break
    else
        retry_count=$((retry_count + 1))
        echo "❌ SSH připojení selhalo (pokus $retry_count/$max_retries)"
        if [ $retry_count -eq $max_retries ]; then
            echo "💡 Spusťte nejdříve: ./ssh_diagnostic.sh"
            exit 1
        fi
        sleep 2
    fi
done

# Upload přes SSH cat
echo "📤 Uploading standalone image přes SSH cat..."
echo "💡 Tip: Může trvat několik minut (236MB soubor)"

if cat "$IMAGE_FILE" | ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "cat > $IMAGE_FILE"; then
    echo "✅ Image úspěšně nahrán přes SSH cat"
else
    echo "❌ Upload selhal!"
    echo "💡 Zkuste jiný deployment method"
    exit 1
fi

# Remote deployment na Raspberry Pi
echo "🔧 Spouštím deployment na Raspberry Pi..."

echo "📊 Kontrola nahraného souboru..."
if ! ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "ls -lh $IMAGE_FILE"; then
    echo "❌ Image soubor nenalezen na Pi!"
    exit 1
fi

echo "✅ Image soubor je na Pi"

echo "🐳 Loading Docker image..."
if ! ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker load < $IMAGE_FILE"; then
    echo "❌ Chyba při načítání Docker image!"
    exit 1
fi

echo "✅ Docker image načten"

echo "🛑 Zastavuji stávající kontejner..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker stop bms-reader-standalone 2>/dev/null || true; sudo docker rm bms-reader-standalone 2>/dev/null || true"

echo "🚀 Spouštím nový standalone kontejner..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker run -d \
    --name bms-reader-standalone \
    --restart unless-stopped \
    --privileged \
    -v /dev:/dev \
    -e BMS_PORT=\"\${BMS_PORT:-/dev/ttyUSB0}\" \
    -e BMS_SLAVE_ID=\"\${BMS_SLAVE_ID:-1}\" \
    -e READ_INTERVAL=\"\${READ_INTERVAL:-30}\" \
    -e MQTT_HOST=\"\${MQTT_HOST:-homeassistant.local}\" \
    -e MQTT_PORT=\"\${MQTT_PORT:-1883}\" \
    -e MQTT_USER=\"\${MQTT_USER:-}\" \
    -e MQTT_PASSWORD=\"\${MQTT_PASSWORD:-}\" \
    -e MQTT_TOPIC_PREFIX=\"\${MQTT_TOPIC_PREFIX:-homeassistant}\" \
    -e DEBUG_MODE=\"\${DEBUG_MODE:-false}\" \
    bms-reader-standalone:1.0.4"

echo "📊 Kontrola běhu kontejneru..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker ps | grep bms-reader-standalone || echo '❌ Kontejner neběží!'"

echo "📝 Zobrazení logů..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker logs --tail 20 bms-reader-standalone"

echo "🧹 Úklid souborů..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "rm -f $IMAGE_FILE"

echo "✅ Deployment dokončen!"

echo ""
echo "🎉 BMS Reader Standalone úspěšně nasazen na Raspberry Pi!"
echo ""
echo "📋 Užitečné příkazy:"
echo "   ssh ${PI_USER}@${PI_HOST} 'sudo docker logs -f bms-reader-standalone'  # Sledování logů"
echo "   ssh ${PI_USER}@${PI_HOST} 'sudo docker restart bms-reader-standalone'   # Restart služby"
echo "   ssh ${PI_USER}@${PI_HOST} 'sudo docker stats bms-reader-standalone'     # Monitoring systému"
echo "   ssh ${PI_USER}@${PI_HOST} 'sudo docker exec -it bms-reader-standalone /bin/bash'  # Debug shell"
echo ""
echo "🏠 Home Assistant integrace:"
echo "   - Automaticky objeveno pomocí MQTT auto-discovery"
echo "   - Zkontrolujte Configuration > Integrations"
echo "   - Entita: sensor.bms_*"
echo ""
echo "🔧 Environment variables pro customizaci:"
echo "   export BMS_PORT=/dev/ttyUSB0"
echo "   export MQTT_HOST=homeassistant.local"
echo "   export DEBUG_MODE=true"
