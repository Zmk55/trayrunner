# TrayRunner

A system tray application for Linux with customizable command menus and a visual GUI editor.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Linux](https://img.shields.io/badge/platform-Linux-lightgrey.svg)](https://www.linux.org/)

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

- Ubuntu 20.04 / 22.04 / 24.04
- Linux Mint 20-22
- Debian 12
- Raspberry Pi OS (Desktop)

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

## 💻 For Developers

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, building, and contributing guidelines.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.