"""
Time Warp II Core Module
==============================

Copyright © 2025 Honey Badger Universe. All rights reserved.

Core functionality for Time Warp II, providing the main interpreter engine
and language execution capabilities.

This module serves as the central hub for:
- TempleCodeInterpreter: Main execution engine for the TempleCode language
- Language executor: TempleCode implementation (a fusion of BASIC, PILOT, and Logo)
- Utility functions: Helper classes and shared functionality

The core module is designed to be lightweight and focused on program execution,
with all GUI components handled by the main TimeWarpII.py application.

Supported Language:
- TempleCode: A fusion of BASIC, PILOT, and Logo for educational programming

Usage:
    from core.interpreter import TempleCodeInterpreter
    interpreter = TempleCodeInterpreter()
    interpreter.run_program("T:Hello World!")
"""

__version__ = "1.3.0"
__author__ = "Honey Badger Universe"

from .interpreter import TempleCodeInterpreter
from . import languages
from . import utilities

__all__ = ["TempleCodeInterpreter", "languages", "utilities"]
