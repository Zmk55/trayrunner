# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

TrayRunner is a Linux system tray application that displays customizable command menus. It consists of two main components:
1. **Tray App** (`src/trayrunner/`) - GTK-based system tray that loads commands from YAML config
2. **GUI Editor** (`gui/trayrunner_gui/`) - PySide6-based visual config editor

The project uses PyInstaller + linuxdeploy to build AppImages containing both components.

## Development Commands

### Build & Run
```bash
# Build AppImage (recommended)
make appimage
# OR
bash scripts/build_appimage.sh

# Run tray app locally (requires GTK dependencies)
python -m trayrunner.app

# Run GUI editor locally
python -m trayrunner_gui.app

# Run with virtualenv
source .venv/bin/activate
python -m trayrunner.app
```

### Testing
```bash
# Run all tests
make test
# OR
python3 -m pytest tests/ -v

# Run specific test
pytest tests/test_yaml_roundtrip.py -v
python3 tests/test_reload_socket.py
```

### Code Formatting
```bash
make fmt
# Uses black (--line-length 100) and isort on src/, gui/, tests/
```

### Cleanup
```bash
make clean
# Removes build_appimage/, dist/, build/, *.spec, __pycache__, .pytest_cache/
```

## Architecture

### Two-Process Architecture
- **Tray App Process**: Runs `src/trayrunner/app.py` using system Python + GTK (not bundled with PyInstaller to avoid GTK conflicts)
- **GUI Editor Process**: Separate PySide6 application bundled with PyInstaller as `trayrunner-gui` binary

### Inter-Process Communication (IPC)
The GUI and tray communicate via Unix domain socket at `~/.local/state/trayrunner/reload.sock`:
- **GUI → Tray**: Sends "RELOAD" command after saving config changes
- **Tray → GUI**: Responds with JSON `{"ok": true/false}`
- Implementation: `gui/trayrunner_gui/services/reloader.py` (client) and `src/trayrunner/app.py:_run_reload_server()` (server)

### Singleton Pattern
Both components enforce single-instance:
- **Tray**: Uses `fcntl.flock()` on `~/.local/state/trayrunner/trayrunner.lock`
- **GUI**: Uses `QLocalServer` with key "trayrunner_gui_singleton" to detect/raise existing windows

### Configuration Management
- **User config**: `~/.config/trayrunner/commands.yaml`
- **Default template**: `config/default.yaml`
- **Test config**: `config/test.yaml` (gitignored)
- **Schema**: Pydantic models in `gui/trayrunner_gui/models/schema.py` define three node types:
  - `ItemNode`: Executable command with label, cmd, terminal, confirm, env, working_dir
  - `GroupNode`: Submenu containing nested items
  - `SeparatorNode`: Visual separator
- **YAML handling**: Uses `ruamel.yaml` to preserve comments/formatting during round-trip edits

### GUI Editor Components
- **MainWindow** (`main_window.py`): QSplitter with TreePanel (left) and EditorPanel (right)
- **TreePanel** (`tree_panel.py`): Qt tree view with drag-and-drop reordering
- **EditorPanel** (`editor_panel.py`): Dynamic form for editing selected node properties
- **Services**:
  - `file_watch.py`: QFileSystemWatcher detects external config changes
  - `save_coordinator.py`: Manages atomic saves with timestamped backups
  - `reloader.py`: Triggers tray app reload via socket/CLI fallback
  - `gui_logger.py`: Debug logging to `~/.local/state/trayrunner/gui-debug.log`

### AppImage Build Process
1. PyInstaller bundles GUI as single `trayrunner-gui` binary
2. Tray app source copied to `AppDir/usr/share/trayrunner/` (not bundled)
3. Shell wrapper `trayrunner` invokes system Python on the source
4. linuxdeploy packages AppDir with both executables
5. Output: `build_appimage/out/TrayRunner-$(uname -m).AppImage`

Key insight: Tray app uses system GTK to avoid library conflicts, while GUI is fully bundled.

## File Locations

### Source Structure
```
src/trayrunner/app.py       # Tray app entry point + main classes
gui/trayrunner_gui/
  ├── app.py                # GUI entry point with singleton logic
  ├── main_window.py        # Main Qt window
  ├── tree_panel.py         # Config tree with drag-drop
  ├── editor_panel.py       # Node property editor
  ├── models/
  │   ├── schema.py         # Pydantic config models
  │   ├── yaml_io.py        # YAML load/save with ruamel.yaml
  │   └── validators.py     # Config validation logic
  └── services/
      ├── reloader.py       # IPC to trigger tray reload
      ├── file_watch.py     # Detect external file changes
      └── save_coordinator.py # Atomic saves + backups
```

### Runtime/User Files
```
~/.config/trayrunner/commands.yaml          # User config
~/.local/state/trayrunner/
  ├── reload.sock                           # IPC socket
  ├── trayrunner.lock                       # Single-instance lock
  ├── run.log                               # Tray execution log
  ├── gui-debug.log                         # GUI debug log
  └── gui-launch.log                        # GUI startup diagnostics
```

## Important Development Notes

### GTK Dependency Handling
- Tray app requires: `python3-gi gir1.2-gtk-3.0 libayatana-appindicator3-1 gir1.2-ayatanaappindicator3-0.1`
- These must be system packages; never bundle GTK in PyInstaller
- AppImage uses system Python to avoid GTK conflicts

### GUI Launcher Logic
The tray app's `open_config_gui()` method (src/trayrunner/app.py:489-569) implements:
1. Fast path: Try `--raise-only` flag to activate existing window (200ms timeout)
2. If no existing window, launch new process with `start_new_session=True` for detachment
3. Wait 1 second to catch immediate failures
4. All operations logged to `gui-launch.log` for debugging

### Testing Reload IPC
```bash
# Terminal 1: Run tray app
python -m trayrunner.app

# Terminal 2: Test reload from CLI
python -m trayrunner.app --reload

# OR use the test script
python tests/test_reload_socket.py
```

### Building for Compatibility
- Build on **Ubuntu 20.04** for maximum glibc compatibility
- Supports x86_64 and aarch64 (Raspberry Pi)
- Use `make tools` to fetch linuxdeploy binaries automatically

### Config Editor Behavior
- Auto-saves create timestamped backups in same directory
- External changes trigger reload prompt (file watcher)
- Drag-drop reordering preserves YAML structure
- Validation runs in real-time, shown in bottom dock panel
- Hitting "Save" automatically triggers tray reload via socket

### Icon Handling
- Tray icon: `src/trayrunner/icons/Gear.ico` (fallback to "applications-system")
- GUI icon: `gui/assets/icon.png`
- AppImage icon: Embedded in desktop file, converted from PNG/ICO at build time

## Common Patterns

### Adding New Menu Item Types
1. Update Pydantic schema in `gui/trayrunner_gui/models/schema.py`
2. Add rendering logic in `src/trayrunner/app.py:create_menu_item()`
3. Update GUI editor panel in `gui/trayrunner_gui/editor_panel.py`
4. Add validation in `gui/trayrunner_gui/models/validators.py`

### Debugging AppImage Issues
1. Extract AppImage: `./TrayRunner-x86_64.AppImage --appimage-extract`
2. Check structure: `ls squashfs-root/usr/bin/`
3. Run manually: `APPDIR=$PWD/squashfs-root squashfs-root/usr/bin/trayrunner`
4. Check logs: `~/.local/state/trayrunner/*.log`

### Environment Variables in AppImage Context
- `APPDIR`: Set when running inside AppImage, used to locate bundled GUI binary
- `QT_DEBUG_PLUGINS`: Set to "0" by tray when launching GUI to reduce noise
