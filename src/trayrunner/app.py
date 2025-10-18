#!/usr/bin/env python3
"""
TrayRunner - A Python 3 tray app for Linux Mint using AppIndicator
Shows a system tray icon with menu items from YAML config

Version: 1.0.0
Author: TrayRunner Team
License: MIT
"""

import os
import sys
import shlex
import subprocess
import yaml
import logging
import fcntl
import tempfile
import argparse
import time

__version__ = "1.0.0"
from pathlib import Path
from typing import Dict, List, Any, Optional

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("AppIndicator3", "0.1")
from gi.repository import Gtk, GdkPixbuf, AppIndicator3

try:
    gi.require_version("Notify", "0.7")
    from gi.repository import Notify
    Notify.init("TrayRunner")
    NOTIFY_AVAILABLE = True
except (ImportError, ValueError):
    NOTIFY_AVAILABLE = False


class ConfigLoader:
    """Handles loading and validation of YAML configuration"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".config" / "trayrunner"
        self.default_config = Path(__file__).parent.parent.parent / "config" / "commands.yaml"
        self.user_config = self.config_dir / "commands.yaml"
        
    def ensure_user_config(self):
        """Ensure user config exists, copy default if missing"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.user_config.exists() and self.default_config.exists():
            import shutil
            shutil.copy2(self.default_config, self.user_config)
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from user config or fallback to default"""
        self.ensure_user_config()
        
        config_path = self.user_config if self.user_config.exists() else self.default_config
        if not config_path.exists():
            return {"items": []}
            
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f) or {}
                return config if isinstance(config, dict) else {"items": []}
        except (yaml.YAMLError, IOError) as e:
            self._show_error(f"Failed to load config: {e}")
            return {"items": []}
    
    def validate_item(self, item: Dict[str, Any]) -> bool:
        """Basic validation of menu item"""
        if item.get("type") == "item":
            return "label" in item and "cmd" in item
        elif item.get("type") == "group":
            return "label" in item and "items" in item
        elif item.get("type") == "separator":
            return True
        return False
    
    def _show_error(self, message: str):
        """Show error notification"""
        self._notify("TrayRunner Error", message, "error")
    
    def _notify(self, title: str, message: str, urgency: str = "normal"):
        """Send notification"""
        if NOTIFY_AVAILABLE:
            try:
                notification = Notify.Notification.new(title, message)
                notification.set_urgency(getattr(Notify.Urgency, urgency.upper(), Notify.Urgency.NORMAL))
                notification.show()
            except Exception as e:
                print(f"Notification error: {e}")
                # Fallback to notify-send
                subprocess.run(["notify-send", "-u", urgency, title, message], 
                             capture_output=True)
        else:
            subprocess.run(["notify-send", "-u", urgency, title, message], 
                         capture_output=True)


class CommandRunner:
    """Handles command execution and logging"""
    
    def __init__(self):
        self.log_dir = Path.home() / ".local" / "state" / "trayrunner"
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "run.log"
        
        # Setup logging
        logging.basicConfig(
            filename=self.log_file,
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
    
    def run_command(self, item: Dict[str, Any], parent_window=None) -> None:
        """Execute a command with optional confirmation"""
        if item.get("confirm", False):
            if not self._confirm_execution(item["label"], parent_window):
                return
        
        # Merge environment variables
        env = os.environ.copy()
        if "env" in item:
            env.update(item["env"])
        
        # Prepare command
        cmd = item["cmd"]
        if item.get("terminal", False):
            terminal_cmd = self._get_terminal_command(cmd)
            if terminal_cmd:
                cmd = terminal_cmd
            else:
                self._notify("TrayRunner Error", "No terminal emulator found", "error")
                return
        
        # Show start notification
        self._notify("TrayRunner", f"Started: {item['label']}")
        
        try:
            # Execute command
            if item.get("terminal", False):
                # For terminal commands, use shell=True
                process = subprocess.Popen(cmd, shell=True, env=env)
            else:
                # Try to split command, fallback to shell if needed
                try:
                    cmd_parts = shlex.split(cmd)
                    process = subprocess.Popen(cmd_parts, env=env, 
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE)
                except (ValueError, FileNotFoundError):
                    process = subprocess.Popen(cmd, shell=True, env=env,
                                            stdout=subprocess.PIPE, 
                                            stderr=subprocess.PIPE)
            
            # Log the execution
            logging.info(f"Started command: {item['label']} -> {cmd}")
            
            # For non-terminal commands, check exit status
            if not item.get("terminal", False):
                stdout, stderr = process.communicate()
                exit_code = process.returncode
                
                logging.info(f"Command finished: {item['label']} (exit code: {exit_code})")
                
                if exit_code != 0 and stderr:
                    error_msg = stderr.decode('utf-8', errors='ignore').strip()
                    if len(error_msg) > 200:
                        error_msg = error_msg[:200] + "..."
                    self._notify("TrayRunner Error", 
                               f"Command failed: {item['label']}\n{error_msg}", "error")
        
        except Exception as e:
            logging.error(f"Failed to execute {item['label']}: {e}")
            self._notify("TrayRunner Error", f"Failed to execute: {item['label']}", "error")
    
    def _get_terminal_command(self, cmd: str) -> Optional[str]:
        """Get terminal command for execution"""
        terminals = ["x-terminal-emulator", "gnome-terminal", "xterm", "konsole"]
        
        for terminal in terminals:
            try:
                subprocess.run(["which", terminal], check=True, capture_output=True)
                if terminal == "x-terminal-emulator":
                    return f"{terminal} -e sh -lc '{cmd}'"
                elif terminal == "gnome-terminal":
                    return f"{terminal} -- bash -lc '{cmd}'"
                elif terminal == "xterm":
                    return f"{terminal} -e bash -lc '{cmd}'"
                elif terminal == "konsole":
                    return f"{terminal} -e bash -lc '{cmd}'"
            except subprocess.CalledProcessError:
                continue
        return None
    
    def _confirm_execution(self, label: str, parent_window) -> bool:
        """Show confirmation dialog"""
        dialog = Gtk.MessageDialog(
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            message_format=f"Execute command: {label}?"
        )
        dialog.set_title("Confirm Execution")
        response = dialog.run()
        dialog.destroy()
        return response == Gtk.ResponseType.YES
    
    def _notify(self, title: str, message: str, urgency: str = "normal"):
        """Send notification"""
        if NOTIFY_AVAILABLE:
            try:
                notification = Notify.Notification.new(title, message)
                notification.set_urgency(getattr(Notify.Urgency, urgency.upper(), Notify.Urgency.NORMAL))
                notification.show()
            except Exception as e:
                print(f"Notification error: {e}")
                # Fallback to notify-send
                subprocess.run(["notify-send", "-u", urgency, title, message], 
                             capture_output=True)
        else:
            subprocess.run(["notify-send", "-u", urgency, title, message], 
                         capture_output=True)


class TrayRunner:
    """Main application class"""
    
    def __init__(self):
        self.config_loader = ConfigLoader()
        self.command_runner = CommandRunner()
        self.menu = None
        self.indicator = None
        
        # Setup reload trigger file path
        self.reload_trigger_file = Path.home() / ".local" / "state" / "trayrunner" / "reload.trigger"
        self.reload_trigger_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Notifications are already initialized at module level
    
    def create_icon(self) -> GdkPixbuf.Pixbuf:
        """Create a simple embedded icon"""
        # Simple 24x24 monochrome icon (gear/settings symbol)
        icon_data = """
        <svg width="24" height="24" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
            <path fill="#333" d="M12 15.5A3.5 3.5 0 0 1 8.5 12A3.5 3.5 0 0 1 12 8.5a3.5 3.5 0 0 1 3.5 3.5a3.5 3.5 0 0 1-3.5 3.5m7.43-2.53c.04-.32.07-.64.07-.97c0-.33-.03-.66-.07-1l2.11-1.63c.19-.15.24-.42.12-.64l-2-3.46c-.12-.22-.39-.31-.61-.22l-2.49 1c-.52-.39-1.06-.73-1.69-.98l-.37-2.65A.506.506 0 0 0 14 2h-4c-.25 0-.46.18-.5.42l-.37 2.65c-.63.25-1.17.59-1.69.98l-2.49-1c-.22-.09-.49 0-.61.22l-2 3.46c-.13.22-.07.49.12.64L4.57 11c-.04.34-.07.67-.07 1c0 .33.03.65.07.97l-2.11 1.66c-.19.15-.25.42-.12.64l2 3.46c.12.22.39.3.61.22l2.49-1.01c.52.4 1.06.74 1.69.99l.37 2.65c.04.24.25.42.5.42h4c.25 0 .46-.18.5-.42l.37-2.65c.63-.26 1.17-.59 1.69-.99l2.49 1.01c.22.08.49 0 .61-.22l2-3.46c.12-.22.07-.49-.12-.64l-2.11-1.66Z"/>
        </svg>
        """
        
        # Convert SVG to pixbuf (simplified approach)
        # For a real implementation, you'd use librsvg or create a PNG
        # Here we'll create a simple pixbuf with a gear-like pattern
        pixbuf = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 24, 24)
        pixbuf.fill(0x00000000)  # Transparent
        
        # Create a simple gear pattern (this is a placeholder)
        # In a real app, you'd load an actual PNG file
        return pixbuf
    
    def create_menu_item(self, item: Dict[str, Any], parent_window) -> Gtk.MenuItem:
        """Create a menu item from config"""
        if item["type"] == "separator":
            return Gtk.SeparatorMenuItem()
        
        elif item["type"] == "item":
            menu_item = Gtk.MenuItem(label=item["label"])
            menu_item.connect("activate", lambda w, i=item: self.command_runner.run_command(i, parent_window))
            return menu_item
        
        elif item["type"] == "group":
            menu_item = Gtk.MenuItem(label=item["label"])
            submenu = Gtk.Menu()
            
            for subitem in item.get("items", []):
                if self.config_loader.validate_item(subitem):
                    submenu.append(self.create_menu_item(subitem, parent_window))
            
            menu_item.set_submenu(submenu)
            return menu_item
        
        return Gtk.MenuItem(label="Invalid Item")
    
    def _build_settings_submenu(self) -> Gtk.MenuItem:
        """Build Settings submenu with housekeeping actions"""
        settings_item = Gtk.MenuItem(label="Settings")
        settings_menu = Gtk.Menu()
        
        # 1) Reload Config
        reload_item = Gtk.MenuItem(label="Reload Config")
        reload_item.connect("activate", self.reload_config)
        settings_menu.append(reload_item)
        
        # 2) Open Config
        open_config_item = Gtk.MenuItem(label="Open Config")
        open_config_item.connect("activate", self.open_config)
        settings_menu.append(open_config_item)
        
        # 3) Open Config GUI
        open_gui_item = Gtk.MenuItem(label="Open Config GUI")
        open_gui_item.connect("activate", self.open_config_gui)
        settings_menu.append(open_gui_item)
        
        # 4) Show Log
        show_log_item = Gtk.MenuItem(label="Show Log")
        show_log_item.connect("activate", self.show_log)
        settings_menu.append(show_log_item)
        
        settings_menu.show_all()
        settings_item.set_submenu(settings_menu)
        return settings_item
    
    def build_menu(self, parent_window):
        """Build the main menu from config"""
        if self.menu:
            self.menu.destroy()
        
        self.menu = Gtk.Menu()
        
        # Load and build menu items from config
        config = self.config_loader.load_config()
        for item in config.get("items", []):
            if self.config_loader.validate_item(item):
                self.menu.append(self.create_menu_item(item, parent_window))
        
        # Add separator
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Add Settings submenu
        settings_item = self._build_settings_submenu()
        self.menu.append(settings_item)
        
        # Add quit item
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", Gtk.main_quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        return self.menu
    
    def reload_config(self, widget):
        """Reload configuration and rebuild menu"""
        self.build_menu(None)
        self.indicator.set_menu(self.menu)
        self.command_runner._notify("TrayRunner", "Configuration reloaded")
    
    def open_config(self, widget):
        """Open config file in default editor"""
        self.config_loader.ensure_user_config()
        subprocess.run(["xdg-open", str(self.config_loader.user_config)])
    
    def show_log(self, widget):
        """Show log file"""
        if self.command_runner.log_file.exists():
            # Check file size, use tail for large files
            if self.command_runner.log_file.stat().st_size > 10000:  # 10KB
                subprocess.run(["x-terminal-emulator", "-e", "tail", "-f", str(self.command_runner.log_file)])
            else:
                subprocess.run(["xdg-open", str(self.command_runner.log_file)])
        else:
            self.command_runner._notify("TrayRunner", "No log file found")
    
    def _find_gui_binary(self, name: str = "trayrunner-gui"):
        """
        Find GUI binary in AppImage or system PATH
        
        Search order:
        1. Inside APPDIR (when running as AppImage)
        2. Next to the running binary (PyInstaller onefile)
        3. System PATH (development/installed)
        """
        import os
        import sys
        import shutil
        
        appdir = os.environ.get("APPDIR")
        
        # 1) When running as AppImage, APPDIR is set
        if appdir:
            candidate = os.path.join(appdir, "usr", "bin", name)
            if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
                logging.info(f"Found {name} in AppImage: {candidate}")
                return candidate
            else:
                # Diagnostic: GUI binary missing from AppImage
                logging.warning(f"{name} not found in AppImage at {candidate}")
                logging.warning(f"APPDIR={appdir}, checking if file exists: {os.path.isfile(candidate)}")
        
        # 2) Next to the running binary (PyInstaller onefile/unpacked)
        here = os.path.dirname(os.path.realpath(sys.argv[0]))
        candidate = os.path.join(here, name)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            logging.info(f"Found {name} next to binary: {candidate}")
            return candidate
        
        # 3) Fallback to system PATH
        candidate = shutil.which(name)
        if candidate:
            logging.info(f"Found {name} on system PATH: {candidate}")
        return candidate

    def open_config_gui(self, widget):
        """Open configuration GUI editor"""
        import subprocess
        import os
        
        exe = self._find_gui_binary("trayrunner-gui")
        if exe:
            try:
                subprocess.Popen([exe], start_new_session=True)
                self.command_runner._notify("TrayRunner", "Config GUI opened")
                logging.info(f"Launched GUI from: {exe}")
            except Exception as e:
                logging.error(f"Failed to open GUI: {e}")
                self.command_runner._notify("TrayRunner Error", f"Failed to open GUI: {e}")
        else:
            appdir = os.environ.get("APPDIR", "not set")
            logging.error(f"trayrunner-gui not found. APPDIR={appdir}")
            
            # Better error message
            if appdir != "not set":
                msg = f"GUI binary missing from AppImage.\nAPPDIR={appdir}\nPlease download the complete AppImage."
            else:
                msg = "Could not locate 'trayrunner-gui'.\nIf not using AppImage, install with: pipx install .[gui]"
            
            self.command_runner._notify("TrayRunner GUI Not Found", msg, "normal")
    
    def check_reload_trigger(self):
        """Check for reload trigger file and reload if found"""
        if self.reload_trigger_file.exists():
            try:
                # Remove trigger file first
                self.reload_trigger_file.unlink()
                # Reload configuration
                self.reload_config(None)
                return True
            except Exception as e:
                logging.error(f"Failed to process reload trigger: {e}")
                return False
        return False
    
    def run(self):
        """Start the application"""
        try:
            print("Starting TrayRunner...")
            
            # Create indicator
            self.indicator = AppIndicator3.Indicator.new(
                "trayrunner",
                "trayrunner",
                AppIndicator3.IndicatorCategory.APPLICATION_STATUS
            )
            print("AppIndicator created successfully")
            
            # Set icon
            icon_path = Path(__file__).parent / "icons" / "Gear.ico"
            if icon_path.exists():
                try:
                    self.indicator.set_icon(str(icon_path))
                    print(f"Using custom icon: {icon_path}")
                except Exception as e:
                    print(f"Warning: Could not set icon from file: {e}")
                    # Try using a simple icon name as fallback
                    self.indicator.set_icon("applications-system")
                    print("Using fallback system icon: applications-system")
            else:
                print(f"Warning: Icon file not found at {icon_path}")
                # Use a system icon as fallback
                self.indicator.set_icon("applications-system")
                print("Using fallback system icon: applications-system")
            
            self.indicator.set_label("TrayRunner", "")
            self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
            print("Indicator status set to ACTIVE")
            
            # Build and set menu
            self.build_menu(None)
            self.indicator.set_menu(self.menu)
            print("Menu built and set successfully")
            
            print("TrayRunner is now running. Look for the icon in your system tray!")
            
            # Setup reload trigger timer (check every 2 seconds)
            def check_reload():
                self.check_reload_trigger()
                return True  # Continue timer
            
            # Use GLib.timeout_add instead of Gtk.timeout_add
            from gi.repository import GLib
            GLib.timeout_add(2000, check_reload)  # 2000ms = 2 seconds
            
            # Start main loop
            Gtk.main()
            
        except Exception as e:
            print(f"Error starting TrayRunner: {e}")
            print("Please check that all dependencies are installed:")
            print("sudo apt install python3-gi gir1.2-appindicator3-0.1 python3-gi-cairo gir1.2-gtk-3.0 libnotify-bin")
            raise


def check_single_instance():
    """Check if another instance is already running"""
    lock_file = Path.home() / ".local" / "state" / "trayrunner" / "trayrunner.lock"
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Try to create and lock the file
        lock_fd = os.open(str(lock_file), os.O_CREAT | os.O_WRONLY | os.O_TRUNC)
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        
        # Write our PID to the lock file
        os.write(lock_fd, str(os.getpid()).encode())
        os.close(lock_fd)
        
        return True  # We got the lock
    except (OSError, IOError):
        # Another instance is running
        return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="TrayRunner - System tray application with customizable menus")
    parser.add_argument("--version", action="version", version=f"TrayRunner {__version__}")
    parser.add_argument("--reload", action="store_true", help="Reload configuration of running TrayRunner instance")
    args = parser.parse_args()
    
    if args.reload:
        # Handle reload request
        reload_trigger_file = Path.home() / ".local" / "state" / "trayrunner" / "reload.trigger"
        reload_trigger_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            # Create trigger file
            reload_trigger_file.write_text(str(int(time.time())))
            print("Reload signal sent to TrayRunner")
            
            # Wait briefly for reload to complete
            time.sleep(1)
            
            # Check if trigger file was processed (removed)
            if not reload_trigger_file.exists():
                print("Configuration reloaded successfully")
                sys.exit(0)
            else:
                print("TrayRunner may not be running or failed to reload")
                sys.exit(1)
                
        except Exception as e:
            print(f"Failed to send reload signal: {e}")
            sys.exit(1)
    
    # Check for single instance
    if not check_single_instance():
        print("TrayRunner is already running!")
        print("Use 'trayrunner status' to check, or 'trayrunner stop' to stop the existing instance.")
        sys.exit(1)
    
    try:
        app = TrayRunner()
        app.run()
    except KeyboardInterrupt:
        print("\nTrayRunner stopped by user")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
