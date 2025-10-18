#!/bin/bash
set -euo pipefail

echo "Building TrayRunner AppImage with bundled GUI..."

# Clean previous builds
rm -rf build dist AppDir TrayRunner-x86_64.AppImage squashfs-root

# Install build dependencies
pip install pyinstaller

# 1) Build BOTH binaries with PyInstaller
echo "Building core tray application..."
pyinstaller --name trayrunner \
    --onefile \
    --noconfirm \
    --clean \
    src/trayrunner/app.py

echo "Building GUI editor..."
pyinstaller --name trayrunner-gui \
    --onefile \
    --windowed \
    --noconfirm \
    --add-data "gui/assets:assets" \
    --hidden-import PySide6.QtCore \
    --hidden-import PySide6.QtWidgets \
    --hidden-import PySide6.QtGui \
    --hidden-import ruamel.yaml \
    --hidden-import pydantic \
    --clean \
    gui/trayrunner_gui/app.py

# 2) Create AppDir structure
mkdir -p AppDir/usr/bin
mkdir -p AppDir/usr/share/applications
mkdir -p AppDir/usr/share/icons/hicolor/256x256/apps
mkdir -p AppDir/usr/share/trayrunner

# 3) Install both binaries
install -m755 dist/trayrunner AppDir/usr/bin/trayrunner
install -m755 dist/trayrunner-gui AppDir/usr/bin/trayrunner-gui

# 4) Copy additional resources
cp -r config AppDir/usr/share/trayrunner/

# 5) Create desktop file (points to trayrunner, not GUI)
# Always include icon since linuxdeploy expects it
cat > AppDir/trayrunner.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=TrayRunner
Comment=System tray application with customizable menus
Exec=trayrunner
Icon=trayrunner
Categories=Utility;
Terminal=false
StartupNotify=false
X-AppImage-Integrate=true
EOF

cp AppDir/trayrunner.desktop AppDir/usr/share/applications/

# 6) Copy icon (handle both PNG and ICO formats)
if [[ -f "gui/assets/icon.png" ]]; then
    # Check if it's actually a PNG or ICO file
    if file gui/assets/icon.png | grep -q "PNG image"; then
        cp gui/assets/icon.png AppDir/trayrunner.png
        cp gui/assets/icon.png AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner.png
    else
        # It's an ICO file, create a simple PNG or skip icon
        echo "Icon is ICO format, creating simple PNG..."
        # Create a simple 256x256 PNG using ImageMagick if available, otherwise skip
        if command -v convert >/dev/null 2>&1; then
            convert gui/assets/icon.png -resize 256x256 AppDir/trayrunner.png
            cp AppDir/trayrunner.png AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner.png
        else
            echo "ImageMagick not available, creating simple fallback icon"
            # Create a simple 256x256 PNG using Python if available
            python3 -c "
import sys
try:
    from PIL import Image, ImageDraw
    # Create a simple 256x256 icon with a gear symbol
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw a simple gear-like circle
    draw.ellipse([32, 32, 224, 224], fill=(100, 100, 100, 255), outline=(200, 200, 200, 255), width=4)
    draw.ellipse([64, 64, 192, 192], fill=(150, 150, 150, 255))
    img.save('AppDir/trayrunner.png')
    img.save('AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner.png')
    print('Created fallback icon')
except ImportError:
    print('PIL not available, skipping icon creation')
    sys.exit(1)
" || echo "Could not create fallback icon"
        fi
    fi
else
    echo "No icon file found, creating simple fallback icon"
    # Create a simple 256x256 PNG using Python if available
    python3 -c "
