#!/usr/bin/env python3
"""
Time Warp II Launcher
Simple launcher script for Time Warp II

Copyright © 2025 Honey Badger Universe
"""

import os
import sys
import subprocess


def main():
    """Launch Time Warp II GUI"""
    print("🚀 Time Warp II Launcher")
    print("=" * 50)

    # Get the directory where this launcher is located
    launcher_dir = os.path.dirname(os.path.abspath(__file__))
    # Go up one level to the project root
    project_root = os.path.dirname(launcher_dir)
    
    # Path to main TimeWarpII.py
    main_script = os.path.join(project_root, "TimeWarpII.py")
    
    if not os.path.exists(main_script):
        print(f"❌ Error: Cannot find TimeWarpII.py at {main_script}")
        sys.exit(1)
    
    # Launch the GUI
    try:
        os.chdir(project_root)
        subprocess.run([sys.executable, "TimeWarpII.py"])
    except Exception as e:
        print(f"❌ Failed to launch Time Warp II: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
