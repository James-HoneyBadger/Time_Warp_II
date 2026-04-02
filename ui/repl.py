"""Interactive REPL panel for Time Warp II."""
from __future__ import annotations

from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:
    from TimeWarpII import TempleCodeApp


class ReplPanel:
    """In-GUI REPL: type TempleCode line by line, see results immediately.

    The panel is added as an extra pane in the right-side vertical
    PanedWindow, sitting below the output area.  It has its own
    interpreter instance (or shares the main one) and supports
    Up/Down history navigation.
    """

    _BG = "#1e1e1e"
    _FG = "#d4d4d4"
    _PROMPT = "tc> "
    _PROMPT_COLOR = "#569cd6"
    _OUTPUT_COLOR = "#ce9178"
    _ERROR_COLOR = "#f44747"

    def __init__(self, app: TempleCodeApp, parent) -> None:
        tk = app.tk
        from tkinter import scrolledtext
        from core.interpreter import TempleCodeInterpreter

        self.app = app
        self._history: list[str] = []
        self._hist_idx: int = -1

        # Frame
        self.frame = tk.LabelFrame(
            parent, text="REPL", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )

        # Scrolled text for output history
        self.output = scrolledtext.ScrolledText(
            self.frame, wrap=tk.WORD, font=("Courier", 10),
            bg=self._BG, fg=self._FG, insertbackground=self._FG,
            height=6, takefocus=0,
        )
        self.output.pack(fill=tk.BOTH, expand=True)
        self.output.bind("<Key>", lambda e: "break")

        # Tags
        self.output.tag_configure("prompt", foreground=self._PROMPT_COLOR)
        self.output.tag_configure("result", foreground=self._OUTPUT_COLOR)
        self.output.tag_configure("error", foreground=self._ERROR_COLOR)

        # Input row
        input_frame = tk.Frame(self.frame, bg="#252526")
        input_frame.pack(fill=tk.X, pady=(3, 0))

        self._prompt_label = tk.Label(
            input_frame, text=self._PROMPT, font=("Courier", 10),
            bg="#252526", fg=self._PROMPT_COLOR,
        )
        self._prompt_label.pack(side=tk.LEFT)

        self.entry = tk.Entry(
            input_frame, font=("Courier", 10),
            bg=self._BG, fg=self._FG, insertbackground=self._FG,
            highlightbackground=self._BG, highlightcolor="#007acc",
            highlightthickness=2,
        )
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.entry.bind("<Return>", lambda e: self._submit())
        self.entry.bind("<Up>", lambda e: self._history_prev())
        self.entry.bind("<Down>", lambda e: self._history_next())

        # Dedicated interpreter for the REPL session
        self._fake_widget = _ReplOutputCapture()
        self._interp = TempleCodeInterpreter(output_widget=self._fake_widget)
        self._interp.running = True

        # Welcome
        self.output.insert(tk.END, "TempleCode REPL — type commands and press Enter\n", "prompt")
        self.output.insert(tk.END, "Type CLEAR to reset, VARS to show variables\n\n", "prompt")

    # ------------------------------------------------------------------
    #  Command submission
    # ------------------------------------------------------------------

    def _submit(self) -> None:
        tk = self.app.tk
        line = self.entry.get().strip()
        if not line:
            return

        self.entry.delete(0, tk.END)

        # Record history
        if not self._history or self._history[-1] != line:
            self._history.append(line)
        self._hist_idx = -1

        # Echo the command
        self.output.insert(tk.END, f"{self._PROMPT}{line}\n", "prompt")

        upper = line.upper()

        # Meta-commands
        if upper in ("CLEAR", "RESET"):
            self._reset_interpreter()
            self.output.insert(tk.END, "Session reset.\n", "result")
            self.output.see(tk.END)
            return

        if upper == "VARS":
            self._show_vars()
            self.output.see(tk.END)
            return

        if upper in ("QUIT", "EXIT"):
            self.output.insert(tk.END, "Use the IDE to close the REPL.\n", "result")
            self.output.see(tk.END)
            return

        # Execute in the interpreter
        self._fake_widget.clear()
        self._interp.running = True
        try:
            self._interp.execute_line(line)
        except Exception as exc:
            self.output.insert(tk.END, f"Error: {exc}\n", "error")

        # Display captured output
        captured = self._fake_widget.get_output()
        if captured:
            self.output.insert(tk.END, captured, "result")
            if not captured.endswith("\n"):
                self.output.insert(tk.END, "\n")

        self.output.see(tk.END)

    # ------------------------------------------------------------------
    #  History navigation
    # ------------------------------------------------------------------

    def _history_prev(self) -> str | None:
        if not self._history:
            return "break"
        if self._hist_idx == -1:
            self._hist_idx = len(self._history) - 1
        elif self._hist_idx > 0:
            self._hist_idx -= 1
        self._set_entry(self._history[self._hist_idx])
        return "break"

    def _history_next(self) -> str | None:
        if not self._history or self._hist_idx == -1:
            return "break"
        if self._hist_idx < len(self._history) - 1:
            self._hist_idx += 1
            self._set_entry(self._history[self._hist_idx])
        else:
            self._hist_idx = -1
            self._set_entry("")
        return "break"

    def _set_entry(self, text: str) -> None:
        tk = self.app.tk
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)

    # ------------------------------------------------------------------
    #  Helpers
    # ------------------------------------------------------------------

    def _reset_interpreter(self) -> None:
        from core.interpreter import TempleCodeInterpreter
        self._fake_widget.clear()
        self._interp = TempleCodeInterpreter(output_widget=self._fake_widget)
        self._interp.running = True

    def _show_vars(self) -> None:
        tk = self.app.tk
        variables = self._interp.variables
        if not variables:
            self.output.insert(tk.END, "(no variables)\n", "result")
            return
        for k, v in sorted(variables.items()):
            if k.startswith("__"):
                continue
            val = repr(v) if isinstance(v, str) else str(v)
            self.output.insert(tk.END, f"  {k} = {val}\n", "result")

    # ------------------------------------------------------------------
    #  Theme support
    # ------------------------------------------------------------------

    def apply_theme(self, theme: dict) -> None:
        self.frame.config(bg=theme.get("editor_frame_bg", "#252526"),
                          fg=theme.get("editor_frame_fg", "#d4d4d4"))
        self.output.config(bg=theme.get("text_bg", self._BG),
                           fg=theme.get("text_fg", self._FG))
        self.entry.config(bg=theme.get("input_bg", self._BG),
                          fg=theme.get("input_fg", self._FG))


class _ReplOutputCapture:
    """Lightweight output widget that captures text for the REPL."""

    def __init__(self) -> None:
        self._parts: list[str] = []

    def insert(self, _index, text) -> None:
        self._parts.append(str(text))

    def see(self, _index) -> None:
        pass

    def delete(self, _start, _end) -> None:
        self._parts.clear()

    def clear(self) -> None:
        self._parts.clear()

    def get_output(self) -> str:
        return "".join(self._parts)