import sys
try:
    from PIL import Image, ImageDraw
    # Create a simple 256x256 icon with a gear symbol
    img = Image.new('RGBA', (256, 256), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    # Draw a simple gear-like circle
    draw.ellipse([32, 32, 224, 224], fill=(100, 100, 100, 255), outline=(200, 200, 200, 255), width=4)
    draw.ellipse([64, 64, 192, 192], fill=(150, 150, 150, 255))
    img.save('AppDir/trayrunner.png')
    img.save('AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner.png')
    print('Created fallback icon')
except ImportError:
    print('PIL not available, will skip icon')
    sys.exit(1)
" || echo "Could not create fallback icon"
fi

# 7) Create AppRun (launches trayrunner by default)
cat > AppDir/AppRun << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export APPDIR="${HERE}"
exec "${HERE}/usr/bin/trayrunner" "$@"
EOF
chmod +x AppDir/AppRun

# 8) Download linuxdeploy and Qt plugin if needed
if [[ ! -f "linuxdeploy-x86_64.AppImage" ]]; then
    echo "Downloading linuxdeploy..."
    wget -c https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
    chmod +x linuxdeploy-x86_64.AppImage
fi

if [[ ! -f "linuxdeploy-plugin-qt-x86_64.AppImage" ]]; then
    echo "Downloading linuxdeploy Qt plugin..."
    wget -c https://github.com/linuxdeploy/linuxdeploy-plugin-qt/releases/download/continuous/linuxdeploy-plugin-qt-x86_64.AppImage
    chmod +x linuxdeploy-plugin-qt-x86_64.AppImage
fi

# 9) Run linuxdeploy (try with Qt plugin, fallback without)
echo "Running linuxdeploy to bundle libraries..."
export LD_LIBRARY_PATH=""

# Try to find qmake
QMAKE_PATH=""
if command -v qmake >/dev/null 2>&1; then
    QMAKE_PATH="$(which qmake)"
    echo "Found qmake at: $QMAKE_PATH"
    export QMAKE="$QMAKE_PATH"
    
    # Try with Qt plugin
    echo "Attempting to bundle Qt libraries..."
    # Build linuxdeploy command with optional icon
    LINUXDEPLOY_CMD="./linuxdeploy-x86_64.AppImage --appdir AppDir \
        --executable AppDir/usr/bin/trayrunner \
        --executable AppDir/usr/bin/trayrunner-gui \
        --desktop-file AppDir/usr/share/applications/trayrunner.desktop"
    
    # Add icon if it exists
    if [[ -f "AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner.png" ]]; then
        LINUXDEPLOY_CMD="$LINUXDEPLOY_CMD --icon-file AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner.png"
    fi
    
    LINUXDEPLOY_CMD="$LINUXDEPLOY_CMD --plugin qt --output appimage"
    
    if eval $LINUXDEPLOY_CMD; then
        echo "Successfully bundled with Qt plugin"
    else
        echo "Qt plugin failed, trying without Qt plugin..."
        # Remove --plugin qt from command
        LINUXDEPLOY_CMD="${LINUXDEPLOY_CMD/--plugin qt /}"
        eval $LINUXDEPLOY_CMD
    fi
else
    echo "qmake not found, bundling without Qt plugin..."
    # Build linuxdeploy command with optional icon
    LINUXDEPLOY_CMD="./linuxdeploy-x86_64.AppImage --appdir AppDir \
        --executable AppDir/usr/bin/trayrunner \
        --executable AppDir/usr/bin/trayrunner-gui \
        --desktop-file AppDir/usr/share/applications/trayrunner.desktop"
    
    # Add icon if it exists
    if [[ -f "AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner.png" ]]; then
        LINUXDEPLOY_CMD="$LINUXDEPLOY_CMD --icon-file AppDir/usr/share/icons/hicolor/256x256/apps/trayrunner.png"
    fi
    
    LINUXDEPLOY_CMD="$LINUXDEPLOY_CMD --output appimage"
    eval $LINUXDEPLOY_CMD
fi

# 10) Rename output
mv TrayRunner-*.AppImage TrayRunner-x86_64.AppImage || true

# 11) Generate SHA256SUMS
sha256sum TrayRunner-x86_64.AppImage > SHA256SUMS

echo "AppImage built successfully: TrayRunner-x86_64.AppImage"
echo "SHA256: $(cat SHA256SUMS)"