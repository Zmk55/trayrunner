#!/bin/bash
# Test runner for working_dir feature
# Runs both schema tests and execution tests

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================"
echo "TrayRunner working_dir Feature Tests"
echo "========================================"
echo

# Test 1: Command execution tests (no GUI dependencies needed)
echo "Running command execution tests..."
echo "-----------------------------------"
python3 "$SCRIPT_DIR/test_working_dir_execution.py"
echo

# Test 2: Schema and YAML tests (requires GUI dependencies)
echo "Running schema and YAML tests..."
echo "-----------------------------------"
if [ -d "$PROJECT_ROOT/.venv" ]; then
    echo "Using virtualenv at $PROJECT_ROOT/.venv"
    source "$PROJECT_ROOT/.venv/bin/activate"
    python3 "$SCRIPT_DIR/test_working_dir.py"
    deactivate
else
    echo "No virtualenv found. Attempting to run with system Python..."
    echo "(This may fail if GUI dependencies are not installed)"
    python3 "$SCRIPT_DIR/test_working_dir.py" || {
        echo
        echo "NOTE: Schema tests require GUI dependencies (pydantic, ruamel.yaml)"
        echo "To run all tests, either:"
        echo "  1. Create virtualenv: python3 -m venv .venv && source .venv/bin/activate && pip install -e .[gui]"
        echo "  2. Install dependencies: pip3 install pydantic ruamel.yaml"
        exit 1
    }
fi

echo
echo "========================================"
echo "All working_dir tests passed!"
echo "========================================"
