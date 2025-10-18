"""
TrayRunner GUI Application Bootstrap
"""

import sys
import os
import time
import argparse
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtNetwork import QLocalServer, QLocalSocket

try:
    from .main_window import MainWindow
except ImportError:
    # Handle direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from trayrunner_gui.main_window import MainWindow


# Singleton management
SINGLETON_KEY = "trayrunner_gui_singleton"

def try_connect_existing_and_raise():
    """Try to connect to existing instance and raise its window"""
    sock = QLocalSocket()
    sock.connectToServer(SINGLETON_KEY)
    if sock.waitForConnected(100):
        sock.write(b"RAISE")
        sock.flush()
        sock.waitForBytesWritten(100)
        sock.disconnectFromServer()
        return True
    return False

def start_singleton_server(main_window):
    """Start singleton server to handle raise requests"""
    server = QLocalServer()
    # Cleanup stale server
    QLocalServer.removeServer(SINGLETON_KEY)
    server.listen(SINGLETON_KEY)
    
    def on_new_connection():
        sock = server.nextPendingConnection()
        if sock:
            data = sock.readAll()  # Read RAISE command
            sock.disconnectFromServer()
            # Raise window
            main_window.showNormal()
            main_window.raise_()
            main_window.activateWindow()
    
    server.newConnection.connect(on_new_connection)
    return server


def setup_application():
    """Setup Qt application with proper settings"""
    # Enable high DPI scaling
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("TrayRunner Config Editor")
    app.setApplicationVersion("1.1.0")
    app.setOrganizationName("TrayRunner")
    app.setOrganizationDomain("trayrunner.github.io")
    
    # Set application icon if available
    icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app


def check_dependencies():
    """Check if required dependencies are available"""
    missing_deps = []
    
    try:
        import PySide6
    except ImportError:
        missing_deps.append("PySide6")
    
    try:
        import ruamel.yaml
    except ImportError:
        missing_deps.append("ruamel.yaml")
    
    try:
        import pydantic
    except ImportError:
        missing_deps.append("pydantic")
    
    if missing_deps:
        app = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Missing Dependencies")
        msg.setText("Required dependencies are missing:")
        msg.setDetailedText("Missing: " + ", ".join(missing_deps) + "\n\n"
                           "Install with: pip install PySide6 ruamel.yaml pydantic")
        msg.exec()
        return False
    
    return True


def main():
    """Main entry point for TrayRunner GUI"""
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="TrayRunner Config GUI")
    parser.add_argument("--raise-only", action="store_true", 
                       help="Try to raise existing instance and exit")
    args = parser.parse_args()
    
    # Log startup for debugging
    log_dir = Path.home() / ".local" / "state" / "trayrunner"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "gui-startup.log"
    
    with open(log_file, "a", encoding="utf-8") as f:
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        f.write(f"\n{timestamp} GUI startup\n")
        f.write(f"Python: {sys.version}\n")
        f.write(f"Args: {sys.argv}\n")
        f.write(f"APPDIR: {os.environ.get('APPDIR', 'Not set')}\n")
    
    # Handle --raise-only flag
    if args.raise_only:
        sock = QLocalSocket()
        sock.connectToServer(SINGLETON_KEY)
        if sock.waitForConnected(100):
            sock.write(b"RAISE")
            sock.flush()
            sock.waitForBytesWritten(100)
            sock.disconnectFromServer()
            return 0  # Success: existing instance raised
        return 1  # Failure: no existing instance
    
    # Normal startup: check if already running
    if try_connect_existing_and_raise():
        return 0  # Exit, existing instance was raised
    
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Setup application
    app = setup_application()
    
    try:
        # Create and show main window
        window = MainWindow()
        
        # Start singleton server
        server = start_singleton_server(window)
        # Keep server alive (store as attribute)
        window._singleton_server = server
        
        window.show()
        
        # Start event loop
        sys.exit(app.exec())
        
    except Exception as e:
        # Show error dialog
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Application Error")
        msg.setText(f"Failed to start TrayRunner GUI: {e}")
        msg.setDetailedText(str(e))
        msg.exec()
        sys.exit(1)


if __name__ == "__main__":
    main()
