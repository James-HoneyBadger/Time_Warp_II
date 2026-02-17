#!/usr/bin/env python3
"""
Test helpers for Time Warp II interpreter tests.
"""

import sys
from pathlib import Path

# Ensure project root is on sys.path
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)


class FakeOutputWidget:
    """
    Minimal stand-in for a tkinter ScrolledText widget.

    Captures all text inserted by the interpreter so tests can inspect
    program output without requiring a running GUI.
    """

    def __init__(self):
        self._parts: list[str] = []

    # --- tkinter Text interface (subset used by the interpreter) ---

    def insert(self, _index, text):
        self._parts.append(str(text))

    def see(self, _index):
        pass

    def delete(self, _start, _end):
        self._parts.clear()

    # --- test helpers ---

    @property
    def raw(self) -> str:
        """Return all captured text concatenated."""
        return "".join(self._parts)

    @property
    def program_lines(self) -> list[str]:
        """Return output lines, excluding interpreter status messages."""
        STATUS_PREFIXES = ("\u2705", "\U0001F4CA", "\u26a0", "\u274c", "\U0001F6A8")
        return [
            line
            for line in self.raw.split("\n")
            if line.strip() and not any(line.strip().startswith(p) for p in STATUS_PREFIXES)
        ]

    @property
    def last_line(self) -> str:
        """Last meaningful program-output line (empty string if none)."""
        lines = self.program_lines
        return lines[-1].strip() if lines else ""


def run_program(code: str, *, language: str = "templecode",
                input_buffer: list[str] | None = None) -> FakeOutputWidget:
    """
    Execute *code* in a headless interpreter and return the output widget.

    Pass *input_buffer* as a list of strings that will be consumed by
    INPUT / A: commands in order (no GUI required).

    Usage::

        out = run_program('PRINT "hello"')
        assert out.last_line == "hello"

        out = run_program('INPUT X\\nPRINT X', input_buffer=["42"])
        assert out.last_line == "42"
    """
    from core.interpreter import TempleCodeInterpreter

    widget = FakeOutputWidget()
    interp = TempleCodeInterpreter(output_widget=widget)
    if input_buffer is not None:
        interp.input_buffer = list(input_buffer)
    interp.run_program(code, language=language)
    return widget


def turtle_state(code: str) -> dict:
    """
    Run *code* and return the turtle_graphics dict for inspection.

    Returns an empty dict if turtle graphics were never initialised.
    """
    from core.interpreter import TempleCodeInterpreter

    widget = FakeOutputWidget()
    interp = TempleCodeInterpreter(output_widget=widget)
    interp.run_program(code, language="templecode")
    return interp.turtle_graphics or {}


def run_with_interp(code: str, *, language: str = "templecode",
                    input_buffer: list[str] | None = None):
    """
    Execute *code* and return *(output_widget, interpreter)*.

    Useful when tests need to inspect interpreter state (variables,
    turtle_graphics, etc.) after execution.
    """
    from core.interpreter import TempleCodeInterpreter

    widget = FakeOutputWidget()
    interp = TempleCodeInterpreter(output_widget=widget)
    if input_buffer is not None:
        interp.input_buffer = list(input_buffer)
    interp.run_program(code, language=language)
    return widget, interp
