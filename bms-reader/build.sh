#!/bin/bash
set -e

# Build script pro BMS Reader Home Assistant Add-on

echo "🏗️  Building BMS Reader Add-on..."

# Zkontroluj, že jsme ve správné složce
if [ ! -f "config.yaml" ]; then
    echo "❌ Error: config.yaml not found. Run from addon directory."
    exit 1
fi

# Build informace
BUILD_VERSION=$(grep "version:" config.yaml | cut -d'"' -f2)
echo "📦 Version: $BUILD_VERSION"

# Podporované architektury (ARM první - hlavní target)
ARCHS=("aarch64" "armv7" "armhf" "amd64")

echo "🔨 Building for architectures: ${ARCHS[*]}"
echo "📱 ARM architektury prioritní pro Raspberry Pi a Apple Silicon"

for arch in "${ARCHS[@]}"; do
    echo "🏗️  Building for $arch..."
    
    # Platform mapping pro Docker
    case $arch in
        "aarch64") platform="linux/arm64" ;;
        "armv7") platform="linux/arm/v7" ;;
        "armhf") platform="linux/arm/v6" ;;
        "amd64") platform="linux/amd64" ;;
        *) echo "❌ Neznámá architektura: $arch"; continue ;;
    esac
    
    echo "🔧 Platform: $platform"
    
    docker buildx build \
        --platform $platform \
        --build-arg BUILD_FROM="homeassistant/${arch}-base:latest" \
        --build-arg BUILD_ARCH="$arch" \
        --build-arg BUILD_VERSION="$BUILD_VERSION" \
        --tag "addon-bms-reader:$arch-$BUILD_VERSION" \
        --tag "addon-bms-reader:$arch-latest" \
        . \
        || echo "⚠️  Build failed for $arch"
    
    echo "✅ Built for $arch"
done

echo "🎉 Build complete!"
echo ""
echo "📋 To test locally:"
echo "   docker run --device=/dev/ttyUSB0 addon-bms-reader:amd64-latest"
echo ""
echo "📋 To publish:"
echo "   1. Push to GitHub repository"
echo "   2. Create GitHub Release with tag v$BUILD_VERSION"
echo "   3. Add repository to Home Assistant Add-on Store"
