"""
TempleCode Language Module
==========================

This package contains the TempleCode language executor -- the sole language
supported by Time Warp II.

TempleCode is a unified educational programming language that blends BASIC,
PILOT, and Logo into a single cohesive language, as if designed in the early
1990s for teaching programming fundamentals.

The executor handles parsing and execution of all TempleCode statements,
including BASIC structured programming, PILOT interactive text commands,
and Logo turtle graphics.
"""

from .templecode import TempleCodeExecutor

__all__ = [
    "TempleCodeExecutor",
]
