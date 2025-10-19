"""
Editor panel for editing configuration items
"""

from typing import Optional, Any, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QCheckBox, QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QStackedWidget, QGroupBox, QHeaderView, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

try:
    from trayrunner_gui.models.schema import ItemNode, GroupNode, SeparatorNode
except ImportError:
    # Handle direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from trayrunner_gui.models.schema import ItemNode, GroupNode, SeparatorNode


class ItemEditor(QWidget):
    """Editor for item nodes"""
    
    # Signals
    data_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_item: Optional[ItemNode] = None
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Form layout for item properties
        form_layout = QFormLayout()
        
        # Label field
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Enter item label")
        form_layout.addRow("Label:", self.label_edit)
        
        # Command field
        self.cmd_edit = QLineEdit()
        self.cmd_edit.setPlaceholderText("Enter command to execute")
        form_layout.addRow("Command:", self.cmd_edit)
        
        # Terminal checkbox
        self.terminal_check = QCheckBox("Run in terminal")
        form_layout.addRow("", self.terminal_check)
        
        # Confirm checkbox
        self.confirm_check = QCheckBox("Show confirmation dialog")
        form_layout.addRow("", self.confirm_check)
        
        layout.addLayout(form_layout)
        
        # Environment variables section
        env_group = QGroupBox("Environment Variables")
        env_layout = QVBoxLayout(env_group)
        
        # Environment variables table
        self.env_table = QTableWidget()
        self.env_table.setColumnCount(2)
        self.env_table.setHorizontalHeaderLabels(["Key", "Value"])
        
        # Setup table
        header = self.env_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        env_layout.addWidget(self.env_table)
        
        # Environment variables buttons
        env_btn_layout = QHBoxLayout()
        
        self.add_env_btn = QPushButton("Add Variable")
        self.add_env_btn.clicked.connect(self.add_env_var)
        env_btn_layout.addWidget(self.add_env_btn)
        
        self.remove_env_btn = QPushButton("Remove Selected")
        self.remove_env_btn.clicked.connect(self.remove_env_var)
        env_btn_layout.addWidget(self.remove_env_btn)
        
        env_btn_layout.addStretch()
        env_layout.addLayout(env_btn_layout)
        
        layout.addWidget(env_group)
        layout.addStretch()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.label_edit.textChanged.connect(self.on_data_changed)
        self.cmd_edit.textChanged.connect(self.on_data_changed)
        self.terminal_check.toggled.connect(self.on_data_changed)
        self.confirm_check.toggled.connect(self.on_data_changed)
        self.env_table.itemChanged.connect(self.on_data_changed)
    
    def set_item(self, item: ItemNode):
        """Set the item to edit"""
        self.current_item = item
        
        # Update fields
        self.label_edit.setText(item.label)
        self.cmd_edit.setText(item.cmd)
        self.terminal_check.setChecked(item.terminal)
        self.confirm_check.setChecked(item.confirm)
        
        # Update environment variables table
        self.update_env_table()
    
    def get_item(self) -> ItemNode:
        """Get the current item data"""
        if not self.current_item:
            return ItemNode(label="", cmd="")
        
        # Get environment variables from table
        env_vars = {}
        for row in range(self.env_table.rowCount()):
            key_item = self.env_table.item(row, 0)
            value_item = self.env_table.item(row, 1)
            
            if key_item and value_item:
                key = key_item.text().strip()
                value = value_item.text().strip()
                if key:
                    env_vars[key] = value
        
        return ItemNode(
            label=self.label_edit.text().strip(),
            cmd=self.cmd_edit.text().strip(),
            terminal=self.terminal_check.isChecked(),
            confirm=self.confirm_check.isChecked(),
            env=env_vars
        )
    
    def update_env_table(self):
        """Update environment variables table"""
        if not self.current_item:
            return
        
        self.env_table.setRowCount(len(self.current_item.env))
        
        for row, (key, value) in enumerate(self.current_item.env.items()):
            self.env_table.setItem(row, 0, QTableWidgetItem(key))
            self.env_table.setItem(row, 1, QTableWidgetItem(value))
    
    def add_env_var(self):
        """Add new environment variable"""
        row = self.env_table.rowCount()
        self.env_table.insertRow(row)
        self.env_table.setItem(row, 0, QTableWidgetItem(""))
        self.env_table.setItem(row, 1, QTableWidgetItem(""))
        self.on_data_changed()
    
    def remove_env_var(self):
        """Remove selected environment variable"""
        current_row = self.env_table.currentRow()
        if current_row >= 0:
            self.env_table.removeRow(current_row)
            self.on_data_changed()
    
    def on_data_changed(self):
        """Handle data change"""
        if self.current_item:
            # Update the current item
            new_item = self.get_item()
            self.current_item.label = new_item.label
            self.current_item.cmd = new_item.cmd
            self.current_item.terminal = new_item.terminal
            self.current_item.confirm = new_item.confirm
            self.current_item.env = new_item.env
            
            self.data_changed.emit()


