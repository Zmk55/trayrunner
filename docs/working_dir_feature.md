# Working Directory Feature

## Overview

TrayRunner now supports specifying a working directory for command execution. When the `working_dir` field is set on a menu item, the command will be executed with that directory as its current working directory (cwd).

## Configuration

### YAML Configuration

Add the `working_dir` field to any item in your `~/.config/trayrunner/commands.yaml`:

```yaml
items:
  - type: item
    label: "Git Status"
    cmd: "git status"
    working_dir: "~/projects/myproject"
    terminal: true

  - type: item
    label: "List Files"
    cmd: "ls -la"
    working_dir: "/var/log"
    terminal: true

  - type: item
    label: "Python Script"
    cmd: "python3 script.py"
    working_dir: "$HOME/scripts"
    terminal: false
```

### Schema Definition

In code, the `ItemNode` model includes the `working_dir` field:

```python
from trayrunner_gui.models.schema import ItemNode

item = ItemNode(
    label="Test Command",
    cmd="pwd",
    working_dir="/tmp",
    terminal=False
)
```

## Features

### Path Expansion

The `working_dir` field supports several path expansion features:

1. **Tilde Expansion**: `~/` expands to the user's home directory
   ```yaml
   working_dir: "~/projects"  # Becomes /home/username/projects
   ```

2. **Environment Variables**: Standard shell variable expansion
   ```yaml
   working_dir: "$HOME/work"  # Expands $HOME
   working_dir: "${PROJECT_ROOT}/src"  # Expands ${PROJECT_ROOT}
   ```

3. **Absolute and Relative Paths**: Both are supported
   ```yaml
   working_dir: "/opt/myapp"  # Absolute path
   ```

### Error Handling

The implementation includes robust error handling:

1. **Nonexistent Directory**: Shows error notification if directory doesn't exist
   ```
   Error: Working directory does not exist: /path/to/nowhere
   ```

2. **Not a Directory**: Shows error if path points to a file
   ```
   Error: Working directory path is not a directory: /path/to/file.txt
   ```

3. **Permission Denied**: Shows error if directory isn't accessible
   ```
   Error: Working directory is not accessible: /path/to/restricted
   ```

4. **Command Not Executed**: If working_dir validation fails, the command is NOT executed for safety

### Logging

All executions with working_dir are logged with the directory information:

```
2025-11-05 14:30:22 - INFO - Started command: Git Status -> git status (cwd: /home/user/projects)
```

### Backward Compatibility

The feature is fully backward compatible:

- Existing configs without `working_dir` work unchanged
- `working_dir: null` or omitted field means no special working directory (uses default)
- Empty string `working_dir: ""` is treated as unset

## Implementation Details

### Code Location

The working directory logic is implemented in:
- **Execution**: `/home/tim/Github/trayrunner/src/trayrunner/app.py` - `CommandRunner.run_command()` method
- **Schema**: `/home/tim/Github/trayrunner/gui/trayrunner_gui/models/schema.py` - `ItemNode` model
- **Tests**: `/home/tim/Github/trayrunner/tests/test_working_dir_execution.py`

### Subprocess Integration

The working directory is passed directly to `subprocess.Popen` as the `cwd` parameter:

```python
process = subprocess.Popen(
    cmd_parts,
    env=env,
    cwd=working_dir,  # Working directory parameter
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)
```

This works for both:
- Regular commands (terminal: false)
- Terminal commands (terminal: true)

## Testing

### Running Tests

Run all working_dir tests:

```bash
# Full test suite
bash tests/run_working_dir_tests.sh

# Just execution tests (no GUI dependencies needed)
python3 tests/test_working_dir_execution.py

# Just schema tests (requires virtualenv with GUI deps)
source .venv/bin/activate
python3 tests/test_working_dir.py
```

### Test Coverage

The test suite includes:

**Unit Tests** (`test_working_dir_execution.py`):
- Command runs in specified working directory
- Command runs normally without working_dir (backward compatibility)
- Nonexistent directory shows error and prevents execution
- File path (not directory) shows error
- Tilde expansion (~/)
- Environment variable expansion ($HOME, ${VAR})
- Permission denied handling
- Terminal command support
- Empty string handling

**Schema Tests** (`test_working_dir.py`):
- Schema accepts working_dir field
- YAML roundtrip preserves working_dir
- Backward compatibility with old configs
- Model serialization includes working_dir

