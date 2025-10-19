"""
Configuration validation logic
"""

from typing import List, Tuple, Set
from .schema import Config, Node, ItemNode, GroupNode, SeparatorNode, ValidationError


class ConfigValidator:
    """Validates TrayRunner configuration"""
    
    def __init__(self):
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []
    
    def validate_config(self, config: Config) -> List[ValidationError]:
        """
        Validate entire configuration
        
        Args:
            config: Config object to validate
            
        Returns:
            List of validation errors and warnings
        """
        self.errors.clear()
        self.warnings.clear()
        
        # Validate items list
        if not config.items:
            self.warnings.append(ValidationError(
                type="warning",
                location="root",
                message="Configuration has no items",
                field="items"
            ))
            return self.errors + self.warnings
        
        # Validate each item
        for i, item in enumerate(config.items):
            self._validate_node(item, f"items[{i}]")
        
        # Check for duplicate labels at same level
        self._check_duplicate_labels(config.items, "root")
        
        # Check separator placement
        self._validate_separator_placement(config.items, "items")
        
        return self.errors + self.warnings
    
    def _validate_node(self, node: Node, path: str) -> None:
        """Validate a single node"""
        if isinstance(node, ItemNode):
            self._validate_item(node, path)
        elif isinstance(node, GroupNode):
            self._validate_group(node, path)
        elif isinstance(node, SeparatorNode):
            # Separator nodes are always valid, no properties to validate
            pass
        else:
            # This should never happen with discriminated union
            self.errors.append(ValidationError(
                type="error",
                location=path,
                message=f"Unknown node type: {type(node).__name__}",
                field="type"
            ))
    
    def _validate_item(self, item: ItemNode, path: str) -> None:
        """Validate an item node"""
        # Label validation
        if not item.label or not item.label.strip():
            self.errors.append(ValidationError(
                type="error",
                location=path,
                message="Item label cannot be empty",
                field="label"
            ))
        
        # Command validation
        if not item.cmd or not item.cmd.strip():
            self.errors.append(ValidationError(
                type="error",
                location=path,
                message="Item command cannot be empty",
                field="cmd"
            ))
        
        # Environment variables validation
        for key, value in item.env.items():
            if not key or not key.strip():
                self.errors.append(ValidationError(
                    type="error",
                    location=path,
                    message=f"Environment variable key cannot be empty",
                    field=f"env.{key}"
                ))
            if not isinstance(value, str):
                self.errors.append(ValidationError(
                    type="error",
                    location=path,
                    message=f"Environment variable value must be string",
                    field=f"env.{key}"
                ))
    
    def _validate_group(self, group: GroupNode, path: str) -> None:
        """Validate a group node"""
        # Label validation
        if not group.label or not group.label.strip():
            self.errors.append(ValidationError(
                type="error",
                location=path,
                message="Group label cannot be empty",
                field="label"
            ))
        
        # Items validation
        if not group.items:
            self.warnings.append(ValidationError(
                type="warning",
                location=path,
                message="Group has no items",
                field="items"
            ))
        else:
            for i, item in enumerate(group.items):
                self._validate_node(item, f"{path}.items[{i}]")
            
            # Check for duplicate labels within group
            self._check_duplicate_labels(group.items, path)
    
    def _check_duplicate_labels(self, items: List[Node], path: str) -> None:
        """Check for duplicate labels at the same level"""
        labels: Set[str] = set()
        
        for i, item in enumerate(items):
            if isinstance(item, ItemNode):
                if item.label in labels:
                    self.errors.append(ValidationError(
                        type="error",
                        location=f"{path}.items[{i}]",
                        message=f"Duplicate label: '{item.label}'",
                        field="label"
                    ))
                labels.add(item.label)
            elif isinstance(item, GroupNode):
                if item.label in labels:
                    self.errors.append(ValidationError(
                        type="error",
                        location=f"{path}.items[{i}]",
                        message=f"Duplicate label: '{item.label}'",
                        field="label"
                    ))
                labels.add(item.label)
    
    def _validate_separator_placement(self, items: List[Node], path: str) -> None:
        """Validate separator placement and warn about edge cases"""
        for i, node in enumerate(items):
            if isinstance(node, SeparatorNode):
                # Warn if separator at edge
                if i == 0:
                    self.warnings.append(ValidationError(
                        type="warning",
                        location=f"{path}[{i}]",
                        message="Separator at beginning has no visual effect",
                        field="type"
                    ))
                if i == len(items) - 1:
                    self.warnings.append(ValidationError(
                        type="warning",
                        location=f"{path}[{i}]",
                        message="Separator at end has no visual effect",
                        field="type"
                    ))
                
                # Warn if adjacent separators
                if i + 1 < len(items) and isinstance(items[i + 1], SeparatorNode):
                    self.warnings.append(ValidationError(
                        type="warning",
                        location=f"{path}[{i}]",
                        message="Back-to-back separators have no visual effect",
                        field="type"
                    ))
            
            elif isinstance(node, GroupNode):
                # Recursively validate group's children
                self._validate_separator_placement(node.items, f"{path}[{i}].items")
    
    def validate_item_command(self, cmd: str) -> List[str]:
        """
        Validate a command string for basic syntax issues
        
        Args:
            cmd: Command string to validate
            
        Returns:
            List of validation messages
        """
        issues = []
        
        if not cmd or not cmd.strip():
            issues.append("Command cannot be empty")
            return issues
        
        cmd = cmd.strip()
        
        # Check for common issues
        if cmd.startswith('|') or cmd.endswith('|'):
            issues.append("Command appears to be a pipe fragment")
        
        if '&&' in cmd and not any(op in cmd for op in [';', '|', '&&', '||']):
            issues.append("Command uses && but may need proper shell syntax")
        
        # Check for potentially dangerous commands
        dangerous_commands = ['rm -rf', 'sudo rm', 'dd if=', 'mkfs', 'fdisk']
        for dangerous in dangerous_commands:
            if dangerous in cmd.lower():
                issues.append(f"Warning: Command contains potentially dangerous operation: {dangerous}")
        
        return issues
    
    def get_validation_summary(self, config: Config) -> dict:
        """
        Get a summary of validation results
        
        Args:
            config: Config object to validate
            
        Returns:
            Dictionary with validation summary
        """
        errors = self.validate_config(config)
        
        error_count = len([e for e in errors if e.type == "error"])
        warning_count = len([e for e in errors if e.type == "warning"])
        
        return {
            "total_errors": error_count,
            "total_warnings": warning_count,
            "is_valid": error_count == 0,
            "errors": errors
        }


# Global validator instance
config_validator = ConfigValidator()
