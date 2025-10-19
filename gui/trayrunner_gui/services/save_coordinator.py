"""
Save coordinator to prevent self-triggered file change notifications
"""

from dataclasses import dataclass
from pathlib import Path
import os
import time
import threading


@dataclass
class SaveWindow:
    """Tracks a save operation window"""
    until: float  # monotonic timestamp
    inode: int | None
    size: int | None
    mtime_ns: int | None


class SaveCoordinator:
    """Prevents self-triggered file change notifications"""
    
    def __init__(self):
        self._lock = threading.Lock()
        self._saves: dict[Path, SaveWindow] = {}
    
    def begin_save(self, path: Path, window_s: float = 2.0):
        """Mark beginning of save operation"""
        with self._lock:
            self._saves[path] = SaveWindow(
                until=time.monotonic() + window_s,
                inode=None, size=None, mtime_ns=None
            )
    
    def end_save(self, path: Path):
        """Mark end of save and record file stats"""
        try:
            st = os.stat(path)
            with self._lock:
                if path in self._saves:
                    self._saves[path].inode = st.st_ino
                    self._saves[path].size = st.st_size
                    self._saves[path].mtime_ns = st.st_mtime_ns
                    # Extend window after save completes
                    self._saves[path].until = time.monotonic() + 1.5
        except FileNotFoundError:
            pass
    
    def should_ignore_change(self, path: Path) -> bool:
        """Check if file change should be ignored (it's our own save)"""
        now = time.monotonic()
        with self._lock:
            window = self._saves.get(path)
            if not window:
                return False
            
            # Window expired - clean up and allow event
            if now > window.until:
                self._saves.pop(path, None)
                return False
            
            # Save in progress (no stats yet)
            if window.inode is None:
                return True
            
            # Compare file stats to confirm it's our write
            try:
                st = os.stat(path)
                if (st.st_ino == window.inode and 
                    st.st_size == window.size and
                    st.st_mtime_ns == window.mtime_ns):
                    return True
            except FileNotFoundError:
                return True  # File missing during save operation
            
            return True  # Conservative: ignore during window


# Global singleton
save_coordinator = SaveCoordinator()