class GroupEditor(QWidget):
    """Editor for group nodes"""
    
    # Signals
    data_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_group: Optional[GroupNode] = None
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Form layout for group properties
        form_layout = QFormLayout()
        
        # Label field
        self.label_edit = QLineEdit()
        self.label_edit.setPlaceholderText("Enter group label")
        form_layout.addRow("Label:", self.label_edit)
        
        layout.addLayout(form_layout)
        
        # Info label
        info_label = QLabel("Group items are managed in the tree view on the left.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(info_label)
        
        layout.addStretch()
    
    def setup_connections(self):
        """Setup signal connections"""
        self.label_edit.textChanged.connect(self.on_data_changed)
    
    def set_group(self, group: GroupNode):
        """Set the group to edit"""
        self.current_group = group
        self.label_edit.setText(group.label)
    
    def get_group(self) -> GroupNode:
        """Get the current group data"""
        if not self.current_group:
            return GroupNode(label="", items=[])
        
        return GroupNode(
            label=self.label_edit.text().strip(),
            items=self.current_group.items  # Keep existing items
        )
    
    def on_data_changed(self):
        """Handle data change"""
        if self.current_group:
            self.current_group.label = self.label_edit.text().strip()
            self.data_changed.emit()


class SeparatorEditor(QWidget):
    """Editor for separator nodes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel("Separators have no editable properties.\n"
                           "They create visual dividers in the menu.")
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: gray; font-style: italic; padding: 20px;")
        layout.addWidget(info_label)
        
        layout.addStretch()


class EditorPanel(QWidget):
    """Main editor panel"""
    
    # Signals
    data_changed = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        
        # Title label
        self.title_label = QLabel("Select an item to edit")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        self.title_label.setFont(title_font)
        layout.addWidget(self.title_label)
        
        # Stacked widget for different editors
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create editors
        self.item_editor = ItemEditor()
        self.group_editor = GroupEditor()
        self.separator_editor = SeparatorEditor()
        
        # Add to stack
        self.stacked_widget.addWidget(self.item_editor)
        self.stacked_widget.addWidget(self.group_editor)
        self.stacked_widget.addWidget(self.separator_editor)
        
        # Show placeholder initially
        self.stacked_widget.setCurrentWidget(self.separator_editor)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.item_editor.data_changed.connect(self.data_changed.emit)
        self.group_editor.data_changed.connect(self.data_changed.emit)
    
    def set_node(self, node_data: Any):
        """Set the node to edit"""
        if isinstance(node_data, ItemNode):
            self.title_label.setText("Edit Item")
            self.item_editor.set_item(node_data)
            self.stacked_widget.setCurrentWidget(self.item_editor)
            
        elif isinstance(node_data, GroupNode):
            self.title_label.setText("Edit Group")
            self.group_editor.set_group(node_data)
            self.stacked_widget.setCurrentWidget(self.group_editor)
            
        elif isinstance(node_data, SeparatorNode):
            self.title_label.setText("Separator")
            self.stacked_widget.setCurrentWidget(self.separator_editor)
            
        else:
            self.title_label.setText("Select an item to edit")
            self.stacked_widget.setCurrentWidget(self.separator_editor)
    
    def get_current_data(self) -> Any:
        """Get current editor data"""
        current_widget = self.stacked_widget.currentWidget()
        
        if current_widget == self.item_editor:
            return self.item_editor.get_item()
        elif current_widget == self.group_editor:
            return self.group_editor.get_group()
        
        return None
