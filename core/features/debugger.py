"""Step debugger controller for Time Warp II.

Provides a state-machine that coordinates between the interpreter's
execution thread and the GUI thread to support:
  - breakpoints (set via the gutter or programmatically)
  - step over  (F10)
  - step into  (F11)  — treated identically for now
  - continue   (F5)
  - stop       (Shift+F5)
  - variable inspector snapshots
"""
from __future__ import annotations

import threading
from enum import Enum, auto
from typing import Any, Callable, Optional


class DebugState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    STEPPING = auto()


class DebugController:
    """State-machine controlling debug execution of a TempleCode program.

    The controller sits between the GUI and the interpreter.  When the
    interpreter thread hits a breakpoint or a step boundary it signals
    the controller, which pauses execution until the GUI issues the
    next command (step / continue / stop).
    """

    def __init__(self) -> None:
        self.state: DebugState = DebugState.STOPPED
        self._pause_event = threading.Event()
        self._pause_event.set()           # start un-paused
        self._step_requested = False

        # Callback fired on the GUI thread whenever we pause
        # Signature: on_pause(line_number: int, variables: dict)
        self.on_pause: Optional[Callable[[int, dict], None]] = None

        # Callback fired when debug session ends
        self.on_stop: Optional[Callable[[], None]] = None

        # Callback fired when we resume (so UI can remove highlight)
        self.on_resume: Optional[Callable[[], None]] = None

    # ------------------------------------------------------------------
    #  Commands issued by the GUI
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Begin a debug session (run until first breakpoint)."""
        self.state = DebugState.RUNNING
        self._step_requested = False
        self._pause_event.set()

    def step_over(self) -> None:
        """Execute exactly one line then pause again."""
        if self.state in (DebugState.PAUSED, DebugState.STOPPED):
            self.state = DebugState.STEPPING
            self._step_requested = True
            self._pause_event.set()       # un-block the interpreter thread

    def continue_(self) -> None:
        """Resume execution until the next breakpoint."""
        if self.state == DebugState.PAUSED:
            self.state = DebugState.RUNNING
            self._step_requested = False
            if self.on_resume:
                self.on_resume()
            self._pause_event.set()

    def stop(self) -> None:
        """Terminate the debug session."""
        self.state = DebugState.STOPPED
        self._step_requested = False
        self._pause_event.set()           # unblock so thread can exit
        if self.on_stop:
            self.on_stop()

    # ------------------------------------------------------------------
    #  Hook called by the interpreter's run loop (background thread)
    # ------------------------------------------------------------------

    def check_pause(self, interpreter) -> bool:
        """Called before each line executes.

        Returns ``True`` if execution should continue, ``False`` if it
        should terminate (STOPPED state).
        """
        if self.state == DebugState.STOPPED:
            return False

        line = interpreter.current_line
        hit_bp = line in interpreter.breakpoints

        should_pause = hit_bp or self._step_requested

        if should_pause:
            self._step_requested = False
            self.state = DebugState.PAUSED

            # Snapshot variables for the inspector
            variables = dict(interpreter.variables)

            # Fire the on_pause callback (will be dispatched to GUI thread)
            if self.on_pause:
                self.on_pause(line, variables)

            # Block the interpreter thread until GUI issues next command
            self._pause_event.clear()
            self._pause_event.wait()

            # After waking up, check if we were stopped while paused
            if self.state == DebugState.STOPPED:
                return False

            # If stepping, flag so next call pauses again
            if self.state == DebugState.STEPPING:
                self._step_requested = True

        return True

    # ------------------------------------------------------------------
    #  Convenience
    # ------------------------------------------------------------------

    @property
    def is_active(self) -> bool:
        return self.state != DebugState.STOPPED

    @property
    def is_paused(self) -> bool:
        return self.state == DebugState.PAUSED

    def snapshot_variables(self, interpreter) -> dict[str, Any]:
        """Return a dict of all user variables for the inspector panel."""
        out: dict[str, Any] = {}
        out.update(interpreter.variables)
        if interpreter.lists:
            for k, v in interpreter.lists.items():
                out[f"LIST {k}"] = v
        if interpreter.dicts:
            for k, v in interpreter.dicts.items():
                out[f"DICT {k}"] = v
        return out
