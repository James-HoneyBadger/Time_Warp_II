#!/bin/bash
################################################################################
# Time Warp II - Complete Setup & Run Script
# 
# This script:
# 1. Creates a Python virtual environment (if needed)
# 2. Installs all required Python dependencies
# 3. Launches the Time Warp II GUI
#
# Usage: ./run.sh [--clean] [--no-install]
#   --clean      Delete and recreate the virtual environment
#   --no-install Skip dependency installation
#
# Copyright © 2025 Honey Badger Universe
################################################################################

set -e  # Exit on any error

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
CLEAN=false
NO_INSTALL=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --clean)
            CLEAN=true
            shift
            ;;
        --no-install)
            NO_INSTALL=true
            shift
            ;;
        *)
            shift
            ;;
    esac
done

VENV_DIR="$SCRIPT_DIR/venv"
VENV_PYTHON="$VENV_DIR/bin/python"
VENV_ACTIVATE="$VENV_DIR/bin/activate"

ensure_python() {
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 not found!${NC}"
        echo "Please install Python 3.9 or higher from https://www.python.org/"
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    echo -e "${GREEN}✓${NC} Python $PYTHON_VERSION found"
    echo ""
}

ensure_venv() {
    echo -e "${YELLOW}[2/4]${NC} Setting up Virtual Environment..."

    if [ "$CLEAN" = true ] && [ -d "$VENV_DIR" ]; then
        echo "🗑️  Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    fi

    if [ ! -d "$VENV_DIR" ]; then
        echo "📦 Creating virtual environment..."
        python3 -m venv "$VENV_DIR"
    else
        echo -e "${GREEN}✓${NC} Virtual environment already exists"
    fi

    if [ ! -f "$VENV_PYTHON" ]; then
        echo -e "${RED}❌ Virtual environment python not found${NC}"
        echo "Repairing broken venv..."
        python3 -m venv --clear "$VENV_DIR"
    fi

    if [ ! -f "$VENV_PYTHON" ]; then
        echo -e "${RED}❌ Failed to create a usable virtual environment${NC}"
        exit 1
    fi

    if ! "$VENV_PYTHON" -m ensurepip --upgrade >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} ensurepip unavailable; attempting to repair pip in the virtual environment"
        python3 -m venv --clear "$VENV_DIR"
    fi

    if ! "$VENV_PYTHON" -c "import sys; print(sys.executable)" >/dev/null 2>&1; then
        echo -e "${RED}❌ Broken virtual environment: cannot run Python from venv${NC}"
        exit 1
    fi

    echo -e "${GREEN}✓${NC} Virtual environment ready"
    echo ""
}

activate_venv() {
    echo "🔗 Activating virtual environment..."

    if [ -f "$VENV_ACTIVATE" ]; then
        # shellcheck disable=SC1090
        source "$VENV_ACTIVATE"
        echo -e "${GREEN}✓${NC} Virtual environment activated"
    else
        echo -e "${RED}❌ Failed to activate virtual environment${NC}"
        exit 1
    fi
    echo ""
}

ensure_package() {
    local package_name="$1"
    local pip_name="${2:-$package_name}"
    local display_name="$3"

    if "$VENV_PYTHON" -c "import $package_name" >/dev/null 2>&1; then
        echo "  ✓ $display_name already installed"
        return 0
    fi

    echo "  📦 Installing missing $display_name..."
    if "$VENV_PYTHON" -m pip install "$pip_name"; then
        echo "  ✓ $display_name installed successfully"
        return 0
    fi

    echo -e "${YELLOW}  ⚠${NC} $display_name could not be installed automatically"
    return 1
}

install_dependencies() {
    if [ "$NO_INSTALL" = true ]; then
        echo -e "${YELLOW}[3/4]${NC} Skipping dependency installation (--no-install)"
        return 0
    fi

    echo -e "${YELLOW}[3/4]${NC} Installing Python dependencies..."

    if [ -f "requirements.txt" ]; then
        echo "📚 Installing packages from requirements.txt..."
        if "$VENV_PYTHON" -m pip install --upgrade pip setuptools wheel; then
            echo -e "${GREEN}✓${NC} Pip tooling updated"
        fi

        if "$VENV_PYTHON" -m pip install -r requirements.txt; then
            echo -e "${GREEN}✓${NC} All dependencies installed successfully"
        else
            echo -e "${YELLOW}⚠️  Some dependencies may have failed to install${NC}"
            echo "    (This is often OK - many features work without optional dependencies)"
        fi
    else
        echo -e "${RED}❌ requirements.txt not found!${NC}"
        exit 1
    fi
    echo ""
}

verify_dependencies() {
    echo -e "${YELLOW}[4/4]${NC} Verifying installation..."

    if "$VENV_PYTHON" -c "import tkinter" >/dev/null 2>&1; then
        echo "  ✓ tkinter available"
    else
        echo -e "${RED}  ❌ tkinter not available!${NC}"
        echo "  This is required. If missing after installation, try:"
        echo "    Ubuntu/Debian: sudo apt-get install python3-tk"
        echo "    Fedora: sudo dnf install python3-tkinter"
        echo "    macOS: brew install python-tk"
    fi

    ensure_package "pygame" "pygame-ce" "pygame (multimedia support)" || true
    ensure_package "pygments" "pygments" "pygments (syntax highlighting)" || true
    ensure_package "PIL" "Pillow" "Pillow (image processing)" || true

    echo ""
}

echo -e "${BLUE}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║        Time Warp II - TempleCode Language IDE              ║${NC}"
echo -e "${BLUE}║              Initialization & Setup Script                 ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

ensure_python
ensure_venv
activate_venv
install_dependencies
verify_dependencies

# Verify TimeWarpII.py exists
if [ ! -f "TimeWarpII.py" ]; then
    echo -e "${RED}❌ TimeWarpII.py not found!${NC}"
    exit 1
fi

echo -e "${GREEN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║     🚀 Launching Time Warp II...                        ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Run the IDE with the venv interpreter explicitly
"$VENV_PYTHON" TimeWarpII.py "$@"

deactivate 2>/dev/null || true

echo ""
echo -e "${BLUE}Goodbye from Time Warp II!${NC}"
