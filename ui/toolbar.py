"""Toolbar and speed controls for Time Warp II."""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from TimeWarpII import TempleCodeApp


def _lighter(hex_color: str) -> str:
    """Return a slightly lighter version of a hex colour (for hover)."""
    try:
        hex_color = hex_color.lstrip("#")
        if len(hex_color) != 6:
            return "#505050"
        r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
        r = min(255, r + 25)
        g = min(255, g + 25)
        b = min(255, b + 25)
        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return "#505050"


class Toolbar:
    """Flat toolbar with Run/Stop/Open/Save buttons and speed sliders."""

    def __init__(self, app: TempleCodeApp) -> None:
        tk = app.tk
        self.app = app

        # --- Button bar ---
        self.button_frame = tk.Frame(app.root, bg="#252526")
        self.button_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        buttons = [
            ("▶  Run",          app.run_code,        "#4CAF50", "white",   True),
            ("⏹  Stop",         app.stop_code,       "#d32f2f", "white",   True),
            ("📂 Open",         app.load_file,       "#3e3e3e", "#d4d4d4", False),
            ("💾 Save",         app.save_file_quick,  "#3e3e3e", "#d4d4d4", False),
            ("🗑  Clear Editor", app.clear_editor,    "#3e3e3e", "#d4d4d4", False),
            ("📄 Clear Output", app.clear_output,     "#3e3e3e", "#d4d4d4", False),
            ("🎨 Clear Canvas", app.clear_canvas,     "#3e3e3e", "#d4d4d4", False),
        ]
        for label, cmd, bg, fg, bold in buttons:
            font = ("Arial", 10, "bold") if bold else ("Arial", 10)
            btn = tk.Button(
                self.button_frame, text=label, command=cmd,
                bg=bg, fg=fg, font=font, padx=12, pady=4,
                relief=tk.FLAT, bd=0, cursor="hand2",
            )
            btn.pack(side=tk.LEFT, padx=3)
            default_bg = bg
            btn.bind("<Enter>", lambda e, b=btn, c=default_bg: b.config(bg=_lighter(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=default_bg: b.config(bg=c))

        # --- Speed controls ---
        self.speed_frame = tk.Frame(app.root, bg="#252526")
        self.speed_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(self.speed_frame, text="Exec delay (ms):", font=("Arial", 9),
                 bg="#252526", fg="#888").pack(side=tk.LEFT, padx=(0, 2))
        self.exec_slider = tk.Scale(
            self.speed_frame, from_=0, to=500, orient=tk.HORIZONTAL,
            length=120, bg="#252526", fg="#aaa", troughcolor="#1e1e1e",
            highlightthickness=0, sliderlength=14, font=("Arial", 8),
            command=lambda v: setattr(app, 'exec_speed', int(v)),
        )
        self.exec_slider.set(app.exec_speed)
        self.exec_slider.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(self.speed_frame, text="Turtle delay (ms):", font=("Arial", 9),
                 bg="#252526", fg="#888").pack(side=tk.LEFT, padx=(0, 2))
        self.turtle_slider = tk.Scale(
            self.speed_frame, from_=0, to=200, orient=tk.HORIZONTAL,
            length=120, bg="#252526", fg="#aaa", troughcolor="#1e1e1e",
            highlightthickness=0, sliderlength=14, font=("Arial", 8),
            command=lambda v: setattr(app, 'turtle_speed', int(v)),
        )
        self.turtle_slider.set(app.turtle_speed)
        self.turtle_slider.pack(side=tk.LEFT)

    def apply_theme(self, tk, theme: dict) -> None:
        """Apply theme colours to toolbar buttons and speed controls."""
        btn_bg = theme.get("btn_bg", theme.get("input_bg", "#3e3e3e"))
        btn_fg = theme.get("btn_fg", theme.get("input_fg", "#d4d4d4"))

        for w in self.button_frame.winfo_children():
            if isinstance(w, tk.Button):
                if "Run" in str(w.cget("text")):
                    w.config(fg="white")
                else:
                    w.config(bg=btn_bg, fg=btn_fg)
                    w.bind("<Enter>", lambda e, b=w, c=btn_bg: b.config(bg=_lighter(c)))
                    w.bind("<Leave>", lambda e, b=w, c=btn_bg: b.config(bg=c))

        for f in (self.button_frame, self.speed_frame):
            f.config(bg=theme["frame_bg"])

        for w in self.speed_frame.winfo_children():
            if isinstance(w, tk.Label):
                w.config(bg=theme["frame_bg"], fg=theme.get("text_fg", "#aaa"))
            elif isinstance(w, tk.Scale):
                w.config(bg=theme["frame_bg"], fg=theme.get("text_fg", "#aaa"),
                         troughcolor=theme["text_bg"])
