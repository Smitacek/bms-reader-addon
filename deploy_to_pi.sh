#!/bin/bash

# BMS Reader ARM Deployment Script pro Raspberry Pi
# Tento script nahraje a spustí BMS Reader na Raspberry Pi

set -e

echo "🚀 BMS Reader ARM Deployment pro Raspberry Pi"
echo "=============================================="

# Konfigurace
IMAGE_FILE="bms-reader-arm-1.0.0.tar.gz"
IMAGE_NAME="bms-reader-arm:1.0.0"
CONTAINER_NAME="bms-reader"
PI_USER=${PI_USER:-"pi"}
PI_HOST=${PI_HOST:-"pi.local"}

# SSH konfigurace
SSH_OPTS="-o ConnectTimeout=10 -o StrictHostKeyChecking=no"

# Kontrola existence image souboru
if [ ! -f "$IMAGE_FILE" ]; then
    echo "❌ Chyba: $IMAGE_FILE nenalezen!"
    echo "💡 Spusťte nejdříve: ./build_arm_quick.sh"
    exit 1
fi

echo "📦 Nalezen image: $IMAGE_FILE ($(du -h $IMAGE_FILE | cut -f1))"

# Test SSH připojení
echo "🔍 Testování SSH připojení k ${PI_USER}@${PI_HOST}..."
if ! ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "echo 'SSH OK'" 2>/dev/null; then
    echo "❌ SSH připojení selhalo!"
    echo ""
    echo "🔧 Troubleshooting kroky:"
    echo "1. Zkontrolujte, že Raspberry Pi je zapnuté a připojené k síti"
    echo "2. Zkuste ping: ping ${PI_HOST}"
    echo "3. Zkuste jiný hostname: export PI_HOST=raspberrypi.local"
    echo "4. Nebo použijte IP adresu: export PI_HOST=192.168.1.XXX"
    echo "5. Zkontrolujte SSH na Pi: sudo systemctl status ssh"
    echo ""
    echo "💡 Alternativní způsoby nasazení:"
    echo "   Manual copy: Zkopírujte ${IMAGE_FILE} ručně na Pi přes USB/síť"
    echo "   Local build: Spusťte build přímo na Pi pomocí addon/build_arm_quick.sh"
    exit 1
fi

echo "✅ SSH připojení funguje"

# Upload na Raspberry Pi
echo "📤 Uploading image na Raspberry Pi..."
echo "💡 Tip: Může trvat několik minut (117MB soubor)"

# Pokus o SCP s rsync jako fallback
if scp $SSH_OPTS "$IMAGE_FILE" "${PI_USER}@${PI_HOST}:~/"; then
    echo "✅ Image úspěšně nahrán přes SCP"
elif command -v rsync >/dev/null && rsync -avz -e "ssh $SSH_OPTS" "$IMAGE_FILE" "${PI_USER}@${PI_HOST}:~/"; then
    echo "✅ Image úspěšně nahrán přes rsync"
else
    echo "❌ Upload selhal!"
    echo ""
    echo "🔧 Alternativní řešení:"
    echo "1. Manual copy přes USB:"
    echo "   cp ${IMAGE_FILE} /Volumes/USB_DISK/"
    echo "   # Pak na Pi: docker load < ${IMAGE_FILE}"
    echo ""
    echo "2. HTTP server (na Mac):"
    echo "   python3 -m http.server 8000"
    echo "   # Na Pi: wget http://YOUR_MAC_IP:8000/${IMAGE_FILE}"
    echo ""
    echo "3. Build přímo na Pi:"
    echo "   scp -r addon/ ${PI_USER}@${PI_HOST}:~/"
    echo "   ssh ${PI_USER}@${PI_HOST} 'cd addon && ./build_arm_quick.sh'"
    exit 1
fi

# Remote deployment na Raspberry Pi
echo "🔧 Spouštím deployment na Raspberry Pi..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" << 'EOF'
    set -e
    
    echo "🐳 Loading Docker image..."
    if ! docker load < bms-reader-arm-1.0.0.tar.gz; then
        echo "❌ Chyba při načítání Docker image!"
        exit 1
    fi
    
    echo "🛑 Zastavuji stávající kontejner (pokud existuje)..."
    docker stop bms-reader 2>/dev/null || true
    docker rm bms-reader 2>/dev/null || true
    
    echo "🚀 Spouštím nový kontejner..."
    docker run -d \
        --name bms-reader \
        --restart unless-stopped \
        --privileged \
        -v /dev:/dev \
        -e BMS_PORT=${BMS_PORT:-"/dev/ttyUSB0"} \
        -e MQTT_HOST=${MQTT_HOST:-"homeassistant.local"} \
        -e MQTT_PORT=${MQTT_PORT:-"1883"} \
        -e MQTT_USER=${MQTT_USER:-""} \
        -e MQTT_PASSWORD=${MQTT_PASSWORD:-""} \
        bms-reader-arm:1.0.0
    
    echo "📊 Status kontejneru:"
    docker ps | grep bms-reader || echo "❌ Kontejner neběží!"
    
    echo "📝 Logs (posledních 10 řádků):"
    docker logs --tail 10 bms-reader
    
    echo "🧹 Úklid..."
    rm -f bms-reader-arm-1.0.0.tar.gz
    
    echo "✅ Deployment dokončen!"
    echo "💡 Pro sledování logů: docker logs -f bms-reader"
    echo "💡 Pro restart: docker restart bms-reader"
    echo "💡 Pro stop: docker stop bms-reader"
EOF

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
