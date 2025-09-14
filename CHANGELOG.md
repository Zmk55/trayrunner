# Changelog

All notable changes to TrayRunner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-09-13

### Added
- Initial release of TrayRunner
- System tray integration using AppIndicator3
- YAML-based configuration system
- Support for menu items, separators, and submenus
- Command execution with optional confirmation dialogs
- Terminal execution mode with multiple emulator support
- Custom environment variables per command
- Notification system with libnotify and notify-send fallback
- Comprehensive logging to `~/.local/state/trayrunner/run.log`
- Built-in utility menu items (Reload Config, Open Config, Show Log, Quit)
- Single-instance protection to prevent multiple tray icons
- Autostart support for automatic login startup
- Global command-line management tool (`trayrunner` command)
- Automated installation script
- Comprehensive documentation and examples

### Features
- **Menu Configuration**: Support for flat items, separators, and nested submenus
- **Command Execution**: Robust command execution with error handling
- **Terminal Support**: Multiple terminal emulator fallback (x-terminal-emulator, gnome-terminal, xterm, konsole)
- **Notifications**: Start notifications and error reporting
- **Logging**: Detailed execution logging with timestamps
- **Configuration Management**: XDG-compliant config directory support
- **Autostart**: Desktop file for automatic startup on login
- **Management**: Command-line tool for easy control

### Technical Details
- Python 3.6+ compatibility
- GTK 3.0 and AppIndicator3 integration
- PyYAML for configuration parsing
- Cross-platform notification support
- File locking for single-instance protection
- Comprehensive error handling and user feedback

### Installation
- Automated installation script with dependency management
- Manual installation instructions
- Support for Linux Mint, Ubuntu, and Debian-based systems
- Global PATH integration for easy command access
