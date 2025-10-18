"""
Tree panel for displaying and editing configuration structure
"""

from typing import Optional, Any, Dict
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QLineEdit,
    QPushButton, QMenu, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, Signal, QMimeData
from PySide6.QtGui import QAction, QIcon, QDragEnterEvent, QDropEvent

try:
    from ..models.schema import Config, Node, ItemNode, GroupNode, SeparatorNode
except ImportError:
    # Handle direct execution
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from trayrunner_gui.models.schema import Config, Node, ItemNode, GroupNode, SeparatorNode


class ConfigTreeModel(QAbstractItemModel):
    """Tree model for configuration items"""
    
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.root_items = config.items if config else []
    
    def set_config(self, config: Config):
        """Update the model with new config"""
        self.beginResetModel()
        self.config = config
        self.root_items = config.items if config else []
        self.endResetModel()
    
    def index(self, row: int, column: int, parent: QModelIndex = QModelIndex()) -> QModelIndex:
        """Create index for given row/column/parent"""
        if not self.hasIndex(row, column, parent):
            return QModelIndex()
        
        if not parent.isValid():
            # Root level
            if row < len(self.root_items):
                return self.createIndex(row, column, self.root_items[row])
        else:
            # Child level
            parent_node = parent.internalPointer()
            if isinstance(parent_node, GroupNode) and row < len(parent_node.items):
                return self.createIndex(row, column, parent_node.items[row])
        
        return QModelIndex()
    
    def parent(self, index: QModelIndex) -> QModelIndex:
        """Get parent index"""
        if not index.isValid():
            return QModelIndex()
        
        node = index.internalPointer()
        
        # Find parent in root items
        for i, root_item in enumerate(self.root_items):
            if root_item is node:
                return QModelIndex()
            if isinstance(root_item, GroupNode):
                for j, child in enumerate(root_item.items):
                    if child is node:
                        return self.createIndex(i, 0, root_item)
        
        return QModelIndex()
    
    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of rows under parent"""
        if not parent.isValid():
            return len(self.root_items)
        
        node = parent.internalPointer()
        if isinstance(node, GroupNode):
            return len(node.items)
        
        return 0
    
    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """Get number of columns"""
        return 1
    
    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """Get data for index"""
        if not index.isValid():
            return None
        
        node = index.internalPointer()
        
        if role == Qt.DisplayRole:
            if isinstance(node, ItemNode):
                return f"📄 {node.label}"
            elif isinstance(node, GroupNode):
                return f"📁 {node.label}"
            elif isinstance(node, dict) and node.get("type") == "separator":
                return "--- Separator ---"
        
        elif role == Qt.DecorationRole:
            if isinstance(node, ItemNode):
                return "📄"
            elif isinstance(node, GroupNode):
                return "📁"
            elif isinstance(node, dict) and node.get("type") == "separator":
                return "---"
        
        return None
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """Get item flags"""
        if not index.isValid():
            return Qt.NoItemFlags
        
        flags = Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled
        return flags
    
    def supportedDropActions(self) -> Qt.DropActions:
        """Supported drop actions"""
        return Qt.MoveAction | Qt.CopyAction
    
    def mimeTypes(self) -> list[str]:
        """Supported MIME types"""
        return ["application/x-trayrunner-item"]
    
    def mimeData(self, indexes: list[QModelIndex]) -> QMimeData:
        """Create MIME data for drag operation"""
        mime_data = QMimeData()
        if indexes:
            # Store the node data
            node = indexes[0].internalPointer()
            mime_data.setData("application/x-trayrunner-item", str(id(node)).encode())
        return mime_data
    
    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
        """Handle drop operation"""
        if action == Qt.IgnoreAction:
            return True
        
        if not data.hasFormat("application/x-trayrunner-item"):
            return False
        
        # TODO: Implement drag and drop reordering
        return True
    
    def add_item(self, parent_index: QModelIndex = QModelIndex()) -> bool:
        """Add new item"""
        if not parent_index.isValid():
            # Add to root
            self.beginInsertRows(QModelIndex(), len(self.root_items), len(self.root_items))
            new_item = ItemNode(label="New Item", cmd="echo 'Hello World'")
            self.root_items.append(new_item)
            self.endInsertRows()
        else:
            # Add to group
            parent_node = parent_index.internalPointer()
            if isinstance(parent_node, GroupNode):
                self.beginInsertRows(parent_index, len(parent_node.items), len(parent_node.items))
                new_item = ItemNode(label="New Item", cmd="echo 'Hello World'")
                parent_node.items.append(new_item)
                self.endInsertRows()
        
        return True
    
    def add_group(self, parent_index: QModelIndex = QModelIndex()) -> bool:
        """Add new group"""
        if not parent_index.isValid():
            # Add to root
            self.beginInsertRows(QModelIndex(), len(self.root_items), len(self.root_items))
            new_group = GroupNode(label="New Group", items=[])
            self.root_items.append(new_group)
            self.endInsertRows()
        else:
            # Add to group
            parent_node = parent_index.internalPointer()
            if isinstance(parent_node, GroupNode):
                self.beginInsertRows(parent_index, len(parent_node.items), len(parent_node.items))
                new_group = GroupNode(label="New Group", items=[])
                parent_node.items.append(new_group)
                self.endInsertRows()
        
        return True
    
    def add_separator(self, parent_index: QModelIndex = QModelIndex()) -> bool:
        """Add new separator"""
        if not parent_index.isValid():
            # Add to root
            self.beginInsertRows(QModelIndex(), len(self.root_items), len(self.root_items))
            new_separator = {"type": "separator"}
            self.root_items.append(new_separator)
            self.endInsertRows()
        else:
            # Add to group
            parent_node = parent_index.internalPointer()
            if isinstance(parent_node, GroupNode):
                self.beginInsertRows(parent_index, len(parent_node.items), len(parent_node.items))
                new_separator = {"type": "separator"}
                parent_node.items.append(new_separator)
                self.endInsertRows()
        
        return True
    
    def remove_item(self, index: QModelIndex) -> bool:
        """Remove item at index"""
        if not index.isValid():
            return False
        
        parent = index.parent()
        if not parent.isValid():
            # Remove from root
            self.beginRemoveRows(QModelIndex(), index.row(), index.row())
            del self.root_items[index.row()]
            self.endRemoveRows()
        else:
            # Remove from group
            parent_node = parent.internalPointer()
            if isinstance(parent_node, GroupNode):
                self.beginRemoveRows(parent, index.row(), index.row())
                del parent_node.items[index.row()]
                self.endRemoveRows()
        
        return True


class TreePanel(QWidget):
    """Tree panel widget"""
    
    # Signals
    selection_changed = Signal(object)  # Emit node data
    data_changed = Signal()  # Emit when data changes
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.model: Optional[ConfigTreeModel] = None
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Search box
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search items...")
        search_layout.addWidget(self.search_edit)
        
        self.clear_search_btn = QPushButton("Clear")
        self.clear_search_btn.clicked.connect(self.clear_search)
        search_layout.addWidget(self.clear_search_btn)
        
        layout.addLayout(search_layout)
        
        # Tree view
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        self.tree_view.setDragDropMode(QTreeView.InternalMove)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        
        layout.addWidget(self.tree_view)
    
    def setup_connections(self):
        """Setup signal connections"""
        self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        self.search_edit.textChanged.connect(self.filter_tree)
    
    def set_config(self, config: Config):
        """Set the configuration to display"""
        self.model = ConfigTreeModel(config)
        self.tree_view.setModel(self.model)
        
        # Expand all items
        self.tree_view.expandAll()
    
    def on_selection_changed(self):
        """Handle selection change"""
        current = self.tree_view.currentIndex()
        if current.isValid() and self.model:
            node = current.internalPointer()
            self.selection_changed.emit(node)
    
    def show_context_menu(self, position):
        """Show context menu"""
        index = self.tree_view.indexAt(position)
        menu = QMenu(self)
        
        # Add actions
        add_item_action = QAction("Add Item", self)
        add_item_action.triggered.connect(lambda: self.add_item(index))
        menu.addAction(add_item_action)
        
        add_group_action = QAction("Add Group", self)
        add_group_action.triggered.connect(lambda: self.add_group(index))
        menu.addAction(add_group_action)
        
        add_separator_action = QAction("Add Separator", self)
        add_separator_action.triggered.connect(lambda: self.add_separator(index))
        menu.addAction(add_separator_action)
        
        if index.isValid():
            menu.addSeparator()
            
            duplicate_action = QAction("Duplicate", self)
            duplicate_action.triggered.connect(lambda: self.duplicate_item(index))
            menu.addAction(duplicate_action)
            
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(lambda: self.delete_item(index))
            menu.addAction(delete_action)
        
        menu.exec(self.tree_view.mapToGlobal(position))
    
    def add_item(self, parent_index=None):
        """Add new item"""
        if self.model:
            if parent_index is None:
                parent_index = self.tree_view.currentIndex()
            self.model.add_item(parent_index)
            self.data_changed.emit()
    
    def add_group(self, parent_index=None):
        """Add new group"""
        if self.model:
            if parent_index is None:
                parent_index = self.tree_view.currentIndex()
            self.model.add_group(parent_index)
            self.data_changed.emit()
    
    def add_separator(self, parent_index=None):
        """Add new separator"""
        if self.model:
            if parent_index is None:
                parent_index = self.tree_view.currentIndex()
            self.model.add_separator(parent_index)
            self.data_changed.emit()
    
    def duplicate_selected(self):
        """Duplicate selected item"""
        current = self.tree_view.currentIndex()
        if current.isValid() and self.model:
            # TODO: Implement duplication
            pass
    
    def delete_selected(self):
        """Delete selected item"""
        current = self.tree_view.currentIndex()
        if current.isValid() and self.model:
            reply = QMessageBox.question(
                self, "Delete Item",
                "Are you sure you want to delete this item?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.model.remove_item(current)
                self.data_changed.emit()
    
    def filter_tree(self, text):
        """Filter tree based on search text"""
        # TODO: Implement tree filtering
        pass
    
    def clear_search(self):
        """Clear search text"""
        self.search_edit.clear()
