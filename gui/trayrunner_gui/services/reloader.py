"""
Service for reloading TrayRunner configuration
"""

import shutil
import subprocess
import sys
from typing import Tuple


def try_reload(retries: int = 3, delay_s: float = 0.2) -> Tuple[bool, str]:
    """
    Attempt to reload TrayRunner configuration with retries
    
    Args:
        retries: Number of retry attempts
        delay_s: Delay between retries in seconds
        
    Returns:
        Tuple of (success, message)
    """
    import os
    import time
    
    # Find trayrunner executable
    # 1) Check if running in AppImage context
    appdir = os.environ.get("APPDIR")
    if appdir:
        # When GUI is in AppImage, trayrunner might be on system PATH
        # or launched from a different AppImage instance
        exe = shutil.which("trayrunner")
    else:
        # Standard PATH lookup (pipx/dev)
        exe = shutil.which("trayrunner")
    
    if not exe:
        return (False, "trayrunner not found on PATH. If using AppImage, ensure TrayRunner is running.")
    
    last_msg = ""
    for attempt in range(retries):
        try:
            # Call trayrunner --reload
            result = subprocess.run(
                [exe, "--reload"],
                capture_output=True,
                text=True,
                timeout=10  # 10 second timeout
            )
            
            last_msg = result.stdout.strip() or result.stderr.strip()
            
            if result.returncode == 0:
                return (True, last_msg or "Reload OK")
            
            # Wait before retry
            if attempt < retries - 1:
                time.sleep(delay_s)
                
        except subprocess.TimeoutExpired:
            last_msg = "Reload command timed out"
        except FileNotFoundError:
            return (False, "trayrunner executable not found")
        except Exception as e:
            last_msg = f"Failed to execute reload: {e}"
    
    return (False, last_msg or "Reload failed after retries")


def is_trayrunner_running() -> bool:
    """
    Check if TrayRunner is currently running
    
    Returns:
        True if running, False otherwise
    """
    try:
        # Check if trayrunner process is running
        result = subprocess.run(
            ["pgrep", "-f", "python.*trayrunner"],
            capture_output=True,
            text=True
        )
        return result.returncode == 0 and result.stdout.strip()
    except Exception:
        return False


def get_trayrunner_status() -> Tuple[bool, str]:
    """
    Get TrayRunner status information
    
    Returns:
        Tuple of (is_running, status_message)
    """
    if not shutil.which("trayrunner"):
        return (False, "trayrunner command not found in PATH")
    
    try:
        # Try to get status using trayrunner status command
        result = subprocess.run(
            ["trayrunner", "status"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            return (True, result.stdout.strip())
        else:
            return (False, result.stderr.strip() or "TrayRunner not running")
            
    except subprocess.TimeoutExpired:
        return (False, "Status check timed out")
    except Exception as e:
        return (False, f"Status check failed: {e}")


class ReloadManager:
    """Manages TrayRunner reload operations"""
    
    def __init__(self):
        self.last_reload_result = None
        self.last_reload_time = None
    
    def reload_config(self) -> Tuple[bool, str]:
        """
        Reload TrayRunner configuration and cache result
        
        Returns:
            Tuple of (success, message)
        """
        success, message = try_reload()
        
        self.last_reload_result = (success, message)
        self.last_reload_time = __import__('time').time()
        
        return success, message
    
    def get_last_reload_result(self) -> Tuple[bool, str]:
        """Get the result of the last reload attempt"""
        return self.last_reload_result or (False, "No reload attempted yet")
    
    def can_reload(self) -> bool:
        """Check if reload is possible (TrayRunner is running)"""
        return is_trayrunner_running()


# Global reload manager instance
reload_manager = ReloadManager()
