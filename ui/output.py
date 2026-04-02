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

        self.frame = tk.LabelFrame(
            parent, text="Output", padx=5, pady=5,
            bg="#252526", fg="#d4d4d4",
        )

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
        self.text.tag_configure("out_error", foreground=theme.get("output_error", "#f44747"))
        self.text.tag_configure("out_warn",  foreground=theme.get("output_warn",  "#cca700"))
        self.text.tag_configure("out_ok",    foreground=theme.get("output_ok",    "#6a9955"))

    def write(self, text: str, tag: str | None = None) -> None:
        """Append *text* to the output pane, optionally with a colour tag."""
        tk = self.app.tk
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

    def apply_theme(self, theme: dict) -> None:
        """Apply theme colours to the output area."""
        self.text.config(
            bg=theme["text_bg"], fg=theme["text_fg"],
            insertbackground=theme["text_fg"],
        )
        self.frame.config(bg=theme["editor_frame_bg"], fg=theme["editor_frame_fg"])
        self.setup_tags(theme)
