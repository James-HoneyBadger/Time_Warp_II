#!/bin/bash
# Time Warp II Launch Script
# This script launches Time Warp II GUI
# Copyright © 2025 Honey Badger Universe

echo "🚀 Launching Time Warp II..."

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project root directory (parent of scripts)
cd "$SCRIPT_DIR/.."

# Check if Python 3 is available
if command -v python3 >/dev/null 2>&1; then
    echo "✅ Found Python 3"
    python3 TimeWarpII.py
elif command -v python >/dev/null 2>&1; then
    echo "✅ Found Python"
    python TimeWarpII.py
else
    echo "❌ Python not found. Please install Python 3.9 or higher."
    exit 1
fi

echo "👋 Time Warp II session ended."