**Integration Tests**:
- Real command execution with working_dir
- Verification of actual subprocess cwd parameter

### Test Results

All tests pass successfully:

```
Ran 11 tests in 0.134s
OK (skipped=1)
```

## Usage Examples

### Example 1: Project-Specific Commands

```yaml
items:
  - type: group
    label: "My Project"
    items:
      - type: item
        label: "Run Tests"
        cmd: "npm test"
        working_dir: "~/projects/myapp"
        terminal: true

      - type: item
        label: "Start Dev Server"
        cmd: "npm run dev"
        working_dir: "~/projects/myapp"
        terminal: true

      - type: item
        label: "Build"
        cmd: "npm run build"
        working_dir: "~/projects/myapp"
        terminal: false
```

### Example 2: System Administration

```yaml
items:
  - type: item
    label: "Check Logs"
    cmd: "tail -f syslog"
    working_dir: "/var/log"
    terminal: true

  - type: item
    label: "Backup Config"
    cmd: "tar -czf backup.tar.gz *.conf"
    working_dir: "/etc/myapp"
    terminal: false
```

### Example 3: Multiple Projects

```yaml
items:
  - type: item
    label: "Project A Status"
    cmd: "git status"
    working_dir: "$PROJECT_A_ROOT"
    terminal: true
    env:
      PROJECT_A_ROOT: "/home/user/projectA"

  - type: item
    label: "Project B Status"
    cmd: "git status"
    working_dir: "$PROJECT_B_ROOT"
    terminal: true
    env:
      PROJECT_B_ROOT: "/home/user/projectB"
```

## GUI Editor Support

The GUI editor fully supports the `working_dir` field:

1. **Edit Panel**: Shows a text input field for working_dir
2. **Validation**: Real-time validation warns if directory doesn't exist
3. **Path Browser**: Use file dialog to select directories (if implemented)
4. **Save/Load**: working_dir preserved in YAML roundtrip

## Migration Guide

### For Existing Configs

No migration needed! Existing configs work as-is:

```yaml
# Old config (still works)
- type: item
  label: "Old Command"
  cmd: "echo hello"
  terminal: false

# New config (with working_dir)
- type: item
  label: "New Command"
  cmd: "echo hello"
  working_dir: "/tmp"
  terminal: false
```

### For Custom Integrations

If you have custom code that creates menu items programmatically:

```python
# Old way (still works)
item = {
    "type": "item",
    "label": "Command",
    "cmd": "pwd"
}

# New way (with working_dir)
item = {
    "type": "item",
    "label": "Command",
    "cmd": "pwd",
    "working_dir": "/tmp"
}
```

## Troubleshooting

### Command Doesn't Execute

**Problem**: Command doesn't run, shows error notification

**Solutions**:
1. Check that working_dir path exists: `ls -ld /path/to/dir`
2. Check permissions: `ls -ld /path/to/dir` (needs r-x)
3. Check logs: `tail ~/.local/state/trayrunner/run.log`
4. Verify path expansion: Use absolute paths first to debug

### Tilde Not Expanding

**Problem**: `~/projects` not expanding to home directory

**Solution**: This is automatically handled. Check logs to see actual expanded path.

### Environment Variable Not Expanding

**Problem**: `$HOME/work` not expanding

**Solution**:
1. Make sure variable is set: `echo $HOME`
2. Use proper syntax: `$VAR` or `${VAR}`
3. Check that variable is in environment (not shell-specific)

### Permission Denied

**Problem**: "Working directory is not accessible"

**Solution**:
1. Check directory permissions: `ls -ld /path`
2. Ensure both read (r) and execute (x) permissions
3. Run: `chmod u+rx /path/to/dir` if you own it
4. Use sudo if accessing system directories (not recommended for tray commands)

## Security Considerations

1. **Path Validation**: All paths are validated before execution
2. **No Command Injection**: working_dir is passed as separate parameter, not concatenated to command
3. **Permission Checks**: Validates read and execute permissions before attempting execution
4. **Error Safety**: Failed validation prevents command execution entirely
5. **Logging**: All executions with working_dir are logged for audit trail

## Future Enhancements

Potential future improvements:

1. **Relative Paths**: Support relative paths from config file location
2. **Path Autocomplete**: GUI editor autocomplete for directories
3. **Recent Directories**: Remember recently used working directories
4. **Directory Validation**: Real-time validation in GUI editor
5. **Path Variables**: Built-in variables like `${CONFIG_DIR}`, `${HOME}`
