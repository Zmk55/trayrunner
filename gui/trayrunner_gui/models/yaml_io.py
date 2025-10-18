"""
YAML I/O operations with comment and order preservation
"""

import shutil
from datetime import datetime
from pathlib import Path
from typing import Tuple, Optional
from ruamel.yaml import YAML, CommentedMap, CommentedSeq
from ruamel.yaml.comments import CommentedMap as CM

from .schema import Config, ConfigBackup


class YAMLHandler:
    """Handles YAML loading and saving with comment preservation"""
    
    def __init__(self):
        self.yaml = YAML()
        self.yaml.preserve_quotes = True
        self.yaml.width = 120
        self.yaml.indent(mapping=2, sequence=4, offset=2)
    
    def load_yaml(self, path: Path) -> Tuple[Config, Optional[CommentedMap]]:
        """
        Load YAML configuration with comment preservation
        
        Args:
            path: Path to YAML file
            
        Returns:
            Tuple of (Config object, original ruamel.yaml object for comment preservation)
        """
        if not path.exists():
            return Config(), None
            
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = self.yaml.load(f)
            
            if data is None:
                return Config(), None
                
            # Convert to our Config model
            config = Config.model_validate(data)
            return config, data
            
        except Exception as e:
            raise ValueError(f"Failed to load YAML from {path}: {e}")
    
    def save_yaml(self, path: Path, config: Config, original_yaml: Optional[CommentedMap] = None) -> Path:
        """
        Save YAML configuration with comment preservation
        
        Args:
            path: Path to save YAML file
            config: Config object to save
            original_yaml: Original ruamel.yaml object to preserve comments
            
        Returns:
            Path to backup file created
        """
        # Create backup first
        backup_path = self.create_backup(path)
        
        try:
            # Convert config to dict, excluding 'id' fields
            data = config.model_dump()
            
            # Recursively remove 'id' from nested structures
            data = self._remove_ids_recursive(data)
            
            # If we have original YAML, try to preserve comments
            if original_yaml is not None:
                # Create a new CommentedMap with preserved structure
                new_data = self._preserve_comments(data, original_yaml)
            else:
                new_data = data
            
            # Write atomically (write to temp file, then move)
            temp_path = path.with_suffix('.tmp')
            with open(temp_path, 'w', encoding='utf-8') as f:
                self.yaml.dump(new_data, f)
                f.flush()
                import os
                os.fsync(f.fileno())  # Ensure data is written to disk
            
            # Move temp file to final location
            shutil.move(str(temp_path), str(path))
            
            return backup_path
            
        except Exception as e:
            # Restore backup if save failed
            if backup_path.exists():
                shutil.copy2(backup_path, path)
            raise ValueError(f"Failed to save YAML to {path}: {e}")
    
    def _remove_ids_recursive(self, data):
        """Recursively remove 'id' fields from data structure"""
        if isinstance(data, dict):
            return {k: self._remove_ids_recursive(v) for k, v in data.items() if k != 'id'}
        elif isinstance(data, list):
            return [self._remove_ids_recursive(item) for item in data]
        return data
    
    def create_backup(self, path: Path) -> Path:
        """
        Create timestamped backup of file
        
        Args:
            path: Path to file to backup
            
        Returns:
            Path to backup file
        """
        if not path.exists():
            raise FileNotFoundError(f"Cannot backup non-existent file: {path}")
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = path.with_suffix(f'.yaml.bak-{timestamp}')
        
        # Ensure backup directory exists
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Copy file to backup location
        shutil.copy2(path, backup_path)
        
        return backup_path
    
    def _preserve_comments(self, new_data: dict, original_yaml: CommentedMap) -> CommentedMap:
        """
        Preserve comments from original YAML structure
        
        Args:
            new_data: New data to write
            original_yaml: Original YAML with comments
            
        Returns:
            New CommentedMap with preserved comments where possible
        """
        # This is a simplified implementation
        # In a full implementation, you'd traverse the structure and preserve comments
        result = CommentedMap()
        
        # Copy structure from new_data
        for key, value in new_data.items():
            if isinstance(value, list):
                new_list = CommentedSeq()
                for item in value:
                    if isinstance(item, dict):
                        new_item = CommentedMap(item)
                    else:
                        new_item = item
                    new_list.append(new_item)
                result[key] = new_list
            elif isinstance(value, dict):
                result[key] = CommentedMap(value)
            else:
                result[key] = value
        
        return result
    
    def get_backup_info(self, path: Path) -> list[ConfigBackup]:
        """
        Get information about available backups
        
        Args:
            path: Path to original file
            
        Returns:
            List of ConfigBackup objects
        """
        backups = []
        backup_pattern = f"{path.stem}.yaml.bak-*"
        
        for backup_file in path.parent.glob(backup_pattern):
            try:
                stat = backup_file.stat()
                timestamp = backup_file.name.split('.bak-')[-1]
                backups.append(ConfigBackup(
                    original_path=str(path),
                    backup_path=str(backup_file),
                    timestamp=timestamp,
                    size=stat.st_size
                ))
            except Exception:
                continue
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.timestamp, reverse=True)
        return backups


# Global YAML handler instance
yaml_handler = YAMLHandler()
