# TrayRunner Config GUI

A modern PySide6-based GUI editor for TrayRunner configuration files. No more manual YAML editing required!

## Features

- **Visual Tree Editor**: Edit your menu structure with drag-and-drop
- **Live Validation**: Real-time error checking with helpful messages
- **Comment Preservation**: Maintains your YAML comments and formatting
- **Backup Management**: Automatic timestamped backups on save
- **Reload Integration**: Seamlessly reload TrayRunner configuration
- **File Watching**: Detects external changes to your config
- **Modern UI**: Clean, intuitive interface with dark/light theme support

## Installation

### Option 1: pip/pipx (Recommended)

```bash
# Install with pipx (isolated environment)
pipx install .[gui]

# Or install with pip
pip install .[gui]
```

### Option 2: AppImage (Standalone)

Download the latest AppImage from the [Releases](https://github.com/yourusername/trayrunner/releases) page:

```bash
# Make executable and run
chmod +x trayrunner-gui-x86_64.AppImage
./trayrunner-gui-x86_64.AppImage
```

## Usage

### Starting the GUI

```bash
# From command line
trayrunner-gui

# Or from TrayRunner tray menu
# Right-click tray icon → "Open Config GUI"
```

### Basic Workflow

1. **Load Configuration**: The GUI automatically loads `~/.config/trayrunner/commands.yaml`
2. **Edit Items**: Use the tree view to add, edit, or remove menu items
3. **Configure Properties**: Use the editor panel to set labels, commands, and options
4. **Validate**: Check the validation panel for any errors
5. **Save**: Save your changes (automatic backup created)
6. **Reload**: Use the "Reload TrayRunner" button to apply changes

### Editor Features

#### Item Editor
- **Label**: Display name in the menu
- **Command**: Command to execute
- **Terminal**: Run command in terminal emulator
- **Confirm**: Show confirmation dialog before execution
- **Environment Variables**: Set custom environment variables

#### Group Editor
- **Label**: Submenu title
- **Items**: Managed in the tree view (drag-and-drop reordering)

#### Separator
- Visual dividers in the menu (no configuration needed)

### Keyboard Shortcuts

- `Ctrl+N`: New configuration
- `Ctrl+O`: Open configuration
- `Ctrl+S`: Save configuration
- `Ctrl+Z`: Undo (planned)
- `Ctrl+Y`: Redo (planned)
- `Delete`: Delete selected item
- `F5`: Reload TrayRunner

### Menu Actions

#### File Menu
- **New**: Create new configuration
- **Open**: Load existing configuration
- **Save**: Save current configuration
- **Save As**: Save to different file
- **Revert**: Discard unsaved changes

#### Edit Menu
- **Add Item**: Create new menu item
- **Add Group**: Create new submenu
- **Add Separator**: Add visual divider
- **Duplicate**: Copy selected item
- **Delete**: Remove selected item

#### Tools Menu
- **Reload TrayRunner**: Apply configuration changes
- **Preferences**: Configure GUI settings

## Configuration

### Default Paths

- **Configuration**: `~/.config/trayrunner/commands.yaml`
- **Backups**: `~/.config/trayrunner/commands.yaml.bak-YYYYmmdd-HHMMSS`
- **Logs**: `~/.local/state/trayrunner/run.log`
- **GUI Settings**: `~/.config/trayrunner/gui-settings.json`

### Preferences

Access via `Tools → Preferences`:

- **Config Path**: Override default configuration file location
- **Auto-reload**: Automatically reload TrayRunner after save
- **File Watcher**: Monitor for external file changes
- **Auto-save**: Periodic automatic saves

## Troubleshooting

### Common Issues

#### GUI Won't Start
```bash
# Check dependencies
python3 -c "import PySide6, ruamel.yaml, pydantic"

# Install missing dependencies
pip install PySide6 ruamel.yaml pydantic
```

#### TrayRunner Not Found
```bash
# Check if TrayRunner is installed
trayrunner --version

# Install TrayRunner first
./install.sh
```

#### Reload Not Working
```bash
# Check if TrayRunner is running
trayrunner status

# Start TrayRunner if needed
trayrunner start
```

#### File Permission Errors
```bash
# Fix config directory permissions
chmod -R 755 ~/.config/trayrunner
```

### Debug Mode

Run with debug output:
```bash
PYTHONPATH=. python3 -m trayrunner_gui.app
```

### Log Files

Check these locations for error details:
- GUI logs: Check terminal output
- TrayRunner logs: `~/.local/state/trayrunner/run.log`

## Development

### Building from Source

```bash
# Clone repository
git clone https://github.com/yourusername/trayrunner.git
cd trayrunner

# Install in development mode
pip install -e .[gui]

# Run GUI
trayrunner-gui
```

### Building AppImage

```bash
# Install build dependencies
pip install pyinstaller

# Build AppImage
bash scripts/build_appimage.sh
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/trayrunner/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/trayrunner/discussions)
- **Documentation**: [Wiki](https://github.com/yourusername/trayrunner/wiki)
