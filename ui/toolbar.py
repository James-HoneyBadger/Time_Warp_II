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
        self._btn_run: object = None
        self._btn_stop: object = None

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
            if "Run" in label:
                self._btn_run = btn
            elif "Stop" in label:
                self._btn_stop = btn

        # Separator
        tk.Label(self.button_frame, text="  │  ", bg="#252526", fg="#555").pack(side=tk.LEFT)

        # Speed presets
        for preset_label, exec_ms, turtle_ms in [("🐢 Slow", 200, 80), ("▷ Normal", 20, 20), ("⚡ Fast", 0, 0)]:
            b = tk.Button(
                self.button_frame, text=preset_label,
                bg="#3e3e3e", fg="#d4d4d4", font=("Arial", 9),
                padx=8, pady=4, relief=tk.FLAT, bd=0, cursor="hand2",
                command=lambda em=exec_ms, tm=turtle_ms: self._apply_preset(em, tm),
            )
            b.pack(side=tk.LEFT, padx=2)
            b.bind("<Enter>", lambda e, b=b: b.config(bg=_lighter("#3e3e3e")))
            b.bind("<Leave>", lambda e, b=b: b.config(bg="#3e3e3e"))

        # --- Speed controls ---
        self.speed_frame = tk.Frame(app.root, bg="#252526")
        self.speed_frame.pack(fill=tk.X, padx=10, pady=(0, 5))

        tk.Label(self.speed_frame, text="Exec delay (ms):", font=("Arial", 9),
                 bg="#252526", fg="#888").pack(side=tk.LEFT, padx=(0, 2))
        self._exec_val_label = tk.Label(self.speed_frame, text=f"{app.exec_speed}",
                                        font=("Arial", 9, "bold"), bg="#252526", fg="#aaa", width=4)
        self._exec_val_label.pack(side=tk.LEFT, padx=(0, 4))
        self.exec_slider = tk.Scale(
            self.speed_frame, from_=0, to=500, orient=tk.HORIZONTAL,
            length=120, bg="#252526", fg="#aaa", troughcolor="#1e1e1e",
            highlightthickness=0, sliderlength=14, font=("Arial", 8),
            showvalue=False,
            command=lambda v: self._on_exec_speed(int(v)),
        )
        self.exec_slider.set(app.exec_speed)
        self.exec_slider.pack(side=tk.LEFT, padx=(0, 15))

        tk.Label(self.speed_frame, text="Turtle delay (ms):", font=("Arial", 9),
                 bg="#252526", fg="#888").pack(side=tk.LEFT, padx=(0, 2))
        self._turtle_val_label = tk.Label(self.speed_frame, text=f"{app.turtle_speed}",
                                          font=("Arial", 9, "bold"), bg="#252526", fg="#aaa", width=4)
        self._turtle_val_label.pack(side=tk.LEFT, padx=(0, 4))
        self.turtle_slider = tk.Scale(
            self.speed_frame, from_=0, to=200, orient=tk.HORIZONTAL,
            length=120, bg="#252526", fg="#aaa", troughcolor="#1e1e1e",
            highlightthickness=0, sliderlength=14, font=("Arial", 8),
            showvalue=False,
            command=lambda v: self._on_turtle_speed(int(v)),
        )
        self.turtle_slider.set(app.turtle_speed)
        self.turtle_slider.pack(side=tk.LEFT)

        # Initial state: not running
        self.set_running_state(False)

    def _on_exec_speed(self, v: int) -> None:
        self.app.exec_speed = v
        self._exec_val_label.config(text=str(v))

    def _on_turtle_speed(self, v: int) -> None:
        self.app.turtle_speed = v
        self._turtle_val_label.config(text=str(v))

    def _apply_preset(self, exec_ms: int, turtle_ms: int) -> None:
        self.app.exec_speed = exec_ms
        self.app.turtle_speed = turtle_ms
        self.exec_slider.set(exec_ms)
        self.turtle_slider.set(turtle_ms)
        self._exec_val_label.config(text=str(exec_ms))
        self._turtle_val_label.config(text=str(turtle_ms))

    def set_running_state(self, is_running: bool) -> None:
        """Update Run/Stop button states to reflect whether a program is running."""
        try:
            if self._btn_run:
                self._btn_run.config(
                    state="disabled" if is_running else "normal",
                    bg="#388E3C" if is_running else "#4CAF50",
                )
            if self._btn_stop:
                self._btn_stop.config(
                    state="normal" if is_running else "disabled",
                    bg="#d32f2f" if is_running else "#7a1a1a",
                )
        except Exception:
            pass

    def apply_theme(self, theme: dict) -> None:
        """Apply theme colours to toolbar buttons and speed controls."""
        tk = self.app.tk
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
