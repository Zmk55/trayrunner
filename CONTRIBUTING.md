# Contributing to TrayRunner

Thank you for your interest in contributing to TrayRunner! This guide will help you get started with development.

## 🛠️ Development Setup

### Prerequisites

- Python 3.8+
- Git
- System dependencies (see below)

### System Dependencies

```bash
# Ubuntu/Debian/Mint
sudo apt install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo gir1.2-gtk-3.0 libnotify-bin

# For GUI development
sudo apt install python3-pip
```

### Development Installation

```bash
# Clone the repository
git clone https://github.com/Zmk55/trayrunner.git
cd trayrunner

# Install in development mode with GUI support
pip install -e .[gui]

# Run the core application
trayrunner

# Run the GUI editor
trayrunner-gui
```

## 🏗️ Building AppImage

To build the AppImage for distribution:

```bash
# Install build dependencies
pip install pyinstaller

# Download linuxdeploy tools (if not present)
wget https://github.com/linuxdeploy/linuxdeploy/releases/download/continuous/linuxdeploy-x86_64.AppImage
chmod +x linuxdeploy-x86_64.AppImage

# Build the AppImage
./scripts/build_appimage.sh
```

The build script will:
- Freeze the GUI with PyInstaller
- Bundle Qt libraries with linuxdeploy
- Create `TrayRunner-x86_64.AppImage`
- Generate SHA256 checksums

## 🧪 Testing

### Manual Testing

1. **Core Application**:
   ```bash
   python3 src/trayrunner/app.py
   ```
   - Verify tray icon appears
   - Test menu items work
   - Check reload functionality

2. **GUI Editor**:
   ```bash
   python3 -m gui.trayrunner_gui.app
   ```
   - Test load/save operations
   - Verify validation works
   - Test duplicate/delete functions
   - Check auto-reload integration

3. **AppImage Testing**:
   ```bash
   ./TrayRunner-x86_64.AppImage
   ```
   - Test on clean system
   - Verify both core and GUI work
   - Check tray menu integration

### Test Systems

- Ubuntu 20.04 LTS (baseline)
- Ubuntu 22.04 LTS
- Debian 12
- Linux Mint 21

## 📁 Project Structure

```
trayrunner/
├── src/trayrunner/           # Core tray application
│   ├── app.py                # Main application logic
│   └── icons/                  # Tray icons
├── gui/trayrunner_gui/       # GUI editor
│   ├── app.py                # GUI entry point
│   ├── main_window.py         # Main window
│   ├── tree_panel.py         # Tree view
│   ├── editor_panel.py        # Property editor
│   ├── models/                # Data models
│   └── services/              # Services (logging, reload, etc.)
├── scripts/                   # Build scripts
│   └── build_appimage.sh      # AppImage builder
├── config/                    # Default configuration
└── requirements.txt           # Python dependencies
```

## 🔧 Code Architecture

### Core Application (`src/trayrunner/`)
- **TrayRunner**: Main application class
- **ConfigLoader**: YAML configuration handling
- **CommandRunner**: Command execution and logging

### GUI Editor (`gui/trayrunner_gui/`)
- **MainWindow**: Main application window
- **TreePanel**: Hierarchical tree view
- **EditorPanel**: Property editing interface
- **Models**: Pydantic schemas for validation
- **Services**: Logging, file watching, reload coordination

### Key Design Patterns
- **MVC Architecture**: Clear separation of concerns
- **Signal/Slot**: Qt-based event handling
- **Observer Pattern**: File watching and validation
- **Factory Pattern**: Node creation and cloning

## 🐛 Debugging

### Debug Logging

The GUI includes comprehensive debug logging:

```bash
# View debug logs
tail -f ~/.local/state/trayrunner/gui-debug.log

# Or use the GUI
Tools → Open GUI Debug Log
```

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **GTK Issues**: Check AppIndicator installation
3. **Qt Issues**: Verify PySide6 installation
4. **File Permissions**: Check config directory permissions

## 📝 Pull Request Guidelines

### Before Submitting

- [ ] Test on multiple systems (Ubuntu, Debian, Mint)
- [ ] Update documentation if needed
- [ ] Add tests for new features
- [ ] Ensure AppImage still builds
- [ ] Check for linting errors

### Commit Messages

Use clear, descriptive commit messages:
- `feat: add duplicate functionality`
- `fix: resolve context menu index issue`
- `docs: simplify README for end users`

### Code Style

- Follow existing code patterns
- Add type hints where appropriate
- Include docstrings for new functions
- Use meaningful variable names

## 🚀 Release Process

### For Maintainers

1. **Update Version**:
   ```bash
   # Update pyproject.toml version
   # Update CHANGELOG.md
   ```

2. **Build AppImage**:
   ```bash
   ./scripts/build_appimage.sh
   ```

3. **Test Release**:
   - Test on Ubuntu 20.04, 22.04, Debian 12
   - Verify both core and GUI work
   - Check tray integration

4. **Create Release**:
   - Tag the release: `git tag v1.2.0`
   - Push tag: `git push origin v1.2.0`
   - Upload AppImage to GitHub releases
   - Include SHA256 checksums

### Release Checklist

- [ ] Version updated in pyproject.toml
- [ ] CHANGELOG.md updated
- [ ] AppImage builds successfully
- [ ] Tested on target systems
- [ ] GitHub release created
- [ ] SHA256SUMS included

## 🤝 Getting Help

- **Issues**: Use GitHub Issues for bug reports
- **Discussions**: Use GitHub Discussions for questions
- **Code**: Submit Pull Requests for contributions

## 📄 License

By contributing to TrayRunner, you agree that your contributions will be licensed under the MIT License.
