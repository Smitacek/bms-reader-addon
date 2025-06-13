#!/bin/bash
set -e

# Rychlý ARM build pro testování na Raspberry Pi / Apple Silicon

echo "🍓 ARM Build Script pro Raspberry Pi / Apple Silicon"
echo "=" * 50

# Zkontroluj, že jsme ve správné složce
if [ ! -f "config.yaml" ]; then
    echo "❌ Error: config.yaml not found. Run from addon directory."
    exit 1
fi

# Build informace
BUILD_VERSION=$(grep "version:" config.yaml | cut -d'"' -f2)
echo "📦 Version: $BUILD_VERSION"

# Detekce aktuální architektury
if [[ $(uname -m) == "arm64" ]]; then
    echo "🍎 Detekováno: Apple Silicon Mac (arm64)"
    PRIMARY_ARCH="aarch64"
elif [[ $(uname -m) == "aarch64" ]]; then
    echo "🍓 Detekováno: ARM64 Linux (Raspberry Pi 4+)"
    PRIMARY_ARCH="aarch64"
elif [[ $(uname -m) == "armv7l" ]]; then
    echo "🍓 Detekováno: ARM32 Linux (Raspberry Pi 3)"
    PRIMARY_ARCH="armv7"
else
    echo "💻 Detekováno: x86_64 - buildíme pro ARM target"
    PRIMARY_ARCH="aarch64"
fi

echo "🎯 Primary target: $PRIMARY_ARCH"

# Build pro primární architekturu
echo "🏗️  Building for $PRIMARY_ARCH..."

# Platform mapping
case $PRIMARY_ARCH in
    "aarch64") platform="linux/arm64" ;;
    "armv7") platform="linux/arm/v7" ;;
    "armhf") platform="linux/arm/v6" ;;
    *) echo "❌ Neznámá architektura: $PRIMARY_ARCH"; exit 1 ;;
esac

echo "🔧 Platform: $platform"

# Build command
docker buildx build \
    --platform $platform \
    --build-arg BUILD_FROM="homeassistant/${PRIMARY_ARCH}-base:latest" \
    --build-arg BUILD_ARCH="$PRIMARY_ARCH" \
    --build-arg BUILD_VERSION="$BUILD_VERSION" \
    --tag "addon-bms-reader:$PRIMARY_ARCH-$BUILD_VERSION" \
    --tag "addon-bms-reader:$PRIMARY_ARCH-latest" \
    --tag "addon-bms-reader:latest" \
    . \
    || (echo "❌ Build failed for $PRIMARY_ARCH" && exit 1)

echo "✅ ARM build complete!"
echo ""
echo "📋 Test na Raspberry Pi:"
echo "   docker run --device=/dev/ttyUSB0 --device=/dev/ttyAMA0 addon-bms-reader:latest"
echo ""
echo "📋 Test na Apple Silicon:"
echo "   docker run --device=/dev/tty.usbserial-XXXXX addon-bms-reader:latest"
echo ""
echo "📋 Push na Raspberry Pi:"
echo "   docker save addon-bms-reader:latest | ssh pi@raspberrypi 'docker load'"
