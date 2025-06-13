#!/bin/bash

# SSH Diagnostic Script pro Raspberry Pi
# Tento script testuje SSH připojení a diagnostikuje problémy

echo "🔍 SSH Diagnostika pro Raspberry Pi"
echo "==================================="

# Konfigurace
PI_USER=${PI_USER:-"pi"}
PI_HOST=${PI_HOST:-"pi.local"}
SSH_OPTS="-o ConnectTimeout=10 -o StrictHostKeyChecking=no"

echo "Testovaný host: ${PI_USER}@${PI_HOST}"
echo ""

# Test 1: Ping test
echo "📡 Test 1: Ping test"
if ping -c 3 ${PI_HOST} >/dev/null 2>&1; then
    echo "✅ Ping úspěšný - Pi je dostupné v síti"
else
    echo "❌ Ping selhal - Pi není dostupné"
    echo "💡 Zkuste:"
    echo "   - Zkontrolovat připojení Pi k síti"
    echo "   - Použít IP adresu místo hostname"
    echo "   - Zkusit raspberrypi.local místo pi.local"
fi
echo ""

# Test 2: Port 22 (SSH)
echo "🔌 Test 2: SSH port (22)"
if nc -z ${PI_HOST} 22 2>/dev/null; then
    echo "✅ Port 22 je otevřený - SSH daemon běží"
else
    echo "❌ Port 22 není dostupný"
    echo "💡 Na Pi spusťte: sudo systemctl enable --now ssh"
fi
echo ""

# Test 3: SSH připojení
echo "🔐 Test 3: SSH připojení"
if ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "echo 'SSH test OK'" 2>/dev/null; then
    echo "✅ SSH připojení funguje"
else
    echo "❌ SSH připojení selhalo"
    echo "💡 Možné příčiny:"
    echo "   - Špatné uživatelské jméno nebo heslo"
    echo "   - SSH klíče nejsou nastavené"
    echo "   - SSH daemon neběží na Pi"
fi
echo ""

# Test 4: SCP funkčnost
echo "📁 Test 4: SCP funkčnost"
echo "test" > /tmp/scp_test.txt
if scp $SSH_OPTS /tmp/scp_test.txt "${PI_USER}@${PI_HOST}:~/scp_test.txt" 2>/dev/null; then
    echo "✅ SCP funguje"
    # Úklid
    ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "rm -f ~/scp_test.txt" 2>/dev/null
else
    echo "❌ SCP nefunguje"
    echo "💡 Možné příčiny:"
    echo "   - SCP subsystém není povolen"
    echo "   - Nedostatečná oprávnění"
    echo "   - Disk plný na Pi"
fi
rm -f /tmp/scp_test.txt
echo ""

# Test 5: Docker na Pi
echo "🐳 Test 5: Docker na Pi"
if ssh $SSH_OPTS "${PI_USER}@${PI_HOST}" "docker --version" 2>/dev/null; then
    echo "✅ Docker je nainstalován a dostupný"
else
    echo "❌ Docker není dostupný"
    echo "💡 Na Pi spusťte: curl -fsSL https://get.docker.com | sh"
    echo "   Pak: sudo usermod -aG docker pi"
fi
echo ""

# Alternativní hostname
echo "🔄 Test alternativních hostname:"
for host in "raspberrypi.local" "homeassistant.local" "pi.lan"; do
    if ping -c 1 $host >/dev/null 2>&1; then
        echo "✅ $host je dostupný"
        echo "💡 Použijte: export PI_HOST=$host"
    fi
done
echo ""

# Síťové informace
echo "🌐 Síťové informace:"
echo "Vaše IP adresa:"
ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -3
echo ""
echo "Dostupné .local zařízení:"
dns-sd -B _ssh._tcp . 2>/dev/null | head -5 || echo "dns-sd nedostupný"
echo ""

echo "📋 Shrnutí pro deployment:"
echo "=========================="
echo "1. Pokud SSH funguje: použijte ./deploy_to_pi.sh"
echo "2. Pokud SCP nefunguje: použijte HTTP server nebo USB"
echo "3. Pokud SSH nefunguje: nastavte SSH na Pi"
echo "4. Pro jiný hostname: export PI_HOST=správný_hostname"
