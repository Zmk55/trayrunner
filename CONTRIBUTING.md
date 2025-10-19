# Contributing to TrayRunner

## 🧭 Overview
This document helps developers understand how to contribute to **TrayRunner** — whether you're fixing a bug, improving the Config GUI, or building the AppImage.

---

## 💻 Development Setup

### Requirements
- Linux (Ubuntu 20.04+ preferred)
- Python 3.9 or newer
- `virtualenv` or `venv`
- `git`
- Optional: Docker (for isolated testing)

### 1️⃣ Clone and Setup
```bash
git clone https://github.com/Zmk55/trayrunner.git
cd trayrunner
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2️⃣ Run Locally
Run the tray app or the config GUI independently:
```bash
# Tray app (uses GTK/AppIndicator)
python -m trayrunner.app

# Config GUI (PySide6)
python -m trayrunner_gui.app
```

### 3️⃣ File Locations
| Path | Description |
|------|--------------|
| `src/trayrunner/` | Tray app (system tray, config reload logic) |
| `gui/trayrunner_gui/` | Config GUI (Qt/PySide6) |
| `tools/` | Developer tools (linuxdeploy, helpers) |
| `scripts/` | Build scripts and packaging helpers |
| `tests/` | Test suite (pytest) |
| `build_appimage/` | Output directory for AppImage builds |
| `~/.config/trayrunner/commands.yaml` | User config file |

---

## 🧱 Building the AppImage (Developers)

TrayRunner uses **PyInstaller** + **linuxdeploy** to bundle both the tray app and the Config GUI into a single AppImage.

### 🧰 Prerequisites (on Ubuntu 20.04+)
```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip rsync patchelf file wget fuse libfuse2
```

### ⚙️ Setup linuxdeploy + Qt Plugin
```bash
# Download linuxdeploy tools automatically
bash tools/helpers/fetch_linuxdeploy.sh

# Or use the Makefile
make tools
```

### 🏗️ Build Commands
```bash
# Using the build script (recommended)
./scripts/build_appimage.sh

# Or using the Makefile
make appimage
```

The resulting AppImage will be in:
```
build_appimage/out/TrayRunner-$(uname -m).AppImage
```

### ✅ Test Run
```bash
chmod +x build_appimage/out/TrayRunner-$(uname -m).AppImage
./build_appimage/out/TrayRunner-$(uname -m).AppImage
```

---

## 🧩 Common Build Issues

| Issue | Fix |
|-------|-----|
| **Tray icon not showing** | Install AppIndicator dependencies (`sudo apt install python3-gi gir1.2-gtk-3.0 libayatana-appindicator3-1 gir1.2-ayatanaappindicator3-0.1`) |
| **GUI doesn't launch** | Ensure both executables (`trayrunner` + `trayrunner-gui`) are registered with linuxdeploy (`--executable`) |
| **glibc mismatch** | Build on Ubuntu 20.04 for maximum compatibility |
| **Wayland / GNOME 45+** | Enable the AppIndicator GNOME extension |

---

## 🧱 Release Process

1. Bump version number in `__init__.py` or metadata.
2. Run:
```bash
./scripts/build_appimage.sh
```
3. Test both AppImages (`x86_64`, `aarch64`) locally.
4. Upload to GitHub Releases with `SHA256SUMS`.
5. Verify tray → Settings → Open Config GUI works.

---

## 🧪 Testing & Logging

### Running Tests
```bash
# Run all tests
pytest tests/ -v

# Or use the Makefile
make test

# Run specific test
pytest tests/test_yaml_roundtrip.py -v
```

### Debug Logging
- Tray logs → `~/.local/state/trayrunner/run.log`
- GUI logs → `~/.local/state/trayrunner/gui-debug.log`
- Run GUI in debug mode:
```bash
python -m trayrunner_gui.app --debug
```

---

## 🧠 Code Style

- Follow **PEP 8**.
- Use **absolute imports** (avoid `..` relative imports in GUI).
- Keep GUI & core separated — no GUI dependencies in `src/trayrunner`.
- Commit messages: present tense, short, imperative ("Fix drag/drop reorder").

---

## 🙌 How to Contribute

1. Fork the repo & branch from `main`:
   ```bash
   git checkout -b feature/drag-drop-improvement
   ```
2. Make your changes.
3. Run and test both tray and GUI locally.
4. Submit a **pull request** with a clear title and short description.

---

## 🧰 Recommended Environment

| Component | Version |
|------------|----------|
| Ubuntu | 20.04 / 22.04 |
| Python | ≥3.9 |
| PySide6 | 6.5+ |
| linuxdeploy | latest continuous |
| AppIndicator libs | installed (system) |

---

## 🏁 Summary

- End users: just run the AppImage.  
- Developers: build or tweak freely using the provided scripts.  
- All builds use **linuxdeploy + PyInstaller** for consistency.  
- Always test tray + GUI together before pushing changes.