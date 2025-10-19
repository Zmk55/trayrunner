# TrayRunner

A system tray application for Linux with customizable command menus and a visual GUI editor.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org/)

[![Download Latest AppImage](https://img.shields.io/badge/Download-Latest%20AppImage-green.svg)](https://github.com/Zmk55/trayrunner/releases)

## 🚀 Quick Start

### Download
[Get the latest AppImage](https://github.com/Zmk55/trayrunner/releases)

### Run
```bash
chmod +x TrayRunner-x86_64.AppImage
./TrayRunner-x86_64.AppImage
```

### Configure
Right-click the tray icon → **Settings → Open Config GUI**

## ✅ Tested Systems

- Ubuntu 20.04 / 22.04 / 24.04 (x86_64)
- Linux Mint 20-22 (x86_64)
- Debian 12 (x86_64)
- Raspberry Pi OS (Desktop) (aarch64)

**Architecture Support:**
- **x86_64**: Most desktop and laptop computers
- **aarch64**: Raspberry Pi 4/5, ARM-based systems

**Optional**: If tray icon doesn't appear:
```bash
sudo apt install libayatana-appindicator3-1
```

## 🎯 Features

- **System Tray Integration**: Clean AppIndicator with customizable icon
- **Visual GUI Editor**: No more manual YAML editing
- **Live Validation**: Real-time error checking and suggestions
- **Auto-Reload**: Changes apply immediately
- **Smart Backup**: Automatic timestamped backups
- **File Watching**: Detects external changes to your config

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| **No tray icon** | `sudo apt install libayatana-appindicator3-1` |
| **AppImage won't run** | `chmod +x TrayRunner-*.AppImage` |
| **Permission denied** | `chmod +x TrayRunner-*.AppImage` |
| **Config didn't update** | Click Save in GUI |
| **GUI won't open** | Update to latest AppImage |

## ⚙️ Autostart (Optional)

To launch TrayRunner on login:
```bash
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/trayrunner.desktop <<EOF
[Desktop Entry]
Type=Application
Name=TrayRunner
Exec=/full/path/to/TrayRunner-*.AppImage
X-GNOME-Autostart-enabled=true
EOF
```

## 📂 Configuration

- **Location**: `~/.config/trayrunner/commands.yaml`
- **Edit**: Use the GUI (recommended) or edit manually
- **Backup**: Automatic backups created on save

**📖 [INSTALL.md](INSTALL.md)** - Traditional installation methods for advanced users

## 💻 For Developers

Building from source requires Linux, Python 3.9+, Qt 6, PySide6.

**📖 [CONTRIBUTING.md](CONTRIBUTING.md)** - Complete developer guide including:
- Development setup and requirements
- Building AppImage with linuxdeploy + PyInstaller
- Common build issues and solutions
- Testing and debugging guidance
- Code style and contribution workflow

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.