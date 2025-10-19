"""Test reload socket path function"""
import os
from pathlib import Path


def _reload_sock_path():
    """Replicate the socket path function for testing"""
    state_dir = Path.home() / ".local" / "state" / "trayrunner"
    state_dir.mkdir(parents=True, exist_ok=True)
    return str(state_dir / "reload.sock")


def test_reload_socket_path():
    """Test that the reload socket path is correctly formatted"""
    sock_path = _reload_sock_path()
    
    # Should be a string
    assert isinstance(sock_path, str), "Socket path should be a string"
    
    # Should end with reload.sock
    assert sock_path.endswith("reload.sock"), "Socket path should end with 'reload.sock'"
    
    # Should be in the expected directory structure
    assert ".local/state/trayrunner" in sock_path, "Socket should be in .local/state/trayrunner"
    
    # Should be an absolute path
    assert os.path.isabs(sock_path), "Socket path should be absolute"
    
    print(f"✓ Socket path test passed: {sock_path}")


def test_socket_path_consistency():
    """Test that the socket path is consistent across calls"""
    path1 = _reload_sock_path()
    path2 = _reload_sock_path()
    
    assert path1 == path2, "Socket path should be consistent across calls"
    print("✓ Socket path consistency test passed")


if __name__ == "__main__":
    test_reload_socket_path()
    test_socket_path_consistency()
    print("All socket tests passed!")
