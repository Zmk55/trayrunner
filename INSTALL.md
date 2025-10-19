# TrayRunner Installation Guide

This guide covers traditional installation methods for TrayRunner, including system-wide installation and manual setup.

## 🎯 Recommended Installation

**For most users, we recommend using the [AppImage](README.md#quick-start) for the simplest experience.**

## 📦 System-Wide Installation

### Prerequisites

```bash
# Ubuntu/Debian/Mint
sudo apt update
sudo apt install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo gir1.2-gtk-3.0 libnotify-bin python3-pip

# For GUI support
sudo apt install python3-pip
```

### Install TrayRunner

```bash
# Clone the repository
git clone https://github.com/Zmk55/trayrunner.git
cd trayrunner

# Install system-wide
sudo ./install.sh

# Or install with GUI support
sudo pip install .[gui]
```

### Verify Installation

```bash
# Test the core application
trayrunner --version

# Test the GUI (if installed)
trayrunner-gui --version
```

## 🏠 User Installation (pipx)

For isolated installation without system-wide changes:

```bash
# Install pipx if not present
sudo apt install pipx

# Install TrayRunner with GUI
pipx install .[gui]

# Run
trayrunner
trayrunner-gui
```

## ⚙️ Autostart Configuration

### Desktop File Method

Create an autostart desktop file:

```bash
mkdir -p ~/.config/autostart

# For AppImage
cat > ~/.config/autostart/trayrunner.desktop <<EOF
[Desktop Entry]
Type=Application
Name=TrayRunner
Exec=/full/path/to/TrayRunner-x86_64.AppImage
X-GNOME-Autostart-enabled=true
EOF

# For system installation
cat > ~/.config/autostart/trayrunner.desktop <<EOF
[Desktop Entry]
Type=Application
Name=TrayRunner
Exec=trayrunner
X-GNOME-Autostart-enabled=true
EOF
```

### Systemd User Service (Advanced)

```bash
# Create user service
mkdir -p ~/.config/systemd/user

cat > ~/.config/systemd/user/trayrunner.service <<EOF
[Unit]
Description=TrayRunner
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/local/bin/trayrunner
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF

# Enable and start
systemctl --user enable trayrunner.service
systemctl --user start trayrunner.service
```

## 🔧 Manual Configuration

### Configuration File

TrayRunner stores its configuration in:
- **Location**: `~/.config/trayrunner/commands.yaml`
- **Format**: YAML with comments preserved
- **Backup**: Automatic backups on save

### Example Configuration

```yaml
items:
  - type: item
    label: "Open Terminal"
    cmd: "gnome-terminal"
    terminal: false
    confirm: false
    env: {}

  - type: separator

  - type: group
    label: "Development"
    items:
      - type: item
        label: "VS Code"
        cmd: "code"
        terminal: false
        confirm: false
        env: {}
      
      - type: item
        label: "Git Status"
        cmd: "git status"
        terminal: true
        confirm: false
        env: {}

  - type: separator

  - type: item
    label: "Shutdown"
    cmd: "sudo shutdown -h now"
    terminal: false
    confirm: true
    env: {}
```

### Environment Variables

You can set environment variables for commands:

```yaml
- type: item
  label: "Custom Project"
  cmd: "cd /path/to/project && make"
  terminal: true
  env:
    PROJECT_ROOT: "/path/to/project"
    BUILD_TYPE: "release"
```

## 🗑️ Uninstallation

### AppImage

Simply delete the AppImage file:
```bash
rm TrayRunner-x86_64.AppImage
```

### System Installation

```bash
# Remove from system
sudo rm -rf /usr/local/bin/trayrunner*
sudo rm -rf /usr/local/share/trayrunner
sudo rm -rf /usr/share/applications/trayrunner.desktop

# Remove user configuration (optional)
rm -rf ~/.config/trayrunner
```

### pipx Installation

```bash
pipx uninstall trayrunner
```

### Remove Autostart

```bash
rm ~/.config/autostart/trayrunner.desktop
# or
systemctl --user disable trayrunner.service
```

## 🔍 Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **Tray icon not visible** | Install AppIndicator: `sudo apt install libayatana-appindicator3-1` |
| **Permission denied** | Check file permissions: `chmod +x trayrunner` |
| **Import errors** | Install dependencies: `sudo apt install python3-gi gir1.2-gtk-3.0` |
| **GUI won't start** | Install GUI dependencies: `pip install PySide6` |
| **Commands not working** | Check command paths and permissions |

### Debug Mode

Run with debug logging:
```bash
# Core application
trayrunner --debug

# GUI editor
trayrunner-gui --debug
```

### Log Files

- **Core logs**: `~/.local/state/trayrunner/run.log`
- **GUI logs**: `~/.local/state/trayrunner/gui-debug.log`
- **System logs**: `journalctl --user -u trayrunner`

## 🔧 Advanced Configuration

### Custom Icon

Replace the default icon:
```bash
# Copy your icon
cp my-icon.png ~/.config/trayrunner/icon.png

# Update configuration
trayrunner --set-icon ~/.config/trayrunner/icon.png
```

### Custom Commands

Add system-specific commands:
```bash
# Create custom command script
cat > ~/.local/bin/my-command.sh <<EOF
#!/bin/bash
# Your custom logic here
EOF

chmod +x ~/.local/bin/my-command.sh

# Add to TrayRunner config
trayrunner-gui
```

### Integration with Other Tools

TrayRunner can integrate with:
- **Window Managers**: i3, Awesome, Openbox
- **Desktop Environments**: GNOME, KDE, XFCE
- **System Monitors**: htop, btop, glances
- **Development Tools**: VS Code, Vim, Emacs

## 📚 Additional Resources

- [Main README](README.md) - Quick start guide
- [Contributing Guide](CONTRIBUTING.md) - Development setup
- [GitHub Issues](https://github.com/Zmk55/trayrunner/issues) - Bug reports
- [GitHub Discussions](https://github.com/Zmk55/trayrunner/discussions) - Questions and ideas
