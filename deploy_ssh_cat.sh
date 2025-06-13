#!/bin/bash

# BMS Reader SSH-CAT Deployment Script
# Alternativní deployment přes SSH s cat místo SCP

set -e

echo "🔧 BMS Reader SSH-CAT Deployment"
echo "================================"

# Konfigurace
IMAGE_FILE="bms-reader-arm-1.0.0.tar.gz"
PI_USER=${PI_USER:-"pi"}
PI_HOST=${PI_HOST:-"pi.local"}
SSH_OPTS="-o ConnectTimeout=10 -o StrictHostKeyChecking=no"

# Kontrola existence image souboru
if [ ! -f "$IMAGE_FILE" ]; then
    echo "❌ Chyba: $IMAGE_FILE nenalezen!"
    echo "💡 Spusťte nejdříve: ./addon/build_arm_quick.sh"
    exit 1
fi

echo "📦 Nalezen image: $IMAGE_FILE ($(du -h $IMAGE_FILE | cut -f1))"

# Test SSH připojení
echo "🔍 Testování SSH připojení..."
if ! ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "echo 'SSH OK'" 2>/dev/null; then
    echo "❌ SSH připojení selhalo!"
    echo "💡 Spusťte nejdříve: ./ssh_diagnostic.sh"
    exit 1
fi

echo "✅ SSH připojení funguje"

# Upload přes SSH cat (alternative to SCP)
echo "📤 Uploading image přes SSH cat..."
echo "💡 Tip: Může trvat několik minut (117MB soubor)"

if cat "$IMAGE_FILE" | ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "cat > $IMAGE_FILE"; then
    echo "✅ Image úspěšně nahrán přes SSH cat"
else
    echo "❌ Upload selhal!"
    echo "💡 Zkuste HTTP deployment: ./deploy_http.sh"
    exit 1
fi

# Remote deployment na Raspberry Pi
echo "🔧 Spouštím deployment na Raspberry Pi..."

# Rozdělíme deployment na menší části kvůli stabilitě SSH
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
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker stop bms-reader 2>/dev/null || true; sudo docker rm bms-reader 2>/dev/null || true"

echo "🚀 Spouštím nový kontejner..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker run -d \
    --name bms-reader \
    --restart unless-stopped \
    --privileged \
    -v /dev:/dev \
    -e BMS_PORT=\"\${BMS_PORT:-/dev/ttyUSB0}\" \
    -e MQTT_HOST=\"\${MQTT_HOST:-homeassistant.local}\" \
    -e MQTT_PORT=\"\${MQTT_PORT:-1883}\" \
    -e MQTT_USER=\"\${MQTT_USER:-}\" \
    -e MQTT_PASSWORD=\"\${MQTT_PASSWORD:-}\" \
    bms-reader-arm:1.0.0"

echo "📊 Kontrola běhu kontejneru..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker ps | grep bms-reader || echo '❌ Kontejner neběží!'"

echo "📝 Zobrazení logů..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker logs --tail 10 bms-reader"

echo "🧹 Úklid souborů..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "rm -f $IMAGE_FILE"

echo "✅ Deployment dokončen!"

echo ""
echo "🎉 BMS Reader úspěšně nasazen na Raspberry Pi!"
echo ""
echo "📋 Užitečné příkazy:"
echo "   ssh ${PI_USER}@${PI_HOST} 'docker logs -f bms-reader'  # Sledování logů"
echo "   ssh ${PI_USER}@${PI_HOST} 'docker restart bms-reader'   # Restart služby"
echo "   ssh ${PI_USER}@${PI_HOST} 'docker stats bms-reader'     # Monitoring systému"
echo ""
echo "🏠 Home Assistant integrace:"
echo "   - Automaticky objeveno pomocí MQTT auto-discovery"
echo "   - Zkontrolujte Configuration > Integrations"
echo "   - Entita: sensor.bms_*"
