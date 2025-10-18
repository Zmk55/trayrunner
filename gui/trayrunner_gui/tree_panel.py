"""
Tree panel for displaying and editing configuration structure
"""

from typing import Optional, Any, Dict, List
import json
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeView, QLineEdit,
    QPushButton, QMenu, QMessageBox, QInputDialog
)
from PySide6.QtCore import Qt, QAbstractItemModel, QModelIndex, Signal, QMimeData, QByteArray
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
    
    # Signal emitted when model data changes
    changed = Signal()
    
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
            elif isinstance(node, SeparatorNode):
                return "--- Separator ---"
        
        elif role == Qt.DecorationRole:
            if isinstance(node, ItemNode):
                return "📄"
            elif isinstance(node, GroupNode):
                return "📁"
            elif isinstance(node, SeparatorNode):
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
    
    MIME_TYPE = "application/x-trayrunner-node"
    
    def mimeTypes(self) -> list[str]:
        """Supported MIME types"""
        return [self.MIME_TYPE]
    
    def mimeData(self, indexes: list[QModelIndex]) -> QMimeData:
        """Create MIME data for drag operation"""
        if not indexes:
            return QMimeData()
        
        index = indexes[0]
        if not index.isValid():
            return QMimeData()
        
        node = index.internalPointer()
        parent_id = self._get_parent_id(index)
        row = index.row()
        
        # Get drag range (block for separators)
        start, end = self._get_drag_range(parent_id, row)
        
        # Create payload
        payload = {
            "parent_id": parent_id,
            "start_row": start,
            "end_row": end,
            "dragged_node_id": node.id
        }
        
        mime_data = QMimeData()
        mime_data.setData(self.MIME_TYPE, QByteArray(json.dumps(payload).encode("utf-8")))
        return mime_data
    
    def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, 
                        row: int, column: int, parent: QModelIndex) -> bool:
        """Validate if drop is allowed"""
        if not data.hasFormat(self.MIME_TYPE):
            return False
        
        if action != Qt.MoveAction:
            return False
        
        # Cannot drop into a separator (only before/after)
        if parent.isValid():
            parent_node = parent.internalPointer()
            if isinstance(parent_node, SeparatorNode):
                return False
            # Can only drop into groups
            if not isinstance(parent_node, GroupNode) and row < 0:
                return False
        
        return True
    
    def dropMimeData(self, data: QMimeData, action: Qt.DropAction, 
                     row: int, column: int, parent: QModelIndex) -> bool:
        """Handle drop operation with block moving support"""
        if action != Qt.MoveAction:
            return False
        
        if not data.hasFormat(self.MIME_TYPE):
            return False
        
        # Parse payload
        payload_bytes = bytes(data.data(self.MIME_TYPE))
        payload = json.loads(payload_bytes.decode("utf-8"))
        
        src_parent_id = payload["parent_id"]
        src_start = payload["start_row"]
        src_end = payload["end_row"]
        
        # Get destination parent
        if parent.isValid():
            dst_parent_node = parent.internalPointer()
            if isinstance(dst_parent_node, SeparatorNode):
                return False  # Cannot drop into separator
            dst_parent_id = dst_parent_node.id
        else:
            dst_parent_id = "ROOT"
        
        # Get source and destination lists
        src_list = self._get_children_list(src_parent_id)
        dst_list = self._get_children_list(dst_parent_id)
        
        # If row is -1, append to end
        if row < 0:
            row = len(dst_list)
        
        # Extract block to move
        block = src_list[src_start:src_end]
        
        # Prevent dropping into self
        for node in block:
            if dst_parent_id == node.id:
                return False
        
        # Signal layout change
        self.layoutAboutToBeChanged.emit()
        
        # Remove from source
        del src_list[src_start:src_end]
        
        # Adjust row if moving within same parent
        if src_parent_id == dst_parent_id and row > src_start:
            row -= (src_end - src_start)
        
        # Insert at destination
        for i, node in enumerate(block):
            dst_list.insert(row + i, node)
        
        # Signal change complete
        self.layoutChanged.emit()
        
        # Emit custom signal for save/validation
        self.changed.emit()
        
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
            new_separator = SeparatorNode()
            self.root_items.append(new_separator)
            self.endInsertRows()
        else:
            # Add to group
            parent_node = parent_index.internalPointer()
            if isinstance(parent_node, GroupNode):
                self.beginInsertRows(parent_index, len(parent_node.items), len(parent_node.items))
                new_separator = SeparatorNode()
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
    
    def _get_children_list(self, parent_id: str) -> List[Node]:
        """Get the children list for a given parent ID"""
        if parent_id == "ROOT":
            return self.root_items
        else:
            # Find the group node with this ID
            node = self._find_node_by_id(parent_id, self.root_items)
            if node and isinstance(node, GroupNode):
                return node.items
        return []
    
    def _find_node_by_id(self, node_id: str, items: List[Node]) -> Optional[Node]:
        """Recursively find a node by its ID"""
        for item in items:
            if item.id == node_id:
                return item
            if isinstance(item, GroupNode):
                found = self._find_node_by_id(node_id, item.items)
                if found:
                    return found
        return None
    
    def _get_drag_range(self, parent_id: str, row: int) -> tuple[int, int]:
        """
        Get the range [start, end) for dragging a node.
        If the node is a separator, returns the block range.
        Otherwise, returns [row, row+1).
        """
        children = self._get_children_list(parent_id)
        if row >= len(children):
            return row, row + 1
        
        node = children[row]
        
        if isinstance(node, SeparatorNode):
            # Find the next separator at the same depth
            end = row + 1
            while end < len(children) and not isinstance(children[end], SeparatorNode):
                end += 1
            return row, end
        else:
            return row, row + 1
    
    def _get_parent_id(self, index: QModelIndex) -> str:
        """Get the parent ID for an index"""
        if not index.isValid():
            return "ROOT"
        
        parent_index = self.parent(index)
        if not parent_index.isValid():
            return "ROOT"
        
        parent_node = parent_index.internalPointer()
        return parent_node.id


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
        
        # Tree view with proper DnD settings
        self.tree_view = QTreeView()
        self.tree_view.setHeaderHidden(True)
        
        # Enable drag and drop
        self.tree_view.setDragEnabled(True)
        self.tree_view.setAcceptDrops(True)
        self.tree_view.setDropIndicatorShown(True)
        self.tree_view.setDragDropMode(QTreeView.InternalMove)
        self.tree_view.setDefaultDropAction(Qt.MoveAction)
        self.tree_view.setSelectionMode(QTreeView.SingleSelection)
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        
        layout.addWidget(self.tree_view)
    
    def setup_connections(self):
        """Setup signal connections"""
        # Only connect non-model dependent signals here
        self.tree_view.customContextMenuRequested.connect(self.show_context_menu)
        self.search_edit.textChanged.connect(self.filter_tree)
    
    def set_config(self, config: Config):
        """Set the configuration to display"""
        self.model = ConfigTreeModel(config)
        self.tree_view.setModel(self.model)
        
        # Connect model changed signal
        self.model.changed.connect(self.on_model_changed)
        
        # Connect selection model after model is set
        if self.tree_view.selectionModel():
            self.tree_view.selectionModel().selectionChanged.connect(self.on_selection_changed)
        
        # Expand all items
        self.tree_view.expandAll()
    
    def on_model_changed(self):
        """Handle model data change"""
        self.data_changed.emit()  # Propagate to main window for validation/save
    
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
            duplicate_action.triggered.connect(self.duplicate_selected)
            menu.addAction(duplicate_action)
            
            delete_action = QAction("Delete", self)
            delete_action.triggered.connect(self.delete_selected)
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
    
    def keyPressEvent(self, event):
        """Handle keyboard events"""
        from PySide6.QtGui import QKeySequence
        from PySide6.QtCore import Qt
        
        if event.matches(QKeySequence.Delete):
            self.delete_selected()
            event.accept()
            return
        
        # Alt+Up: Move item up
        if event.modifiers() == Qt.AltModifier and event.key() == Qt.Key_Up:
            self._move_selected_up()
            event.accept()
            return
        
        # Alt+Down: Move item down
        if event.modifiers() == Qt.AltModifier and event.key() == Qt.Key_Down:
            self._move_selected_down()
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def _move_selected_up(self):
        """Move selected item up one position"""
        index = self.tree_view.currentIndex()
        if not index.isValid() or index.row() == 0:
            return
        
        # Use the same move logic as DnD
        parent_index = index.parent()
        target_row = index.row() - 1
        
        # Simulate drop one row up
        self._move_node_to_position(index, parent_index, target_row)
    
    def _move_selected_down(self):
        """Move selected item down one position"""
        index = self.tree_view.currentIndex()
        if not index.isValid():
            return
        
        parent_index = index.parent()
        parent_node = parent_index.internalPointer() if parent_index.isValid() else None
        
        if parent_node:
            max_row = len(parent_node.items) - 1 if isinstance(parent_node, GroupNode) else 0
        else:
            max_row = len(self.model.root_items) - 1
        
        if index.row() >= max_row:
            return
        
        target_row = index.row() + 2  # +2 because we insert before the item after next
        self._move_node_to_position(index, parent_index, target_row)
    
    def _move_node_to_position(self, index, parent_index, target_row):
        """Move a node to a specific position using the same logic as DnD"""
        if not self.model:
            return
        
        node = index.internalPointer()
        parent_id = self.model._get_parent_id(index)
        row = index.row()
        
        # Get drag range (block for separators)
        start, end = self.model._get_drag_range(parent_id, row)
        
        # Get destination parent
        if parent_index.isValid():
            dst_parent_node = parent_index.internalPointer()
            if isinstance(dst_parent_node, SeparatorNode):
                return False  # Cannot drop into separator
            dst_parent_id = dst_parent_node.id
        else:
            dst_parent_id = "ROOT"
        
        # Get source and destination lists
        src_list = self.model._get_children_list(parent_id)
        dst_list = self.model._get_children_list(dst_parent_id)
        
        # Extract block to move
        block = src_list[start:end]
        
        # Prevent dropping into self
        for node in block:
            if dst_parent_id == node.id:
                return False
        
        # Signal layout change
        self.model.layoutAboutToBeChanged.emit()
        
        # Remove from source
        del src_list[start:end]
        
        # Adjust row if moving within same parent
        if parent_id == dst_parent_id and target_row > start:
            target_row -= (end - start)
        
        # Insert at destination
        for i, node in enumerate(block):
            dst_list.insert(target_row + i, node)
        
        # Signal change complete
        self.model.layoutChanged.emit()
        
        # Emit custom signal for save/validation
        self.model.changed.emit()
    
    def filter_tree(self, text):
        """Filter tree based on search text"""
        # TODO: Implement tree filtering
        pass
    
    def clear_search(self):
        """Clear search text"""
        self.search_edit.clear()
