#!/bin/bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOOLS="$ROOT/tools/linuxdeploy"
APPDIR="$ROOT/build_appimage/AppDir"
OUTDIR="$ROOT/build_appimage/out"

echo "Building TrayRunner AppImage with bundled GUI..."

# Ensure linuxdeploy tools are present
echo "Ensuring linuxdeploy tools are available..."
"$ROOT/tools/helpers/fetch_linuxdeploy.sh" >/dev/null

# Clean previous builds
rm -rf "$ROOT/build_appimage" dist AppDir TrayRunner-x86_64.AppImage squashfs-root

# Install build dependencies
pip install pyinstaller

# 1) Build ONLY GUI with PyInstaller (core uses source + wrapper)
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
mkdir -p "$APPDIR/usr/bin"
mkdir -p "$APPDIR/usr/share/applications"
mkdir -p "$APPDIR/usr/share/icons/hicolor/256x256/apps"
mkdir -p "$APPDIR/usr/share/trayrunner"
mkdir -p "$OUTDIR"

# 3) Install GUI binary + copy core source files
install -m755 dist/trayrunner-gui "$APPDIR/usr/bin/trayrunner-gui"
cp -r src/trayrunner "$APPDIR/usr/share/trayrunner/"
cp -r config "$APPDIR/usr/share/trayrunner/"

# 4) Create wrapper script for core tray app
cat > "$APPDIR/usr/bin/trayrunner" << 'EOF'
#!/bin/bash
# TrayRunner core wrapper - uses system Python with GTK
HERE="$(dirname "$(readlink -f "${0}")")"
cd "$HERE/../share/trayrunner"
exec python3 trayrunner/app.py "$@"
EOF
chmod +x "$APPDIR/usr/bin/trayrunner"

# Make sure the script is executable and has proper shebang
sed -i '1s|^|#!/bin/bash\n|' "$APPDIR/usr/bin/trayrunner"

# 5) Create desktop file (points to trayrunner, not GUI)
# Always include icon since linuxdeploy expects it
cat > "$APPDIR/trayrunner.desktop" << 'EOF'
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

cp "$APPDIR/trayrunner.desktop" "$APPDIR/usr/share/applications/"

# 6) Copy icon (handle both PNG and ICO formats)
if [[ -f "gui/assets/icon.png" ]]; then
    # Check if it's actually a PNG or ICO file
    if file gui/assets/icon.png | grep -q "PNG image"; then
        cp gui/assets/icon.png "$APPDIR/trayrunner.png"
        cp gui/assets/icon.png "$APPDIR/usr/share/icons/hicolor/256x256/apps/trayrunner.png"
    else
        # It's an ICO file, create a simple PNG or skip icon
        echo "Icon is ICO format, creating simple PNG..."
        # Create a simple 256x256 PNG using ImageMagick if available, otherwise skip
        if command -v convert >/dev/null 2>&1; then
            convert gui/assets/icon.png -resize 256x256 "$APPDIR/trayrunner.png"
            cp "$APPDIR/trayrunner.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/trayrunner.png"
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
    img.save('$APPDIR/trayrunner.png')
    img.save('$APPDIR/usr/share/icons/hicolor/256x256/apps/trayrunner.png')
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
    img.save('$APPDIR/trayrunner.png')
    img.save('$APPDIR/usr/share/icons/hicolor/256x256/apps/trayrunner.png')
    print('Created fallback icon')
except ImportError:
    print('PIL not available, will skip icon')
    sys.exit(1)
" || echo "Could not create fallback icon"
fi

# 7) Create AppRun (launches trayrunner by default)
cat > "$APPDIR/AppRun" << 'EOF'
#!/bin/bash
HERE="$(dirname "$(readlink -f "${0}")")"
export APPDIR="${HERE}"
exec "${HERE}/usr/bin/trayrunner" "$@"
EOF
chmod +x "$APPDIR/AppRun"

# 8) Run linuxdeploy (try with Qt plugin, fallback without)
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
    # Build linuxdeploy command with optional icon - only analyze GUI binary
    LINUXDEPLOY_CMD="$TOOLS/linuxdeploy-x86_64.AppImage --appdir $APPDIR \
        --executable $APPDIR/usr/bin/trayrunner-gui \
        --desktop-file $APPDIR/usr/share/applications/trayrunner.desktop"
    
    # Add icon if it exists
    if [[ -f "$APPDIR/usr/share/icons/hicolor/256x256/apps/trayrunner.png" ]]; then
        LINUXDEPLOY_CMD="$LINUXDEPLOY_CMD --icon-file $APPDIR/usr/share/icons/hicolor/256x256/apps/trayrunner.png"
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
    # Build linuxdeploy command with optional icon - only analyze GUI binary
    LINUXDEPLOY_CMD="$TOOLS/linuxdeploy-x86_64.AppImage --appdir $APPDIR \
        --executable $APPDIR/usr/bin/trayrunner-gui \
        --desktop-file $APPDIR/usr/share/applications/trayrunner.desktop"
    
    # Add icon if it exists
    if [[ -f "$APPDIR/usr/share/icons/hicolor/256x256/apps/trayrunner.png" ]]; then
        LINUXDEPLOY_CMD="$LINUXDEPLOY_CMD --icon-file $APPDIR/usr/share/icons/hicolor/256x256/apps/trayrunner.png"
    fi
    
    LINUXDEPLOY_CMD="$LINUXDEPLOY_CMD --output appimage"
    eval $LINUXDEPLOY_CMD
fi

# 9) Move output to out directory
mv TrayRunner-*.AppImage "$OUTDIR/TrayRunner-$(uname -m).AppImage" || true

# 10) Generate SHA256SUMS
( cd "$OUTDIR" && sha256sum "TrayRunner-$(uname -m).AppImage" > SHA256SUMS )

# 11) Sanity checks
echo "Running sanity checks..."
if [[ -f "$OUTDIR/TrayRunner-$(uname -m).AppImage" ]]; then
    echo "✓ AppImage created"
    
    # Check both binaries exist in AppDir
    if [[ -x "$APPDIR/usr/bin/trayrunner" ]] && [[ -x "$APPDIR/usr/bin/trayrunner-gui" ]]; then
        echo "✓ Both binaries present and executable"
    else
        echo "✗ Missing binaries in AppDir"
        exit 1
    fi
    
    # Check AppRun points to trayrunner (either symlink or script content)
    if readlink "$APPDIR/AppRun" 2>/dev/null | grep -q "trayrunner" || grep -q "trayrunner" "$APPDIR/AppRun"; then
        echo "✓ AppRun points to core tray app"
    else
        echo "✗ AppRun misconfigured"
        exit 1
    fi
else
    echo "✗ AppImage build failed"
    exit 1
fi

echo "AppImage built successfully: $OUTDIR/TrayRunner-$(uname -m).AppImage"
echo "SHA256: $(cat "$OUTDIR/SHA256SUMS")"