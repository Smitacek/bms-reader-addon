#!/bin/bash
set -e

# Rychlý ARM build pouze pro aktuální platformu (Mac M1/M2 nebo Raspberry Pi)

echo "🚀 Rychlý ARM Build pro aktuální platformu"
echo "=" * 50

# Zkontroluj, že jsme ve správné složce
if [ ! -f "config.yaml" ]; then
    echo "❌ Error: config.yaml not found. Run from addon directory."
    exit 1
fi

# Detekce architektury
ARCH=$(uname -m)
case $ARCH in
    arm64|aarch64)
        DOCKER_ARCH="linux/arm64"
        echo "🍎 Detekováno: ARM64 (Mac M1/M2 nebo Raspberry Pi 4)"
        ;;
    armv7l)
        DOCKER_ARCH="linux/arm/v7"
        echo "🍓 Detekováno: ARMv7 (Raspberry Pi 3)"
        ;;
    armv6l)
        DOCKER_ARCH="linux/arm/v6"
        echo "🍓 Detekováno: ARMv6 (Starší Raspberry Pi)"
        ;;
    *)
        echo "❌ Nepodporovaná architektura: $ARCH"
        exit 1
        ;;
esac

# Build informace
BUILD_VERSION=$(grep "version:" config.yaml | cut -d'"' -f2)
IMAGE_NAME="bms-reader-arm"
TAG="$IMAGE_NAME:$BUILD_VERSION"

echo "📦 Version: $BUILD_VERSION"
echo "🏗️ Platform: $DOCKER_ARCH"
echo "🏷️ Tag: $TAG"

# Build Docker image pro aktuální platformu
echo "🔨 Building Docker image..."
docker build \
    --platform $DOCKER_ARCH \
    --tag $TAG \
    --tag $IMAGE_NAME:latest \
    .

echo "✅ Build dokončen!"
echo "🎯 Image: $TAG"
echo ""
echo "🚀 Pro test spuštění:"
echo "docker run --rm -it $TAG"
echo ""
echo "📤 Pro export:"
echo "docker save $TAG | gzip > bms-reader-arm-$BUILD_VERSION.tar.gz"