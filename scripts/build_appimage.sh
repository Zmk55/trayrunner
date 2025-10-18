#!/bin/bash
set -e

echo "Building TrayRunner AppImage on Ubuntu 20.04 baseline..."

# Clean previous builds
rm -rf build dist AppDir TrayRunner-x86_64.AppImage trayrunner-gui-x86_64.AppImage

# Install build dependencies
pip install pyinstaller

# Build core tray application (main binary) - use system Python for GTK
# Note: GTK/gi modules are system-level and can't be bundled with PyInstaller
# We'll create a wrapper script that uses the system Python

# Build GUI editor (optional secondary binary)
pyinstaller --name trayrunner-gui \
    --onefile \
    --windowed \
    --add-data "gui/assets:assets" \
    --hidden-import PySide6.QtCore \
    --hidden-import PySide6.QtWidgets \
    --hidden-import PySide6.QtGui \
    --hidden-import ruamel.yaml \
    --hidden-import pydantic \
    --clean \
    gui/trayrunner_gui/app.py

# Create AppDir structure
mkdir -p AppDir/usr/bin AppDir/usr/share/trayrunner
cp dist/trayrunner-gui AppDir/usr/bin/
chmod +x AppDir/usr/bin/trayrunner-gui

# Copy source files for the core tray app (since it needs system GTK)
cp -r src/trayrunner AppDir/usr/share/trayrunner/
cp -r config AppDir/usr/share/trayrunner/

# Create wrapper script for trayrunner (core) that uses system Python
cat > AppDir/usr/bin/trayrunner << 'EOF'
#!/bin/bash
# TrayRunner core app wrapper - uses system Python with GTK support
HERE="$(dirname "$(readlink -f "${0}")")"
cd "$HERE/../share/trayrunner"
exec python3 trayrunner/app.py "$@"
EOF
chmod +x AppDir/usr/bin/trayrunner

# Create desktop file in AppDir root (required by appimagetool)
cat > AppDir/trayrunner.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=TrayRunner
Comment=System tray application with customizable menus
Exec=trayrunner
Icon=trayrunner
Categories=Utility;System;
Keywords=tray;menu;system;
Terminal=false
StartupNotify=false
X-AppImage-Integrate=true
EOF

# Also create in standard location for completeness
mkdir -p AppDir/usr/share/applications
cp AppDir/trayrunner.desktop AppDir/usr/share/applications/

# Copy icon to AppDir root (required by appimagetool)
if [[ -f "gui/assets/icon.png" ]]; then
    cp gui/assets/icon.png AppDir/trayrunner.png
    # Also copy to standard location
    mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
    cp gui/assets/icon.png AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner.png
fi

# Create AppRun script (required for AppImage)
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/trayrunner" "$@"
EOF
chmod +x AppDir/AppRun

# Download appimagetool if needed
if [[ ! -f "appimagetool-x86_64.AppImage" ]]; then
    echo "Downloading appimagetool..."
    wget -c https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x appimagetool-x86_64.AppImage
fi

# Build AppImage
echo "Building AppImage..."
./appimagetool-x86_64.AppImage AppDir TrayRunner-x86_64.AppImage

# Generate SHA256SUMS
sha256sum TrayRunner-x86_64.AppImage > SHA256SUMS

echo "AppImage built successfully: TrayRunner-x86_64.AppImage"
echo "SHA256: $(cat SHA256SUMS)"
