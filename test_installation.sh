#!/bin/bash

# TrayRunner Installation Test Script
# Tests the installation and basic functionality

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}TrayRunner Installation Test${NC}"
echo "=============================="
echo ""

# Test 1: Check if trayrunner command is available
echo -e "${YELLOW}Test 1: Checking if 'trayrunner' command is available...${NC}"
if command -v trayrunner >/dev/null 2>&1; then
    echo -e "${GREEN}✓ trayrunner command found${NC}"
else
    echo -e "${RED}✗ trayrunner command not found in PATH${NC}"
    exit 1
fi

# Test 2: Check version
echo -e "${YELLOW}Test 2: Checking version...${NC}"
VERSION_OUTPUT=$(trayrunner version)
if [[ $VERSION_OUTPUT == *"1.0.0"* ]]; then
    echo -e "${GREEN}✓ Version check passed: $VERSION_OUTPUT${NC}"
else
    echo -e "${RED}✗ Version check failed: $VERSION_OUTPUT${NC}"
    exit 1
fi

# Test 3: Check if app can start (without actually starting it)
echo -e "${YELLOW}Test 3: Checking if app can be imported...${NC}"
if python3 -c "import sys; sys.path.insert(0, 'src'); from trayrunner.app import TrayRunner; print('Import successful')" 2>/dev/null; then
    echo -e "${GREEN}✓ App imports successfully${NC}"
else
    echo -e "${RED}✗ App import failed${NC}"
    echo "This might be due to missing dependencies. Run: sudo apt install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo gir1.2-gtk-3.0 libnotify-bin"
    exit 1
fi

# Test 4: Check if config directory exists
echo -e "${YELLOW}Test 4: Checking configuration setup...${NC}"
if [[ -d "$HOME/.config/trayrunner" ]]; then
    echo -e "${GREEN}✓ Configuration directory exists${NC}"
else
    echo -e "${YELLOW}! Configuration directory not found (will be created on first run)${NC}"
fi

# Test 5: Check if autostart is configured
echo -e "${YELLOW}Test 5: Checking autostart configuration...${NC}"
if [[ -f "$HOME/.config/autostart/trayrunner.desktop" ]]; then
    echo -e "${GREEN}✓ Autostart configured${NC}"
else
    echo -e "${YELLOW}! Autostart not configured (run 'trayrunner enable-autostart' to enable)${NC}"
fi

# Test 6: Check if icon file exists
echo -e "${YELLOW}Test 6: Checking icon file...${NC}"
if [[ -f "src/trayrunner/icons/Gear.ico" ]]; then
    echo -e "${GREEN}✓ Icon file found${NC}"
else
    echo -e "${YELLOW}! Icon file not found (app will use fallback icon)${NC}"
fi

echo ""
echo -e "${GREEN}Installation test completed!${NC}"
echo ""
echo -e "${BLUE}Next steps:${NC}"
echo "1. Run 'trayrunner start' to start the application"
echo "2. Look for the gear icon in your system tray"
echo "3. Click the icon to see the menu"
echo "4. Edit ~/.config/trayrunner/commands.yaml to customize your menu"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "- trayrunner status    # Check if running"
echo "- trayrunner stop      # Stop the app"
echo "- trayrunner restart   # Restart the app"
echo "- trayrunner version   # Show version"
