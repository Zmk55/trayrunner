#!/usr/bin/env bash
set -euo pipefail

# Fetch linuxdeploy tools for AppImage building
# This script is idempotent - it only downloads if files don't exist

TDIR="$(cd "$(dirname "$0")/.." && pwd)/linuxdeploy"
mkdir -p "$TDIR"
cd "$TDIR"

LDEP=linuxdeploy-x86_64.AppImage
QPLG=linuxdeploy-plugin-qt-x86_64.AppImage

# Download linuxdeploy if not present
if [ ! -f "$LDEP" ]; then
    echo "Downloading linuxdeploy-x86_64.AppImage..."
    wget -qO "$LDEP" https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x "$LDEP"
fi

# Download Qt plugin if not present
if [ ! -f "$QPLG" ]; then
    echo "Downloading linuxdeploy-plugin-qt-x86_64.AppImage..."
    wget -qO "$QPLG" https://github.com/linuxdeploy/linuxdeploy-plugin-qt/releases/download/continuous/linuxdeploy-plugin-qt-x86_64.AppImage
    chmod +x "$QPLG"
fi

echo "linuxdeploy tools ready in $TDIR"
