#!/bin/bash

# TrayRunner Installation Script
# Installs dependencies and sets up autostart for TrayRunner
# Version: 1.0.0

set -e

# Version information
VERSION="1.0.0"
APP_NAME="TrayRunner"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the absolute path of the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$SCRIPT_DIR/src/trayrunner/app.py"

echo -e "${BLUE}${APP_NAME} Installation Script v${VERSION}${NC}"
echo "=============================================="
echo ""

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root${NC}"
   echo "Please run as a regular user. The script will prompt for sudo when needed."
   exit 1
fi

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to install system packages
install_system_packages() {
    echo -e "${YELLOW}Installing system dependencies...${NC}"
    
    # Update package list
    sudo apt update
    
    # Install required packages
    sudo apt install -y \
        python3-gi \
        gir1.2-appindicator3-0.1 \
        python3-gi-cairo \
        gir1.2-gtk-3.0 \
        libnotify-bin \
        python3-pip
    
    echo -e "${GREEN}System dependencies installed successfully${NC}"
}

# Function to install Python packages
install_python_packages() {
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    
    # Install PyYAML
    pip3 install --user PyYAML
    
    echo -e "${GREEN}Python dependencies installed successfully${NC}"
}

# Function to setup user configuration
setup_user_config() {
    echo -e "${YELLOW}Setting up user configuration...${NC}"
    
    # Create config directory
    mkdir -p "$HOME/.config/trayrunner"
    
    # Copy default config if it doesn't exist
    if [[ ! -f "$HOME/.config/trayrunner/commands.yaml" ]]; then
        cp "$SCRIPT_DIR/config/commands.yaml" "$HOME/.config/trayrunner/"
        echo -e "${GREEN}Default configuration copied to ~/.config/trayrunner/commands.yaml${NC}"
    else
        echo -e "${YELLOW}Configuration file already exists at ~/.config/trayrunner/commands.yaml${NC}"
    fi
    
    # Create state directory for logs
    mkdir -p "$HOME/.local/state/trayrunner"
    
    echo -e "${GREEN}User configuration setup complete${NC}"
}

# Function to setup autostart
setup_autostart() {
    echo -e "${YELLOW}Setting up autostart...${NC}"
    
    # Create autostart directory
    mkdir -p "$HOME/.config/autostart"
    
    # Create desktop file with correct path
    cat > "$HOME/.config/autostart/trayrunner.desktop" << EOF
[Desktop Entry]
Type=Application
Name=TrayRunner
Comment=System tray application for running custom commands
Exec=python3 $APP_PATH
Icon=$SCRIPT_DIR/src/trayrunner/icons/gear.ico
X-GNOME-Autostart-enabled=true
StartupNotify=false
NoDisplay=false
Hidden=false
EOF
    
    echo -e "${GREEN}Autostart configured successfully${NC}"
    echo -e "${BLUE}TrayRunner will start automatically on login${NC}"
}

# Function to make app executable
make_executable() {
    echo -e "${YELLOW}Making application executable...${NC}"
    chmod +x "$APP_PATH"
    echo -e "${GREEN}Application is now executable${NC}"
}

# Function to test installation
test_installation() {
    echo -e "${YELLOW}Testing installation...${NC}"
    
    # Check if Python can import required modules
    if python3 -c "import gi; gi.require_version('Gtk', '3.0'); gi.require_version('AppIndicator3', '0.1'); from gi.repository import Gtk, AppIndicator3; print('GTK and AppIndicator imports successful')" 2>/dev/null; then
        echo -e "${GREEN}GTK and AppIndicator modules are working${NC}"
    else
        echo -e "${RED}Error: GTK or AppIndicator modules not working properly${NC}"
        echo "Please check the installation of system dependencies"
        return 1
    fi
    
    # Check if PyYAML is available
    if python3 -c "import yaml; print('PyYAML is working')" 2>/dev/null; then
        echo -e "${GREEN}PyYAML is working${NC}"
    else
        echo -e "${RED}Error: PyYAML not working properly${NC}"
        echo "Please check the installation of Python dependencies"
        return 1
    fi
    
    # Check if icon file exists
    if [[ -f "$SCRIPT_DIR/src/trayrunner/icons/gear.ico" ]]; then
        echo -e "${GREEN}Icon file found${NC}"
    else
        echo -e "${YELLOW}Warning: Icon file not found at $SCRIPT_DIR/src/trayrunner/icons/gear.ico${NC}"
        echo "The application will use a fallback icon"
    fi
    
    echo -e "${GREEN}Installation test completed successfully${NC}"
}

# Function to show usage instructions
show_usage() {
    echo -e "${BLUE}Installation Complete!${NC}"
    echo "====================="
    echo ""
    echo -e "${GREEN}To run TrayRunner:${NC}"
    echo "  python3 $APP_PATH"
    echo ""
    echo -e "${GREEN}To configure:${NC}"
    echo "  Edit ~/.config/trayrunner/commands.yaml"
    echo ""
    echo -e "${GREEN}To disable autostart:${NC}"
    echo "  rm ~/.config/autostart/trayrunner.desktop"
    echo ""
    echo -e "${GREEN}Logs are stored at:${NC}"
    echo "  ~/.local/state/trayrunner/run.log"
    echo ""
    echo -e "${GREEN}To install the GUI editor:${NC}"
    echo "  pip3 install --user .[gui]"
    echo "  or: pipx install .[gui]"
    echo ""
    echo -e "${BLUE}Enjoy using TrayRunner!${NC}"
}

# Main installation process
main() {
    echo -e "${BLUE}Starting TrayRunner installation...${NC}"
    echo ""
    
    # Check if we're on a supported system
    if ! command_exists apt; then
        echo -e "${RED}Error: This script is designed for Debian/Ubuntu-based systems${NC}"
        echo "Please install dependencies manually and copy the configuration files"
        exit 1
    fi
    
    # Install system packages
    install_system_packages
    echo ""
    
    # Install Python packages
    install_python_packages
    echo ""
    
    # Setup user configuration
    setup_user_config
    echo ""
    
    # Setup autostart
    setup_autostart
    echo ""
    
    # Make app executable
    make_executable
    echo ""
    
    # Test installation
    if test_installation; then
        echo ""
        show_usage
    else
        echo -e "${RED}Installation test failed. Please check the errors above.${NC}"
        exit 1
    fi
}

# Run main function
main "$@"
