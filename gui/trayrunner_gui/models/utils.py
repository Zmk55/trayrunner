"""
Utility functions for node operations
"""

from __future__ import annotations
from copy import deepcopy
from typing import Callable
import re
from trayrunner_gui.models.schema import ItemNode, GroupNode, SeparatorNode, Node


def clone_node(node: Node, id_factory: Callable[[], str], label_deduper: Callable[[str], str]) -> Node:
    """
    Deep-copy a node, assign new id(s), and adjust the label
    
    Args:
        node: Node to clone
        id_factory: Function that generates new unique IDs
        label_deduper: Function that ensures label uniqueness among siblings
        
    Returns:
        Cloned node with new IDs and adjusted label
    """
    # Deep copy the entire node structure
    cloned = deepcopy(node)
    
    # Recursively assign new IDs
    def _assign_ids(n: Node):
        n.id = id_factory()
        if isinstance(n, GroupNode):
            for child in n.items:
                _assign_ids(child)
    
    _assign_ids(cloned)
    
    # Adjust label for Items/Groups (Separators have no label)
    if isinstance(cloned, (ItemNode, GroupNode)) and cloned.label:
        cloned.label = _add_copy_suffix(cloned.label, label_deduper)
    
    return cloned


def _add_copy_suffix(label: str, label_deduper: Callable[[str], str]) -> str:
    """
    Add '(copy)' or increment '(copy N)' suffix to a label
    
    Args:
        label: Original label
        label_deduper: Function to ensure uniqueness
        
    Returns:
        Label with copy suffix
    """
    # Check if label already ends with (copy) or (copy N)
    match = re.search(r'\(copy(?:\s+(\d+))?\)$', label)
    
    if match:
        # Increment the counter
        counter = int(match.group(1) or 1) + 1
        base_label = re.sub(r'\(copy(?:\s+\d+)?\)$', f'(copy {counter})', label)
    else:
        # Add initial (copy) suffix
        base_label = f"{label} (copy)"
    
    # Ensure uniqueness among siblings
    return label_deduper(base_label)
