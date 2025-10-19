.PHONY: tools appimage test fmt clean help

# Default target
help:
	@echo "TrayRunner Development Makefile"
	@echo ""
	@echo "Available targets:"
	@echo "  tools     - Download linuxdeploy tools"
	@echo "  appimage  - Build AppImage (requires tools)"
	@echo "  test      - Run pytest tests"
	@echo "  fmt       - Format code (if formatters available)"
	@echo "  clean     - Clean build artifacts"
	@echo "  help      - Show this help"

tools:
	@echo "Downloading linuxdeploy tools..."
	bash tools/helpers/fetch_linuxdeploy.sh

appimage: tools
	@echo "Building AppImage..."
	bash scripts/build_appimage.sh

test:
	@echo "Running tests..."
	python -m pytest tests/ -v

fmt:
	@echo "Formatting code..."
	@if command -v black >/dev/null 2>&1; then \
		black --line-length 100 src/ gui/ tests/; \
	else \
		echo "black not available, skipping Python formatting"; \
	fi
	@if command -v isort >/dev/null 2>&1; then \
		isort src/ gui/ tests/; \
	else \
		echo "isort not available, skipping import sorting"; \
	fi

clean:
	@echo "Cleaning build artifacts..."
	rm -rf build_appimage/ dist/ build/ *.spec
	rm -rf __pycache__ src/__pycache__ gui/__pycache__ tests/__pycache__
	rm -rf .pytest_cache/ .coverage htmlcov/
	@echo "Clean complete"
