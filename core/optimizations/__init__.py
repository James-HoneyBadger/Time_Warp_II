#!/usr/bin/env python3
"""
Performance optimizations package for Time Warp II.

Provides expression caching and GUI responsiveness helpers.
"""

from .performance_optimizer import ExpressionCache

from .gui_optimizer import (
    GUIOptimizer,
    initialize_gui_optimizer,
)

__all__ = [
    'ExpressionCache',
    'GUIOptimizer',
    'initialize_gui_optimizer',
]

__version__ = '1.0.0'