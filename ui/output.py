"""Output panel for Time Warp II."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TimeWarpII import TempleCodeApp


class OutputPanel:
    """Scrollable output text pane with colour-tagged messages."""

    def __init__(self, app: TempleCodeApp, parent) -> None:
        tk = app.tk
        from tkinter import scrolledtext

        self.app = app
        self._line_nums = False  # track output line-numbering state
        self._line_counter = 0   # line counter for numbering

        self.frame = tk.LabelFrame(
            parent, text="Output", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )

        # Toolbar row: Copy-all and line-numbers toggle buttons
        btn_row = tk.Frame(self.frame, bg="#252526")
        btn_row.pack(fill=tk.X, pady=(0, 3))
        copy_btn = tk.Button(
            btn_row, text="⎘ Copy All", font=("Arial", 8),
            bg="#3e3e3e", fg="#d4d4d4", padx=6, pady=2,
            relief=tk.FLAT, bd=0, cursor="hand2",
            command=self._copy_all,
        )
        copy_btn.pack(side=tk.RIGHT, padx=2)
        self._ln_btn = tk.Button(
            btn_row, text="# Lines", font=("Arial", 8),
            bg="#3e3e3e", fg="#d4d4d4", padx=6, pady=2,
            relief=tk.FLAT, bd=0, cursor="hand2",
            command=self._toggle_line_nums,
        )
        self._ln_btn.pack(side=tk.RIGHT, padx=2)

        self.text = scrolledtext.ScrolledText(
            self.frame, wrap=tk.WORD, font=("Courier", 10),
            bg="#1e1e1e", fg="#d4d4d4", insertbackground="#d4d4d4",
            takefocus=0,
        )
        self.text.pack(fill=tk.BOTH, expand=True)
        # Block keyboard input without setting state=DISABLED.
        self.text.bind("<Key>", lambda e: "break")

    def setup_tags(self, theme: dict) -> None:
        """Configure colour tags for error / warning / ok output."""
        self.text.tag_configure("out_error",   foreground=theme.get("output_error", "#f44747"))
        self.text.tag_configure("out_warn",    foreground=theme.get("output_warn",  "#cca700"))
        self.text.tag_configure("out_ok",      foreground=theme.get("output_ok",    "#6a9955"))
        self.text.tag_configure("out_linenum", foreground="#858585", font=("Courier", 9))

    def write(self, text: str, tag: str | None = None) -> None:
        """Append *text* to the output pane, optionally with a colour tag."""
        tk = self.app.tk
        if self._line_nums:
            # Prefix each newline-terminated line with a line number
            lines = text.split("\n")
            for i, line in enumerate(lines):
                if i < len(lines) - 1:
                    # Full lines get a number prefix
                    self._line_counter += 1
                    prefix = f"{self._line_counter:>4} | "
                    self.text.insert(tk.END, prefix, "out_linenum")
                    if tag:
                        self.text.insert(tk.END, line + "\n", tag)
                    else:
                        self.text.insert(tk.END, line + "\n")
                elif line:
                    # Trailing partial line (no trailing newline) — no number yet
                    if tag:
                        self.text.insert(tk.END, line, tag)
                    else:
                        self.text.insert(tk.END, line)
        else:
            if tag:
                self.text.insert(tk.END, text, tag)
            else:
                self.text.insert(tk.END, text)
        interp = self.app.interpreter
        if not (interp and getattr(interp, '_waiting_for_input', False)):
            self.text.see(tk.END)

    def clear(self) -> None:
        """Clear all text from the output pane."""
        self.text.delete("1.0", self.app.tk.END)
        self._line_counter = 0  # reset line counter on clear

    def _toggle_line_nums(self) -> None:
        """Toggle line-number prefixes on future output lines."""
        self._line_nums = not self._line_nums
        self._line_counter = 0
        active_bg = "#569cd6" if self._line_nums else "#3e3e3e"
        self._ln_btn.config(bg=active_bg)

    def _copy_all(self) -> None:
        """Copy the full output text to the system clipboard."""
        try:
            content = self.text.get("1.0", "end-1c")
            self.app.root.clipboard_clear()
            self.app.root.clipboard_append(content)
        except Exception:
            pass

    def apply_theme(self, theme: dict) -> None:
        """Apply theme colours to the output area."""
        self.text.config(
            bg=theme["text_bg"], fg=theme["text_fg"],
            insertbackground=theme["text_fg"],
        )
        self.frame.config(bg=theme["editor_frame_bg"], fg=theme["editor_frame_fg"])
        self.setup_tags(theme)
