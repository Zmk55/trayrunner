#!/bin/bash
set -e

# TrayRunner GUI AppImage Build Script
# Creates a self-contained AppImage for the GUI editor

echo "Building TrayRunner GUI AppImage..."

# Install build dependencies
echo "Installing build dependencies..."
pip install pyinstaller

# Clean previous builds
rm -rf build dist AppDir

# Build with PyInstaller
echo "Building with PyInstaller..."
pyinstaller --name trayrunner-gui \
    --onefile \
    --windowed \
    --add-data "gui/assets:assets" \
    --hidden-import PySide6.QtCore \
    --hidden-import PySide6.QtWidgets \
    --hidden-import PySide6.QtGui \
    --hidden-import ruamel.yaml \
    --hidden-import pydantic \
    gui/trayrunner_gui/app.py

# Create AppDir structure
echo "Creating AppDir structure..."
mkdir -p AppDir/usr/bin
cp dist/trayrunner-gui AppDir/usr/bin/
chmod +x AppDir/usr/bin/trayrunner-gui

# Create desktop file
mkdir -p AppDir/usr/share/applications
cat > AppDir/usr/share/applications/trayrunner-gui.desktop << EOF
[Desktop Entry]
Type=Application
Name=TrayRunner Config Editor
Comment=GUI editor for TrayRunner configuration
Exec=trayrunner-gui
Icon=trayrunner-gui
Categories=Utility;System;
Keywords=config;editor;tray;system;
EOF

# Copy icon if it exists
if [[ -f "gui/assets/icon.png" ]]; then
    mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
    cp gui/assets/icon.png AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner-gui.png
fi

# Download appimagetool if needed
if [[ ! -f "appimagetool-x86_64.AppImage" ]]; then
    echo "Downloading appimagetool..."
    wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
echo "Building AppImage..."
./appimagetool-x86_64.AppImage AppDir trayrunner-gui-x86_64.AppImage

echo "AppImage built successfully: trayrunner-gui-x86_64.AppImage"
echo "Size: $(du -h trayrunner-gui-x86_64.AppImage | cut -f1)"
