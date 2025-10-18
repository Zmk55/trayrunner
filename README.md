# TrayRunner

A Python 3 tray application for Linux Mint (Cinnamon) using AppIndicator that shows a system tray icon with menu items populated from a YAML configuration file.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org/)

## Quick Start

```bash
# Clone the repository
git clone https://github.com/Zmk55/trayrunner.git
cd trayrunner

# Run the installer
chmod +x install.sh
./install.sh

# Start using TrayRunner
trayrunner status
```

## Features

- **System Tray Integration**: Clean AppIndicator integration with customizable icon
- **YAML Configuration**: Easy-to-edit menu configuration with support for:
  - Simple command items
  - Menu separators
  - Nested submenus (groups)
  - Optional confirmation dialogs
  - Terminal execution mode
  - Custom environment variables
- **Command Execution**: Robust command execution with:
  - Terminal emulator support (x-terminal-emulator, gnome-terminal, xterm, konsole)
  - Notification system (libnotify with notify-send fallback)
  - Command logging to `~/.local/state/trayrunner/run.log`
  - Error handling and user feedback
- **Built-in Utilities**:
  - Reload configuration without restart
  - Open configuration in default editor
  - View execution logs
  - Graceful quit
- **Config GUI Editor** (NEW!):
  - Visual tree editor with drag-and-drop
  - Live validation with error highlighting
  - Comment and formatting preservation
  - Automatic backup management
  - Integrated reload functionality
  - File change monitoring

## Config GUI

TrayRunner now includes a modern GUI editor for configuration files! No more manual YAML editing required.

### Quick Start with GUI

```bash
# Install TrayRunner with GUI support
pip install .[gui]

# Or use pipx for isolated installation
pipx install .[gui]

# Launch the GUI
trayrunner-gui

# Or launch from tray menu
# Right-click tray icon → "Open Config GUI"
```

### GUI Features

- **Visual Editor**: Tree-based interface for menu structure
- **Live Validation**: Real-time error checking and suggestions
- **Smart Backup**: Automatic timestamped backups on save
- **Reload Integration**: One-click TrayRunner configuration reload
- **File Watching**: Detects external changes to your config
- **Modern UI**: Clean interface with theme support

For detailed GUI documentation, see [gui/README.md](gui/README.md).

## Requirements

### System Dependencies
```bash
sudo apt install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo gir1.2-gtk-3.0 libnotify-bin
```

### Python Dependencies
```bash
pip3 install -r requirements.txt
```

## Installation

### Automated Installation (Recommended)

The easiest way to install TrayRunner is using the provided installation script:

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/trayrunner.git
cd trayrunner

# Run the installer
chmod +x install.sh
./install.sh
```

The installer will:
- Install all required system dependencies
- Install Python dependencies
- Set up user configuration
- Enable autostart (optional)
- Add the `trayrunner` command to your PATH
- Test the installation

### Manual Installation

If you prefer to install manually:

1. **Install system dependencies**:
   ```bash
   sudo apt install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo gir1.2-gtk-3.0 libnotify-bin python3-yaml
   ```

2. **Set up the application**:
   ```bash
   # Copy to a permanent location
   sudo cp -r src/trayrunner /opt/
   sudo cp trayrunner.sh /usr/local/bin/trayrunner
   sudo chmod +x /usr/local/bin/trayrunner
   
   # Set up user configuration
   mkdir -p ~/.config/trayrunner
   cp config/commands.yaml ~/.config/trayrunner/
   
   # Set up autostart (optional)
   mkdir -p ~/.config/autostart
   cp autostart/trayrunner.desktop ~/.config/autostart/
   ```

### Supported Systems

- **Linux Mint** (Cinnamon) - Primary target
- **Ubuntu** (with AppIndicator support)
- **Debian** (with AppIndicator support)
- **Other GTK-based distributions** (may require additional setup)

## Usage

### Running the Application
```bash
python3 src/trayrunner/app.py
```

The application will appear in your system tray with a gear icon. Click the icon to access the menu.

### Configuration

Edit `~/.config/trayrunner/commands.yaml` to customize your menu items:

```yaml
items:
  - type: item
    label: "Open Terminal"
    cmd: "x-terminal-emulator"
    terminal: false
    confirm: false

  - type: separator

  - type: group
    label: "System"
    items:
      - type: item
        label: "Update System"
        cmd: "bash -lc 'sudo apt update && sudo apt -y upgrade'"
        terminal: true
        confirm: true
        env:
          DEBIAN_FRONTEND: "noninteractive"
```

### Configuration Schema

#### Item Types

**Simple Item**:
```yaml
- type: item
  label: "Display Name"        # Required: Menu item text
  cmd: "command to run"        # Required: Command to execute
  terminal: false              # Optional: Run in terminal (default: false)
  confirm: false               # Optional: Show confirmation dialog (default: false)
  env:                         # Optional: Environment variables
    VAR_NAME: "value"
```

**Separator**:
```yaml
- type: separator
```

**Group (Submenu)**:
```yaml
- type: group
  label: "Group Name"          # Required: Submenu title
  items:                       # Required: List of items in submenu
    - type: item
      label: "Sub Item"
      cmd: "command"
```

### Built-in Menu Items

The application automatically adds these utility items to every menu:

- **Reload Config**: Rebuilds the menu from the current configuration file
- **Open Config**: Opens the configuration file in your default editor
- **Show Log**: Displays the execution log (uses `tail -f` for large files)
- **Quit**: Exits the application

## File Locations

- **Configuration**: `~/.config/trayrunner/commands.yaml`
- **Logs**: `~/.local/state/trayrunner/run.log`
- **Icon**: `src/trayrunner/icons/gear.ico`
- **Autostart**: `~/.config/autostart/trayrunner.desktop`

## Troubleshooting

### Icon Not Showing
- Ensure the icon file exists at `src/trayrunner/icons/gear.ico`
- Check that AppIndicator is supported in your desktop environment
- Try running with `APPINDICATOR_DEBUG=1 python3 src/trayrunner/app.py`

### Commands Not Executing
- Check the log file at `~/.local/state/trayrunner/run.log`
- Verify command paths and permissions
- Test commands manually in terminal first

### Notifications Not Working
- Install `libnotify-bin`: `sudo apt install libnotify-bin`
- Check notification daemon is running: `pgrep notification-daemon`

### Configuration Issues
- Validate YAML syntax using an online YAML validator
- Check file permissions on the configuration file
- Use "Reload Config" from the menu to test changes

## Development

### Project Structure
```
TrayRunner/
├── src/trayrunner/
│   ├── app.py                 # Main application
│   └── icons/
│       └── gear.ico           # Tray icon
├── config/
│   └── commands.yaml          # Default configuration
├── autostart/
│   └── trayrunner.desktop     # Autostart desktop file
├── requirements.txt           # Python dependencies
├── install.sh                 # Installation script
└── README.md                  # This file
```

### Extending the Application

The codebase is designed to be easily extensible:

- **ConfigLoader**: Handles YAML loading and validation
- **CommandRunner**: Manages command execution and logging
- **TrayRunner**: Main application class with menu building

To add new features:
1. Extend the configuration schema in `ConfigLoader.validate_item()`
2. Add handling in `TrayRunner.create_menu_item()`
3. Implement execution logic in `CommandRunner.run_command()`

## License

This project is provided as-is for educational and personal use. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.
