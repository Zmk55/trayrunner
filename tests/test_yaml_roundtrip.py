"""Test YAML save/load with all node types"""
import tempfile
import os
from pathlib import Path

# Import the modules we need to test
try:
    from trayrunner_gui.models.yaml_io import YAMLHandler
    from trayrunner_gui.models.schema import Config, ItemNode, GroupNode, SeparatorNode
except ImportError:
    # If running from repo root, adjust import path
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
    from gui.trayrunner_gui.models.yaml_io import YAMLHandler
    from gui.trayrunner_gui.models.schema import Config, ItemNode, GroupNode, SeparatorNode


def test_yaml_roundtrip():
    """Test that we can save and load a complex configuration"""
    # Create a test configuration with all node types
    config = Config(items=[
        ItemNode(type='item', label='Test Item', cmd='echo "Hello World"', terminal=False, confirm=False),
        SeparatorNode(type='separator'),
        GroupNode(type='group', label='Test Group', items=[
            ItemNode(type='item', label='Nested Item', cmd='ls -la', terminal=True, confirm=False),
            SeparatorNode(type='separator'),
            ItemNode(type='item', label='Another Item', cmd='pwd', terminal=False, confirm=True)
        ]),
        SeparatorNode(type='separator'),
        ItemNode(type='item', label='Final Item', cmd='date', terminal=False, confirm=False)
    ])
    
    # Save to temporary file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        tmp_path = Path(tmp.name)
    
    try:
        # Use YAMLHandler to save the configuration
        handler = YAMLHandler()
        handler.save_yaml(tmp_path, config)
        
        # Verify file exists and has content
        assert tmp_path.exists(), "File should exist after save"
        content = tmp_path.read_text()
        assert len(content) > 0, "File should not be empty"
        
        # Check that key elements are present
        assert "type: item" in content, "Should contain item nodes"
        assert "type: separator" in content, "Should contain separator nodes"
        assert "type: group" in content, "Should contain group nodes"
        assert "Test Item" in content, "Should contain our test item"
        assert "Test Group" in content, "Should contain our test group"
        
        # Load the configuration back
        loaded_config, _ = handler.load_yaml(tmp_path)
        
        # Debug: print what we actually got
        print(f"Loaded config has {len(loaded_config.items)} items")
        for i, item in enumerate(loaded_config.items):
            print(f"  Item {i}: {type(item).__name__} - {getattr(item, 'label', 'no label')}")
        
        # Verify structure
        assert len(loaded_config.items) == 5, f"Should have 5 top-level items, got {len(loaded_config.items)}"
        
        # Check first item
        first_item = loaded_config.items[0]
        assert isinstance(first_item, ItemNode), "First item should be ItemNode"
        assert first_item.label == "Test Item", "Label should match"
        assert first_item.cmd == 'echo "Hello World"', "Command should match"
        
        # Check separator
        assert isinstance(loaded_config.items[1], SeparatorNode), "Second item should be SeparatorNode"
        
        # Check group
        group = loaded_config.items[2]
        assert isinstance(group, GroupNode), "Third item should be GroupNode"
        assert group.label == "Test Group", "Group label should match"
        assert len(group.items) == 3, "Group should have 3 items"
        
        # Check nested items
        nested_item = group.items[0]
        assert isinstance(nested_item, ItemNode), "First nested item should be ItemNode"
        assert nested_item.label == "Nested Item", "Nested item label should match"
        assert nested_item.terminal == True, "Nested item should be terminal"
        
        # Check nested separator
        assert isinstance(group.items[1], SeparatorNode), "Nested separator should be SeparatorNode"
        
        # Check final nested item
        final_nested = group.items[2]
        assert isinstance(final_nested, ItemNode), "Last nested item should be ItemNode"
        assert final_nested.confirm == True, "Last nested item should require confirmation"
        
        # Check final separator and item
        assert isinstance(loaded_config.items[3], SeparatorNode), "Fourth item should be SeparatorNode"
        assert isinstance(loaded_config.items[4], ItemNode), "Fifth item should be ItemNode"
        assert loaded_config.items[4].label == "Final Item", "Final item label should match"
        
        print("✓ YAML roundtrip test passed")
        
    finally:
        # Clean up
        if tmp_path.exists():
            tmp_path.unlink()


def test_empty_config():
    """Test saving and loading an empty configuration"""
    config = Config(items=[])
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as tmp:
        tmp_path = Path(tmp.name)
    
    try:
        handler = YAMLHandler()
        handler.save_yaml(tmp_path, config)
        loaded_config, _ = handler.load_yaml(tmp_path)
        assert len(loaded_config.items) == 0, "Empty config should have no items"
        print("✓ Empty config test passed")
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


if __name__ == "__main__":
    test_yaml_roundtrip()
    test_empty_config()
    print("All tests passed!")
