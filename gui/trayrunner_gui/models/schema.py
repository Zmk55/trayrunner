"""
Pydantic schema models for TrayRunner configuration
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal, Dict, Union, Annotated
from enum import Enum
from uuid import uuid4


def generate_node_id() -> str:
    """Generate a unique node ID"""
    return str(uuid4())


class NodeType(str, Enum):
    """Node type enumeration"""
    ITEM = "item"
    GROUP = "group"
    SEPARATOR = "separator"


class ItemNode(BaseModel):
    """Configuration item node"""
    type: Literal["item"] = "item"
    id: str = Field(default_factory=generate_node_id, description="Unique node identifier")
    label: str = Field(..., description="Display name for the menu item")
    cmd: str = Field(..., description="Command to execute")
    terminal: bool = Field(False, description="Run command in terminal")
    confirm: bool = Field(False, description="Show confirmation dialog before execution")
    env: Dict[str, str] = Field(default_factory=dict, description="Environment variables")
    
    @field_validator('label')
    @classmethod
    def validate_label(cls, v):
        if not v or not v.strip():
            raise ValueError('Label cannot be empty')
        return v.strip()
    
    @field_validator('cmd')
    @classmethod
    def validate_cmd(cls, v):
        if not v or not v.strip():
            raise ValueError('Command cannot be empty')
        return v.strip()


class GroupNode(BaseModel):
    """Configuration group node (submenu)"""
    type: Literal["group"] = "group"
    id: str = Field(default_factory=generate_node_id, description="Unique node identifier")
    label: str = Field(..., description="Display name for the submenu")
    items: List["Node"] = Field(default_factory=list, description="Items in this group")
    
    @field_validator('label')
    @classmethod
    def validate_label(cls, v):
        if not v or not v.strip():
            raise ValueError('Group label cannot be empty')
        return v.strip()


class SeparatorNode(BaseModel):
    """Configuration separator node"""
    type: Literal["separator"] = "separator"
    id: str = Field(default_factory=generate_node_id, description="Unique node identifier")


# Forward reference for Node union type with discriminated union
Node = Annotated[Union[ItemNode, GroupNode, SeparatorNode], Field(discriminator='type')]

# Update forward references
GroupNode.model_rebuild()


class Config(BaseModel):
    """Root configuration model"""
    items: List[Node] = Field(default_factory=list, description="List of menu items")
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        """Validate that items list is not None"""
        if v is None:
            return []
        return v


class ValidationError(BaseModel):
    """Validation error model"""
    type: str = Field(..., description="Error type (error, warning)")
    location: str = Field(..., description="Node path in configuration")
    message: str = Field(..., description="Error message")
    field: Optional[str] = Field(None, description="Specific field that caused the error")


class ConfigBackup(BaseModel):
    """Configuration backup information"""
    original_path: str = Field(..., description="Path to original file")
    backup_path: str = Field(..., description="Path to backup file")
    timestamp: str = Field(..., description="Backup timestamp")
    size: int = Field(..., description="File size in bytes")
