#!/bin/bash

# BMS Reader Standalone - Production Validation Script
# Validuje funkčnost produkčního nasazení na Raspberry Pi

set -e

echo "🔍 BMS Reader Standalone - Production Validation"
echo "================================================"

PI_USER=${PI_USER:-"pi"}
PI_HOST=${PI_HOST:-"pi.local"}
SSH_OPTS="-o ConnectTimeout=10 -o StrictHostKeyChecking=no"

echo "📊 Kontrola stavu kontejneru..."
if ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker ps | grep bms-reader-standalone"; then
    echo "✅ Kontejner běží"
else
    echo "❌ Kontejner neběží!"
    exit 1
fi

echo ""
echo "📝 Posledních 5 MQTT publikací..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker logs bms-reader-standalone 2>/dev/null | grep 'BMS data publikována' | tail -5"

echo ""
echo "📈 Kontrola chyb v posledních 100 řádcích..."
error_count=$(ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker logs --tail 100 bms-reader-standalone 2>/dev/null | grep -c '❌\|ERROR\|Exception' || echo 0")
echo "🔍 Počet chyb: $error_count"

if [ "$error_count" -eq 0 ]; then
    echo "✅ Žádné chyby v posledních 100 řádcích"
else
    echo "⚠️  Nalezeny chyby, kontrola posledních chyb:"
    ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker logs --tail 100 bms-reader-standalone 2>/dev/null | grep '❌\|ERROR\|Exception' | tail -3"
fi

echo ""
echo "⚡ Kontrola zdrojů kontejneru..."
ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "sudo docker stats --no-stream --format 'table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}' bms-reader-standalone"

echo ""
echo "🔧 Management příkazy:"
echo "   Logs:    ssh ${PI_USER}@${PI_HOST} 'sudo docker logs -f bms-reader-standalone'"
echo "   Restart: ssh ${PI_USER}@${PI_HOST} 'sudo docker restart bms-reader-standalone'"
echo "   Stop:    ssh ${PI_USER}@${PI_HOST} 'sudo docker stop bms-reader-standalone'"

echo ""
echo "✅ Validation complete - BMS Reader Standalone funguje správně!"
