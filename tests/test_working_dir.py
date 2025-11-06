#!/usr/bin/env python3
"""
Test working_dir feature implementation
"""

import os
import sys
import tempfile
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))

from gui.trayrunner_gui.models.schema import ItemNode, Config
from gui.trayrunner_gui.models.yaml_io import YAMLHandler


def test_schema_working_dir():
    """Test that ItemNode schema supports working_dir"""
    print("Testing schema with working_dir...")

    # Test with working_dir
    item = ItemNode(
        label="Test Command",
        cmd="pwd",
        working_dir="/tmp"
    )
    assert item.working_dir == "/tmp"
    assert item.label == "Test Command"
    assert item.cmd == "pwd"
    print("✓ Schema accepts working_dir")

    # Test without working_dir (backward compatibility)
    item_no_dir = ItemNode(
        label="Test Command 2",
        cmd="echo hello"
    )
    assert item_no_dir.working_dir is None
    print("✓ Schema works without working_dir (backward compatible)")

    # Test model_dump includes working_dir
    data = item.model_dump()
    assert "working_dir" in data
    assert data["working_dir"] == "/tmp"
    print("✓ model_dump includes working_dir")


def test_yaml_roundtrip():
    """Test that working_dir survives YAML save/load cycle"""
    print("\nTesting YAML roundtrip...")

    handler = YAMLHandler()

    # Create config with working_dir
    config = Config(items=[
        ItemNode(
            label="Command with Dir",
            cmd="ls -la",
            working_dir="/home",
            terminal=False
        ),
        ItemNode(
            label="Command without Dir",
            cmd="echo test",
            terminal=True
        )
    ])

    # Save to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_path = Path(f.name)

    try:
        # Save
        handler.save_yaml(temp_path, config)
        print(f"✓ Saved config to {temp_path}")

        # Load back
        loaded_config, _ = handler.load_yaml(temp_path)
        print("✓ Loaded config back")

        # Verify first item has working_dir
        assert len(loaded_config.items) == 2
        item1 = loaded_config.items[0]
        assert item1.label == "Command with Dir"
        assert item1.working_dir == "/home"
        print("✓ First item working_dir preserved")

        # Verify second item doesn't have working_dir
        item2 = loaded_config.items[1]
        assert item2.label == "Command without Dir"
        assert item2.working_dir is None
        print("✓ Second item working_dir is None (backward compatible)")

        # Check YAML content
        with open(temp_path, 'r') as f:
            yaml_content = f.read()
            print("\nGenerated YAML:")
            print(yaml_content)
            assert "working_dir: /home" in yaml_content
            print("✓ working_dir present in YAML file")

    finally:
        # Cleanup
        if temp_path.exists():
            temp_path.unlink()
        # Remove backup files
        for backup in temp_path.parent.glob(f"{temp_path.stem}*.bak-*"):
            backup.unlink()


def test_backward_compatibility():
    """Test loading old configs without working_dir"""
    print("\nTesting backward compatibility...")

    handler = YAMLHandler()

    # Create a YAML file without working_dir
    yaml_content = """items:
  - type: item
    label: Old Command
    cmd: echo hello
    terminal: false
    confirm: false
    env: {}
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(yaml_content)
        temp_path = Path(f.name)

    try:
        # Load old config
        config, _ = handler.load_yaml(temp_path)
        print("✓ Old config loaded successfully")

        assert len(config.items) == 1
        item = config.items[0]
        assert item.label == "Old Command"
        assert item.working_dir is None
        print("✓ working_dir defaults to None for old configs")

    finally:
        if temp_path.exists():
            temp_path.unlink()


def test_command_execution_mock():
    """Test that command data structure is correct for execution"""
    print("\nTesting command execution data structure...")

    # Create item with working_dir
    item = ItemNode(
        label="Test Command",
        cmd="pwd",
        working_dir="/tmp",
        terminal=False,
        confirm=False
    )

    # Convert to dict (as would be passed to command runner)
    item_dict = item.model_dump()

    # Verify structure
    assert item_dict["working_dir"] == "/tmp"
    assert item_dict["cmd"] == "pwd"
    print("✓ Command data structure includes working_dir")

    # Test with None working_dir
    item_no_dir = ItemNode(
        label="Test Command 2",
        cmd="echo hello"
    )
    item_dict_no_dir = item_no_dir.model_dump()
    assert item_dict_no_dir["working_dir"] is None
    print("✓ Command data structure handles None working_dir")


def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing working_dir Feature Implementation")
    print("=" * 60)

    try:
        test_schema_working_dir()
        test_yaml_roundtrip()
        test_backward_compatibility()
        test_command_execution_mock()

        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return 0

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
