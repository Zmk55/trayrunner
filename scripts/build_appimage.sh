#!/bin/bash
set -e

echo "Building TrayRunner GUI AppImage on Ubuntu 20.04 baseline..."

# Clean previous builds
rm -rf build dist AppDir trayrunner-gui-x86_64.AppImage

# Install build dependencies
pip install pyinstaller

# Build with PyInstaller (freeze Python app)
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
mkdir -p AppDir/usr/bin
cp dist/trayrunner-gui AppDir/usr/bin/
chmod +x AppDir/usr/bin/trayrunner-gui

# Create desktop file in AppDir root (required by appimagetool)
cat > AppDir/trayrunner-gui.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=TrayRunner Config Editor
Comment=GUI editor for TrayRunner configuration
Exec=trayrunner-gui
Icon=trayrunner-gui
Categories=Utility;
Keywords=config;editor;tray;menu;
Terminal=false
EOF

# Also create in standard location for completeness
mkdir -p AppDir/usr/share/applications
cp AppDir/trayrunner-gui.desktop AppDir/usr/share/applications/

# Copy icon to AppDir root (required by appimagetool)
if [[ -f "gui/assets/icon.png" ]]; then
    cp gui/assets/icon.png AppDir/trayrunner-gui.png
    # Also copy to standard location
    mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
    cp gui/assets/icon.png AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner-gui.png
fi

# Create AppRun script (required for AppImage)
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
exec "${HERE}/usr/bin/trayrunner-gui" "$@"
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
./appimagetool-x86_64.AppImage AppDir trayrunner-gui-x86_64.AppImage

# Generate SHA256SUMS
sha256sum trayrunner-gui-x86_64.AppImage > SHA256SUMS

echo "AppImage built successfully: trayrunner-gui-x86_64.AppImage"
echo "SHA256: $(cat SHA256SUMS)"
