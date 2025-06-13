#!/bin/bash

# BMS Reader Smart Deployment Script
# Automaticky vybere nejlepší způsob deploymentu na Raspberry Pi

set -e

echo "🚀 BMS Reader Smart Deployment"
echo "=============================="

# Konfigurace
IMAGE_FILE="bms-reader-arm-1.0.0.tar.gz"
PI_USER=${PI_USER:-"pi"}
PI_HOST=${PI_HOST:-"pi.local"}
SSH_OPTS="-o ConnectTimeout=10 -o StrictHostKeyChecking=no"

echo "Target: ${PI_USER}@${PI_HOST}"
echo ""

# Kontrola existence image souboru
if [ ! -f "$IMAGE_FILE" ]; then
    echo "❌ Chyba: $IMAGE_FILE nenalezen!"
    echo "💡 Spusťte nejdříve: ./addon/build_arm_quick.sh"
    exit 1
fi

echo "📦 Image nalezen: $IMAGE_FILE ($(du -h $IMAGE_FILE | cut -f1))"

# Test SSH připojení
echo "🔍 Testování připojení..."
if ! ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "echo 'SSH OK'" 2>/dev/null; then
    echo "❌ SSH připojení selhalo!"
    echo ""
    echo "🔧 Možná řešení:"
    echo "1. Spusťte diagnostiku: ./ssh_diagnostic.sh"
    echo "2. Zkuste jiný hostname: export PI_HOST=raspberrypi.local"
    echo "3. Použijte IP adresu: export PI_HOST=192.168.1.XXX"
    exit 1
fi

echo "✅ SSH připojení funguje"

# Test SCP funkčnosti
echo "🔍 Testování SCP..."
echo "test" > /tmp/scp_test.txt
if scp $SSH_OPTS /tmp/scp_test.txt "${PI_USER}@${PI_HOST}:~/scp_test.txt" 2>/dev/null; then
    echo "✅ SCP funguje - použije se standardní deployment"
    rm -f /tmp/scp_test.txt
    ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "rm -f ~/scp_test.txt" 2>/dev/null
    
    echo ""
    echo "🚀 Spouštím standardní deployment..."
    exec ./deploy_to_pi.sh
else
    echo "❌ SCP nefunguje - použije se SSH cat alternativa"
    rm -f /tmp/scp_test.txt
    
    echo ""
    echo "🔧 Spouštím SSH-CAT deployment..."
    exec ./deploy_ssh_cat.sh
fi
