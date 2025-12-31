#!/bin/bash

# Phase I Todo App - Setup Script
# Verifies Python 3.11+ installation and project readiness

set -e

echo "=== Phase I Todo App Setup ==="
echo ""

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    echo "Found Python $PYTHON_VERSION"

    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 11 ]; then
        echo "✓ Python version is compatible (3.11+)"
    else
        echo "✗ Python 3.11+ required (found $PYTHON_VERSION)"
        echo "Install Python 3.11+ in WSL 2:"
        echo "  sudo apt update"
        echo "  sudo apt install python3.11"
        exit 1
    fi
else
    echo "✗ Python 3 not found"
    echo "Install Python 3.11+ in WSL 2:"
    echo "  sudo apt update"
    echo "  sudo apt install python3.11"
    exit 1
fi

echo ""
echo "Checking WSL 2 environment..."
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo "✓ Running in WSL 2 environment"
else
    echo "⚠ Warning: Not detected as WSL 2 (may be native Linux)"
fi

echo ""
echo "Verifying project structure..."
if [ -d "src" ] && [ -d "src/models" ] && [ -d "src/services" ] && [ -d "src/cli" ]; then
    echo "✓ Project structure exists"
else
    echo "✗ Project structure incomplete"
    exit 1
fi

echo ""
echo "Checking main application..."
if [ -f "src/main.py" ]; then
    echo "✓ Main application found"
else
    echo "⚠ Main application not yet created"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "Phase I uses Python stdlib only (no pip install needed)"
echo ""
echo "To run the application:"
echo "  python3 src/main.py"
echo ""
echo "For detailed usage instructions:"
echo "  See specs/001-todo-crud/quickstart.md"
echo ""
