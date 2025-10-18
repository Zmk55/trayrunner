"""
Main window for TrayRunner GUI
"""

import json
from pathlib import Path
from typing import Optional
from PySide6.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QToolBar, QStatusBar, QMessageBox, QFileDialog,
    QApplication, QDockWidget, QTableWidget, QTableWidgetItem,
    QHeaderView, QLabel, QPushButton
)
from PySide6.QtCore import Qt, QTimer, Signal, QSettings
from PySide6.QtGui import QAction, QKeySequence, QIcon

try:
    from .tree_panel import TreePanel
    from .editor_panel import EditorPanel
    from ..models.schema import Config, ValidationError
    from ..models.yaml_io import yaml_handler
    from ..models.validators import config_validator
    from ..services.reloader import reload_manager
    from ..services.file_watch import ConfigFileWatcher
except ImportError:
    # Handle direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from trayrunner_gui.tree_panel import TreePanel
    from trayrunner_gui.editor_panel import EditorPanel
    from trayrunner_gui.models.schema import Config, ValidationError
    from trayrunner_gui.models.yaml_io import yaml_handler
    from trayrunner_gui.models.validators import config_validator
    from trayrunner_gui.services.reloader import reload_manager
    from trayrunner_gui.services.file_watch import ConfigFileWatcher


