"""
TrayRunner GUI Application Bootstrap
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

try:
    from .main_window import MainWindow
except ImportError:
    # Handle direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from trayrunner_gui.main_window import MainWindow


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
    # Check dependencies first
    if not check_dependencies():
        sys.exit(1)
    
    # Setup application
    app = setup_application()
    
    try:
        # Create and show main window
        window = MainWindow()
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
