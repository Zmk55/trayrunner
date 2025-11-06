# Repository Guidelines

## Project Structure & Module Organization
TrayRunner provides two entry points: the GTK tray app in `src/trayrunner` and the Qt editor in `gui/trayrunner_gui`. Assets live under `src/trayrunner/icons` and `gui/assets`, with packaging helpers in `scripts/` and `tools/`. Tests sit in `tests/`, default YAML templates in `config/`, and AppImage outputs in `build_appimage/out/`.

## Build, Test, and Development Commands
Create a virtual environment and install dependencies with `pip install -r requirements.txt` (add `.[gui]` extras for editor work). Run `python -m trayrunner.app` and `python -m trayrunner_gui.app` during development. Use `make test` and `make fmt` before pushing; `make appimage` wraps `scripts/build_appimage.sh` to emit `TrayRunner-$(uname -m).AppImage` in `build_appimage/out/`. For focused checks run `pytest tests/test_yaml_roundtrip.py -v`.

## Coding Style & Naming Conventions
Keep to PEP 8 with four-space indentation. Files and functions stay snake_case, classes use CapWords, and constants remain UPPER_SNAKE_CASE. Avoid Qt imports under `src/trayrunner`; shared helpers should remain GUI-agnostic. Run `black --line-length 100` and `isort` (via `make fmt`) before committing. Prefer structured `logging` calls and add typed signatures on new public functions.

## Testing Guidelines
Add pytest files under `tests/` using the `test_*.py` pattern. Cover success and failure paths for YAML parsing, reload sockets, and working-directory handling. Run `pytest tests/ -v` after changes and mention targeted commands in PRs. Use temporary directories to exercise file-watch logic and keep shell helpers such as `tests/run_working_dir_tests.sh` deterministic.

## Commit & Pull Request Guidelines
Use conventional commit subjects (`feat:`, `fix:`, `refactor:`) in imperative mood under ~72 characters; add short bodies when context helps. Branch from `main` with descriptive slugs such as `feature/tray-icon-refresh`. PRs should summarise the change, link issues, list manual test commands, and attach screenshots or GIFs for GUI updates. Ensure generated artifacts stay out of version control.

## Configuration & Logging Tips
Default configs live in `config/default.yaml` and seed `~/.config/trayrunner/commands.yaml` on first run; update both when schemas shift. Runtime logs write to `~/.local/state/trayrunner/run.log` (tray) and `gui-debug.log` (editor) for troubleshooting. Keep secrets out of sample YAML and document required environment variables in `docs/` instead.