class ValidationPanel(QDockWidget):
    """Dock widget for showing validation errors"""
    
    # Signal emitted when user clicks on an error
    error_clicked = Signal(str, str)  # location, field
    
    def __init__(self, parent=None):
        super().__init__("Validation", parent)
        self.setAllowedAreas(Qt.BottomDockWidgetArea)
        
        # Create table widget
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Type", "Location", "Message"])
        
        # Setup table
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        # Connect double-click to emit signal
        self.table.itemDoubleClicked.connect(self._on_item_double_clicked)
        
        # Set as widget
        self.setWidget(self.table)
    
    def update_errors(self, errors: list[ValidationError]):
        """Update the validation errors table"""
        self.table.setRowCount(len(errors))
        
        for row, error in enumerate(errors):
            # Type column
            type_item = QTableWidgetItem(error.type.title())
            if error.type == "error":
                type_item.setBackground(Qt.red)
            else:
                type_item.setBackground(Qt.yellow)
            self.table.setItem(row, 0, type_item)
            
            # Location column
            self.table.setItem(row, 1, QTableWidgetItem(error.location))
            
            # Message column
            self.table.setItem(row, 2, QTableWidgetItem(error.message))
    
    def _on_item_double_clicked(self, item):
        """Handle double-click on error item"""
        row = item.row()
        location = self.table.item(row, 1).text()
        field = self.table.item(row, 2).text()
        self.error_clicked.emit(location, field)


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config: Optional[Config] = None
        self.config_path: Optional[Path] = None
        self.original_yaml = None
        self.has_unsaved_changes = False
        self.file_watcher: Optional[ConfigFileWatcher] = None
        
        # Load settings
        self.settings = QSettings()
        
        # Setup UI
        self.setup_ui()
        self.setup_menus()
        self.setup_toolbar()
        self.setup_statusbar()
        self.setup_connections()
        
        # Load default configuration
        self.load_default_config()
        
        # Setup file watcher
        self.setup_file_watcher()
    
    def setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("TrayRunner Config Editor")
        self.setMinimumSize(800, 600)
        self.resize(1200, 800)
        
        # Create central widget with splitter
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter
        self.splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.splitter)
        
        # Create panels
        self.tree_panel = TreePanel()
        self.editor_panel = EditorPanel()
        
        # Add to splitter
        self.splitter.addWidget(self.tree_panel)
        self.splitter.addWidget(self.editor_panel)
        
        # Set splitter proportions
        self.splitter.setSizes([300, 500])
        
        # Create validation panel
        self.validation_panel = ValidationPanel(self)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.validation_panel)
    
    def setup_menus(self):
        """Setup menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        self.new_action = QAction("&New", self)
        self.new_action.setShortcut(QKeySequence.New)
        self.new_action.triggered.connect(self.new_config)
        file_menu.addAction(self.new_action)
        
        self.open_action = QAction("&Open...", self)
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.triggered.connect(self.open_config)
        file_menu.addAction(self.open_action)
        
        file_menu.addSeparator()
        
        self.save_action = QAction("&Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        self.save_action.triggered.connect(self.save_config)
        file_menu.addAction(self.save_action)
        
        self.save_as_action = QAction("Save &As...", self)
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.triggered.connect(self.save_as_config)
        file_menu.addAction(self.save_as_action)
        
        self.revert_action = QAction("&Revert", self)
        self.revert_action.triggered.connect(self.revert_config)
        file_menu.addAction(self.revert_action)
        
        file_menu.addSeparator()
        
        self.exit_action = QAction("E&xit", self)
        self.exit_action.setShortcut(QKeySequence.Quit)
        self.exit_action.triggered.connect(self.close)
        file_menu.addAction(self.exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("&Edit")
        
        self.add_item_action = QAction("Add &Item", self)
        self.add_item_action.triggered.connect(self.add_item)
        edit_menu.addAction(self.add_item_action)
        
        self.add_group_action = QAction("Add &Group", self)
        self.add_group_action.triggered.connect(self.add_group)
        edit_menu.addAction(self.add_group_action)
        
        self.add_separator_action = QAction("Add &Separator", self)
        self.add_separator_action.triggered.connect(self.add_separator)
        edit_menu.addAction(self.add_separator_action)
        
        edit_menu.addSeparator()
        
        self.duplicate_action = QAction("&Duplicate", self)
        self.duplicate_action.triggered.connect(self.duplicate_item)
        edit_menu.addAction(self.duplicate_action)
        
        self.delete_action = QAction("&Delete", self)
        self.delete_action.setShortcut(QKeySequence.Delete)
        self.delete_action.triggered.connect(self.delete_item)
        edit_menu.addAction(self.delete_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        self.reload_action = QAction("&Reload TrayRunner", self)
        self.reload_action.triggered.connect(self.reload_trayrunner)
        tools_menu.addAction(self.reload_action)
        
        self.preferences_action = QAction("&Preferences", self)
        self.preferences_action.triggered.connect(self.show_preferences)
        tools_menu.addAction(self.preferences_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        self.about_action = QAction("&About", self)
        self.about_action.triggered.connect(self.show_about)
        help_menu.addAction(self.about_action)
    
    def setup_toolbar(self):
        """Setup toolbar"""
        toolbar = QToolBar("Main Toolbar")
        self.addToolBar(toolbar)
        
        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.add_item_action)
        toolbar.addAction(self.add_group_action)
        toolbar.addSeparator()
        toolbar.addAction(self.reload_action)
    
    def setup_statusbar(self):
        """Setup status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # File path label
        self.file_path_label = QLabel("No file loaded")
        self.status_bar.addWidget(self.file_path_label)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.status_label)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Tree panel connections
        self.tree_panel.selection_changed.connect(self.on_selection_changed)
        self.tree_panel.data_changed.connect(self.on_data_changed)
        
        # Editor panel connections
        self.editor_panel.data_changed.connect(self.on_data_changed)
        
        # Validation panel connections
        self.validation_panel.error_clicked.connect(self.on_error_clicked)
    
    def setup_file_watcher(self):
        """Setup file watcher for external changes"""
        if self.config_path:
            self.file_watcher = ConfigFileWatcher(self.config_path)
            self.file_watcher.start_watching(self.on_external_file_change)
    
    def load_default_config(self):
        """Load default configuration"""
        default_path = Path.home() / ".config" / "trayrunner" / "commands.yaml"
        if default_path.exists():
            self.load_config_file(default_path)
        else:
            # Create new empty config
            self.config = Config()
            self.tree_panel.set_config(self.config)
            self.update_validation()
    
    def load_config_file(self, path: Path):
        """Load configuration from file"""
        try:
            self.config, self.original_yaml = yaml_handler.load_yaml(path)
            self.config_path = path
            self.tree_panel.set_config(self.config)
            self.update_validation()
            self.update_window_title()
            self.update_status()
            
            # Setup file watcher
            if self.file_watcher:
                self.file_watcher.stop_watching()
            self.setup_file_watcher()
            
        except Exception as e:
            QMessageBox.critical(self, "Load Error", f"Failed to load configuration: {e}")
    
    def save_config(self):
        """Save current configuration"""
        if not self.config_path:
            self.save_as_config()
            return
        
        try:
            backup_path = yaml_handler.save_yaml(
                self.config_path, 
                self.config, 
                self.original_yaml
            )
            
            # Update original YAML for future saves
            _, self.original_yaml = yaml_handler.load_yaml(self.config_path)
            
            self.has_unsaved_changes = False
            self.update_window_title()
            self.update_status()
            
            # Show backup info
            self.status_bar.showMessage(f"Saved. Backup created: {backup_path.name}", 3000)
            
        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save configuration: {e}")
    
    def save_as_config(self):
        """Save configuration to new file"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Configuration", 
            str(self.config_path or Path.home() / ".config" / "trayrunner" / "commands.yaml"),
            "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        
        if path:
            self.config_path = Path(path)
            self.save_config()
    
    def new_config(self):
        """Create new configuration"""
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_config()
            elif reply == QMessageBox.Cancel:
                return
        
        self.config = Config()
        self.config_path = None
        self.original_yaml = None
        self.has_unsaved_changes = False
        self.tree_panel.set_config(self.config)
        self.update_validation()
        self.update_window_title()
        self.update_status()
    
    def open_config(self):
        """Open configuration file"""
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_config()
            elif reply == QMessageBox.Cancel:
                return
        
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Configuration",
            str(Path.home() / ".config" / "trayrunner"),
            "YAML Files (*.yaml *.yml);;All Files (*)"
        )
        
        if path:
            self.load_config_file(Path(path))
    
    def revert_config(self):
        """Revert to saved version"""
        if not self.config_path:
            return
        
        reply = QMessageBox.question(
            self, "Revert Changes",
            "Are you sure you want to revert all unsaved changes?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.load_config_file(self.config_path)
    
    def add_item(self):
        """Add new item"""
        self.tree_panel.add_item()
        self.mark_unsaved()
    
    def add_group(self):
        """Add new group"""
        self.tree_panel.add_group()
        self.mark_unsaved()
    
    def add_separator(self):
        """Add new separator"""
        self.tree_panel.add_separator()
        self.mark_unsaved()
    
    def duplicate_item(self):
        """Duplicate selected item"""
        self.tree_panel.duplicate_selected()
        self.mark_unsaved()
    
    def delete_item(self):
        """Delete selected item"""
        self.tree_panel.delete_selected()
        self.mark_unsaved()
    
    def reload_trayrunner(self):
        """Reload TrayRunner configuration"""
        if not reload_manager.can_reload():
            QMessageBox.warning(
                self, "TrayRunner Not Running",
                "TrayRunner is not currently running. Start it first, then try reloading."
            )
            return
        
        success, message = reload_manager.reload_config()
        
        if success:
            QMessageBox.information(self, "Reload Successful", message)
        else:
            QMessageBox.warning(self, "Reload Failed", message)
    
    def show_preferences(self):
        """Show preferences dialog"""
        # TODO: Implement preferences dialog
        QMessageBox.information(self, "Preferences", "Preferences dialog not yet implemented.")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self, "About TrayRunner Config Editor",
            "TrayRunner Config Editor v1.1.0\n\n"
            "A GUI editor for TrayRunner configuration files.\n\n"
            "Built with PySide6, ruamel.yaml, and pydantic."
        )
    
    def on_selection_changed(self, node_data):
        """Handle selection change in tree"""
        self.editor_panel.set_node(node_data)
    
    def on_data_changed(self):
        """Handle data change"""
        self.mark_unsaved()
        self.update_validation()
    
    def on_error_clicked(self, location, field):
        """Handle error click in validation panel"""
        # TODO: Navigate to error location
        pass
    
    def on_external_file_change(self, file_path):
        """Handle external file change"""
        reply = QMessageBox.question(
            self, "File Changed Externally",
            f"The configuration file has been modified externally:\n{file_path}\n\n"
            "Do you want to reload it? (This will discard your unsaved changes.)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.load_config_file(Path(file_path))
    
    def mark_unsaved(self):
        """Mark document as having unsaved changes"""
        self.has_unsaved_changes = True
        self.update_window_title()
    
    def update_window_title(self):
        """Update window title"""
        title = "TrayRunner Config Editor"
        if self.config_path:
            title += f" - {self.config_path.name}"
        if self.has_unsaved_changes:
            title += " *"
        self.setWindowTitle(title)
    
    def update_status(self):
        """Update status bar"""
        if self.config_path:
            self.file_path_label.setText(str(self.config_path))
        else:
            self.file_path_label.setText("New configuration")
        
        if self.has_unsaved_changes:
            self.status_label.setText("Modified")
        else:
            self.status_label.setText("Ready")
    
    def update_validation(self):
        """Update validation panel"""
        if not self.config:
            return
        
        errors = config_validator.validate_config(self.config)
        self.validation_panel.update_errors(errors)
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.has_unsaved_changes:
            reply = QMessageBox.question(
                self, "Unsaved Changes",
                "You have unsaved changes. Do you want to save them?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )
            
            if reply == QMessageBox.Save:
                self.save_config()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
                return
        
        # Cleanup file watcher
        if self.file_watcher:
            self.file_watcher.stop_watching()
        
        event.accept()
