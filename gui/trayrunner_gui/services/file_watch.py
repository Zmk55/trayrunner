"""
File watching service for external configuration changes
"""

import os
from pathlib import Path
from typing import Optional, Callable
from PySide6.QtCore import QObject, Signal, QTimer
from trayrunner_gui.services.save_coordinator import save_coordinator

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    # Create dummy classes when watchdog is not available
    class Observer:
        def __init__(self, *args, **kwargs): pass
        def schedule(self, *args, **kwargs): pass
        def start(self, *args, **kwargs): pass
        def stop(self, *args, **kwargs): pass
        def is_alive(self): return False
        def join(self, *args, **kwargs): pass
    
    class FileSystemEventHandler:
        def __init__(self, *args, **kwargs): pass
        def on_modified(self, *args, **kwargs): pass


class ConfigFileHandler(FileSystemEventHandler):
    """Handles file system events for configuration files"""
    
    def __init__(self, callback: Callable[[str], None]):
        super().__init__()
        self.callback = callback
        self.last_modified = {}
    
    def on_modified(self, event):
        """Handle file modification events"""
        if event.is_directory:
            return
        
        # Only handle YAML files
        if not event.src_path.endswith(('.yaml', '.yml')):
            return
        
        # Debounce rapid file changes
        current_time = os.path.getmtime(event.src_path)
        if event.src_path in self.last_modified:
            if current_time - self.last_modified[event.src_path] < 1.0:  # 1 second debounce
                return
        
        self.last_modified[event.src_path] = current_time
        
        # Notify callback
        if self.callback:
            self.callback(event.src_path)


class FileWatcher(QObject):
    """Qt-based file watcher with optional watchdog backend"""
    
    # Signal emitted when file changes
    file_changed = Signal(str)
    
    def __init__(self, watch_path: Path, parent=None):
        super().__init__(parent)
        self.watch_path = watch_path
        self.observer: Optional[Observer] = None
        self.timer = QTimer()
        self.timer.timeout.connect(self._check_file_changes)
        self.last_modified = {}
        
        # Setup watchdog if available
        if WATCHDOG_AVAILABLE:
            self._setup_watchdog()
        else:
            # Fallback to polling
            self._setup_polling()
    
    def _setup_watchdog(self):
        """Setup watchdog-based file monitoring"""
        try:
            self.observer = Observer()
            handler = ConfigFileHandler(self._on_file_changed)
            self.observer.schedule(handler, str(self.watch_path.parent), recursive=False)
            self.observer.start()
        except Exception as e:
            print(f"Failed to setup watchdog: {e}")
            self._setup_polling()
    
    def _setup_polling(self):
        """Setup polling-based file monitoring (fallback)"""
        self.timer.start(2000)  # Check every 2 seconds
    
    def _on_file_changed(self, file_path: str):
        """Handle file change from watchdog"""
        if Path(file_path) == self.watch_path:
            self.file_changed.emit(file_path)
    
    def _check_file_changes(self):
        """Check for file changes (polling fallback)"""
        if not self.watch_path.exists():
            return
        
        current_time = self.watch_path.stat().st_mtime
        if self.watch_path in self.last_modified:
            if current_time > self.last_modified[self.watch_path]:
                self.file_changed.emit(str(self.watch_path))
        
        self.last_modified[self.watch_path] = current_time
    
    def start(self):
        """Start watching for file changes"""
        if self.observer and not self.observer.is_alive():
            self.observer.start()
        elif not self.observer:
            self.timer.start()
    
    def stop(self):
        """Stop watching for file changes"""
        if self.observer and self.observer.is_alive():
            self.observer.stop()
        self.timer.stop()
    
    def is_watching(self) -> bool:
        """Check if currently watching for changes"""
        if self.observer:
            return self.observer.is_alive()
        return self.timer.isActive()
    
    def cleanup(self):
        """Cleanup resources"""
        self.stop()
        if self.observer:
            self.observer.join()


class ConfigFileWatcher:
    """High-level configuration file watcher"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.watcher: Optional[FileWatcher] = None
        self.change_callback: Optional[Callable[[str], None]] = None
        self._paused = 0  # Reference counter for nested pauses
    
    def start_watching(self, callback: Callable[[str], None]):
        """
        Start watching for configuration file changes
        
        Args:
            callback: Function to call when file changes
        """
        self.change_callback = callback
        
        if self.watcher:
            self.stop_watching()
        
        self.watcher = FileWatcher(self.config_path)
        self.watcher.file_changed.connect(self._on_file_changed)
        self.watcher.start()
    
    def stop_watching(self):
        """Stop watching for file changes"""
        if self.watcher:
            self.watcher.cleanup()
            self.watcher = None
    
    def pause(self):
        """Pause file watching (reference counted)"""
        self._paused += 1
    
    def resume(self):
        """Resume file watching (reference counted)"""
        self._paused = max(0, self._paused - 1)
    
    def _on_file_changed(self, file_path: str):
        """Handle file change event"""
        if self._paused:
            return  # Ignore events while paused
        
        # Check if this is our own save
        if save_coordinator.should_ignore_change(Path(file_path)):
            return
        
        if self.change_callback:
            self.change_callback(file_path)
    
    def is_watching(self) -> bool:
        """Check if currently watching"""
        return self.watcher and self.watcher.is_watching()
    
    def __del__(self):
        """Cleanup on destruction"""
        self.stop_watching()
