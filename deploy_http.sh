#!/bin/bash

# BMS Reader HTTP Deployment Script
# Alternativní deployment přes HTTP server pro případy, kdy SCP nefunguje

set -e

echo "📡 BMS Reader HTTP Deployment"
echo "============================="

# Konfigurace
IMAGE_FILE="bms-reader-arm-1.0.0.tar.gz"
PI_USER=${PI_USER:-"pi"}
PI_HOST=${PI_HOST:-"pi.local"}
HTTP_PORT=${HTTP_PORT:-"8000"}
SSH_OPTS="-o ConnectTimeout=10 -o StrictHostKeyChecking=no"

# Kontrola existence image souboru
if [ ! -f "$IMAGE_FILE" ]; then
    echo "❌ Chyba: $IMAGE_FILE nenalezen!"
    echo "💡 Spusťte nejdříve: ./addon/build_arm_quick.sh"
    exit 1
fi

echo "📦 Nalezen image: $IMAGE_FILE ($(du -h $IMAGE_FILE | cut -f1))"

# Získání lokální IP adresy
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)
if [ -z "$LOCAL_IP" ]; then
    echo "❌ Nelze zjistit lokální IP adresu!"
    exit 1
fi

echo "🌐 Lokální IP adresa: $LOCAL_IP"

# Test SSH připojení
echo "🔍 Testování SSH připojení..."
if ! ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "echo 'SSH OK'" 2>/dev/null; then
    echo "❌ SSH připojení selhalo!"
    echo "💡 Spusťte nejdříve: ./ssh_diagnostic.sh"
    exit 1
fi

echo "✅ SSH připojení funguje"

# Spuštění HTTP serveru
echo "🚀 Spouštím HTTP server na portu $HTTP_PORT..."
echo "💡 Server bude dostupný na: http://$LOCAL_IP:$HTTP_PORT/"

# Spuštění serveru na pozadí
python3 -m http.server $HTTP_PORT 2>/dev/null &
HTTP_PID=$!

# Čekání na spuštění serveru
sleep 2

# Kontrola, že server běží
if ! kill -0 $HTTP_PID 2>/dev/null; then
    echo "❌ HTTP server se nepodařilo spustit!"
    exit 1
fi

echo "✅ HTTP server běží (PID: $HTTP_PID)"

# Remote deployment na Raspberry Pi
echo "📤 Stahování image na Raspberry Pi..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" << EOF
    set -e
    
    echo "📥 Stahování image z HTTP serveru..."
    if ! wget -q --show-progress "http://$LOCAL_IP:$HTTP_PORT/$IMAGE_FILE" -O "$IMAGE_FILE"; then
        echo "❌ Stahování selhalo!"
        exit 1
    fi
    
    echo "✅ Image stažen úspěšně"
    echo "📊 Velikost: \$(du -h $IMAGE_FILE | cut -f1)"
    
    echo "🐳 Loading Docker image..."
    if ! docker load < $IMAGE_FILE; then
        echo "❌ Chyba při načítání Docker image!"
        exit 1
    fi
    
    echo "🛑 Zastavuji stávající kontejner (pokud existuje)..."
    docker stop bms-reader 2>/dev/null || true
    docker rm bms-reader 2>/dev/null || true
    
    echo "🚀 Spouštím nový kontejner..."
    docker run -d \\
        --name bms-reader \\
        --restart unless-stopped \\
        --privileged \\
        -v /dev:/dev \\
        -e BMS_PORT=\${BMS_PORT:-"/dev/ttyUSB0"} \\
        -e MQTT_HOST=\${MQTT_HOST:-"homeassistant.local"} \\
        -e MQTT_PORT=\${MQTT_PORT:-"1883"} \\
        -e MQTT_USER=\${MQTT_USER:-""} \\
        -e MQTT_PASSWORD=\${MQTT_PASSWORD:-""} \\
        bms-reader-arm:1.0.0
    
    echo "📊 Status kontejneru:"
    docker ps | grep bms-reader || echo "❌ Kontejner neběží!"
    
    echo "📝 Logs (posledních 10 řádků):"
    docker logs --tail 10 bms-reader
    
    echo "🧹 Úklid..."
    rm -f $IMAGE_FILE
    
    echo "✅ Deployment dokončen!"
EOF

# Zastavení HTTP serveru
echo "🛑 Zastavuji HTTP server..."
kill $HTTP_PID 2>/dev/null || true

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
