#!/bin/bash
# Build script pro BMS Reader Home Assistant Add-on

set -e

# Barvy pro výstup
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

ADDON_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$ADDON_DIR")"
VERSION="1.0.4"
IMAGE_NAME="bms-reader-addon"

echo -e "${GREEN}🏗️  Building BMS Reader Home Assistant Add-on v${VERSION}${NC}"
echo "Addon directory: $ADDON_DIR"
echo "Project root: $PROJECT_ROOT"

# Kontrola, že máme potřebné soubory v parent directory
REQUIRED_FILES=(
    "$PROJECT_ROOT/main.py"
    "$PROJECT_ROOT/bms_parser.py"
    "$PROJECT_ROOT/modbus.py"
    "$PROJECT_ROOT/mqtt_helper.py"
)

echo -e "${YELLOW}🔍 Kontroluji požadované soubory...${NC}"
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Chybí soubor: $file${NC}"
        exit 1
    fi
    echo "✅ $(basename "$file")"
done

# Build Docker image pro různé architektury
echo -e "${YELLOW}🐳 Building Docker image...${NC}"
cd "$ADDON_DIR"

# Build pro AMD64 (nejdřív otestujeme jednu architekturu)
docker build --platform linux/amd64 -t "${IMAGE_NAME}:${VERSION}" .

echo -e "${GREEN}✅ Docker image úspěšně vytvořen: ${IMAGE_NAME}:${VERSION}${NC}"

# Zobrazit informace o image
echo -e "${YELLOW}📊 Informace o image:${NC}"
docker images "${IMAGE_NAME}:${VERSION}"

# Test spuštění s environment proměnnými (fallback mode)
echo -e "${YELLOW}🧪 Testování fallback konfigurace...${NC}"
docker run --rm \
    -e BMS_PORT="/dev/ttyUSB0" \
    -e MQTT_HOST="test-mqtt" \
    -e DEVICE_ID="test_bms" \
    -e LOG_LEVEL="DEBUG" \
    "${IMAGE_NAME}:${VERSION}" \
    python3 -c "
import sys
sys.path.append('/app')
from config import Config
cfg = Config()
print(f'BMS Port: {cfg.bms.port}')
print(f'MQTT Host: {cfg.mqtt.host}')
print(f'Device ID: {cfg.device.id}')
print(f'Log Level: {cfg.app.log_level}')
"

echo -e "${GREEN}🎉 Add-on build dokončen!${NC}"
echo ""
echo "Další kroky:"
echo "1. Zkopírujte addon/ složku do vašeho HA Add-ons repository"
echo "2. Nebo použijte lokální installation přes 'Local add-ons' v Home Assistant"
echo "3. Nakonfigurujte addon přes HA UI nebo použijte environment proměnné"
