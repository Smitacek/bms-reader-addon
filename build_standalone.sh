#!/bin/bash

# Build standalone ARM Docker image bez Home Assistant závislostí

set -e

echo "🚀 Building Standalone ARM Docker Image"
echo "======================================="

# Konfigurace
IMAGE_NAME="bms-reader-standalone"
TAG="1.0.0"
PLATFORM="linux/arm64,linux/amd64"

echo "📦 Image: ${IMAGE_NAME}:${TAG}"
echo "🎯 Platformy: ${PLATFORM}"

# Build image
echo "🔨 Building Docker image..."
docker buildx build \
    --platform ${PLATFORM} \
    -t ${IMAGE_NAME}:${TAG} \
    -t ${IMAGE_NAME}:latest \
    -f Dockerfile.standalone \
    . \
    --load

echo "✅ Build dokončen!"

# Zobrazení velikosti
echo "📊 Velikost image:"
docker images | grep ${IMAGE_NAME} | head -1

# Test základní funkčnosti
echo "🧪 Test image..."
docker run --rm ${IMAGE_NAME}:${TAG} python3 --version

echo ""
echo "🎉 Standalone ARM image je připraven!"
echo ""
echo "📋 Použití:"
echo "   docker run -d --name bms-reader \\"
echo "     --privileged -v /dev:/dev \\"
echo "     -e BMS_PORT=/dev/ttyUSB0 \\"
echo "     -e MQTT_HOST=homeassistant.local \\"
echo "     ${IMAGE_NAME}:${TAG}"
echo ""
echo "🔧 Export pro Pi:"
echo "   docker save ${IMAGE_NAME}:${TAG} | gzip > ${IMAGE_NAME}-${TAG}.tar.gz"
