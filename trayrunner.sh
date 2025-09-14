#!/bin/bash

# TrayRunner Management Script
# Usage: ./trayrunner.sh [start|stop|restart|status|version|enable-autostart|disable-autostart]

VERSION="1.0.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_PATH="$SCRIPT_DIR/src/trayrunner/app.py"
AUTOSTART_FILE="$HOME/.config/autostart/trayrunner.desktop"

case "$1" in
    start)
        echo "Starting TrayRunner..."
        if pgrep -f "python3.*trayrunner" > /dev/null; then
            echo "TrayRunner is already running"
        else
            python3 "$APP_PATH" &
            echo "TrayRunner started"
        fi
        ;;
    stop)
        echo "Stopping TrayRunner..."
        pkill -f "python3.*trayrunner"
        echo "TrayRunner stopped"
        ;;
    restart)
        echo "Restarting TrayRunner..."
        pkill -f "python3.*trayrunner"
        sleep 1
        python3 "$APP_PATH" &
        echo "TrayRunner restarted"
        ;;
    status)
        if pgrep -f "python3.*trayrunner" > /dev/null; then
            echo "TrayRunner is running"
            pgrep -f "python3.*trayrunner" | xargs ps -p
        else
            echo "TrayRunner is not running"
        fi
        ;;
    enable-autostart)
        echo "Enabling autostart..."
        mkdir -p "$HOME/.config/autostart"
        cp "$SCRIPT_DIR/autostart/trayrunner.desktop" "$AUTOSTART_FILE"
        echo "Autostart enabled. TrayRunner will start automatically on login."
        ;;
    disable-autostart)
        echo "Disabling autostart..."
        rm -f "$AUTOSTART_FILE"
        echo "Autostart disabled."
        ;;
    version)
        echo "TrayRunner v$VERSION"
        echo "A Python 3 tray application for Linux using AppIndicator"
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|version|enable-autostart|disable-autostart}"
        echo ""
        echo "Commands:"
        echo "  start           - Start TrayRunner"
        echo "  stop            - Stop TrayRunner"
        echo "  restart         - Restart TrayRunner"
        echo "  status          - Check if TrayRunner is running"
        echo "  version         - Show version information"
        echo "  enable-autostart - Enable automatic startup on login"
        echo "  disable-autostart- Disable automatic startup on login"
        exit 1
        ;;
esac
